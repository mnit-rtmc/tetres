# -*- coding: utf-8 -*-
import datetime

from pyticas.tool import tb
from pyticas.ttypes import Route
from pyticas_tetres.ttypes import ActionLogInfo

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import json as python_json

from flask import request
from pyticas_server import protocol as prot
from pyticas_tetres.da.actionlog import ActionLogDataAccess
from pyticas_tetres.util import actionlog
from pyticas_tetres import admin_auth



class TeTRESApi(object):
    def __init__(self, app, name, json2obj, da_class, uris, **kwargs):
        self.app = app
        self.name = name
        self.datatype = name
        self.json2obj = json2obj
        self.da_class = da_class
        self.uris = uris
        self.do_post_process_fields = None # if these fields are updated, set `handled` field as False in action log
        """:type: list[str] """
        self.requires_auth = kwargs.get('requires_auth', False)

    def add_actionlog(self, action_type, tablename, target_id, data_desc, handled=False, dbsession=None):
        """

        :type action_type: str
        :type tablename: str
        :type target_id: int
        :type data_desc: str
        :type handled: bool
        :type dbsession: sqlalchemy.orm.Session
        :rtype; Union(pyticas_tetres.db.model.ActionLog, False)
        """
        return actionlog.add(action_type, self.datatype, tablename, target_id, data_desc, handled, dbsession)


    def register(self):
        for fname, value in self.uris.items():
            if not hasattr(self, fname):  # or not hasattr(self.data_access_class, fname):
                continue
            if fname == 'update' and len(value) == 3:
                (uri, methods, do_post_process_fields) = value
                if do_post_process_fields:
                    self.do_post_process_fields = do_post_process_fields
            else:
                (uri, methods) = value
            self.app.add_url_rule(uri,
                                  'tetres_%s_%s' % (self.name, fname),
                                  getattr(self, fname),
                                  methods=methods)

    def insert(self):

        if self.requires_auth and not admin_auth.check_auth():
            return admin_auth.authenticate()

        # db session is created and share the session with all other database access module
        da_instance = self.da_class()

        json_data = request.form.get('data')
        obj = self.json2obj(json_data)

        # obj.id = da_instance.da_base.get_next_pk()
        model_data = da_instance.insert(obj)

        if model_data is False or not da_instance.commit():
            da_instance.close_session()
            return prot.response_fail("Fail to insert data")

        inserted_id = model_data.id

        self.add_actionlog(ActionLogDataAccess.INSERT,
                           da_instance.get_tablename(),
                           model_data.id,
                           ActionLogDataAccess.data_description(self.datatype, model_data),
                           handled=False,
                           dbsession=da_instance.get_session())

        da_instance.close_session()

        return prot.response_success(obj=inserted_id)

    def insert_all(self):

        if self.requires_auth and not admin_auth.check_auth():
            return admin_auth.authenticate()

        json_str = request.form.get('data')
        json_str_list = python_json.loads(json_str)

        # db session is created and share the session with all other database access module
        da_instance = self.da_class()

        obj_list = []
        dict_list = []
        for idx, json_data in enumerate(json_str_list):
            obj = self.json2obj(json_data)
            dict_list.append(obj.get_dict())
            obj_list.append(obj)

        inserted_ids = da_instance.bulk_insert(dict_list)
        if not inserted_ids or not da_instance.commit():
            da_instance.close_session()
            return prot.response_fail("Fail to add data into database")

        tablename = da_instance.get_tablename()
        for obj_id in inserted_ids:
            insertedObj = da_instance.get_model_by_id(obj_id)
            self.add_actionlog(ActionLogDataAccess.INSERT,
                               tablename,
                               obj_id,
                               ActionLogDataAccess.data_description(self.datatype, insertedObj),
                               handled=False)

        da_instance.close_session()
        return prot.response_success()

    def list(self):
        if self.requires_auth and not admin_auth.check_auth():
            return admin_auth.authenticate()

        # db session is created and share the session with all other database access module
        da_instance = self.da_class()

        data_list = da_instance.list()
        da_instance.close_session()
        return prot.response_success({'list': data_list})
        # return prot.response_success(self.da.list())

    def list_by_year(self):
        if self.requires_auth and not admin_auth.check_auth():
            return admin_auth.authenticate()

        year = request.form.get('year')

        # db session is created and share the session with all other database access module
        da_instance = self.da_class()

        if year:
            obj_list = [obj for obj in da_instance.list_by_year([year])]
        else:
            obj_list = [obj for obj in da_instance.list_by_year(None)]

        da_instance.close_session()

        return prot.response_success({'list': obj_list}, True)

    def get_by_id(self):
        if self.requires_auth and not admin_auth.check_auth():
            return admin_auth.authenticate()

        id = request.form.get('id')

        # db session is created and share the session with all other database access module
        da_instance = self.da_class()

        obj = da_instance.get_by_id(id)
        if not obj:
            da_instance.close_session()
            return prot.response_invalid_request()

        da_instance.close_session()

        return prot.response_success(obj)

    def get_by_name(self):
        if self.requires_auth and not admin_auth.check_auth():
            return admin_auth.authenticate()

        name = request.form.get('name')

        # db session is created and share the session with all other database access module
        da_instance = self.da_class()

        obj = da_instance.get_by_name(name)
        if not obj:
            da_instance.close_session()
            return prot.response_invalid_request()

        da_instance.close_session()
        return prot.response_success(obj)

    def _is_handled(self, exobj, newobj):
        if not self.do_post_process_fields:
            return True
        for field_name in self.do_post_process_fields:
            v1 = getattr(exobj, field_name, None)
            v2 = getattr(newobj, field_name, None)
            is_route_v1 = isinstance(v1, Route)
            is_route_v2 = isinstance(v2, Route)
            if not is_route_v1 or not is_route_v2:
                if v1 != v2:
                    return False
            else: # both items are Route instances
                if v1.rnodes != v2.rnodes:
                    return False
        return True

    def update(self):
        if self.requires_auth and not admin_auth.check_auth():
            return admin_auth.authenticate()

        id = request.form.get('id')
        json_data = request.form.get('data')

        # db session is created and share the session with all other database access module
        da_instance = self.da_class()

        obj = self.json2obj(json_data)
        exobj = da_instance.get_by_id(id)
        if not exobj:
            da_instance.close_session()
            return prot.response_fail("item does not exist (id={})".format(id))

        is_updated = da_instance.update(id, obj.get_dict())
        if not is_updated:
            da_instance.close_session()
            return prot.response_fail("fail to update (id={})".format(id))

        if not da_instance.commit():
            return prot.response_fail("fail to update (id={})".format(id))

        callback = getattr(self, 'on_update_success', None)
        if callback:
            callback(obj, da_instance.get_session())

        exobj = da_instance.get_by_id(id)
        self.add_actionlog(ActionLogDataAccess.UPDATE,
                           da_instance.get_tablename(),
                           id,
                           ActionLogDataAccess.data_description(self.datatype, exobj),
                           self._is_handled(exobj, obj),
                           dbsession=da_instance.get_session())

        da_instance.close_session()

        return prot.response_success(obj=id)

    def delete(self):
        if self.requires_auth and not admin_auth.check_auth():
            return admin_auth.authenticate()

        json_str = request.form.get('ids')
        ids = python_json.loads(json_str)

        # db session is created and share the session with all other database access module
        da_instance = self.da_class()

        deleted_objs = [da_instance.get_by_id(id) for id in ids]
        deleted_objs = [v for v in deleted_objs if v]
        ex_ids = [v.id for v in deleted_objs if v]
        is_deleted = da_instance.delete_items(ex_ids, print_exception=True)
        if not is_deleted:
            da_instance.close_session()
            return prot.response_fail("fail to delete items")

        if not da_instance.commit():
            return prot.response_fail("fail to delete items")

        callback = getattr(self, 'on_delete_success', None)
        if callback:
            callback(deleted_objs, da_instance.get_session())

        for idx, obj_id in enumerate(ex_ids):
            deletedObj = deleted_objs[idx]
            self.add_actionlog(ActionLogDataAccess.DELETE,
                               da_instance.get_tablename(),
                               obj_id,
                               ActionLogDataAccess.data_description(self.datatype, deletedObj),
                               handled=True,
                               dbsession=da_instance.get_session())

        da_instance.close_session()

        return prot.response_success(ids)

    def years(self):
        if self.requires_auth and not admin_auth.check_auth():
            return admin_auth.authenticate()

        # db session is created and share the session with all other database access module
        da_instance = self.da_class()

        years = da_instance.years()

        da_instance.close_session()
        return prot.response_success(years)

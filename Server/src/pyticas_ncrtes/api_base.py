# -*- coding: utf-8 -*-
"""
pyticas_ncrtes.api_base
=========================
- API handler class in general way.
- a specific API handler can use this API to serve insert/delete/update/list functions
"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import json as python_json

from flask import request
from sqlalchemy import exc
from pyticas_server import protocol as prot

class NCRTESApi(object):

    def __init__(self, app, name, json2obj, da_class, uris):
        self.app = app
        self.name = name
        self.json2obj = json2obj
        self.data_access_class = da_class
        self.uris = uris

    def register(self):
        for fname, (uri, methods) in self.uris.items():
            if not hasattr(self, fname):# or not hasattr(self.data_access_class, fname):
                continue
            self.app.add_url_rule(uri,
                                  'ncrtes_%s_%s' % (self.name, fname),
                                  getattr(self, fname),
                                  methods=methods)

    def insert(self):
        json_data = request.form.get('data')
        obj = self.json2obj(json_data)
        da_instance = self.data_access_class()
        try:
            model_data = da_instance.insert(obj, autocommit=True)
        except exc.IntegrityError:
            da_instance.close()
            return prot.response_fail("Integrity Error")
        except:
            da_instance.close()
            return prot.response_fail("Unknown Error")

        da_instance.close()

        callback = getattr(self, 'on_insert_success', None)
        if callback:
            callback(obj)

        return prot.response_success(obj=model_data.id)

    def insert_all(self):
        json_str = request.form.get('data')
        json_str_list = python_json.loads(json_str)
        da_instance = self.data_access_class()
        obj_list = []
        for json_data in json_str_list:
            obj = self.json2obj(json_data)
            obj_list.append(obj)
            try:
                model_data = da_instance.insert(obj, autocommit=False)
            except exc.IntegrityError:
                print('integrity error')
                da_instance.rollback()
                da_instance.close()
                return prot.response_fail("Integrity Error")
            except Exception as ex:
                print('Unknown error')
                print(ex)
                da_instance.rollback()
                da_instance.close()
                return prot.response_fail("Unknown Error")

        da_instance.commit()
        da_instance.close()

        callback = getattr(self, 'on_insert_all_success', None)
        if callback:
            callback(obj_list)

        return prot.response_success()

    def list(self):
        da_instance = self.data_access_class()
        data_list = da_instance.list()
        da_instance.close()
        return prot.response_success({'list': data_list})
        # return prot.response_success(self.da.list())

    def list_by_year(self):
        year = request.form.get('year')
        da_instance = self.data_access_class()
        if year:
            obj_list = [obj for obj in da_instance.list_by_year([year])]
        else:
            obj_list = [obj for obj in da_instance.list_by_year(None) ]
        da_instance.close()
        return prot.response_success({'list': obj_list}, True)

    def get_by_id(self):
        id = request.form.get('id')
        da_instance = self.data_access_class()
        obj = da_instance.get_by_id(id)
        da_instance.close()
        if not obj:
            return prot.response_invalid_request()
        return prot.response_success(obj)

    def get_by_name(self):
        name = request.form.get('name')
        da_instance = self.data_access_class()
        obj = da_instance.get_by_name(name)
        da_instance.close()
        if not obj:
            return prot.response_invalid_request()
        return prot.response_success(obj)

    def update(self):
        id = request.form.get('id')
        json_data = request.form.get('data')
        da_instance = self.data_access_class()
        obj = self.json2obj(json_data)
        updated = da_instance.update(id, obj.get_dict(), autocommit=True)
        da_instance.close()
        if updated:
            callback = getattr(self, 'on_update_success', None)
            if callback:
                callback(obj)
            return prot.response_success(obj=id)
        else:
            return prot.response_fail("fail to update (id={})".format(id))

    # def delete_single(self):
    #     id = request.form.get('id')
    #     if not id:
    #         return prot.response_invalid_request()
    #     da_instance = self.data_access_class()
    #     obj = da_instance.get_by_id(id)
    #     if not obj:
    #         return prot.response_fail('not exist')
    #     deleted = da_instance.delete(id, autocommit=True)
    #     da_instance.close()
    #     if deleted:
    #         return prot.response_success(obj=id)
    #     else:
    #         return prot.response_fail("fail to delete (id=%d)" % id)

    def delete(self):
        json_str = request.form.get('ids')
        ids = python_json.loads(json_str)
        da_instance = self.data_access_class()
        has_error = False
        deleted_objs = []
        for id in ids:
            try:
                ex = da_instance.get_by_id(id)
                deleted = da_instance.delete(id, autocommit=False)
            except:
                has_error = True
                break

            if not deleted:
                has_error = True
                break
            else:
                deleted_objs.append(ex)

        if has_error:
            da_instance.rollback()
            da_instance.close()
            return prot.response_fail("fail to delete items")

        da_instance.commit()
        da_instance.close()

        callback = getattr(self, 'on_delete_success', None)
        if callback:
            callback(deleted_objs)

        return prot.response_success(ids)

    def years(self):
        da_instance = self.data_access_class()
        years = da_instance.years()
        da_instance.close()
        return prot.response_success(years)

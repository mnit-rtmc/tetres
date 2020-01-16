# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
from inspect import isfunction

from sqlalchemy import extract
from sqlalchemy.orm.exc import NoResultFound

from pyticas_tetres.db.tetres import model_yearly
from pyticas.tool import json, tb
from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.tt import TravelTimeDataAccess
from pyticas_tetres.db.tetres import model


class ExtDataAccessBase(DataAccessBase):
    def __init__(self, year, dbModel, extModel, dataInfoType, **kwargs):
        """
        :param dbModel: DB model for tt_<ext data> table defined in `pyticas_tetres.db.model`
        :param extModel: DB model for external data defined in `pyticas_tetres.db.model`
        :param dataInfoType:  corresponding class to DB model defined in `pyticas_tetres.ttrms_types`
        """
        super().__init__(dbModel, dataInfoType, **kwargs)
        self.year = year
        self.extModel = extModel
        self.ttModel = model_yearly.get_tt_table(year)
        self.ttDA = TravelTimeDataAccess(year)

    def list(self, ttri_id, sdt, edt, **kwargs):
        """ search data overlapped with the given data range

        :type ttri_id: int
        :type sdt: datetime.datetime
        :type edt: datetime.datetime
        :return:
        """
        if ttri_id and sdt and edt:
            qry = (self.session.query(self.dbModel).join(self.ttModel).join(self.extModel)
                   .filter(self.ttModel.route_id == ttri_id)
                   .filter(self.ttModel.time <= edt)
                   .filter(self.ttModel.time >= sdt))
        else:
            qry = (self.session.query(self.dbModel).join(self.ttModel).join(self.extModel))

        weekdays = kwargs.get('weekdays', None)
        if weekdays:
            qry.filter(extract('dow', self.ttModel.time) in weekdays)

        as_model = kwargs.get('as_model', False)
        data_list = []
        for model_data in qry:
            if not as_model:
                try:
                    data_list.append(self.to_info(model_data))
                except Exception as ex:
                    print('=> ', ttri_id, sdt, edt, model_data)
                    raise ex
            else:
                data_list.append(model_data)
        return data_list

    def delete_range(self, ttri_id, sdt, edt, **kwargs):
        """
        :type ttri_id: int
        :type sdt: datetime.datetime
        :type edt: datetime.datetime
        """
        print_exception = kwargs.get('print_exception', False)
        item_ids = kwargs.get('item_ids', None)

        try:
            tt_ids = (self.session.query(self.ttModel.id)
                      .filter(self.ttModel.route_id == ttri_id)
                      .filter(self.ttModel.time <= edt)
                      .filter(self.ttModel.time >= sdt))

            qry = (self.session.query(self.dbModel).filter(self.dbModel.tt_id.in_(tt_ids.subquery())))

            if item_ids and hasattr(self.dbModel, 'oc_field'):
                qry = qry.filter(getattr(self.dbModel, self.dbModel.oc_field).in_(item_ids))

            qry.delete(synchronize_session=False)
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def delete_all_for_a_route(self, ttri_id, **kwargs):
        """
        :type ttri_id: int
        """
        print_exception = kwargs.get('print_exception', False)
        try:
            tt_ids = (self.session.query(self.ttModel.id)
                      .filter(self.ttModel.route_id == ttri_id))
            stmt = self.dbModel.__table__.delete(synchronize_session=False).where(
                self.dbModel.tt_id.in_(tt_ids.subquery()))

            self.session.execute(stmt)
            # conn.engine.execute(stmt)
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def delete_if_route_is_deleted(self, **kwargs):
        """
        :type ttri_id: int
        """
        print_exception = kwargs.get('print_exception', False)

        sess = self.session
        dbModel = self.dbModel
        ttModel = self.ttModel
        try:
            ex = sess.query(ttModel).filter(ttModel.id == dbModel.tt_id)
            qry1 = sess.query(dbModel).filter(~ex.exists())
            qry1.delete(synchronize_session=False)
            ex = sess.query(model.TTRoute).filter(ttModel.route_id == model.TTRoute.id).filter(
                ttModel.id == dbModel.tt_id)
            qry2 = sess.query(dbModel).filter(~ex.exists())
            qry2.delete(synchronize_session=False)
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def to_model(self, info_data, data_info_type=None):
        """ change info type to DB model type

        :param info_data: corresponding class instance to DB model
        :return: converted DB model data
        """
        route_attrs = data_info_type._route_attrs_ if data_info_type else self.route_attrs
        dt_attrs = data_info_type._dt_attrs_ if data_info_type else self.dt_attrs
        rel_attrs = data_info_type._rel_attrs_ if data_info_type else self.rel_attrs
        enum_attrs = data_info_type._enum_attrs_ if data_info_type else self.enum_attrs

        model_data = self.dbModel()
        for key, value in info_data.__dict__.items():
            valueToSet = value
            if key in dt_attrs:
                if value:
                    valueToSet = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            elif key in route_attrs:
                valueToSet = json.dumps(value, only_name=True)
            elif key in enum_attrs:
                if not value:
                    valueToSet = value
                elif isinstance(value.value, tuple):
                    valueToSet = value.value[0]
                else:
                    valueToSet = value.value
            setattr(model_data, key, valueToSet)

        for attr_name, rel_info in rel_attrs.items():
            value = getattr(info_data, attr_name, None)
            valueToSet = value
            if value:
                continue
            rel_key = rel_info['key']
            rel_model_cls = rel_info['model_cls']
            if isfunction(rel_model_cls):
                rel_model_cls = rel_model_cls(self.year)
            try:
                rel_id = getattr(info_data, rel_key)
                if rel_id:
                    with self.session.no_autoflush:
                        valueToSet = self.session.query(rel_model_cls).filter(rel_model_cls.id == rel_id).one()
            except NoResultFound as ex:
                pass

            setattr(model_data, attr_name, valueToSet)

        return model_data

# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from sqlalchemy import Time, cast
from sqlalchemy import and_, extract
from sqlalchemy import asc
from sqlalchemy import func

from pyticas_tetres.db.tetres import model_yearly
from pyticas.tool import tb
from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import TravelTimeInfo


class TravelTimeDataAccess(DataAccess):
    def __init__(self, year, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model_yearly.get_tt_table(year), TravelTimeInfo,
                                      **kwargs)

    def list(self, **kwargs):
        """
        :rtype: list[TravelTimeInfo]
        """
        return self.da_base.list(**kwargs)

    def list_by_generator(self, **kwargs):
        """
        :rtype: list[TravelTimeInfo]
        """
        return self.da_base.list_as_generator(**kwargs)

    def list_with_deleted_route(self, **kwargs):
        """
        :rtype: list[TravelTimeInfo]
        """
        res = []
        as_model = kwargs.get('as_model', False)
        sess = self.da_base.session
        dbModel = self.da_base.dbModel
        ex = sess.query(model.TTRoute).filter(dbModel.route_id == model.TTRoute.id)
        if ex.count():
            qry = sess.query(dbModel).filter(~ex.exists())
            for m in qry:
                if as_model:
                    res.append(m)
                else:
                    res.append(self.da_base.to_info(m))
        return res

    def delete_if_route_is_deleted(self, **kwargs):
        """
        :rtype: bool
        """
        print_exception = kwargs.get('print_exception', False)

        sess = self.get_session()
        dbModel = self.da_base.dbModel
        try:
            ex = sess.query(model.TTRoute).filter(dbModel.route_id == model.TTRoute.id)
            if ex.count():
                sess.query(dbModel).filter(~ex.exists()).delete(synchronize_session=False)
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def generator_by_period(self, ttr_id, prd, **kwargs):
        """
        :type ttr_id: int
        :type prd: pyticas.ttypes.Period
        :rtype: list[TravelTimeInfo]
        """
        as_model = kwargs.get('as_model', False)
        limit = kwargs.get('limit', None)
        group_by = kwargs.get('group_by', None)
        order_by = kwargs.get('order_by', None)
        window_size = kwargs.get('window_size', 1000)

        sfield, sdt = 'time', prd.start_date
        efield, edt = 'time', prd.end_date
        qry = (self.da_base.session.query(self.da_base.dbModel)
               .filter(getattr(self.da_base.dbModel, 'route_id') == ttr_id)
               .filter(getattr(self.da_base.dbModel, sfield) <= edt)
               .filter(getattr(self.da_base.dbModel, efield) > sdt))

        # apply 'order by'
        if order_by and isinstance(order_by, tuple):
            # e.g. order_by = ('id', 'desc')
            # e.g. order_by = ('name', 'asc')
            qry = qry.order_by(getattr(getattr(self.da_base.dbModel, order_by[0]), order_by[1])())

        if group_by:
            if isinstance(group_by, str):
                qry = qry.group_by(getattr(self.da_base.dbModel, group_by))
            else:
                qry = qry.group_by(group_by)

        # apply 'limit'
        if limit:
            qry = qry.limit(limit)

        for m in self.da_base.query_generator(qry, window_size):
            if as_model:
                yield m
            else:
                yield self.da_base.to_info(m)

    def list_by_period(self, ttr_id, prd, **kwargs):
        """
        :type ttr_id: int
        :type prd: pyticas.ttypes.Period
        :rtype: list[pyticas_tetres.ttypes.TravelTimeInfo]
        """
        weekdays = kwargs.get('weekdays', None)
        window_size = kwargs.get('window_size', 1000)
        start_time = kwargs.get('start_time', None)
        end_time = kwargs.get('end_time', None)
        as_model = kwargs.get('as_model', False)
        order_by = kwargs.get('order_by', None)
        limit = kwargs.get('limit', None)

        sfield, sdt = 'time', prd.start_date
        efield, edt = 'time', prd.end_date

        qry = self.da_base.session.query(self.da_base.dbModel)

        if ttr_id:
            qry = qry.filter(self.da_base.dbModel.route_id == ttr_id)

        if sdt:
            qry = qry.filter(self.da_base.dbModel.time <= edt)

        if edt:
            qry = qry.filter(self.da_base.dbModel.time >= sdt)

        if weekdays:
            qry = qry.filter(extract('dow', self.da_base.dbModel.time).in_(weekdays))

        if start_time and end_time:
            qry = qry.filter(cast(self.da_base.dbModel.time, Time) >= start_time).filter(
                cast(self.da_base.dbModel.time, Time) <= end_time)

        if order_by and isinstance(order_by, tuple):
            # e.g. order_by = ('id', 'desc')
            # e.g. order_by = ('name', 'asc')
            qry = qry.order_by(getattr(getattr(self.da_base.dbModel, order_by[0]), order_by[1])())
        else:
            qry = qry.order_by(asc(self.da_base.dbModel.time))

        if limit:
            qry = qry.limit(limit)


        data_list = []
        for model_data in qry:
            if as_model:
                data_list.append(model_data)
            else:
                data_list.append(self.da_base.to_info(model_data))
        return data_list

    def get_by_id(self, id):
        """
        :type id: int
        :rtype: TravelTimeInfo
        """
        return self.da_base.get_data_by_id(id)

    def delete_range(self, route_id, start_time, end_time, **kwargs):
        """

        :type route_id: int
        :type start_time: datetime.datetime
        :type end_time: datetime.datetime
        :rtype: bool
        """
        print_exception = kwargs.get('print_exception', False)

        try:
            dbModel = self.da_base.dbModel
            qry = (self.da_base.session.query(dbModel)
             .filter(dbModel.route_id == route_id)
             .filter(dbModel.time >= start_time)
             .filter(dbModel.time <= end_time))
            qry.delete(synchronize_session=False)
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def delete_all_for_a_route(self, ttr_id, **kwargs):
        """
        :type ttr_id: int
        """
        print_exception = kwargs.get('print_exception', False)

        try:
            dbModel = self.da_base.dbModel
            stmt = dbModel.__table__.delete(synchronize_session=False).where(dbModel.route_id == ttr_id)
            self.execute(stmt)
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def insert(self, tti, **kwargs):
        """
        :type tti: TravelTimeInfo
        :rtype: model.TravelTime
        """
        return self.da_base.insert(tti, **kwargs)

    def search_date_range(self, sdt, edt):
        """ search data overlapped with the given data range

        :type sdt: datetime.datetime
        :type sdt: datetime.datetime
        :rtype: list[pyticas_tetres.ttypes.TravelTimeInfo]
        """
        return self.da_base.search_date_range(('time', sdt), ('time', edt))

    def get_count(self, route_id, sdt, edt):
        """

        :type route_id: int
        :type sdt: datetime.datetime
        :type sdt: datetime.datetime
        :rtype: int
        """
        dbModel = self.get_model()
        qry = self.get_session().query(func.count(dbModel.id))
        qry = qry.filter(dbModel.route_id == route_id)
        qry = qry.filter(dbModel.time >= sdt)
        qry = qry.filter(dbModel.time <= edt)
        cnt = qry.scalar()
        return cnt

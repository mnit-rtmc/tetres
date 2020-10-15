# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from sqlalchemy import or_

from pyticas.tool import tb
from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import ActionLogInfo


class ActionLogDataAccess(DataAccess):
    INSERT = 'insert'
    UPDATE = 'update'
    DELETE = 'delete'

    DT_TTROUTE = 'tt_route'
    DT_WEATHER = 'weather'
    DT_INCIDENT = 'incident'
    DT_WORKZONE = 'workzone'
    DT_WORKZONE_GROUP = 'workzone_group'
    DT_SPECIALEVENT = 'special_event'
    DT_SNOWEVENT = 'snow_event'
    DT_SNOWROUTE = 'snow_route'
    DT_SNOWMGMT = 'snow_management'
    DT_SYSTEMCONFIG = 'sysconfig'
    DT_ROUTE_WISE_MOE_PARAMETERS = 'route_wise_moe_parameters'

    STATUS_WAIT = 'wait'
    STATUS_RUNNING = 'running'
    STATUS_FAIL = 'fail'
    STATUS_STOPPED = 'stopped'
    STATUS_DONE = 'done'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model.ActionLog, ActionLogInfo, **kwargs)

    def list(self, start_time=None, action_types=None, handled=None, target_datatypes=None, data_desc=None, status=None, **kwargs):
        """
        :param start_time: e.g. 2013-12-04 12:00:00
        :type start_time: Union(str, datetime.datetime)
        :type action_types: list[str]
        :type handled: bool
        :type target_datatypes: list[str]
        :rtype: list[pyticas_tetres.ttypes.ActionLogInfo]
        """
        if isinstance(start_time, str):
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        as_model = kwargs.get('as_model', False)
        limit = kwargs.get('limit', None)
        order_by = kwargs.get('order_by', None)

        dbModel = model.ActionLog
        session = self.da_base.session

        qry = session.query(dbModel)

        if start_time:
            qry = qry.filter(dbModel.reg_date >= start_time)

        if action_types:
            cond = or_(*[dbModel.action_type == action_type for action_type in action_types])
            qry = qry.filter(cond)

        if handled is not None:
            qry = qry.filter(dbModel.handled == handled)

        if target_datatypes:
            cond = or_(*[dbModel.target_datatype == target_datatype for target_datatype in target_datatypes])
            qry = qry.filter(cond)

        if data_desc:
            qry = qry.filter(dbModel.data_desc.like(data_desc))

        if status:
            qry = qry.filter(dbModel.status == status)

        # apply 'order by'
        if order_by and isinstance(order_by, tuple):
            # e.g. order_by = ('id', 'desc')
            # e.g. order_by = ('name', 'asc')
            qry = qry.order_by(getattr(getattr(dbModel, order_by[0]), order_by[1])())
        else:
            qry = qry.order_by(dbModel.reg_date.asc())

        # apply 'limit'
        if limit:
            qry = qry.limit(limit)

        qry = qry.all()

        data_list = []
        for m in qry:
            if as_model:
                data_list.append(m)
            else:
                data_list.append(self.da_base.to_info(m))

        return data_list

    def get_by_id(self, pkey):
        """
        :type pkey: int
        :rtype: Union(list[ActionLogInfo], list[model.ActionLog])
        """
        return self.da_base.get_data_by_id(pkey)

    def delete_range(self, start_time=None, end_time=None, action_types=None,
                                handled=None, target_datatypes=None, **kwargs):
        """
        :param start_time: e.g. 2013-12-04 12:00:00
        :type start_time: Union(str, datetime.datetime)
        :param end_time: e.g. 2013-12-04 12:00:00
        :type end_time: Union(str, datetime.datetime)
        :type action_types: list[str]
        :type handled: bool
        :type target_datatypes: list[str]
        :rtype: Union(list[ActionLogInfo], list[model.ActionLog])
        """
        print_exception = kwargs.get('print_exception', False)

        if isinstance(start_time, str):
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        if isinstance(end_time, str):
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

        dbModel = model.ActionLog
        session = self.da_base.session

        qry = session.query(dbModel)

        if start_time:
            qry = qry.filter(dbModel.reg_date >= start_time)

        if end_time:
            qry = qry.filter(dbModel.reg_date <= end_time)

        if action_types:
            cond = or_(*[dbModel.action_type == action_type for action_type in action_types])
            qry = qry.filter(cond)

        if handled:
            qry = qry.filter(dbModel.handled == handled)

        if target_datatypes:
            cond = or_(*[dbModel.target_datatype == target_datatype for target_datatype in target_datatypes])
            qry = qry.filter(cond)

        try:
            qry.delete(synchronize_session=False)
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def insert(self, r, **kwargs):
        """
        :type r: ActionLogInfo
        :rtype: model.ActionLog
        """
        return self.da_base.insert(r, **kwargs)

    def search(self, searches, op='and', cond='match', **kwargs):
        """ search data

        **Example**
            - find item that `sevent_id` is 1
                >>> search([('sevent_id', 1)]

            - find item that `name` == 'test and start_time == 2016-01-01 00:00 and end_time == 2016-01-01 07:00
                >>> search([('name', 'test'), ('start_time', datetime(2016, 1, 1, 0, 0)), ('end_time', 2016, 1, 1, 7, 0)], op='and', cond='match')

            - find items that `years` contains one of 2014, 2015 and 2016
                >>> search([('years', y) for y in [2014, 2015, 2016]], op='or', cond='like')

        :param searches: search condition list (see the above example)
        :param op: operand ('and', 'or')
        :param cond: condition ('match', 'like')
        :param kwargs: if `as_model` is True, returns data as `dbModel` type
        :rtype: list[pyticas_tetres.ttypes.ActionLogInfo]
        """
        return self.da_base.search(searches, op, cond, **kwargs)

    @classmethod
    def data_description(cls, datatype, data):
        """

        :type datatype: str
        :type data: object
        :rtype: str
        """
        def _(d, a):
            attrs = a.split('.')
            obj = d
            for attr in attrs:
                obj = getattr(d, attr, None)
                if obj == None:
                    break
            return obj

        if datatype == ActionLogDataAccess.DT_TTROUTE:
            return 'Travel Time Route (id=%s, name=%s)' % (_(data, 'id'), _(data, 'name'))

        if datatype == ActionLogDataAccess.DT_WEATHER:
            return 'Weather (id=%s, usaf=%s, wban=%s, time=%s)' % (_(data, 'id'), _(data, 'usaf'), _(data, 'wban'), _(data, 'dtime'))

        if datatype == ActionLogDataAccess.DT_INCIDENT:
            return ('Incident (id=%s, type=%s, time=%s, lat=%s, lon=%s area=%s)'
                    % (_(data, 'id'), _(data, '_incident_type.eventtype'), _(data, 'cdts'), _(data, 'lat'), _(data, 'lon'), _(data, 'earea')))

        if datatype == ActionLogDataAccess.DT_WORKZONE_GROUP:
            return 'Workzone Group (id=%s, name=%s)' % (_(data, 'id'), _(data, 'name'))

        if datatype == ActionLogDataAccess.DT_WORKZONE:
            return ('Workzone (id=%s, wz_group=%s, start_time=%s, end_time=%s)'
                    % (_(data, 'id'),
                       data._wz_group.name if hasattr(data, '_wz_group') and data._wz_group else None,
                       _(data, 'start_time'), _(data, 'end_time')))

        if datatype == ActionLogDataAccess.DT_SPECIALEVENT:
            return ('Special Event (id=%s, name=%s, start_time=%s, end_time=%s)'
                    % (_(data, 'id'), _(data, 'name'), _(data, 'start_time'), _(data, 'end_time')))

        if datatype == ActionLogDataAccess.DT_SNOWMGMT:
            return ('Road Condition during Snow Event (id=%s, truck_route=[%s, %s], snow_event=[%s, %s ~ %s], lost=%s, regain=%s)'
                    % (_(data, 'id'),
                       _(data, 'sroute_id'),
                       data._snowroute.name if hasattr(data, '_snowroute') and data._snowroute else None,
                       _(data, 'sevent_id'),
                       data._snowevent.start_time if hasattr(data, '_snowevent') and data._snowevent else None,
                       data._snowevent.end_time if hasattr(data, '_snowevent') and data._snowevent else None,
                       _(data, 'lane_lost_time'), _(data, 'lane_regain_time')))

        if datatype == ActionLogDataAccess.DT_SNOWROUTE:
            return ('Truck Route (id=%s, name=%s, prj_id=%s)' % (_(data, 'id'), _(data, 'name'), _(data, 'prj_id')))

        if datatype == ActionLogDataAccess.DT_SNOWEVENT:
            return ('Snow Event (id=%s, start_time=%s, end_time=%s)' % (_(data, 'id'), _(data, 'start_time'), _(data, 'end_time')))

        return 'Unknown'
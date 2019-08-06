# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from sqlalchemy import or_, and_

from pyticas.tool import tb
from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import IncidentInfo


class IncidentDataAccess(DataAccess):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model.Incident, IncidentInfo, **kwargs)

    def list(self, sdate, edate, corridor, direction, **kwargs):
        """
        :param sdate: e.g. 2013-12-04 12:00:00
        :type sdate: str or datetime.datetime
        :param edate: e.g. 2013-12-04 13:00:00
        :type edate: str or datetime.datetime
        :param corridor: only number part of corridor name e.g. 35W, 94, 494, 100, 169
        :type corridor: str
        :param direction: e.g. NB, SB, EB, WB
        :type direction: str
        :rtype: list[IncidentInfo]
        """
        if isinstance(sdate, str):
            sdate = datetime.datetime.strptime(sdate, '%Y-%m-%d %H:%M:%S')

        if isinstance(edate, str):
            edate = datetime.datetime.strptime(edate, '%Y-%m-%d %H:%M:%S')

        sdate = sdate.replace(second=0, microsecond=0)
        edate = edate.replace(second=59, microsecond=59)

        as_model = kwargs.get('as_model', False)
        eventtype = kwargs.get('eventtype', None)
        limit = kwargs.get('limit', None)
        order_by = kwargs.get('order_by', None)

        dbModel = model.Incident
        session = self.da_base.session
        qry = (session.query(dbModel)
            .filter(
            or_(
                and_(
                    dbModel.cdts >= sdate,
                    dbModel.cdts <= edate
                ),
                and_(
                    dbModel.udts >= sdate,
                    dbModel.udts <= edate
                ),
                and_(
                    dbModel.xdts >= sdate,
                    dbModel.xdts <= edate
                )
            )
        )
            .filter(
            or_(
                and_(
                    dbModel.efeanme == corridor,
                    dbModel.edirpre == direction
                ),
                dbModel.ecompl.like('%s %s%%' % (direction, corridor))
            )
        )
        )

        # add 'eventtype' filter
        if eventtype:
            qry = qry.filter(dbModel._incident_type.eventtype == eventtype)

        # apply 'order by'
        if order_by and isinstance(order_by, tuple):
            # e.g. order_by = ('id', 'desc')
            # e.g. order_by = ('name', 'asc')
            qry = qry.order_by(getattr(getattr(dbModel, order_by[0]), order_by[1])())
        else:
            qry = qry.order_by(dbModel.cdts.asc())

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
        :rtype: IncidentInfo
        """
        return self.da_base.get_data_by_id(pkey)

    def delete_range(self, corridor_route, corridor_dir, start_time, end_time, **kwargs):
        """

        :type corridor_route: str
        :type corridor_dir: str
        :type start_time: datetime.datetime
        :type end_time: datetime.datetime
        :rtype: bool
        """
        print_exception = kwargs.get('print_exception', False)

        dbModel = self.da_base.dbModel
        qry = self.da_base.session.query(dbModel)

        try:
            qry = qry.filter(dbModel.road == corridor_route)
            qry = qry.filter(dbModel.direction == corridor_dir)
            qry = qry.filter(or_(and_(dbModel.cdts >= start_time, dbModel.cdts <= end_time),
                                 and_(dbModel.udts >= start_time, dbModel.udts <= end_time),
                                 and_(dbModel.xdts >= start_time, dbModel.xdts <= end_time))
                             )

            qry = qry.delete(synchronize_session=False)
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def delete_range_all(self, start_time, end_time, **kwargs):
        """

        :type corridor_route: str
        :type corridor_dir: str
        :type start_time: datetime.datetime
        :type end_time: datetime.datetime
        :rtype: bool
        """
        print_exception = kwargs.get('print_exception', False)

        dbModel = self.da_base.dbModel
        qry = self.da_base.session.query(dbModel)
        qry = qry.filter(or_(and_(dbModel.cdts >= start_time, dbModel.cdts <= end_time),
                             and_(dbModel.udts >= start_time, dbModel.udts <= end_time),
                             and_(dbModel.xdts >= start_time, dbModel.xdts <= end_time)))

        try:
            qry.delete(synchronize_session=False)
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def insert(self, r, **kwargs):
        """
        :type r: IncidentInfo
        :rtype: model.Incident
        """
        return self.da_base.insert(r, **kwargs)

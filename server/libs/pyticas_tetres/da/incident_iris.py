# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from sqlalchemy import and_

from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.db.iris import model,conn
from pyticas_tetres.ttypes import IrisIncidentInfo


class IrisIncidentDataAccess(object):
    def __init__(self, **kwargs):
        kwargs['session'] = conn.get_session()
        kwargs['primary_key'] = 'event_id'
        self.da_base = DataAccessBase(model.IrisIncident, IrisIncidentInfo, **kwargs)

    def list_as_generator(self, sdate, edate, corridor, direction, **kwargs):
        """
        :param sdate: e.g. 2013-12-04 12:00:00
        :type sdate: str or datetime.datetime
        :param edate: e.g. 2013-12-04 13:00:00
        :type edate: str or datetime.datetime
        :param corridor: only number part of corridor name e.g. 35W, 94, 494, 100, 169
        :type corridor: str
        :param direction: e.g. NB, SB, EB, WB
        :type direction: str
        :rtype: Generator : IncidentInfo
        """
        if isinstance(sdate, str):
            sdate = datetime.datetime.strptime(sdate, '%Y-%m-%d %H:%M:%S')

        if isinstance(edate, str):
            edate = datetime.datetime.strptime(edate, '%Y-%m-%d %H:%M:%S')

        as_model = kwargs.get('as_model', False)
        limit = kwargs.get('limit', None)
        order_by = kwargs.get('order_by', None)
        window_size = kwargs.get('window_size', 1000)

        dbModel = model.IrisIncident
        session = self.da_base.session
        if corridor and direction:
            qry = (session.query(dbModel)
                .filter(
                and_(
                    dbModel.event_date >= sdate,
                    dbModel.event_date <= edate
                ),
            )
                .filter(
                and_(
                    dbModel.road == corridor,
                    dbModel.direction == direction
                ),
            )
            )
        else:
            qry = (session.query(dbModel)
                .filter(
                and_(
                    dbModel.event_date >= sdate,
                    dbModel.event_date <= edate
                ),
            )
            )

        # apply 'order by'
        if order_by and isinstance(order_by, tuple):
            # e.g. order_by = ('id', 'desc')
            # e.g. order_by = ('name', 'asc')
            qry = qry.order_by(getattr(getattr(dbModel, order_by[0]), order_by[1])())
        else:
            qry = qry.order_by(dbModel.event_date.asc())

        # apply 'limit'
        if limit:
            qry = qry.limit(limit)

        for m in self.da_base.query_generator(qry, window_size):
            if as_model:
                yield m
            else:
                yield self.da_base.to_info(m)

    def list(self, sdate, edate, corridor=None, direction=None, **kwargs):
        """
        :param sdate: e.g. 2013-12-04 12:00:00
        :type sdate: str or datetime.datetime
        :param edate: e.g. 2013-12-04 13:00:00
        :type edate: str or datetime.datetime
        :param corridor: only number part of corridor name e.g. 35W, 94, 494, 100, 169
        :type corridor: str
        :param direction: e.g. NB, SB, EB, WB
        :type direction: str
        :rtype: list[IrisIncidentInfo]
        """
        return [m for m in self.list_as_generator(sdate, edate, corridor, direction, **kwargs)]

    def get_by_id(self, pkey):
        """
        :type pkey: int
        :rtype: IrisIncidentInfo
        """
        return self.da_base.get_data_by_id(pkey)

    def get_by_event_id(self, event_id):
        """
        :type event_id: int
        :rtype: IrisIncidentInfo
        """
        res = self.da_base.search([('event_id', event_id)])
        if res:
            return res[0]
        else:
            return None

    def close_session(self):
        self.da_base.close()

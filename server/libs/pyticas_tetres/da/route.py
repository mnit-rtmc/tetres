# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import TTRouteInfo


class TTRouteDataAccess(DataAccess):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model.TTRoute, TTRouteInfo, **kwargs)

    def list(self):
        """
        :rtype: list[TTRouteInfo]
        """
        return self.da_base.list()

    def list_by_corridor(self, corridor_name, **kwargs):
        sess = self.da_base.session
        dbModel = self.da_base.dbModel
        qry = sess.query(dbModel).filter(dbModel.corridor == corridor_name)

        as_model = kwargs.get('as_model', False)
        limit = kwargs.get('limit', None)
        group_by = kwargs.get('group_by', None)
        order_by = kwargs.get('order_by', None)
        window_size = kwargs.get('window_size', 1000)

        # apply 'order by'
        if order_by and isinstance(order_by, tuple):
            # e.g. order_by = ('id', 'desc')
            # e.g. order_by = ('name', 'asc')
            qry = qry.order_by(getattr(getattr(dbModel, order_by[0]), order_by[1])())

        if group_by:
            if isinstance(group_by, str):
                qry = qry.group_by(getattr(dbModel, group_by))
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

    def get_by_id(self, route_id):
        """
        :type route_id: int
        :rtype: TTRouteInfo
        """
        return self.da_base.get_data_by_id(route_id)

    def get_by_name(self, route_name):
        """
        :type route_name: str
        :rtype: TTRouteInfo
        """
        return self.da_base.get_data_by_name(route_name)

    def insert(self, r, **kwargs):
        """
        :type r: TTRouteInfo
        :rtype: model.TTRoute
        """
        return self.da_base.insert(r, **kwargs)
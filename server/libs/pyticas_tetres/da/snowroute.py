# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import SnowRouteInfo


class SnowRouteDataAccess(DataAccess):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model.SnowRoute, SnowRouteInfo, **kwargs)

    def list(self):
        """
        :rtype: list[SnowRouteInfo]
        """
        return self.da_base.list()

    def get_by_id(self, route_id):
        """
        :type route_id: int
        :rtype: SnowRouteInfo
        """
        return self.da_base.get_data_by_id(route_id)

    def get_by_name(self, route_name):
        """
        :type route_name: str
        :rtype: SnowRouteInfo
        """
        return self.da_base.get_data_by_name(route_name)

    def insert(self, r, **kwargs):
        """
        :type r: SnowRouteInfo
        :rtype: model.SnowRoute
        """
        return self.da_base.insert(r, **kwargs)
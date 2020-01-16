# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import SnowEventInfo


class SnowEventDataAccess(DataAccess):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model.SnowEvent, SnowEventInfo, **kwargs)

    def list(self):
        """
        :rtype: list[SnowEventInfo]
        """
        return self.da_base.list()

    def list_by_year(self, years):
        """
        :type years: list[int]
        :rtype: list[SpecialEventInfo]
        """
        results = []
        for year in years:
            res = self.da_base.search_date_range(('start_time', datetime.datetime(int(year), 1, 1, 0, 0, 0)),
                                                 ('end_time', datetime.datetime(int(year), 12, 31, 11, 59, 59)))
            if res:
                results.extend(res)
        return results

    def years(self):
        """
        :rtype: list[int]:
        """
        ys = []
        for snei in self.da_base.list(as_model=True):
            y = snei.start_time.year
            if y not in ys:
                ys.append(y)
        return sorted(ys)

    def get_by_id(self, id):
        """
        :type id: int
        :rtype: SnowEventInfo
        """
        return self.da_base.get_data_by_id(id)

    def get_by_name(self, route_name):
        """
        :type route_name: str
        :rtype: SnowEventInfo
        """
        return self.da_base.get_data_by_name(route_name)

    def insert(self, r, **kwargs):
        """
        :type r: SnowEventInfo
        :rtype: model.SnowEvent
        """
        return self.da_base.insert(r, **kwargs)
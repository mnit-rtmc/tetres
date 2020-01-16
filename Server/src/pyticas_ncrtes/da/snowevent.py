# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas_ncrtes.da.base import DataAccessBase
from pyticas_ncrtes.db import model
from pyticas_ncrtes.itypes import SnowEventInfo
from pyticas_ncrtes.da import snowroute
from pyticas_tetres.da.snowmgmt import SnowMgmtDataAccess


class SnowEventDataAccess(object):
    def __init__(self, **kwargs):
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

    def delete(self, id, autocommit=False):


        deleted = self.da_base.delete(id, autocommit=autocommit)
        if deleted:
            da_snowmgmt = SnowMgmtDataAccess(session=self.da_base.session)
            for snm in da_snowmgmt.search([('sevent_id', 1)], cond='match', as_model=True):
                da_snowmgmt.delete(snm.id, autocommit=autocommit)
        return deleted

    def insert(self, r, autocommit=False):
        """
        :type r: SnowEventInfo
        :type autocommit: bool
        :raise AlreadyExist
        :rtype: model.SnowEvent
        """
        return self.da_base.insert(r, autocommit=autocommit)

    def update(self, id, field_data, autocommit=False):
        """
        :type id: int
        :type field_data: dict
        :raise AlreadyExist
        :rtype: bool
        """
        return self.da_base.update(id, field_data, autocommit=autocommit)

    def rollback(self):
        self.da_base.session.rollback()

    def commit(self):
        self.da_base.commit()

    def close(self):
        self.da_base.close()
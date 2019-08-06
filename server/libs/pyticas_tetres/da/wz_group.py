# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import WorkZoneGroupInfo


class WZGroupDataAccess(DataAccess):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model.WorkZoneGroup, WorkZoneGroupInfo, **kwargs)

    def list(self):
        """
        :rtype: list[pyticas_tetres.ttypes.WorkZoneGroupInfo]
        """
        return self.da_base.list()

    def list_by_year(self, years):
        """
        :type years: list[int]
        :return:
        """
        if years:
            wheres = [('years', y) for y in years]
            return self.da_base.search(wheres, op='or', cond='like')
        else:
            return self.da_base.search([('years', None), ('years', '')], op='or', cond='match')

    def years(self):
        """
        :rtype: list[int]:
        """
        ys = []
        for wzi in self.da_base.list():
            if not wzi.years:
                continue
            for y in wzi.years.split(','):
                iy = int(y)
                if iy not in ys:
                    ys.append(iy)
        return sorted(ys)

    def get_by_id(self, wz_id):
        """
        :type wz_id: int
        :rtype: pyticas_tetres.ttypes.WorkZoneGroupInfo
        """
        return self.da_base.get_data_by_id(wz_id)

    def get_by_name(self, wz_name):
        """
        :type wz_name: str
        :rtype: pyticas_tetres.ttypes.WorkZoneGroupInfo
        """
        return self.da_base.get_data_by_name(wz_name)

    def insert(self, wzi, **kwargs):
        """
        :type wzi: pyticas_tetres.ttypes.WorkZoneGroupInfo
        :rtype: model.WorkZoneGroup
        """
        return self.da_base.insert(wzi, **kwargs)

    def update_years(self, id, **kwargs):
        """
        :type id: int
        :rtype: bool
        """
        wzgm = self.da_base.get_model_by_id(id)
        years = []
        for wzm in wzgm._wzs:
            syear = wzm.start_time.year
            eyear = wzm.end_time.year
            for y in range(syear, eyear + 1):
                y = str(y)
                if y not in years:
                    years.append(y)
        return self.update(id, {'years': ','.join(years)}, **kwargs)

    def search(self, searches, op='and', cond='match', **kwargs):
        """ search data

        **Example**
            - find item that `sevent_id` is 1
                >>> search([('sevent_id', 1)]

            - find item that `name` == 'test and start_time == 2016-01-01 00:00 and end_time == 2016-01-01 07:00
                >>> search([('name', 'test'), ('start_time', datetime(2016, 1, 1, 0, 0)), ('end_time', 2016, 1, 1, 7, 0)], op='and', cond='match')

            - find items that `years` contains one of 2014, 2015 and 2016
                >>> search([('years', y) for y in [2014, 2015, 2016]], op='or', cond='like')
        """
        return self.da_base.search(searches, op, cond, **kwargs)
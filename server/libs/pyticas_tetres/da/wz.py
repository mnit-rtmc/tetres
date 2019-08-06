# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from sqlalchemy import or_, not_

from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import WorkZoneInfo


class WorkZoneDataAccess(DataAccess):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model.WorkZone, WorkZoneInfo, **kwargs)

    def list(self, **kwargs):
        """
        :rtype: list[pyticas_tetres.ttypes.WorkZoneInfo]
        """
        return self.da_base.list(**kwargs)

    def list_by_year(self, years):
        """
        :type years: list[int]
        :return:
        """
        wheres = [('years', y) for y in years]
        return self.da_base.search(wheres, op='or', cond='like')

    def years(self):
        """
        :rtype: list[int]:
        """
        ys = []
        for wzi in self.da_base.list():
            for y in wzi.years.split(','):
                iy = int(y)
                if iy not in ys:
                    ys.append(iy)
        return sorted(ys)

    def get_model_by_id(self, wz_id):
        """
        :type wz_id: int
        :rtype: pyticas_tetres.db.model.WorkZone
        """
        return self.da_base.get_model_by_id(wz_id)

    def get_by_id(self, wz_id):
        """
        :type wz_id: int
        :rtype: pyticas_tetres.ttypes.WorkZoneInfo
        """
        return self.da_base.get_data_by_id(wz_id)

    def get_by_name(self, wz_name):
        """
        :type wz_name: str
        :rtype: pyticas_tetres.ttypes.WorkZoneInfo
        """
        return self.da_base.get_data_by_name(wz_name)

    def insert(self, wzi, **kwargs):
        """
        :type wzi: pyticas_tetres.ttypes.WorkZoneInfo
        :rtype: model.WorkZone
        """
        return self.da_base.insert(wzi, **kwargs)

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

    def search_date_range(self, sdt, edt, **kwargs):
        """ search data overlapped with the given data range

        :type sdt: datetime.datetime
        :type sdt: datetime.datetime
        :rtype: list[pyticas_tetres.ttypes.WorkZoneInfo]
        """
        as_model = kwargs.get('as_model', False)
        clauses = or_()
        clauses = or_(clauses, self.da_base.dbModel.end_time < sdt)
        clauses = or_(clauses, self.da_base.dbModel.start_time > edt)
        clauses = not_(clauses)

        data_list = []
        for model_data in self.da_base.session.query(self.da_base.dbModel).filter(clauses):
            if as_model:
                data_list.append(model_data)
            else:
                data_list.append(self.da_base.to_info(model_data))
        return data_list
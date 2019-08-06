# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from sqlalchemy import or_, not_

from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import SpecialEventInfo


class SpecialEventDataAccess(DataAccess):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model.Specialevent, SpecialEventInfo, **kwargs)

    def exist(self, name, start_time, end_time):
        """
        :type name: str
        :type start_time: str
        :type end_time: str
        :rtype: pyticas_tetres.db.model.SpecialEvent
        """

        if isinstance(start_time, str):
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        if isinstance(end_time, str):
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        exs = self.da_base.search([('name', name), ('start_time', start_time), ('end_time', end_time)], op='and',
                                  cond='match')
        return exs

    def list(self):
        """
        :rtype: list[SpecialEventInfo]
        """
        return self.da_base.list()

    def list_by_year(self, years):
        """
        :type years: list[int]
        :rtype: list[SpecialEventInfo]
        """
        wheres = [('years', y) for y in years]
        return self.da_base.search(wheres, op='or', cond='like')

    def search_date_range(self, sdt, edt, **kwargs):
        """ search data overlapped with the given data range

        :type sdt: datetime.datetime
        :type sdt: datetime.datetime
        :rtype: list[pyticas_tetres.ttypes.SpecialEventInfo]
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

    def years(self):
        """
        :rtype: list[int]:
        """
        ys = []
        for sei in self.da_base.list():
            for y in sei.years.split(','):
                iy = int(y)
                if iy not in ys:
                    ys.append(iy)
        return sorted(ys)

    def get_by_id(self, se_id):
        """
        :type se_id: int
        :rtype: SpecialEventInfo
        """
        return self.da_base.get_data_by_id(se_id)

    def insert(self, sei, **kwargs):
        """
        :type sei: SpecialEventInfo
        """
        return self.da_base.insert(sei, **kwargs)
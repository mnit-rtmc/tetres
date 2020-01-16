# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.db.tetres import model_yearly
from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import WeatherInfo


class WeatherDataAccess(DataAccess):
    def __init__(self, year, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model_yearly.get_weather_table(year), WeatherInfo,
                                      **kwargs)

    def list(self):
        """
        :rtype: list[WeatherInfo]
        """
        return self.da_base.list()

    def list_by_period(self, site_id, prd, sen_id=0):
        """
        :type site_id: int
        :type prd: pyticas.ttypes.Period
        :type sen_id: int
        :rtype: list[WeatherInfo]
        """
        sfield, sdt = 'dtime', prd.start_date
        efield, edt = 'dtime', prd.end_date
        qry = (self.da_base.session.query(self.da_base.dbModel)
               .filter(getattr(self.da_base.dbModel, 'site_id') == site_id)
               .filter(getattr(self.da_base.dbModel, 'sen_id') == sen_id)
               .filter(getattr(self.da_base.dbModel, efield) <= edt)
               .filter(getattr(self.da_base.dbModel, sfield) >= sdt))
        data_list = []
        for model_data in qry:
            data_list.append(self.da_base.to_info(model_data))
        return data_list

    def get_by_id(self, id):
        """
        :type id: int
        :rtype: WeatherInfo
        """
        return self.da_base.get_data_by_id(id)

    def insert(self, r, **kwargs):
        """
        :type r: WeatherInfo
        :rtype: model.Weather
        """
        return self.da_base.insert(r, **kwargs)

# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from sqlalchemy import and_

from pyticas_tetres.db.tetres import model_yearly
from pyticas.tool import tb
from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import NoaaWeatherInfo


class NoaaWeatherDataAccess(DataAccess):
    def __init__(self, year, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model_yearly.get_noaa_table(year), NoaaWeatherInfo, **kwargs)

    def list(self, **kwargs):
        """
        :rtype: list[NoaaWeatherInfo]
        """
        return self.da_base.list(**kwargs)

    def list_by_period(self, usaf, wban, prd):
        """
        :type usaf: str or int
        :type wban: wban or int
        :type prd: pyticas.ttypes.Period
        :rtype: list[NoaaWeatherInfo]
        """
        sfield, sdt = 'dtime', prd.start_date
        efield, edt = 'dtime', prd.end_date
        qry = (self.da_base.session.query(self.da_base.dbModel)
               .filter(getattr(self.da_base.dbModel, 'usaf') == usaf)
               .filter(getattr(self.da_base.dbModel, 'wban') == wban)
               .filter(getattr(self.da_base.dbModel, efield) <= edt)
               .filter(getattr(self.da_base.dbModel, sfield) >= sdt))
        data_list = []
        for model_data in qry:
            data_list.append(self.da_base.to_info(model_data))
        return data_list

    def get_by_id(self, id):
        """
        :type id: int
        :rtype: NoaaWeatherInfo
        """
        return self.da_base.get_data_by_id(id)

    def delete_range(self, usaf, wban, start_time, end_time, **kwargs):
        """

        :type usaf: str
        :type wban: str
        :type start_time: datetime.datetime
        :type end_time: datetime.datetime
        :rtype: bool
        """
        print_exception = kwargs.get('print_exception', False)

        dbModel = self.da_base.dbModel

        try:
            qry = self.da_base.session.query(dbModel)
            if usaf is not None:
                qry = qry.filter(dbModel.usaf == usaf)
            if wban is not None:
                qry = qry.filter(dbModel.wban == wban)
            if start_time is not None and end_time is not None:
                qry = qry.filter(and_(dbModel.dtime >= start_time, dbModel.dtime <= end_time))
            qry.delete(synchronize_session=False)
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def insert(self, r, **kwargs):
        """
        :type r: NoaaWeatherInfo
        :rtype: model.Weather
        """
        return self.da_base.insert(r, **kwargs)

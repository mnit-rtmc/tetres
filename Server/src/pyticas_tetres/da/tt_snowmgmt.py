# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.db.tetres import model_yearly
from pyticas_tetres.da.base_ext import ExtDataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import SnowManagementInfo, TTSnowManagementInfo


class TTSnowManagementDataAccess(DataAccess):
    def __init__(self, year, **kwargs):
        super().__init__(**kwargs)
        self.da_base = ExtDataAccessBase(year,
                                         model_yearly.get_tt_snowmgmt_table(year),
                                         model.SnowManagement,
                                         TTSnowManagementInfo,
                                         **kwargs)

    def list(self, ttri_id, sdt, edt, **kwargs):
        """

        :type ttri_id: int
        :type sdt: datetime.datetime
        :type edt: datetime.datetime
        :rtype: Union(list[TTSnowManagementInfo], list[model.SnowManagement])
        """
        return self.da_base.list(ttri_id, sdt, edt, **kwargs)

    def get_by_id(self, id):
        """
        :type id: int
        :rtype: SnowManagementInfo
        """
        return self.da_base.get_data_by_id(id)

    def delete_range(self, ttri_id, sdt, edt, **kwargs):
        """
        :type ttri_id: int
        :type sdt: datetime.datetime
        :type edt: datetime.datetime
        """
        return self.da_base.delete_range(ttri_id, sdt, edt, **kwargs)

    def delete_all_for_a_route(self, ttri_id, **kwargs):
        """
        :type ttri_id: int
        :rtype: bool
        """
        return self.da_base.delete_all_for_a_route(ttri_id, **kwargs)

    def delete_if_route_is_deleted(self, **kwargs):
        """
        :rtype: bool
        """
        return self.da_base.delete_if_route_is_deleted(**kwargs)

    def insert(self, ttsmi, **kwargs):
        """
        :type ttsmi: TTSnowManagementInfo
        :rtype: model.TTSnowManagement<year>
        """
        return self.da_base.insert(ttsmi, **kwargs)

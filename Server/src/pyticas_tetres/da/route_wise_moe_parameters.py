# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import RouteWiseMOEParametersInfo


class RouteWiseMOEParametersDataAccess(DataAccess):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model.RouteWiseMOEParameters, RouteWiseMOEParametersInfo, **kwargs)

    def list(self):
        """
        :rtype: list[pyticas_tetres.ttypes.WorkZoneGroupInfo]
        """
        data_list = self.da_base.list()
        for data in data_list:
            data.start_time = str(data.start_time) if data.start_time else ""
            data.end_time = str(data.end_time) if data.end_time else ""
            data.update_time = str(data.update_time) if data.update_time else ""
        return data_list

    def get_by_id(self, moe_param_id):
        """
        :type wz_id: int
        :rtype: pyticas_tetres.ttypes.WorkZoneGroupInfo
        """
        return self.da_base.get_data_by_id(moe_param_id)

    def insert(self, route_wise_moe_param_info, **kwargs):
        """
        :type wzi: pyticas_tetres.ttypes.WorkZoneGroupInfo
        :rtype: model.WorkZoneGroup
        """
        return self.da_base.insert(route_wise_moe_param_info, **kwargs)

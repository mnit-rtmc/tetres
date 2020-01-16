# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import IncidentTypeInfo


class IncidentTypeDataAccess(DataAccess):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model.IncidentType, IncidentTypeInfo, **kwargs)

    def list(self):
        """
        :rtype: list[IncidentTypeInfo]
        """
        return self.da_base.list()

    def get_by_id(self, id):
        """
        :type id: int
        :rtype: IncidentTypeInfo
        """
        return self.da_base.get_data_by_id(id)

    def insert(self, r, **kwargs):
        """
        :type r: IncidentTypeInfo
        :rtype: model.IncidentType
        """
        return self.da_base.insert(r, **kwargs)

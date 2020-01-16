# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.cad import model
from pyticas_tetres.db.cad import conn
from pyticas_tetres.ttypes import CADIncidentTypeInfo


class IncidentTypeDataAccess(object):
    def __init__(self, **kwargs):
        kwargs['session'] = conn.get_session()
        kwargs['primary_key'] = 'pkey'
        self.da_base = DataAccessBase(model.CADIncidentType, CADIncidentTypeInfo, **kwargs)

    def list(self):
        """
        :rtype: list[CADIncidentTypeInfo]
        """
        return self.da_base.list()

    def get_by_id(self, id):
        """
        :type id: int
        :rtype: CADIncidentTypeInfo
        """
        return self.da_base.get_data_by_id(id)

    def insert(self, r, **kwargs):
        """
        :type r: CADIncidentTypeInfo
        :rtype: model.CADIncidentType
        """
        return self.da_base.insert(r, **kwargs)

    def close_session(self):
        return self.da_base.close()
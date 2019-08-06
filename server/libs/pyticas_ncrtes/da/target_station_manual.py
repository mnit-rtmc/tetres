# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas_ncrtes.da.base import DataAccessBase
from pyticas_ncrtes.db import model
from pyticas_ncrtes import itypes
from sqlalchemy.orm.exc import NoResultFound


class TargetStationManualDataAccess(object):
    def __init__(self, **kwargs):
        self.da_base = DataAccessBase(model.TargetStationManual, itypes.TargetStationManualInfo, **kwargs)

    def list(self):
        """
        :rtype: list[itypes.TargetStationManualInfo]
        """
        return self.da_base.list()

    def list_by_corridor(self, corridor_name):
        """
        :type corridor_name: str
        :rtype: list[itypes.TargetStationManualInfo]
        """
        return self.da_base.search([('corridor_name', corridor_name)], cond='match')

    def get_by_id(self, id):
        """
        :type id: int
        :rtype: itypes.TargetStationInfo
        """
        return self.da_base.get_data_by_id(id)

    def delete(self, id, autocommit=False):
        """
        :type id: int
        :type autocommit: bool
        """
        return self.da_base.delete(id, autocommit=autocommit)

    def insert(self, tsi, autocommit=False):
        """
        :type tsi: itypes.TargetStationInfo
        :type autocommit: bool
        :raise AlreadyExist
        :rtype: model.TargetStation
        """
        return self.da_base.insert(tsi, autocommit=autocommit)

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

# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas_ncrtes.da.base import DataAccessBase
from pyticas_ncrtes.db import model
from pyticas_ncrtes import itypes
from sqlalchemy.orm.exc import NoResultFound


class DataAccess(object):
    def __init__(self, **kwargs):
        self.da_base = DataAccessBase(model.NormalData, itypes.NormalDataInfo, **kwargs)

    def list(self):
        """
        :rtype: list[itypes.NormalDataInfo]
        """
        return self.da_base.list()

    def list_by_winterseason(self, wid):
        """
        :type wid: int
        :rtype: list[itypes.NormalDataInfo]
        """
        return self.da_base.search([('winterseason_id', wid)], cond='match')


    def get_by_id(self, id):
        """
        :type id: int
        :rtype: itypes.NormalDataInfo
        """
        return self.da_base.get_data_by_id(id)

    def get_by_station(self, wid, station_id):
        """
        :type wid: int
        :type station_id: str
        :rtype: itypes.NormalDataInfo
        """
        try:
            md = self.da_base.session.query(model.NormalData).filter(model.NormalData.station_id == station_id,
                                                                         model.NormalData.winterseason_id == wid).one()
            return self.da_base.to_info(md)
        except NoResultFound as ex:
            return None

    def delete(self, id, autocommit=False):
        """
        :type id: int
        :type autocommit: bool
        """
        return self.da_base.delete(id, autocommit=autocommit)

    def insert(self, ndi, autocommit=False):
        """
        :type ndi: itypes.NormalDataInfo
        :type autocommit: bool
        :raise AlreadyExist
        :rtype: model.NormalData
        """
        return self.da_base.insert(ndi, autocommit=autocommit)

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

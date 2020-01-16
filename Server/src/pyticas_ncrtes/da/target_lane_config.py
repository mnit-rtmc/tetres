# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas_ncrtes.da.base import DataAccessBase
from pyticas_ncrtes.db import model
from pyticas_ncrtes import itypes
from sqlalchemy import or_, and_


class TargetLaneConfigDataAccess(object):
    def __init__(self, **kwargs):
        self.da_base = DataAccessBase(model.TargetLaneConfig, itypes.TargetLaneConfigInfo, **kwargs)

    def years(self):
        """
        :rtype: list[int]:
        """
        ys = []
        for tlci in self.da_base.list(group_by='winterseason_id'):
            if tlci._winterseason.year not in ys:
                ys.append(tlci._winterseason.year)
        return sorted(ys)

    def list(self):
        """
        :rtype: list[itypes.TargetLaneConfigInfo]
        """
        return self.da_base.list()

    def list_by_winterseason(self, wid):
        """
        :type wid: int
        :rtype: list[itypes.TargetLaneConfigInfo]
        """
        return self.da_base.search([('winterseason_id', wid)], cond='match')

    def list_by_year(self, year, **kwargs):
        """
        :type year: int
        :rtype: list[itypes.TargetLaneConfigInfo]
        """
        as_model = kwargs.get('as_model', False)

        qry = self.da_base.session.query(model.TargetLaneConfig).filter(
            model.TargetLaneConfig._winterseason.has(year=year))

        res = []
        for item in qry:
            if as_model:
                res.append(item)
            else:
                res.append(self.da_base.to_info(item))
        return res

    def get_by_station_id(self, year, station_id, **kwargs):
        """
        :type year: int
        :type station_id: str
        :rtype: itypes.TargetLaneConfigInfo
        """
        as_model = kwargs.get('as_model', False)

        item = (self.da_base.session.query(model.TargetLaneConfig)
                .filter(model.TargetLaneConfig._winterseason.has(year=year))
                .filter(model.TargetLaneConfig.station_id == station_id).first())

        if not item:
            return None

        if as_model:
            return item
        else:
            return self.da_base.to_info(item)

    def list_by_corridor_name(self, year, corridor_name, **kwargs):
        """
        :type year: int
        :rtype: list[itypes.TargetLaneConfigInfo]
        """
        as_model = kwargs.get('as_model', False)

        qry = self.da_base.session.query(model.TargetLaneConfig).filter(
            model.TargetLaneConfig._winterseason.has(year=year)).filter(model.TargetLaneConfig.corridor_name == corridor_name)

        res = []
        for item in qry:
            if as_model:
                res.append(item)
            else:
                res.append(self.da_base.to_info(item))
        return res



    def get_by_id(self, id):
        """
        :type id: int
        :rtype: itypes.TargetLaneConfigInfo
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
        :type tsi: itypes.TargetLaneConfigInfo
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

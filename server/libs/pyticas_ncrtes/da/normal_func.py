# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.tool import json
from pyticas_ncrtes import itypes
from sqlalchemy.orm.exc import NoResultFound
from pyticas_ncrtes.da.base import DataAccessBase
from pyticas_ncrtes.db import model


class NormalFunctionDataAccess(object):
    def __init__(self, **kwargs):
        self.da_base = DataAccessBase(model.NormalFunction, itypes.NormalFunctionInfo, **kwargs)


    def list(self):
        """
        :rtype: list[itypes.NormalFunctionInfo]
        """
        return self.da_base.list()


    def get_by_station(self, year, station_id, **kwargs):
        """
        :type year: int
        :rtype: itypes.NormalFunctionInfo
        """
        try:
            md = self.da_base.session.query(model.NormalFunction).filter(model.NormalFunction.station_id == station_id,
                                                                         model.NormalFunction._winterseason.has(year=year)).one()
            return self.da_base.to_info(md)
        except NoResultFound as ex:
            return None
        except Exception as ex:
            from pyticas.tool import tb
            tb.traceback(ex)
            return None


    def list_by_winterseason(self, wid):
        """
        :type wid: int
        :rtype: list[itypes.NormalFunctionInfo]
        """
        return self.da_base.search([('winterseason_id', wid)], cond='match')


    def get_by_id(self, id):
        """
        :type id: int
        :rtype: itypes.NormalFunctionInfo
        """
        return self.da_base.get_data_by_id(id)

    def get_by_winter_id(self, wid, station_id):
        """
        :type wid: int
        :type station_id: str
        :rtype: itypes.NormalFunctionInfo
        """
        try:
            md = self.da_base.session.query(model.NormalFunction).filter(model.NormalFunction.station_id == station_id,
                                                                         model.NormalFunction.winterseason_id == wid).one()
            return self.da_base.to_info(md)
        except NoResultFound as ex:
            return None
        except Exception as ex:
            from pyticas.tool import tb
            tb.traceback(ex)
            return None

    def delete(self, id, autocommit=False):
        """
        :type id: int
        :type autocommit: bool
        """
        return self.da_base.delete(id, autocommit=autocommit)

    def insert(self, nfi, autocommit=False):
        """
        :type nfi: itypes.NormalFunctionInfo
        :type autocommit: bool
        :raise AlreadyExist
        :rtype: model.NormalFunction
        """
        return self.da_base.insert(nfi, autocommit=autocommit)

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

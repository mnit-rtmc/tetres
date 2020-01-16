# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas_ncrtes.da.base import DataAccessBase
from pyticas_ncrtes.db import model
from pyticas_ncrtes import itypes
from sqlalchemy.orm.exc import NoResultFound


class WinterSeasonDataAccess(object):
    def __init__(self, **kwargs):
        self.da_base = DataAccessBase(model.WinterSeason, itypes.WinterSeasonInfo, **kwargs)

    def get_by_months(self, months):
        """ return nsr_data by months

        :type months: list[(int, int)]
        :rtype: itypes.WinterSeasonInfo
        """
        year, mstr = itypes.WinterSeasonInfo.months_str(months)
        try:
            md = self.da_base.session.query(model.WinterSeason).filter(model.WinterSeason.months == mstr).first()
            if not md:
                return None
            return self.da_base.to_info(md)
        except NoResultFound as ex:
            return None

    def list(self):
        """
        :rtype: list[itypes.WinterSeasonInfo]
        """
        return self.da_base.list()

    def get_by_id(self, id):
        """
        :type id: int
        :rtype: itypes.WinterSeasonInfo
        """
        return self.da_base.get_data_by_id(id)

    def get_by_year(self, year, **kwargs):
        """
        :type year: int
        :rtype: itypes.WinterSeasonInfo
        """
        as_model = kwargs.get('as_model', False)
        try:
            model_data = self.da_base.session.query(model.WinterSeason).filter(model.WinterSeason.year == year).one()
            if not model_data:
                return None
            if as_model:
                return model_data
            else:
                return self.da_base.to_info(model_data)
        except NoResultFound as ex:
            return None


    def delete(self, id, autocommit=False):
        """
        :type id: int
        :type autocommit: bool
        """
        return self.da_base.delete(id, autocommit=autocommit)

    def insert(self, ws, autocommit=False):
        """
        :type ws: itypes.WinterSeasonInfo
        :type autocommit: bool
        :raise AlreadyExist
        :rtype: model.WinterSeason
        """
        return self.da_base.insert(ws, autocommit=autocommit)

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

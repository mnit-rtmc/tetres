# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_ncrtes.da.base import DataAccessBase
from pyticas_ncrtes.db import model
from pyticas_ncrtes.itypes import SnowRouteGroupInfo


class SnowRouteGroupDataAccess(object):
    def __init__(self, **kwargs):
        self.da_base = DataAccessBase(model.SnowRouteGroup, SnowRouteGroupInfo, **kwargs)

    def list(self, **kwargs):
        """
        :rtype: list[SnowRouteGroupInfo]
        """
        return self.da_base.list(**kwargs)

    def list_by_year(self, years):
        """
        :type years: list[int]
        :return:
        """
        if years:
            wheres = [('year', y) for y in years]
            return self.da_base.search(wheres, op='or', cond='match')
        else:
            return self.da_base.search([('year', None), ('year', '')], op='or', cond='match')

    def search(self, searches, op='and', cond='match', **kwargs):
        """ search nsr_data

        **Example**
            - find item that `sevent_id` is 1
                >>> search([('sevent_id', 1)]

            - find item that `name` == 'test and start_time == 2016-01-01 00:00 and end_time == 2016-01-01 07:00
                >>> search([('name', 'test'), ('start_time', datetime(2016, 1, 1, 0, 0)), ('end_time', 2016, 1, 1, 7, 0)], op='and', cond='match')

            - find items that `years` contains one of 2014, 2015 and 2016
                >>> search([(ymds, y) for y in [2014, 2015, 2016]], op='or', cond='like')

        :rtype: list[SnowRouteGroupInfo]
        """
        return self.da_base.search(searches, op, cond, **kwargs)

    def years(self):
        """
        :rtype: list[int]:
        """
        ys = []
        for snrgi in self.da_base.list():
            if snrgi.year not in ys:
                ys.append(snrgi.year)
        return sorted(ys)

    def get_by_id(self, snrg_id):
        """
        :type snrg_id: int
        :rtype: SnowRouteGroupInfo
        """
        return self.da_base.get_data_by_id(snrg_id)

    def get_by_name(self, prj_id):
        """
        :type prj_id: str
        :rtype: SnowRouteGroupInfo
        """
        return self.da_base.get_data_by_name(prj_id)

    def delete(self, id, autocommit=False):
        """
        :type route_name: str
        :type autocommit: bool
        """
        deleted = self.da_base.delete(id, autocommit=autocommit)
        return deleted

    def insert(self, r, autocommit=False):
        """
        :type r: SnowRouteGroupInfo
        :type autocommit: bool
        :raise AlreadyExist
        :rtype: model.SnowRoute
        """
        return self.da_base.insert(r, autocommit=autocommit)

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
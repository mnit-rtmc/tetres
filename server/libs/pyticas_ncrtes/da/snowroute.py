# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_ncrtes.da.base import DataAccessBase
from sqlalchemy import or_, and_
from pyticas_ncrtes.db import model
from pyticas_ncrtes.itypes import SnowRouteInfo


class SnowRouteDataAccess(object):
    def __init__(self, **kwargs):
        self.da_base = DataAccessBase(model.SnowRoute, SnowRouteInfo, **kwargs)

    def list(self, **kwargs):
        """
        :rtype: list[SnowRouteInfo]
        """
        return self.da_base.list(**kwargs)

    def get_by_id(self, route_id):
        """
        :type route_id: int
        :rtype: SnowRouteInfo
        """
        return self.da_base.get_data_by_id(route_id)

    def get_by_name(self, route_name):
        """
        :type route_name: str
        :rtype: SnowRouteInfo
        """
        return self.da_base.get_data_by_name(route_name)

    def delete(self, id, autocommit=False):
        """
        :type route_name: str
        :type autocommit: bool
        """
        deleted = self.da_base.delete(id, autocommit=autocommit)
        return deleted


    def get_by_rnode_id(self, year, rnode_id, **kwargs):
        """

        :param year:
        :type year: int
        :param rnode_id:
        :type rnode_id: str
        :rtype: SnowRouteInfo
        """
        as_model = kwargs.get('as_model', False)
        sstr = '"%s"'%rnode_id

        item = self.da_base.session.query(model.SnowRoute).filter(
            and_(
                or_(
                    model.SnowRoute.route1.like('%{}%'.format(sstr)),
                    model.SnowRoute.route2.like('%{}%'.format(sstr)),
                ),
                model.SnowRoute._snowroute_group.has(year=year)
            )
        ).first()

        if as_model:
            return item
        else:
            return self.da_base.to_info(item)

    def list_by_year(self, year, **kwargs):
        """

        :param year:
        :type year: int
        :rtype: list[SnowRouteInfo]
        """
        as_model = kwargs.get('as_model', False)

        qry = self.da_base.session.query(model.SnowRoute).filter(
            model.SnowRoute._snowroute_group.has(year=year))

        res = []
        for item in qry:
            if as_model:
                res.append(item)
            else:
                res.append(self.da_base.to_info(item))
        return res

    def insert(self, r, autocommit=False):
        """
        :type r: SnowRouteInfo
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

    def search(self, searches, op='and', cond='match', **kwargs):
        """ search nsr_data

        **Example**
            - find item that `sevent_id` is 1
                >>> search([('sevent_id', 1)]

            - find item that `name` == 'test and start_time == 2016-01-01 00:00 and end_time == 2016-01-01 07:00
                >>> search([('name', 'test'), ('start_time', datetime(2016, 1, 1, 0, 0)), ('end_time', 2016, 1, 1, 7, 0)], op='and', cond='match')

            - find items that `ymds` contains one of 2014, 2015 and 2016
                >>> search([('ymds', y) for y in [2014, 2015, 2016]], op='or', cond='like')
        """
        return self.da_base.search(searches, op, cond, **kwargs)

    def rollback(self):
        self.da_base.session.rollback()

    def commit(self):
        self.da_base.commit()

    def close(self):
        self.da_base.close()
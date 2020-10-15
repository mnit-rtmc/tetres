# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from sqlalchemy import or_, and_

from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import SnowManagementInfo


class SnowMgmtDataAccess(DataAccess):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model.SnowManagement, SnowManagementInfo, **kwargs)

    def list(self, **kwargs):
        """
        :rtype: list[SnowManagementInfo]
        """
        return self.da_base.list(**kwargs)

    def list_by_period(self, sdt, edt, **kwargs):
        """

        :type sdt: datetime.datetime
        :type edt: datetime.datetime
        :rtype: list[SnowManagementInfo]
        """

        sdt = sdt.replace(second=0, microsecond=0)
        edt = edt.replace(second=59, microsecond=59)

        qry = (self.da_base.session.query(self.da_base.dbModel)
            .join(model.SnowEvent)
            .filter(
            or_(
                and_(model.SnowEvent.start_time <= sdt, model.SnowEvent.end_time >= sdt),
                and_(model.SnowEvent.start_time >= sdt, model.SnowEvent.end_time <= edt),
                and_(model.SnowEvent.start_time <= edt, model.SnowEvent.end_time >= edt),
            )
        ))

        data_list = []
        for model_data in qry:
            data_list.append(self.da_base.to_info(model_data, **kwargs))
        return data_list

    def get_by_id(self, route_id):
        """
        :type route_id: int
        :rtype: SnowManagementInfo
        """
        return self.da_base.get_data_by_id(route_id)

    def get_by_name(self, route_name):
        """
        :type route_name: str
        :rtype: SnowManagementInfo
        """
        return self.da_base.get_data_by_name(route_name)

    def insert(self, r, **kwargs):
        """
        :type r: SnowManagementInfo
        :rtype: model.SnowManagement
        """
        return self.da_base.insert(r, **kwargs)

    def search(self, searches, op='and', cond='match', **kwargs):
        """
        :type searches: list
        :return:
        """
        return self.da_base.search(searches, op=op, cond=cond, **kwargs)
# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.tool import tb
from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import TODReliabilityInfo


class TODReliabilityDataAccess(DataAccess):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model.TODReliability, TODReliabilityInfo, **kwargs)

    def list(self):
        """
        :rtype: list[TODReliabilityInfo]
        """
        return self.da_base.list()

    def list_by_route(self, ttr_id, regime_type, **kwargs):
        """
        :type ttr_id: int
        :rtype: list[TODReliabilityInfo]
        """
        as_model = kwargs.get('as_model', False)
        qry = (self.da_base.session.query(self.da_base.dbModel)
               .filter(model.TODReliability.route_id == ttr_id)
               .filter(model.TODReliability.regime_type == regime_type)
               )
        data_list = []
        for model_data in qry:
            if as_model:
                data_list.append(model_data)
            else:
                data_list.append(self.da_base.to_info(model_data))
        return data_list

    def get_by_id(self, id):
        """
        :type id: int
        :rtype: TODReliabilityInfo
        """
        return self.da_base.get_data_by_id(id)

    def delete_all_for_a_route(self, ttri_id, **kwargs):
        """
        :type ttri_id: int
        """
        print_exception = kwargs.get('print_exception', False)

        try:
            qry = (self.da_base.session.query(self.da_base.dbModel)
                   .filter(self.da_base.dbModel.route_id == ttri_id))

            qry.delete(synchronize_session=False)
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def insert(self, r, **kwargs):
        """
        :type r: TODReliabilityInfo
        :rtype: model.TTRoute
        """
        return self.da_base.insert(r, **kwargs)
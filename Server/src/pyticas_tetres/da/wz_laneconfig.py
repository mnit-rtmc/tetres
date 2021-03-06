# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import WorkZoneLaneConfigInfo


class WZLaneConfigDataAccess(DataAccess):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model.WorkZoneLaneConfig, WorkZoneLaneConfigInfo, **kwargs)

    def list(self, wz_id, **kwargs):
        """

        :type wz_id: int
        :rtype: list[WorkZoneLaneConfigInfo] or list[model.WorkZoneLaneConfig]
        """
        return self.da_base.search([('wz_id', wz_id)], cond='match', **kwargs)

    def list_by_wz_ids(self, wz_ids, **kwargs):
        """

        :type wz_ids: list[int]
        :rtype: Union(list[WorkZoneLaneConfigInfo], list[model.WorkZoneLaneConfig])
        """
        if not wz_ids:
            return []
        as_model = kwargs.get('as_model', False)
        window_size = kwargs.get('window_size', 1000)

        sess = self.da_base.session
        dbModel = self.da_base.dbModel
        qry = sess.query(dbModel).filter(dbModel.wz_id.in_(wz_ids))

        for m in self.da_base.query_generator(qry, window_size):
            if as_model:
                yield m
            else:
                yield self.da_base.to_info(m)

    def get_by_id(self, wzf_id):
        """
        :type wzf_id: int
        :rtype: pyticas_tetres.ttypes.WorkZoneLaneConfigInfo
        """
        return self.da_base.get_data_by_id(wzf_id)

    def insert(self, wzli, **kwargs):
        """
        :type wzli: pyticas_tetres.ttypes.WorkZoneLaneConfigInfo
        :rtype: model.WorkZoneLaneConfig
        """
        return self.da_base.insert(wzli, **kwargs)

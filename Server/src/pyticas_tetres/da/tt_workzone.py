# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
from collections import defaultdict

from pyticas_tetres.db.tetres import model_yearly
from pyticas_tetres.da.base_ext import ExtDataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.da.wz_feature import WZFeatureDataAccess
from pyticas_tetres.da.wz_laneconfig import WZLaneConfigDataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import TTWorkzoneInfo


class TTWorkZoneDataAccess(DataAccess):
    def __init__(self, year, **kwargs):
        super().__init__(**kwargs)
        self.da_base = ExtDataAccessBase(year,
                                         model_yearly.get_tt_workzone_table(year),
                                         model.WorkZone,
                                         TTWorkzoneInfo,
                                         **kwargs)
        self.wzfDA = WZFeatureDataAccess(session=self.da_base.session)
        self.wzlDA = WZLaneConfigDataAccess(session=self.da_base.session)

    def list(self, ttri_id, sdt, edt, **kwargs):
        """

        :type ttri_id: int
        :type sdt: datetime.datetime
        :type edt: datetime.datetime
        :rtype: list[TTWorkzoneInfo]
        """
        return self.da_base.list(ttri_id, sdt, edt, **kwargs)

    def list_with_features(self, ttri_id, sdt, edt, **kwargs):
        """

        :type ttri_id: int
        :type sdt: datetime.datetime
        :type edt: datetime.datetime
        :rtype: (list[TTWorkzoneInfo], dict[int, list[model.WorkZoneFeature]], dict[int, list[model.WorkZoneLaneConfig]]) or (list[TTWorkzoneInfo], dict[int, list[WorkZoneFeatureInfo]], dict[int, list[model.WorkZoneLaneConfigInfo]])
        """
        qry = (self.da_base.session.query(self.da_base.dbModel, model.WorkZoneFeature, model.WorkZoneLaneConfig)
               .join(self.da_base.ttModel)
               .join(self.da_base.extModel)
               .join(model.WorkZoneFeature)
               .join(model.WorkZoneLaneConfig)
               .filter(self.da_base.extModel.id == model.WorkZoneFeature.wz_id)
               .filter(self.da_base.extModel.id == model.WorkZoneLaneConfig.wz_id)
               .filter(self.da_base.ttModel.route_id == ttri_id)
               .filter(self.da_base.ttModel.time <= edt)
               .filter(self.da_base.ttModel.time >= sdt))

        as_model = kwargs.get('as_model', False)

        ttwzs = []
        features = defaultdict(list)
        lncfgs = defaultdict(list)

        for (ttwz, wzf, wzl) in qry:
            if ttwz not in ttwzs:
                ttwzs.append(ttwz)
            if wzf not in features[ttwz.id]:
                features[ttwz.id].append(wzf)
            if wzl not in lncfgs[ttwz.id]:
                lncfgs[ttwz.id].append(wzl)

        if not as_model:
            for idx, ttwz in enumerate(ttwzs):
                ttwzs[idx] = self.da_base.to_info(ttwz)
                for fidx, wzf in enumerate(features[ttwz.id]):
                    features[ttwz.id][fidx] = self.wzfDA.da_base.to_info(wzf)
                for lidx, wzl in enumerate(lncfgs[ttwz.id]):
                    lncfgs[ttwz.id][lidx] = self.wzlDA.da_base.to_info(wzl)

        return ttwzs, features, lncfgs

    def get_by_id(self, id):
        """
        :type id: int
        :rtype: TTWorkzoneInfo
        """
        return self.da_base.get_data_by_id(id)

    def delete_range(self, ttri_id, sdt, edt, **kwargs):
        """
        :type ttri_id: int
        :type sdt: datetime.datetime
        :type edt: datetime.datetime
        """
        return self.da_base.delete_range(ttri_id, sdt, edt, **kwargs)

    def delete_all_for_a_route(self, ttri_id, **kwargs):
        """
        :type ttri_id: int
        :rtype: bool
        """
        return self.da_base.delete_all_for_a_route(ttri_id, **kwargs)

    def delete_if_route_is_deleted(self, **kwargs):
        """
        :rtype: bool
        """
        return self.da_base.delete_if_route_is_deleted(**kwargs)

    def insert(self, ttwzi, **kwargs):
        """
        :type ttwzi: TTWorkzoneInfo
        :rtype: model.TTWorkzone<Year>
        """
        return self.da_base.insert(ttwzi, **kwargs)

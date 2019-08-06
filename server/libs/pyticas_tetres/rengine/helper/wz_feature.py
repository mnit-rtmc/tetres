# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'
import json

from pyticas_tetres import tetres
from pyticas_tetres.da.wz_feature import WZFeatureDataAccess
from pyticas_tetres.da.wz_laneconfig import WZLaneConfigDataAccess
from pyticas_tetres.rengine.helper import wz as wz_helper
from pyticas_tetres.ttypes import WorkZoneInfo, WorkZoneFeatureInfo, WorkZoneLaneConfigInfo, WZCharacteristics


def wz_insert_feature(wzi):
    """
    :type wzi: WorkZoneInfo
    :rtype: bool
    """
    wz_id = wzi.id

    wzfDA = WZFeatureDataAccess()
    wzlDA = WZLaneConfigDataAccess()

    (wz_length1, _features1, _lncfgs1, n_closed_ramps1) = wz_helper.features(wzi, 1)
    (wz_length2, _features2, _lncfgs2, n_closed_ramps2) = wz_helper.features(wzi, 2)

    for wzfi in wzfDA.list(wz_id):
        if not wzfDA.delete(wzfi.id):
            return False

    for wzli in wzlDA.list(wz_id):
        if not wzlDA.delete(wzli.id):
            return False

    wzli_data = _get_wzli_data(wz_id, 1, _lncfgs1) + _get_wzli_data(wz_id, 2, _lncfgs2)
    if not wzlDA.bulk_insert(wzli_data):
        return False

    wzfi_data = [_get_wzfi_data(wz_id, 1, wz_length1, _features1, n_closed_ramps1),
                 _get_wzfi_data(wz_id, 2, wz_length2, _features2, n_closed_ramps2)]

    if not wzfDA.bulk_insert(wzfi_data):
        return False

    return True


def update_all_workzone_features():
    from pyticas_tetres.da.wz import WorkZoneDataAccess
    da_wz = WorkZoneDataAccess()
    for wzi in da_wz.list():
        wz_insert_feature(wzi)


def get_wz_feature(wzi, wz_features, wz_lncfgs, corridor):
    """
    :type wzi: WorkZoneInfo
    :type wz_features: list[pyticas_tetres.db.model.WorkZoneFeature]
    :type wz_lncfgs: list[pyticas_tetres.db.model.WorkZoneLaneConfig]
    :type corridor: pyticas.ttypes.CorridorObject or str
    :rtype: (pyticas_tetres.db.model.WorkZoneFeature, pyticas_tetres.db.model.WorkZoneLaneConfig)
    """

    infra = tetres.get_infra()
    corr_name = corridor if isinstance(corridor, str) else corridor.name
    route1_dict = json.loads(wzi.route1)
    route_num = 1 if infra.get_rnode(route1_dict['rnodes'][0]).corridor.name == corr_name else 2
    features = [v for v in wz_features if v.route_num == route_num]
    lncfgs = [v for v in wz_lncfgs if v.route_num == route_num]
    return (features, lncfgs)

def _get_wzli_data(wz_id, route_num, lncfgs):
    dict_data = []
    for (origin_lanes, open_lanes) in lncfgs:
        dict_data.append({
            'wz_id' : wz_id,
            'route_num' : route_num,
            'origin_lanes' : origin_lanes,
            'open_lanes' : open_lanes
        })
    return dict_data

def _get_wzfi_data(wz_id, route_num, wz_length, features, n_closed_ramps):
    return {
        'wz_id' : wz_id,
        'route_num' : route_num,
        'closed_length' : wz_length,
        'closed_ramps' : n_closed_ramps,
        'use_opposing_lane' : WZCharacteristics.USE_OPPOSING_LANE in features,
        'used_by_opposing_traffic' : WZCharacteristics.USED_BY_OPPOSING_TRAFFICS in features,
        'has_closed' : WZCharacteristics.HAS_CLOSED_LANES in features,
        'has_shifted' : WZCharacteristics.HAS_SHIFTED_LANES in features,
    }
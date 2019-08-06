# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.cfg import WZ_DOWNSTREAM_DISTANCE_LIMIT, WZ_UPSTREAM_DISTANCE_LIMIT
from pyticas_tetres.da.tt_workzone import TTWorkZoneDataAccess
from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine.helper import loc
from pyticas_tetres.rengine.helper import wz as wz_helper
from pyticas_tetres.ttypes import LOC_TYPE
from pyticas_tetres.util.noop_context import nonop_with


def categorize(ttri, prd, ttdata, **kwargs):
    """

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type prd: pyticas.ttypes.Period
    :type ttdata: list[pyticas_tetres.ttypes.TravelTimeInfo]
    :return:
    """
    lock = kwargs.get('lock', nonop_with())

    given_wzs = kwargs.get('workzones', None)
    wzs = given_wzs or wz_helper.find_workzones(prd)

    workzones = []
    for wzi in wzs:
        loc_type, distance, off_distance = loc.location(ttri.route, wzi.route1)
        r = wzi.route1
        if loc_type == None:
            # distance : distance between the most upstream rnodes
            # off-distance : 0 if it is overlapeed,
            #                negative : workzone is located in upstream of the route
            #                positive : workzone is located in downstream of the route
            loc_type, distance, off_distance = loc.location(ttri.route, wzi.route2)
            r = wzi.route2

        if loc_type == None:
            continue

        if (loc_type == LOC_TYPE.DOWN and off_distance > WZ_DOWNSTREAM_DISTANCE_LIMIT
                or loc_type == LOC_TYPE.UP and abs(off_distance) > WZ_UPSTREAM_DISTANCE_LIMIT):
            continue

        workzones.append((loc_type, distance, off_distance, wzi, r))

    year = prd.start_date.year
    da_tt_wz = TTWorkZoneDataAccess(year)

    # avoid to save duplicated data
    with lock:
        is_deleted = da_tt_wz.delete_range(ttri.id, prd.start_date, prd.end_date, item_ids=[v.id for v in wzs])
        if not is_deleted or not da_tt_wz.commit():
            da_tt_wz.close_session()
            getLogger(__name__).warning('! workzone.categorize(): fail to delete existing data')
            return -1

    dict_data = []
    for idx, tti in enumerate(ttdata):
        wzs = _find_wzs(workzones, tti.str2datetime(tti.time))
        for (loc_type, distance, off_distance, wzi, r) in wzs:
            dict_data.append({
                'tt_id': tti.id,
                'workzone_id': wzi.id,
                'loc_type': loc_type.value,
                'distance': distance,
                'off_distance': off_distance
            })

    if dict_data:
        with lock:
            inserted_ids = da_tt_wz.bulk_insert(dict_data, print_exception=True)
            if not inserted_ids or not da_tt_wz.commit():
                da_tt_wz.rollback()
                da_tt_wz.close_session()
                getLogger(__name__).warning('! workzone.categorize(): fail to insert categorized data')
                return -1

    da_tt_wz.close_session()
    return len(dict_data)


def _find_wzs(workzones, dt):
    """
    :type workzones: list[(pyticas_tetres.ttypes.LOC_TYPE, float, float, pyticas_tetres.ttypes.WorkZoneInfo, pyticas.ttypes.Route)]
    :type dt: datetime.datetime
    :rtype: list[(pyticas_tetres.ttypes.LOC_TYPE, float, float, pyticas_tetres.ttypes.WorkZoneInfo, pyticas.ttypes.Route)]
    """
    wzs = []
    for idx, (loc_type, distance, off_distance, wz, r) in enumerate(workzones):
        if wz.str2datetime(wz.start_time) <= dt <= wz.str2datetime(wz.end_time):
            wzs.append((loc_type, distance, off_distance, wz, r))
    return wzs


def _get_wz_feature(wzi, wz_features, wz_lncfgs, corridor):
    """
    :type wzi: WorkZoneInfo
    :type wz_features: list[pyticas_tetres.ttypes.WorkZoneFeatureInfo]
    :type wz_lncfgs: list[pyticas_tetres.ttypes.WorkZoneLaneConfigInfo]
    :type corridor: pyticas.ttypes.CorridorObject or str
    :rtype: (list[pyticas_tetres.ttypes.WorkZoneFeatureInfo], list[pyticas_tetres.ttypes.WorkZoneLaneConfigInfo])
    """

    # infra = Infra.get_infra()
    corr_name = corridor if isinstance(corridor, str) else corridor.name
    # route1_dict = json.loads(wzi.route1)
    route_num = 1 if wzi.route1.rnodes[0].corridor.name == corr_name else 2
    features = [v for v in wz_features if v.route_num == route_num]
    lncfgs = [v for v in wz_lncfgs if v.route_num == route_num]
    return (features, lncfgs)

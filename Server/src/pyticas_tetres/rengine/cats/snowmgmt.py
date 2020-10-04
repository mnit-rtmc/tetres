# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas_tetres.da.snowmgmt import SnowMgmtDataAccess
from pyticas_tetres.da.tt_snowmgmt import TTSnowManagementDataAccess
from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine.helper import loc
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

    snmDA = SnowMgmtDataAccess()
    ttsnmDA = TTSnowManagementDataAccess(prd.start_date.year, session=snmDA.get_session())

    given_snowmgmts = kwargs.get('snowmgmts', None)
    snowmgmts = given_snowmgmts or snmDA.list_by_period(prd.start_date, prd.end_date, set_related_model_info=True)
    snmis = _decide_location(ttri, snowmgmts)

    with lock:
        is_deleted = ttsnmDA.delete_range(ttri.id, prd.start_date, prd.end_date, item_ids=[v.id for v in snowmgmts])
        if not is_deleted or not ttsnmDA.commit():
            ttsnmDA.rollback()
            ttsnmDA.close_session()
            getLogger(__name__).warning('! snowmgmt.categorize(): fail to delete existing data')
            return -1

    dict_data = []
    for idx, tti in enumerate(ttdata):
        dt = tti.str2datetime(tti.time)
        _snmis = _find_snowmgmts(snmis, dt)
        for (loc_type, distance, off_distance, snmi, r) in _snmis:
            dict_data.append({
                'tt_id': tti.id,
                'snowmgmt_id': snmi.id,
                'loc_type': loc_type.value,
                'distance': distance,
                'off_distance': off_distance,
                'road_status': -1,
            })

    if dict_data:
        with lock:
            inserted_ids = ttsnmDA.bulk_insert(dict_data, print_exception=True)
            if not inserted_ids or not ttsnmDA.commit():
                ttsnmDA.rollback()
                ttsnmDA.close_session()
                getLogger(__name__).warning('! snowmgmt.categorize(): fail to insert categorized data')
                return -1

    ttsnmDA.close_session()

    return len(dict_data)


def _road_status(dt, snmi):
    """
    :type dt: datetime.datetime
    :type snmi: pyticas_tetres.ttypes.SnowManagementInfo
    :rtype: int
    """
    if snmi.str2datetime(snmi.lane_lost_time) <= dt < snmi.str2datetime(snmi.lane_regain_time):
        return -1
    else:
        return 1


def _decide_location(ttri, snowmgmts):
    """
    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type snowmgmts: list[pyticas_tetres.ttypes.SnowManagementInfo]
    :type dt: datetime.datetime
    :rtype: list[(pyticas_tetres.ttypes.LOC_TYPE, float, float, pyticas_tetres.ttypes.SnowManagementInfo, pyticas.ttypes.Route)]
    """
    overlapped_loc_types = [LOC_TYPE.DOWN_OVERLAPPED.value, LOC_TYPE.UP_OVERLAPPED.value, LOC_TYPE.WRAP.value,
                            LOC_TYPE.INSIDE.value]
    snmis = []
    for snmi in snowmgmts:
        loc_type, distance, off_distance = loc.location(ttri.route, snmi._snowroute.route1)
        r = snmi._snowroute.route1
        if loc_type == None:
            loc_type, distance, off_distance = loc.location(ttri.route, snmi._snowroute.route2)
            r = snmi._snowroute.route2

        if loc_type not in overlapped_loc_types:
            continue
        snmis.append((loc_type, distance, off_distance, snmi, r))
    return snmis


def _find_snowmgmts(snowmgmts, dt):
    """
    :type snowmgmts: list[(pyticas_tetres.ttypes.LOC_TYPE, float, float, pyticas_tetres.ttypes.SnowManagementInfo, pyticas.ttypes.Route)]
    :type dt: datetime.datetime
    :rtype: list[(pyticas_tetres.ttypes.LOC_TYPE, float, float, pyticas_tetres.ttypes.SnowManagementInfo, pyticas.ttypes.Route)]
    """
    seis = []
    for idx, (loc_type, distance, off_distance, snmi, r) in enumerate(snowmgmts):
        start_time = snmi.str2datetime(snmi.lane_lost_time)
        end_time = snmi.str2datetime(snmi.lane_regain_time)
        # only for lane-lost data
        if start_time <= dt < end_time:
            seis.append((loc_type, distance, off_distance, snmi, r))
    return seis

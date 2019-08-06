# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.tool import distance as dist_util
from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core.est.target import lane

DISTANCE_LIMIT_TO_CHECK_ANGLE = 0.2
WITHRAW_STATION_ANGLE = 120 # use only the stations that the angle is over 120 degree

def get_target_stations(corr_name):
    """ Returns potential target stations satisfying the following conditions
    
    **Conditions**
        - normal station 
            - not temporary station
            - not wavetronics station
            - not radar station
            - not velocity station
        - has target lanes
            - lane 2 or lane 3 (when lane 1 is an auxiliary lane)
        - not on curve
            - the station on curve shows lower-level of U-K comparing to nearby stations

    :type corr_name: str
    :rtype: list[pyticas.ttypes.RNodeObject]
    """
    infra = ncrtes.get_infra()
    corr = infra.get_corridor_by_name(corr_name)
    stations = []
    for st in corr.stations:
        if not st.is_normal_station():
            continue
        if not any(lane.get_target_detectors(st)):
            continue

        up_station, dn_station = _find_up_and_down_stations(st)
        if up_station is not None:
            angle = infra.geo.angle_of_rnodes(up_station, st, dn_station)
            if angle < WITHRAW_STATION_ANGLE:
                continue

        stations.append(st)

    return stations


def _find_up_and_down_stations(station):
    """
    
    :type station: pyticas.ttypes.RNodeObject 
    :rtype: (pyticas.ttypes.RNodeObject, pyticas.ttypes.RNodeObject)
    """
    up_station, dn_station = None, None
    cur_station = station
    acc_d = 0.0
    while cur_station.up_station is not None:
        cur_station = cur_station.up_station
        acc_d += dist_util.distance_in_mile(cur_station, cur_station.down_station)
        if acc_d >= DISTANCE_LIMIT_TO_CHECK_ANGLE:
            up_station = cur_station
            break
    if not up_station:
        return None, None

    cur_station = station
    acc_d = 0.0
    while cur_station.down_station is not None:
        cur_station = cur_station.down_station
        acc_d += dist_util.distance_in_mile(cur_station, cur_station.up_station)
        if acc_d >= DISTANCE_LIMIT_TO_CHECK_ANGLE:
            dn_station= cur_station
            break
    if not dn_station:
        return None, None

    return up_station, dn_station
# -*- coding: utf-8 -*-
from typing import List

import numpy as np
from colorama import Fore

from pyticas.moe import moe
from pyticas.moe.imputation import spatial_avg
from pyticas.rc import route_config
from pyticas.tool import tb
from pyticas.ttypes import RNodeData
from pyticas_tetres.da.route import TTRouteDataAccess
from pyticas_tetres.da.tt import TravelTimeDataAccess
from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine.helper.wz import apply_workzone
from pyticas_tetres.util.noop_context import nonop_with

"""
Travel Time Calculation
=======================

- run at beginning of the day to calculate tt of the previous day for all TTR routes

"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def calculate_all_routes(prd, **kwargs):
    """ calculate travel time, average speed and VMT during the given time period
    and put whole_data to database (travel time table)

    :type prd: pyticas.ttypes.Period
    :rtype: list[dict]
    """
    logger = getLogger(__name__)
    logger.info('calculating travel time : %s' % prd.get_period_string())

    res = []
    ttr_route_da = TTRouteDataAccess()
    routes = ttr_route_da.list()
    ttr_route_da.close_session()
    total = len(routes)
    for ridx, ttri in enumerate(routes):
        logger.info('(%d/%d) calculating travel time for %s(%s) : %s'
                    % ((ridx + 1), total, ttri.name, ttri.id, prd.get_period_string()))
        is_inserted = calculate_a_route(prd, ttri, lock=kwargs.get('lock', nonop_with()))
        res.append({'route_id': ttri.id, 'done': is_inserted})

    return res


def print_rnode_data(lst: List[RNodeData]) -> None:
    for i in range(len(lst)):
        print(f"> {Fore.MAGENTA}Title[{lst[i].get_title(no_lane_info=True)}] DataListLength[{len(lst[i].data)}]")


def calculate_a_route(prd, ttri, **kwargs):
    """

    :type prd: pyticas.ttypes.Period
    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    """

    logger = getLogger(__name__)
    dbsession = kwargs.get('dbsession', None)

    if dbsession:
        da_tt = TravelTimeDataAccess(prd.start_date.year, session=dbsession)
    else:
        da_tt = TravelTimeDataAccess(prd.start_date.year)

    lock = kwargs.get('lock', nonop_with())

    # delete data to avoid duplicated data
    with lock:
        is_deleted = da_tt.delete_range(ttri.id, prd.start_date, prd.end_date, print_exception=True)
        if not is_deleted or not da_tt.commit():
            logger.warning('fail to delete the existing travel time data')
            if not dbsession:
                da_tt.close_session()
            return False

    # faverolles 10/20/2019 NOTE: HERE

    print(f"{Fore.GREEN}CALCULATING TRAVEL-TIME FOR ROUTE[{ttri.name}]")

    res_list = _calculate_tt(ttri.route, prd)

    names = ["tt", "speed", "vmt", "vht",
             "dvh", "lvmt", "sv", "acceleration", "cm", "cmh"]
    ctr = 0
    for i in res_list:
        print(f"{Fore.YELLOW}MOE[{names[ctr]}] RNodeDataCount[{len(i)}]")
        print_rnode_data(i)
        ctr += 1

    if res_list[0] is None:
        logger.warning('fail to calculate travel time')
        return False

    travel_time = res_list[0][-1].data
    avg_speeds = _route_avgs(res_list[1])
    total_vmts = _route_total(res_list[2])  # flow
    res_vht = _route_total(res_list[3])  # speed
    res_dvh = _route_total(res_list[4])  # flow
    res_lvmt = _route_total(res_list[5])  # density
    res_sv = _route_avgs(res_list[6])  # speed

    avg_accel = _route_avgs(res_list[7])
    total_cm = _route_total(res_list[8])
    total_cmh = _route_total(res_list[9])

    timeline = prd.get_timeline(as_datetime=False, with_date=True)
    print(f"{Fore.CYAN}Start[{timeline[0]}] End[{timeline[-1]}] TimelineLength[{len(timeline)}]")
    data = []
    for index, dateTimeStamp in enumerate(timeline):
        data.append({
            'route_id': ttri.id,
            'time': dateTimeStamp,
            'tt': travel_time[index],
            'speed': avg_speeds[index],
            'vmt': total_vmts[index],
            'vht': res_vht[index],
            'dvh': res_dvh[index],
            'lvmt': res_lvmt[index],
            'sv': res_sv[index],
        })

    with lock:
        inserted_ids = da_tt.bulk_insert(data)
        if not inserted_ids or not da_tt.commit():
            logger.warning('fail to insert the calculated travel time into database')
            if not dbsession:
                da_tt.close_session()
            return False

    if not dbsession:
        da_tt.close_session()

    return inserted_ids


def _calculate_tt(r, prd, **kwargs) -> List[List[RNodeData]]:
    """

    :type r: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    """
    # 1. update lane configuration according to work zone
    cloned_route = r.clone()

    if kwargs.get('nowz', False):
        updated_route = cloned_route
    else:
        cloned_route.cfg = route_config.create_route_config(cloned_route.rnodes)
        updated_route = apply_workzone(cloned_route, prd)

    # 2. calculate TT and Speed and VMT
    try:
        return [moe.travel_time(updated_route, prd),
                moe.speed(updated_route, prd),
                moe.vmt(updated_route, prd),
                moe.vht(updated_route, prd),
                moe.dvh(updated_route, prd),
                moe.lvmt(updated_route, prd),
                moe.sv(updated_route, prd),
                moe.acceleration(updated_route, prd),
                moe.cm(updated_route, prd),
                moe.cmh(updated_route, prd)]

    except Exception as ex:
        getLogger(__name__).warning(tb.traceback(ex))


def _route_avgs(res_list):
    """

    :type res_list: list[pyticas.ttypes.RNodeData]
    :rtype: list[float]
    """
    data_list = [res.data for res in res_list]
    imputated_data = spatial_avg.imputation(data_list)
    n_stations = len(res_list)
    n_data = len(res_list[0].prd.get_timeline())
    avgs = []
    for didx in range(n_data):
        data = [imputated_data[sidx][didx] for sidx in range(n_stations) if imputated_data[sidx][didx] >= 0]
        avgs.append(np.mean(data))
    return avgs


def _route_total(res_list):
    """

    :type res_list: list[pyticas.ttypes.RNodeData]
    :rtype: list[float]
    """
    data_list = [res.data for res in res_list]
    n_stations = len(res_list)
    n_data = len(res_list[0].prd.get_timeline())
    total_values = []
    for didx in range(n_data):
        total_values.append(sum([data_list[sidx][didx] for sidx in range(n_stations)]))
    return total_values

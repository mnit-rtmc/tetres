# -*- coding: utf-8 -*-

import datetime
import math

from pyticas.moe import moe_helper
from pyticas.moe.imputation import spatial_avg
from pyticas.ttypes import TrafficType

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

# load_data speed data of 2 hour after the given period to calculate travel time
DEFAULT_END_HOUR_EXTENSION = 2

# add virtual rnode every 0.1 mile
VIRTUAL_RNODE_DISTANCE = moe_helper.VIRTUAL_RNODE_DISTANCE


def run(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :return:
    """
    ext_hour = kwargs.get('ext_hour', DEFAULT_END_HOUR_EXTENSION)
    now = datetime.datetime.now()
    ext_prd = prd.clone().extend_end_hour(ext_hour)

    if ext_prd.end_date > datetime.datetime.now():
        ext_prd.end_date = now

    n_origin_data = len(prd.get_timeline())

    # load_data speed data (load_data more data than given period)
    us = moe_helper.get_speed(route.get_stations(), ext_prd, **kwargs)
    us_results = moe_helper.add_virtual_rnodes(us, route)

    us_data = [res.data for res in us_results]
    us_data = spatial_avg.imputation(us_data)

    # make empty whole_data for travel time by copying speed whole_data and reseting data
    tt_results = [res.clone() for res in us_results]
    for idx, res in enumerate(tt_results):
        tt_results[idx].traffic_type = TrafficType.travel_time

    for ridx, res in enumerate(tt_results):
        tt_results[ridx].data = [-1] * n_origin_data
        tt_results[ridx].prd = prd

    # calculate travel time by increasing time index
    for tidx in range(n_origin_data):
        partial_data = [pd[tidx:] for pd in us_data]
        tts = _calculate_tt(partial_data, prd.interval, **kwargs)
        for ridx, tt_data in enumerate(tt_results):
            tt_results[ridx].data[tidx] = tts[ridx]

    return tt_results


def _calculate_tt(data, interval, **kwargs):
    """

    :param data: list of speed data list for each rnode.
                 e.g. data = [ [ u(i,t), u(i,t+1), u(i,t+2) .. ], [ u(i+1,t), u(i+1,t+1), u(i+1,t+2) .. ], [ u(i+2,t), u(i+2,t+1), u(i+2,t+2) .. ],,,]
    :type data: list[list[float]]
    :param interval: data interval in second
    :type interval: int
    :type kwargs: dict
    :return:
    """
    vd = VIRTUAL_RNODE_DISTANCE
    seconds_per_hour = 3600
    max_ridx = len(data)
    max_tidx = len(data[0])
    goal_distance = vd * (max_ridx - 1)

    def tt_next(p):
        """
        :param p: (tt, td, tts, cur_idx),
                   - tt=travel time by the current time point
                   - td=travel distance by the current time point
                   - tts=list to store travel time to each rnode
                   - cur_idx=current rnode index
        :type p: (float, float, list[float], float)
        :rtype: (float, float, list[float], float)
        """
        (tt, td, tts, cur_ridx) = p

        ridx = int(math.floor(p[1] / vd))  # rnode index
        tidx = int(math.floor(p[0] // interval))  # time index

        if (interval * (tidx + 1)) - tt == 0:
            tidx += 1
        if (vd * (ridx + 1)) - td == 0:
            ridx += 1

        if ridx >= max_ridx or tidx >= max_tidx:
            return (None, None)

        if cur_ridx != ridx:
            tts[ridx] = tt / 60.0
        remaining_interval = (interval * (tidx + 1)) - tt
        remaining_distance = (vd * (ridx + 1)) - td

        try:
            u = data[ridx][tidx]
        except Exception as ex:
            print('=> error occured : ', len(data), len(data[0]), ridx, tidx)
            raise ex

        tt_for_remaining_distance = remaining_distance / u * seconds_per_hour
        tt_to_go = min(remaining_interval, tt_for_remaining_distance)
        d_to_go = u * tt_to_go / seconds_per_hour

        return (tt + tt_to_go, td + d_to_go, tts, cur_ridx)

    tts = [0, ] + [-1] * (max_ridx - 1)
    p = (0, 0, tts, 0)  # (tt, td, tts, cur_ridx)
    while True:
        p = tt_next(p)
        if not p[0] or not p[1] or p[0] < 0:
            break
        if p[1] >= goal_distance:
            break

    tts[-1] = p[0] / 60.0 if p[1] >= goal_distance else -1

    return tts


def calculate_tt_dynamically(us_results, us_data, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :return:
    """

    n_origin_data = len(prd.get_timeline())

    # make empty whole_data for travel time by copying speed whole_data and reseting data
    tt_results = [res.clone() for res in us_results]
    for idx, res in enumerate(tt_results):
        tt_results[idx].traffic_type = TrafficType.travel_time

    for ridx, res in enumerate(tt_results):
        tt_results[ridx].data = [-1] * n_origin_data
        tt_results[ridx].prd = prd

    # calculate travel time by increasing time index
    for tidx in range(n_origin_data):
        partial_data = [pd[tidx:] for pd in us_data]
        tts = _calculate_tt(partial_data, prd.interval, **kwargs)
        for ridx, tt_data in enumerate(tt_results):
            tt_results[ridx].data[tidx] = tts[ridx]

    return tt_results

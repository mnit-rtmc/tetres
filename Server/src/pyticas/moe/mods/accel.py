# -*- coding: utf-8 -*-

import copy

from pyticas import cfg
from pyticas.moe import moe_helper
from pyticas.tool.distance import distance_in_mile

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def run(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :return:
    """
    rnode_list = route.get_stations()

    # load_data speed data (load_data more data than given period)
    us_results = moe_helper.get_speed(rnode_list, prd, **kwargs)

    # make empty whole_data for acceleration by copying speed whole_data and reseting data
    accel_results = [res.clone() for res in us_results]

    # calculate travel time by increasing time index
    for ridx, rnode_data in enumerate(_calculate_accel(us_results, prd.interval, **kwargs)):
        accel_results[ridx].data = rnode_data

    return accel_results


def _calculate_accel(speed_results, interval, **kwargs):
    """

    :type speed_results: list[RNodeData]
    :param interval: data interval in second
    :type interval: int
    :type kwargs: dict
    :return:
    """
    missing_data = kwargs.get('missing_data', cfg.MISSING_VALUE)
    us_data = [res.data for res in speed_results]
    accel_data = copy.deepcopy(us_data)
    accel_data[0] = [0] * len(accel_data[0])
    for ridx, rnode_data in enumerate(us_data):
        if not ridx: continue
        for tidx, value in enumerate(rnode_data):
            u1 = us_data[ridx - 1][tidx]
            u2 = value
            if missing_data in [u1, u2]:
                a = missing_data
            else:
                d = distance_in_mile(speed_results[ridx].rnode, speed_results[ridx - 1].rnode)
                a = calculate_acceleration(u1, u2, d)

            accel_data[ridx][tidx] = a

    return accel_data


def calculate_acceleration(u1, u2, mileDistance):
    return (u2 * u2 - u1 * u1) / (2 * mileDistance)

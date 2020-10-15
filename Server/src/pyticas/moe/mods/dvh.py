# -*- coding: utf-8 -*-

import copy

from pyticas import cfg
from pyticas.moe import moe_helper
from pyticas.moe.mods import speed
from pyticas.moe.mods import vmt

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def run(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :return:
    """

    # load_data vmt data
    vmt_results = vmt.run(route, prd)

    # load_data speed data
    us_results = speed.run(route, prd)
    us_results = moe_helper.add_virtual_rnodes(us_results, route)

    # copy whole_data to save VMT values
    dvh_results = [res.clone() for res in vmt_results]

    # calculate VHT
    dvh_data = _calculate_dvh(vmt_results, us_results, prd.interval, **kwargs)
    for ridx, res in enumerate(dvh_results):
        res.data = dvh_data[ridx]

    return dvh_results


def _calculate_dvh(vmt_results, us_results, interval, **kwargs):
    """
    Delayed Vehicle Hour

    Equation : VMT = total flow of station(v/h) * interval(hour) * 0.1(distance in mile);

    Equation : DVH = (VMT / speed) - (VMT / speedLimit)

    :type vmt_results: list[RNodeData]
    :type us_results: list[RNodeData]
    :param interval: data interval in second
    :type interval: int
    :type kwargs: dict
    :return:
    """
    missing_data = kwargs.get('missing_data', cfg.MISSING_VALUE)

    vmt_data = [res.data for res in vmt_results]
    us_data = [res.data for res in us_results]

    dvh_data = copy.deepcopy(vmt_data)
    for ridx, rnode_data in enumerate(vmt_data):
        for tidx, value in enumerate(rnode_data):
            dvh = (vmt_data[ridx][tidx] / us_data[ridx][tidx]) - (vmt_data[ridx][tidx] / vmt_results[ridx].speed_limit)
            if dvh < 0 or missing_data in [vmt_data[ridx][tidx], us_data[ridx][tidx]]:
                dvh = 0
            dvh_data[ridx][tidx] = dvh
    return dvh_data


def calculate_dvh_dynamically(meta_data, interval, **kwargs):
    """
    Vehicle Miles Traveled (Trips per vehicle X miles per trip)
    Equation : VMT = total flow of station(v/h) * interval(hour) * 0.1(distance in mile);

    :param data: list of speed data list for each rnode.
                 e.g. data = [ [ u(i,t), u(i,t+1), u(i,t+2) .. ], [ u(i+1,t), u(i+1,t+1), u(i+1,t+2) .. ], [ u(i+2,t), u(i+2,t+1), u(i+2,t+2) .. ],,,]
    :type data: list[list[float]]
    :param interval: data interval in second
    :type interval: int
    :type kwargs: dict
    :return:
    """
    flow_data = meta_data.get('flow')
    speed_data = meta_data.get('speed')
    speed_limit_data = meta_data.get('speed_limit')
    missing_data = kwargs.get('missing_data', cfg.MISSING_VALUE)
    vd = moe_helper.VIRTUAL_RNODE_DISTANCE
    seconds_per_hour = 3600
    dvh_data = []
    for flow, speed, speed_limit in zip(flow_data, speed_data, speed_limit_data):
        try:
            dvh = ((vd / speed) - (vd / speed_limit)) * flow * interval / seconds_per_hour
            if dvh < 0 or missing_data in [flow, speed_data]:
                dvh = 0
        except Exception as e:
            print(e)
            dvh = 0
        dvh_data.append(dvh)
    return sum(dvh_data)

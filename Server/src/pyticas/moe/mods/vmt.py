# -*- coding: utf-8 -*-

import copy

from pyticas import cfg
from pyticas.moe import moe_helper

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def run(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :return:
    """
    rnode_list = route.get_stations()

    # load_data total flow data
    tq = moe_helper.get_total_flow(rnode_list, prd, **kwargs)
    tq_results = moe_helper.add_virtual_rnodes(tq, route)
    tq_data = [res.data for res in tq_results]

    # copy whole_data to save VMT values
    n_data = len(prd.get_timeline())
    vmt_results = [res.clone() for res in tq_results]

    # calculate VMT
    vmt_data = _calculate_vmt(tq_data, prd.interval, **kwargs)
    for ridx, res in enumerate(vmt_results):
        res.data = vmt_data[ridx]

    return vmt_results


def _calculate_vmt(data, interval, **kwargs):
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
    missing_data = kwargs.get('missing_data', cfg.MISSING_VALUE)
    vd = moe_helper.VIRTUAL_RNODE_DISTANCE
    seconds_per_hour = 3600
    vmt_data = copy.deepcopy(data)
    for ridx, rnode_data in enumerate(data):
        for tidx, value in enumerate(rnode_data):
            vmt = value * interval / seconds_per_hour * vd
            if value == missing_data:
                vmt = missing_data
            vmt_data[ridx][tidx] = vmt
    return vmt_data


def calculate_vmt_dynamically(meta_data, interval, **kwargs):
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
    data = meta_data.get('flow')
    missing_data = kwargs.get('missing_data', cfg.MISSING_VALUE)
    vd = moe_helper.VIRTUAL_RNODE_DISTANCE
    seconds_per_hour = 3600
    vmt_data = copy.deepcopy(data)
    for ridx, rnode_data in enumerate(data):
        for tidx, value in enumerate(rnode_data):
            vmt = value * interval / seconds_per_hour * vd
            if value == missing_data:
                vmt = missing_data
            vmt_data[ridx][tidx] = vmt
    return vmt_data

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
    rnode_list = route.get_stations()

    # load_data vmt data
    vmt_results = vmt.run(route, prd)
    vmt_data = [res.data for res in vmt_results]

    # load_data speed data
    us_results = speed.run(route, prd)
    us_results = moe_helper.add_virtual_rnodes(us_results, route)
    us_data = [res.data for res in us_results]

    # copy results to save VMT values
    vht_results = [res.clone() for res in us_results]

    # calculate VMT
    vht_data = _calculate_vht(vmt_data, us_data, prd.interval, **kwargs)
    for ridx, res in enumerate(vht_results):
        res.data = vht_data[ridx]

    return vht_results


def _calculate_vht(vmt_data, speed_data, interval, **kwargs):
    """
    Vehicle Hour Traveled

    Equation : VHT = VMT / speed

    :param vmt_data: list of speed data list for each rnode.
                 e.g. data = [ [ u(i,t), u(i,t+1), u(i,t+2) .. ], [ u(i+1,t), u(i+1,t+1), u(i+1,t+2) .. ], [ u(i+2,t), u(i+2,t+1), u(i+2,t+2) .. ],,,]
    :type vmt_data: list[list[float]]
    :param speed_data: list of speed data list for each rnode.
                 e.g. data = [ [ u(i,t), u(i,t+1), u(i,t+2) .. ], [ u(i+1,t), u(i+1,t+1), u(i+1,t+2) .. ], [ u(i+2,t), u(i+2,t+1), u(i+2,t+2) .. ],,,]
    :type speed_data: list[list[float]]
    :param interval: data interval in second
    :type interval: int
    :type kwargs: dict
    :return:
    """
    missing_data = kwargs.get('missing_data', cfg.MISSING_VALUE)
    vht_data = copy.deepcopy(vmt_data)
    for ridx, rnode_data in enumerate(vmt_data):
        for tidx, value in enumerate(rnode_data):
            vht = vmt_data[ridx][tidx] / speed_data[ridx][tidx]
            if missing_data in [vmt_data[ridx][tidx], speed_data[ridx][tidx]]:
                vht = missing_data
            vht_data[ridx][tidx] = vht
    return vht_data

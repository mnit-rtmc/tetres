# -*- coding: utf-8 -*-

import copy

from pyticas import cfg
from pyticas.moe import moe_helper
from pyticas.moe.mods import density
from pyticas.moe.mods import total_flow

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

DEFAULT_CRITICAL_DENSITY = 40
DEFAULT_LANE_CAPACITY = 2200


def run(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :return:
    """

    critical_density = kwargs.get('critical_k', DEFAULT_CRITICAL_DENSITY)
    lane_capacity = kwargs.get('lan_capacity', DEFAULT_LANE_CAPACITY)

    # load_data total flow data
    tq_results = total_flow.run(route, prd)
    tq_results = moe_helper.add_virtual_rnodes(tq_results, route)

    # load_data density data
    ks_results = density.run(route, prd)
    ks_results = moe_helper.add_virtual_rnodes(ks_results, route)

    # copy results to save LVMT values
    lvmt_results = [res.clone() for res in ks_results]

    # calculate LVMT
    lvmt_data = _calculate_lvmt(tq_results, ks_results, prd.interval, critical_density, lane_capacity, **kwargs)
    for ridx, res in enumerate(lvmt_results):
        res.data = lvmt_data[ridx]

    return lvmt_results


def _calculate_lvmt(tq_results, ks_results, interval, critical_denisty, lane_capacity, **kwargs):
    """
     Lost VMT for congestion

     Equation :

         capacity balance = lane capacity (v/h) * lane - total flow of station (v/h)

         LVMT = capacity balance (v/h) * interval(hour) * 0.1(distance in mile),   if capacity balance > 0

    :type tq_results: list[RNodeData]
    :type ks_results: list[RNodeData]
    :type interval: int
    :type critical_density: float
    :type lane_capacity: float
    :type kwargs: dict
    :return:
    """
    missing_data = kwargs.get('missing_data', cfg.MISSING_VALUE)
    vd = moe_helper.VIRTUAL_RNODE_DISTANCE
    seconds_per_hour = 3600
    ks_data = [res.data for res in ks_results]
    tq_data = [res.data for res in tq_results]
    lvmt_data = copy.deepcopy(ks_data)
    for ridx, rnode_data in enumerate(ks_data):
        for tidx, value in enumerate(rnode_data):
            k = value
            tq = tq_data[ridx][tidx]
            lanes = tq_results[ridx].lanes
            if critical_denisty < k:
                lvmt = max(lane_capacity * lanes - tq, 0)
                lvmt = (lvmt * interval / seconds_per_hour * vd)
            else:
                lvmt = 0
            lvmt_data[ridx][tidx] = lvmt

    return lvmt_data

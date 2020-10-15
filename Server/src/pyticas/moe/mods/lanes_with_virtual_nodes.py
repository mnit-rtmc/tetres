# -*- coding: utf-8 -*-

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
    lane_data = [res.lanes for res in tq_results]

    return lane_data

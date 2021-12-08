# -*- coding: utf-8 -*-

from pyticas.moe import moe_helper
from pyticas.moe.imputation import spatial_avg

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def run(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :return:
    """
    rnode_list = route.get_stations()

    # load_data total flow data
    us = moe_helper.get_speed(rnode_list, prd, **kwargs)
    us_data = [res.data for res in us]
    us_data = spatial_avg.imputation(us_data)

    us_with_virtual_nodes = moe_helper.add_virtual_rnodes(us, route)
    us_with_virtual_nodes_data = [res.data for res in us_with_virtual_nodes]
    us_with_virtual_nodes_data = spatial_avg.imputation(us_with_virtual_nodes_data)

    return us, us_data, us_with_virtual_nodes, us_with_virtual_nodes_data

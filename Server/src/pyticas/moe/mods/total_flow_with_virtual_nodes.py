# -*- coding: utf-8 -*-

from pyticas.moe import moe_helper
from pyticas.moe.mods import total_flow

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def run(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :return:
    """

    # load_data total flow data
    tq = total_flow.run(route, prd)
    tq_data = [res.data for res in tq]

    tq_with_virtual_nodes = moe_helper.add_virtual_rnodes(tq, route)
    tq_with_virtual_nodes_data = [res.data for res in tq_with_virtual_nodes]

    return tq, tq_data, tq_with_virtual_nodes, tq_with_virtual_nodes_data

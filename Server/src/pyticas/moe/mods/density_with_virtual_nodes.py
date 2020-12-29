# -*- coding: utf-8 -*-

from pyticas.moe import moe_helper
from pyticas.moe.mods import density

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def run(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :return:
    """

    # load_data total flow data
    ks = density.run(route, prd)
    ks_data = [res.data for res in ks]

    ks_with_virtual_nodes = moe_helper.add_virtual_rnodes(ks, route)
    ks_with_virtual_nodes_data = [res.data for res in ks_with_virtual_nodes]

    return ks, ks_data, ks_with_virtual_nodes, ks_with_virtual_nodes_data

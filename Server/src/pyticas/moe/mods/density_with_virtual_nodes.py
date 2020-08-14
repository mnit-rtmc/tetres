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
    ks_results = density.run(route, prd)
    ks_results = moe_helper.add_virtual_rnodes(ks_results, route)
    ks_data = [res.data for res in ks_results]

    return ks_results, ks_data

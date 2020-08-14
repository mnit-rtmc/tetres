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
    tq_results = total_flow.run(route, prd)
    tq_results = moe_helper.add_virtual_rnodes(tq_results, route)
    tq_data = [res.data for res in tq_results]

    return tq_results, tq_data

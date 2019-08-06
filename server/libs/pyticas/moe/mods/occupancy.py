# -*- coding: utf-8 -*-

from pyticas.moe import moe_helper

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def run(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :return:
    """
    return moe_helper.get_occupancy(route.get_stations(), prd, **kwargs)

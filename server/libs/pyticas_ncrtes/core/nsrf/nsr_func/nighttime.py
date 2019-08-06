# -*- coding: utf-8 -*-

"""
Nighttime Function Maker
========================

this module creates the speed-timeline function for nighttime

"""

from pyticas_ncrtes.core import etypes

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def make(night_data):
    """

    :type night_data: pyticas_ncrtes.core.etypes.NighttimeData
    :rtype: NighttimeFunction
    """
    if not night_data.avg_us:
        return etypes.NighttimeFunction([], [], None, None, 300)
    start_time = night_data.periods[0].start_date.time()
    end_time = night_data.periods[0].end_date.time()
    interval = night_data.periods[0].interval

    return etypes.NighttimeFunction(night_data.avg_us, night_data.avg_ks, start_time, end_time, interval)

# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import pyticas_ncrtes.core.etypes
from pyticas_ncrtes.core.nsrf import cache as nsr_cache
from pyticas_ncrtes.core.nsrf.nsr_data import daytime
from pyticas_ncrtes.core.nsrf.nsr_data import nighttime
from pyticas_ncrtes.core.nsrf import dryday_finder


def get(target_station, normal_months, **kwargs):
    """ get normal function and data using cache

    :type target_station: pyticas.ttypes.RNodeObject
    :type normal_months: list[(int, int)]
    :rtype: pyticas_ncrtes.core.etypes.NSRData
    """
    cache_file = nsr_cache.cache_file_path(target_station.station_id, normal_months)
    if os.path.exists(cache_file):
        nd = nsr_cache.loads_data(target_station.station_id, normal_months)
    else:
        nd = collect(target_station, normal_months, **kwargs)
        if nd:
            nsr_cache.dumps_data(nd, normal_months)
        else:
            cache_path = nsr_cache.cache_file_path(target_station.station_id, normal_months)
            with open(cache_path, 'w') as f:
                f.write('')
    return nd


def collect(target_station, months, **kwargs):
    """ collects normal dryday nsr_data

    :type target_station: pyticas.ttypes.RNodeObject
    :type months: list[(int, int)]
    :rtype: pyticas_ncrtes.core.etypes.NSRData
    """
    # collecting daytime data
    normal_periods, weather_source = dryday_finder.drydays_for_daytime(target_station, months)
    if not normal_periods:
        return None

    (used_periods, all_patterns, recovery_patterns, reduction_patterns,
     uss, kss, rd_uss, rd_kss, valid_detectors, not_congested_periods, not_congested_patterns) = daytime.collect(
        target_station, normal_periods, **kwargs)

    if not valid_detectors:
        return None

    # collecting nighttime data
    nt_normal_periods, nt_weather_source = dryday_finder.drydays_for_nighttime(target_station, months)
    avg_nt_us, avg_nt_ks, nt_uss, nt_kss, nt_periods = nighttime.collect(target_station, nt_normal_periods, **kwargs)

    # valid detector names for the given station
    det_names = [det.name for det in valid_detectors]

    data = pyticas_ncrtes.core.etypes.NSRData(target_station,
                                              months,
                                              pyticas_ncrtes.core.etypes.DaytimeData(target_station,
                                                                                     used_periods,
                                                                                     recovery_patterns,
                                                                                     not_congested_periods,
                                                                                     not_congested_patterns),
                                              pyticas_ncrtes.core.etypes.NighttimeData(target_station, avg_nt_us,
                                                                                       avg_nt_ks, nt_periods),
                                              det_names)

    return data

# -*- coding: utf-8 -*-

import pyticas_ncrtes.core.etypes
from pyticas_ncrtes.core.nsrf import nsr_data
from pyticas_ncrtes.core.nsrf import cache as nsr_cache
from pyticas_ncrtes.core.nsrf.nsr_func import daytime, nighttime
from pyticas_ncrtes.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def _read_snow_uk(station_id):
    """

    :type station_id: str
    :rtype: dict[float, float]
    """
    import os
    import json
    from pyticas_ncrtes import ncrtes
    infra = ncrtes.get_infra()
    json_path = os.path.join(infra.get_path('ncrtes', create=True), 'uk-snow', '%s.json' % station_id)
    if not os.path.exists(json_path):
        return None
    data = json.load(open(json_path, 'r'))
    uk = {}
    for k, u in data.items():
        k = float(k)
        while k in uk:
            k += 0.000001
        uk[k] = u
    return uk



def get(target_station, normal_months, **kwargs):
    """ get normal function and data using cache

    :type target_station: pyticas.ttypes.RNodeObject
    :type normal_months: list[(int, int)]
    :rtype: (pyticas_ncrtes.core.etypes.NSRFunction, pyticas_ncrtes.core.etypes.NSRData)
    """
    nfi = nsr_cache.loads_function(target_station.station_id, normal_months)
    if not nfi:
        nd = nsr_data.get(target_station, normal_months)
        kwargs['normal_data'] = nd
        nf = make(target_station, normal_months, **kwargs)
        nfi = nsr_cache.dumps_function(nf, normal_months)

    return nfi.func, nd


def make(target_station, normal_months, **kwargs):
    """
    
    :type target_station: pyticas.ttypes.RNodeObject 
    :type normal_months: list[tuple(int, int)]
    :rtype: pyticas_ncrtes.core.etypes.NSRFunction 
    """
    log = getLogger(__name__)
    data = kwargs.get('normal_data', None)
    if not data:
        data = nsr_data.get(target_station, normal_months, **kwargs)

    if not data:
        log.warn('Cannot collect normal data for %s' % target_station.station_id)
        return None
    dt_func = daytime.make(data.daytime_data)
    nt_func = nighttime.make(data.night_data)
    return pyticas_ncrtes.core.etypes.NSRFunction(target_station, normal_months, dt_func, nt_func)

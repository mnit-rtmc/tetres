# -*- coding: utf-8 -*-

import os

from pyticas_ncrtes import itypes
from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core.nsrf import cache as nsr_cache
from pyticas_ncrtes.core.nsrf import nsr_data
from pyticas_ncrtes.core.nsrf import nsr_func
from pyticas_ncrtes.core.nsrf.target import get_target_detectors
from pyticas_ncrtes.da.target_station import TargetStationDataAccess
from pyticas_ncrtes.da.winter_season import WinterSeasonDataAccess

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def get(target_station, normal_months, **kwargs):
    """ get normal function and data using cache
    
    :type target_station: pyticas.ttypes.RNodeObject 
    :type normal_months: list[(int, int)]
    :rtype: (pyticas_ncrtes.core.etypes.NSRFunction, pyticas_ncrtes.core.etypes.NSRData)
    """
    cache_file = nsr_cache.cache_file_path(target_station.station_id, normal_months)
    if os.path.exists(cache_file):
        nd = nsr_cache.loads_data(target_station.station_id, normal_months)
    else:
        nd = normal_data(target_station, normal_months, **kwargs)
        if nd:
            nsr_cache.dumps_data(nd, normal_months)
        else:
            cache_path = nsr_cache.cache_file_path(target_station.station_id, normal_months)
            with open(cache_path, 'w') as f:
                f.write('')

    nfi = nsr_cache.loads_function(target_station.station_id, normal_months)
    if not nfi:
        kwargs['normal_data'] = nd
        nf = normal_function(target_station, normal_months, **kwargs)
        nfi = nsr_cache.dumps_function(nf, normal_months)

    return nfi.func, nd


def get_normal_data(target_station, normal_months, **kwargs):
    """ get normal function and data using cache

    :type target_station: pyticas.ttypes.RNodeObject
    :type normal_months: list[(int, int)]
    :rtype: pyticas_ncrtes.core.etypes.NSRData
    """
    cache_file = nsr_cache.cache_file_path(target_station.station_id, normal_months)
    if os.path.exists(cache_file):
        nd = nsr_cache.loads_data(target_station.station_id, normal_months)
    else:
        nd = normal_data(target_station, normal_months, **kwargs)
        if nd:
            nsr_cache.dumps_data(nd, normal_months)
        else:
            cache_path = nsr_cache.cache_file_path(target_station.station_id, normal_months)
            with open(cache_path, 'w') as f:
                f.write('')

    return nd


def get_normal_function(target_station, normal_months, update_target_station=True, **kwargs):
    """ get normal function and data using cache
    
    :type target_station: pyticas.ttypes.RNodeObject 
    :type normal_months: list[(int, int)]
    :rtype: pyticas_ncrtes.core.etypes.NSRFunction
    """
    nfi, nf = nsr_cache.loads_function(target_station.station_id, normal_months), None
    wsDA = kwargs.get('wsDA', None)
    nfDA = kwargs.get('nfDA', None)
    tsDA = kwargs.get('tsDA', None)
    autocommit = kwargs.get('autocommit', True)

    if not nfi:
        # load_data normal data
        cache_file = nsr_cache.cache_file_path(target_station.station_id, normal_months)
        if os.path.exists(cache_file):
            nd = nsr_cache.loads_data(target_station.station_id, normal_months)
        else:
            nd = normal_data(target_station, normal_months, **kwargs)
            if nd:
                nsr_cache.dumps_data(nd, normal_months)

        if nd:
            kwargs['normal_data'] = nd
            nf = normal_function(target_station, normal_months, **kwargs)
            if not autocommit:
                nfi = nsr_cache.dumps_function_without_commit(nf, normal_months, wsDA, nfDA, tsDA, autocommit)
            else:
                nfi = nsr_cache.dumps_function(nf, normal_months)

        # if update_target_station and nf is not None and nf.is_valid():
        #     update_target_station_db(nfi.id, nf.station, normal_months, wsDA, tsDA, autocommit)

    else:
        nf = nfi.func

    return nf


def cache_normal_function(nf, normal_months):
    return nsr_cache.dumps_function(nf, normal_months)


# def update_target_station_db(nf_id, station, normal_months, wsDA=None, tsDA=None, autocommit=True):
#     """
#
#     :type nf_id: int
#     :type station: pyticas.ttypes.RNodeObject
#     :type normal_months: list[(int, int)]
#     :type wsDA: WinterSeasonDataAccess
#     :type tsDA: TargetStationDataAccess
#     :return:
#     :rtype:
#     """
#     should_close = (wsDA is not None and tsDA is not None)
#
#     ws = WinterSeasonDataAccess() if wsDA is None else wsDA
#     wsi = ws.get_by_months(normal_months)
#     if not wsi:
#         wsi = itypes.WinterSeasonInfo()
#         wsi.set_months(normal_months)
#         wsi.name = 'WinterSeason %s-%s' % (normal_months[0][0], normal_months[-1][0])
#         ws.insert(wsi, autocommit=True)
#
#     ta = TargetStationDataAccess() if tsDA is None else tsDA
#     tsi = itypes.TargetStationInfo()
#     tsi.station_id = station.station_id
#     tsi.winterseason_id = wsi.id
#     tsi.corridor_name = station.corridor.name
#     tsi.snowroute_id = None
#     tsi.snowroute_name = None
#     tsi.normal_function_id = nf_id
#
#     infra = ncrtes.get_infra()
#     target_dets = get_target_detectors(infra.get_rnode(tsi.station_id))
#
#     ex = ta.get_by_station_id(wsi.year, tsi.station_id, as_model=True)
#     if ex:
#         ex.normal_function_id = nf_id
#         if not target_dets:
#             ex.detectors = None
#         else:
#             ex.detectors = ','.join([det.name for det in target_dets])
#         if autocommit:
#             ta.commit()
#     else:
#         if not target_dets:
#             tsi.detectors = None
#         else:
#             tsi.detectors = ','.join([det.name for det in target_dets])
#         ta.insert(tsi)
#         if autocommit:
#             ta.commit()
#
#     if should_close:
#         ta.close()
#         ws.close()


# function alias
normal_data = nsr_data.collect
normal_function = nsr_func.make

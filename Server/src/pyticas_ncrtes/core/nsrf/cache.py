# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os

from pyticas.tool import json
from pyticas_ncrtes import itypes
from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core import etypes
from pyticas_ncrtes.core.nsrf.target.lane import get_target_detectors
from pyticas_ncrtes.da.normal_func import NormalFunctionDataAccess
from pyticas_ncrtes.da.winter_season import WinterSeasonDataAccess
from pyticas_ncrtes.da.target_station import TargetStationDataAccess

if etypes not in json.TYPE_MODULES:
    json.TYPE_MODULES.append(etypes)

DATA_DIR = 'normal_data'


def dumps_data(nsr_data, months):
    """

    :type nsr_data: pyticas_ncrtes.core.etypes.NSRData
    :type months: list[(int, int)]
    :rtype: str
    """
    json_path = cache_file_path(nsr_data.station.station_id, months)
    _save_json(nsr_data, json_path)
    return json_path


def clear_data(station_id, months):
    """

    :type station_id: str
    :type months: list[(int, int)]
    :rtype: pyticas_ncrtes.core.etypes.NSRData
    """
    file_path = cache_file_path(station_id, months)
    if os.path.exists(file_path):
        os.remove(file_path)

def loads_data(station_id, months):
    """

    :type station_id: str
    :type months: list[(int, int)]
    :rtype: pyticas_ncrtes.core.etypes.NSRData
    """
    return _load_json(cache_file_path(station_id, months))


def dumps_function(ncr_func, months):
    """

    :type ncr_func: pyticas_ncrtes.core.etypes.NSRFunction
    :type months: list[(int, int)]
    :rtype: itypes.NormalFunctionInfo
    """
    wsDA = WinterSeasonDataAccess()
    nfDA = NormalFunctionDataAccess()
    tsDA = TargetStationDataAccess()
    res =  dumps_function_without_commit(ncr_func, months, wsDA, nfDA, tsDA, autocommit=True)
    wsDA.close()
    nfDA.close()
    tsDA.close()
    return res


def dumps_function_without_commit(ncr_func, months, wsDA, nfDA, tsDA, autocommit=False):
    """

    :type ncr_func: pyticas_ncrtes.core.etypes.NSRFunction
    :type months: list[(int, int)]
    :type wsDA: WinterSeasonDataAccess
    :type nfDA: NormalFunctionDataAccess
    :type tsDA: TargetStationDataAccess
    :rtype: itypes.NormalFunctionInfo
    """
    wsi = wsDA.get_by_months(months)
    if not wsi:
        wsi = itypes.WinterSeasonInfo()
        wsi.set_months(months)
        wsi.name = 'WinterSeason %s-%s' % (months[0][0], months[-1][0])
        wsDA.insert(wsi, autocommit=True)

    nfi = itypes.NormalFunctionInfo()
    nfi.func = ncr_func
    nfi.station_id = ncr_func.station.station_id
    nfi.winterseason_id = wsi.id

    ex = nfDA.get_by_station(wsi.id, ncr_func.station.station_id)
    if ex:
        nfDA.delete(ex.id, autocommit=True)

    nfDA.insert(nfi, autocommit=autocommit)

    if ncr_func.is_valid():
        tsi = itypes.TargetStationInfo()
        tsi.station_id = ncr_func.station.station_id
        tsi.winterseason_id = wsi.id
        tsi.corridor_name = ncr_func.station.corridor.name
        tsi.sroute_id = None
        tsi.normal_function_id = nfi.id

        infra = ncrtes.get_infra()
        target_dets = get_target_detectors(infra.get_rnode(tsi.station_id))

        ex = tsDA.get_by_station_id(wsi.year, tsi.station_id, as_model=True)
        if ex:
            if not target_dets:
                ex.detectors = None
            else:
                ex.detectors = ','.join([ det.name for det in target_dets ])
            if autocommit:
                tsDA.commit()
        else:
            if not target_dets:
                tsi.detectors = None
            else:
                tsi.detectors = ','.join([ det.name for det in target_dets ])
            tsDA.insert(tsi)
            if autocommit:
                tsDA.commit()

    return nfi

def loads_function(station_id, months):
    """

    :type station_id: str
    :type months: list[(int, int)]
    :rtype: pyticas_ncrtes.itypes.NormalFunctionInfo
    """
    ws = WinterSeasonDataAccess()
    wsi = ws.get_by_months(months)
    if not wsi:
        return None

    da = NormalFunctionDataAccess()
    nfi = da.get_by_winter_id(wid=wsi.id, station_id=station_id)
    da.close()

    if nfi:
        return nfi
    else:
        return None


def cache_file_path(station_id, months):
    """ returns nsr_data path

    :type station_id: str
    :type months: list[(int, int)]
    :rtype: str
    """
    # ymds = ['%d%02d' % (y, m) for (y, m) in months]
    years = list(set(['%d' % y for (y, m) in months]))
    ystr = '-'.join(sorted(years))
    path = 'ncrtes/%s/%s' % (ystr, DATA_DIR)
    return os.path.join(ncrtes.get_infra().get_path(path, create=True), '%s.json' % station_id)


def _load_json(json_path):
    if not os.path.exists(json_path):
        return None

    nsr_data = None
    try:
        with open(json_path, 'r') as f:
            json_str = f.read()
            nsr_data = json.loads(json_str)
    except:
        pass

    return nsr_data


def _save_json(json_data, json_path):
    json_str = json.dumps(json_data, indent=4)
    with open(json_path, 'w') as f:
        f.write(json_str)

#############


# def dumps_nsr_function(nsr_func, months):
#     """
#
#     :type nsr_func: pyticas_ncrtes.core.etypes.NSRFunction
#     :type months: list[(int, int)]
#     :rtype: str
#     """
#     json_path = cache_file_path(CacheType.FUNCION, nsr_func.station.station_id, months)
#     _save_json(nsr_func, json_path)
#     return json_path
#
#
# def loads_nsr_function(station_id, months):
#     """
#
#     :type station_id: str
#     :type months: list[(int, int)]
#     :rtype: pyticas_ncrtes.core.etypes.NSRFunction
#     """
#     return _load_json(cache_file_path(CacheType.FUNCION, station_id, months))

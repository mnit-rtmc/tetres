# -*- coding: utf-8 -*-

"""
Traffic Measurement Helper Module
"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import math

from pyticas import cfg
from pyticas.ttypes import RNodeData
from pyticas.infra import Infra
from pyticas.tool.cache import lru_cache
from pyticas.tool.concurrent import Worker
from pyticas.rn.geo import get_mile_point_map

THREAD_LIMIT_PER_CALL = 5
VIRTUAL_RNODE_DISTANCE = 0.1  # add virtual rnode every 0.1 mile


def replace_zero_with_missing_value(speed_data):
    for ridx, rnode_object in enumerate(speed_data):
        for tidx, speed in enumerate(rnode_object.data):
            if speed == 0:
                speed_data[ridx].data[tidx] = cfg.MISSING_VALUE
    return speed_data


def get_speed(rnode_list, prd, **kwargs):
    """
    :type rnode_list: list[RNodeObject]
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return replace_zero_with_missing_value(get_traffic_data(rnode_list, prd, 'u', **kwargs))


def get_total_flow(rnode_list, prd, **kwargs):
    """
    :type rnode_list: list[RNodeObject]
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return get_traffic_data(rnode_list, prd, 'tq', **kwargs)


def get_average_flow(rnode_list, prd, **kwargs):
    """
    :type rnode_list: list[RNodeObject]
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return get_traffic_data(rnode_list, prd, 'aq', **kwargs)


def get_density(rnode_list, prd, **kwargs):
    """
    :type rnode_list: list[RNodeObject]
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return get_traffic_data(rnode_list, prd, 'k', **kwargs)


def get_volume(rnode_list, prd, **kwargs):
    """
    :type rnode_list: list[RNodeObject]
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return get_traffic_data(rnode_list, prd, 'v', **kwargs)


def get_occupancy(rnode_list, prd, **kwargs):
    """
    :type rnode_list: list[RNodeObject]
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return get_traffic_data(rnode_list, prd, 'o', **kwargs)


def get_scan(rnode_list, prd, **kwargs):
    """
    :type rnode_list: list[RNodeObject]
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return get_traffic_data(rnode_list, prd, 's', **kwargs)


@lru_cache
def get_traffic_data(rnode_list, prd, datatype, **kwargs):
    """

    :type rnode_list: list[RNodeObject]
    :type prd: Period
    :type datatype: str
    :rtype: list[RNodeData]
    """
    dc = kwargs.get('detector_checker', None)
    infra = kwargs.get('infra', Infra.get_infra())
    assert isinstance(infra, Infra)

    funcs = {
        'u': infra.rdr.get_speed,
        'tq': infra.rdr.get_total_flow,
        'aq': infra.rdr.get_average_flow,
        'v': infra.rdr.get_volume,
        'k': infra.rdr.get_density,
        'o': infra.rdr.get_occupancy,
        's': infra.rdr.get_scan,
    }

    # res = []
    # for rnode in rnode_list:
    #     res.append(funcs[datatype](rnode, prd, dc))
    # return res
    worker = Worker(n_threads=THREAD_LIMIT_PER_CALL)
    for rnode in rnode_list:
        worker.add_task(funcs[datatype], rnode, prd, dc)
    return worker.run()


def add_virtual_rnodes(results, r, **kwargs):
    """
    :type results: list[RNodeData]
    :type r: pyticas.ttypes.Route
    :rtype: list[RNodeData]
    """

    # if isinstance(results[0], list):
    #    return [ add_virtual_rnodes(res, **kwargs) for res in results ]
    mp_map = get_mile_point_map(r.get_stations())

    def _add_virtual_data(new_data, n, up_data_obj, dn_data_obj, missing_data):
        """
        :type new_data: list[RNodeData]
        :type n: int
        :type up_data_obj: RNodeData
        :type dn_data_obj: RNodeData
        :type missing_data: number
        :return:
        """
        for _ in range(n):
            i_data = _virtual_data(up_data_obj, dn_data_obj)
            if not up_data_obj or not dn_data_obj:
                new_data.append(i_data)
                continue
            i_data.data = []
            for didx, up_data in enumerate(up_data_obj.data):
                dn_data = dn_data_obj.data[didx]
                if up_data > 0 and dn_data > 0:
                    i_data.data.append((up_data + dn_data) / 2)
                else:
                    i_data.data.append(missing_data)
            new_data.append(i_data)

    def _virtual_data(idata1=None, idata2=None):
        """

        :type idata1: RNodeData
        :type idata2: RNodeData
        :rtype: RNodeData
        """
        idata = idata1.clone() if idata1 else idata2.clone()
        idata.rnode = ''
        idata.rnode_name = ''  # '({}, {})'.format(idata1.rnode_name if idata1 else 'NA', idata2.rnode_name if idata2 else 'NA')
        idata.station_id = ''
        idata.detector_data = []
        idata.detector_names = []
        idata.dup_detector_names = []
        idata.missing_lanes = []
        # if idata1 and idata2:
        #     #if idata1.lanes == None: print('idata1 : ', idata1.rnode_name, idata1.station_id)
        #     #if idata2.lanes == None: print('idata2 : ', idata2.rnode_name, idata2.station_id)
        #     idata.lanes = (idata1.lanes + idata2.lanes) / 2
        #     idata.speed_limit = (idata1.speed_limit + idata2.speed_limit) / 2

        return idata

    missing_data = kwargs.get('missing_value', cfg.MISSING_VALUE)

    new_data = []
    for ridx in range(len(results) - 1):
        up_data_obj = results[ridx]
        dn_data_obj = results[ridx + 1]
        new_data.append(up_data_obj)
        up_acc_distance = mp_map.get(up_data_obj.rnode_name)
        acc_distance = mp_map.get(dn_data_obj.rnode_name)
        if not acc_distance:
            print('up:', up_data_obj)
            print('down:', dn_data_obj)
        n_v = round(round(acc_distance, 1) - round(up_acc_distance, 1) - VIRTUAL_RNODE_DISTANCE, 1)
        n_13 = int(math.floor(n_v / 3.0 * 10)) if n_v >= 0.3 else 0
        n_2 = int((n_v * 10.0) - 2 * n_13)
        _add_virtual_data(new_data, n_13, up_data_obj, None, missing_data)
        _add_virtual_data(new_data, n_2, up_data_obj, dn_data_obj, missing_data)
        _add_virtual_data(new_data, n_13, None, dn_data_obj, missing_data)

    new_data.append(results[-1])

    return new_data


def has_virtual_rnodes(results):
    """
    :type results: list[RNodeData]
    :rtype: boolean
    """
    for rnd in results:
        if not rnd.rnode_name:
            return True
    return False


def remove_virtual_rnodes(results):
    """
    :type results: list[RNodeData]
    :rtype: boolean
    """
    return [rnd for rnd in results if rnd.rnode_name]


def used_lanes(results, r, **kwargs):
    """
    :type results: list[RNodeData]
    :type r: pyticas.ttypes.Route
    :rtype: list[str]
    """

    laneinfos = []
    for ridx in range(len(results)):
        rnode_data = results[ridx]
        lane_info = []
        if isinstance(rnode_data.rnode, str):
            laneinfos.append('-')
            continue
        if rnode_data.rnode.is_station():
            for det in rnode_data.rnode.detectors:
                missing = ' (missing)'
                if det in rnode_data.detectors:
                    missing = ''
                elif det.name in rnode_data.dup_detector_names:
                    missing = ' (duplicated lane)'

                lane_info.append('%d:%s%s' % (det.lane, det.name, missing))
        else:
            for det in rnode_data.rnode.detectors:
                lane_info.append('%s:%s' % (det.category, det.name))

        laneinfos.append('\n'.join(lane_info))

    return laneinfos


def accumulated_distances(results, r, **kwargs):
    """
    :type results: list[RNodeData]
    :type r: pyticas.ttypes.Route
    :rtype: list[float]
    """

    mp_map = get_mile_point_map(r.get_rnodes())

    ads = []
    if has_virtual_rnodes(results):
        for ridx, rnd in enumerate(results):
            ads.append(VIRTUAL_RNODE_DISTANCE * ridx)
        return ads

    ads.append(0.0)
    for ridx in range(1, len(results)):
        down_rnode_data = results[ridx]
        acc_distance = mp_map.get(down_rnode_data.rnode_name)
        ads.append(round(acc_distance, 1))

    return ads


def confidences(results, **kwargs):
    """
    :type results: list[RNodeData]
    :rtype: list[float]
    """
    missing_data = kwargs.get('missing_data', cfg.MISSING_VALUE)
    cnfs = []
    for ridx, rnd in enumerate(results):
        cnf = len([d for d in rnd.data if d != missing_data]) / len(rnd.data) * 100
        cnfs.append(cnf)
    return cnfs

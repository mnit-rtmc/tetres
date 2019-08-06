# -*- coding: utf-8 -*-

import os

import matplotlib.pyplot as plt
import numpy as np
import xlsxwriter

from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core import setting, data_util
from pyticas_ncrtes.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


DEBUG_MODE = False
FFS_K = setting.FFS_K

def determine(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: (bool, int)
    """
    # return False, None
    sw1 = 41
    sw2 = 7
    ss = 5

    logger = getLogger(__name__)
    logger.debug('>>>>>> Determine Wet-Normal FFS : U-T Mode')

    us, ks = edata.us, edata.ks

    if us is None or not any(us):
        return False, None

    sus, qus = _data(us, sw1, sw2, ss)
    sks, qks = _data(ks, sw1, sw2, ss)

    is_found, wn_ffs = _recovered_to_normal_directly(edata, qus, qks)

    if not is_found:
        is_found, wn_ffs = _find_wn_ffs_using_stable_time(edata, qus, qks)

    if not is_found:
        is_found, wn_ffs = _find_wn_ffs_using_vertex(edata, qus, qks)

    logger.debug('<<<<<< End of Determine Wet-Normal FFS : U-T Mode')
    return is_found, wn_ffs


def _recovered_to_normal_directly(edata, qus, qks):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type qus: numpy.ndarray
    :type qks: numpy.ndarray
    :rtype: (bool, float)
    """
    logger = getLogger(__name__)
    nrth = 0.7
    u_change = 5
    small_u_change = 3
    sidx, eidx = edata.ncrt_search_sidx, edata.ncrt_search_eidx
    tus, tks = qus[sidx:eidx], qks[sidx:eidx]
    maxu, minu = max(tus), min(tus)

    # speed is not changed during recovery interval
    if maxu - minu < small_u_change or minu >= edata.may_recovered_speed:
        wn_ffs = _wn_ffs(edata, sidx)
        worst_u = qus[edata.worst_ratio_idx]
        if wn_ffs - worst_u < u_change:
            maxu_idx = np.argmax(qus[sidx:sidx+setting.INTV2HOUR]).item() + sidx
            wn_ffs = _wn_ffs(edata, maxu_idx)
        edata.wn_ffs_idx = _find_wn_ffs_idx(edata, wn_ffs, sidx, eidx)
        edata.wn_ffs = wn_ffs
        logger.debug(' - Directly Recovered to Normal (1) : wn_ffs = %.1f, wn_ffs_idx = %d' %
                     (edata.wn_ffs, edata.wn_ffs_idx))
        _chart(edata, qus, qks)
        return True, wn_ffs

    wh = np.where(tus >= edata.may_recovered_speed)[0]
    n_recovered = float(len(wh))
    n_data = len(tus)

    if n_recovered > n_data * nrth and tus[0] > edata.may_recovered_speed:
        wn_ffs = _wn_ffs(edata, wh[0]+sidx)
        worst_u = qus[edata.worst_ratio_idx]
        if wn_ffs - worst_u < u_change:
            maxu_idx = np.argmax(qus[sidx:sidx+setting.INTV2HOUR]).item() + sidx
            wn_ffs = _wn_ffs(edata, maxu_idx)
        edata.wn_ffs_idx = _find_wn_ffs_idx(edata, wn_ffs, sidx, eidx)
        edata.wn_ffs = wn_ffs
        logger.debug(' - Directly Recovered to Normal (2) : wn_ffs = %.1f, wn_ffs_idx = %d' %
                     (edata.wn_ffs, edata.wn_ffs_idx))
        _chart(edata, qus, qks)
        return True, wn_ffs

    return False, None


def _find_wn_ffs_using_stable_time(edata, qus, qks):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type qus: numpy.ndarray
    :type qks: numpy.ndarray
    :rtype: (bool, float)
    """
    logger = getLogger(__name__)
    nrth = 0.7
    sidx, eidx, tus, tks = _ut_data_range(edata, qus, qks)

    logger.debug(' - WN-FFS using Stable Time Duration : adjust range (%d, %d) -> (%d, %d)' %
                 (edata.ncrt_search_sidx, edata.ncrt_search_eidx, sidx, eidx))

    cregions = _continuous_regions(tus)
    sorted_cregions = sorted(cregions, key=lambda r: r[1] - r[0])
    s_sidx, s_eidx = sorted_cregions[-1]
    region_duration = (s_eidx - s_sidx)
    recovery_duration = (eidx - sidx)

    if region_duration / recovery_duration >= nrth:
        s_sidx, s_eidx = s_sidx + sidx, s_eidx + sidx
        wn_ffs = np.mean(edata.merged_sus[s_sidx:s_eidx]).item()
        edata.wn_ffs_idx = _find_wn_ffs_idx(edata, wn_ffs, sidx, eidx)
        edata.wn_ffs = wn_ffs
        logger.debug(' - WN-FFS using Stable Time Duration : stable_region=(%d, %d), wn_ffs=%.1f, wn_ffs_idx=%d' %
                     (s_sidx, s_eidx, edata.wn_ffs, edata.wn_ffs_idx))

        _chart(edata, qus, qks)
        return True, wn_ffs

    return False, None


def _find_wn_ffs_using_vertex(edata, qus, qks):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type qus: numpy.ndarray
    :type qks: numpy.ndarray
    :rtype: (bool, float)
    """
    logger = getLogger(__name__)

    sidx, eidx, tus, tks = _ut_data_range(edata, qus, qks)

    logger.debug(' - WN-FFS using Vertex : adjust range (%d, %d) -> (%d, %d)' %
                 (edata.ncrt_search_sidx, edata.ncrt_search_eidx, sidx, eidx))

    indices = list(range(sidx, eidx))

    up_vertex_idx, d_to_up_vertex, _, _ = _find_vertex(indices, tus, find_under=False, offset=sidx)

    if up_vertex_idx < 0:
        logger.debug(' - cannot find vertex : data range = (%d, %d)' % (sidx, eidx))
        wn_ffs = _wn_ffs(edata, sidx)
        edata.wn_ffs_idx = _find_wn_ffs_idx(edata, wn_ffs, edata.ncrt_search_sidx, eidx)
        edata.wn_ffs = wn_ffs
        logger.debug(' - WN-FFS using Vertex : wn_ffs = %.1f, wn_ffs_idx = %d' %
                     (edata.wn_ffs, edata.wn_ffs_idx))
        return True, wn_ffs

    wn_ffs = _wn_ffs(edata, up_vertex_idx)
    edata.wn_ffs_idx = _find_wn_ffs_idx(edata, wn_ffs, edata.ncrt_search_sidx, eidx)
    edata.wn_ffs = wn_ffs

    logger.debug(' - WN-FFS using Vertex : wn_ffs = %.1f, wn_ffs_idx = %d' %
                 (edata.wn_ffs, edata.wn_ffs_idx))

    _chart(edata, qus, qks)

    return True, wn_ffs


def _ut_data_range(edata, qus, qks):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type qus: numpy.ndarray
    :type qks: numpy.ndarray
    :rtype: (int, int, numpy.ndarray, numpy.ndarray)
    """
    sidx, eidx = edata.ncrt_search_sidx, edata.ncrt_search_eidx
    sidx = np.argmin(qus[sidx:eidx]).item() + sidx

    tus, tks = qus[sidx:eidx], qks[sidx:eidx]
    wh = np.where(tus >= edata.may_recovered_speed)[0]

    if any(wh):
        eidx = wh[0] - 1 + sidx
        tus, tks = qus[sidx:eidx], qks[sidx:eidx]

    return sidx, eidx, tus, tks


def _wn_ffs(edata, recovered_idx):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type recovered_idx: int
    :rtype: float
    """
    return np.mean(edata.merged_sus[recovered_idx-setting.INTV15MIN:recovered_idx+setting.INTV15MIN]).item()


def _data(data, sw1, sw2, ss):
    """

    :type data: numpy.ndarray
    :type sw1: int
    :type sw2: int
    :type ss: int
    :rtype: numpy.ndarray, numpy.ndarray
    """
    sdata = data_util.smooth(data, sw1)
    qdata = data_util.stepping(sdata, ss)
    sdata = qdata
    # sdata = data_util.smooth(qdata, sw2)

    sdata = [ round(v, 2) for v in sdata ]
    qdata = [ round(v, 2) for v in qdata ]

    return np.array(sdata), np.array(qdata)


def _find_vertex(xs, ys, find_under=True, offset=0):
    """
    :type target_x: numpy.ndarray
    :type target_y: numpy.ndarray
    :rtype: (int, float, float, float)
    """
    x_first, y_first, x_last, y_last = xs[0], ys[0], xs[-1], ys[-1]
    max_d, x_at_max_d, y_at_max_d, max_d_idx = -1, -1, -1, -1
    for idx, x in enumerate(xs):
        y = ys[idx]
        fy = data_util.get_value_on_line(x, y_first, y_last, x_first, x_last)
        d = data_util.distance_to_line(x, y, y_first, y_last, x_first, x_last)
        if d > max_d and ((find_under and fy >= y) or (not find_under and fy <= y)):
            max_d = d
            x_at_max_d = x
            y_at_max_d = y
            max_d_idx = idx

    return max_d_idx+offset if max_d_idx > 0 else -1, max_d, x_at_max_d, y_at_max_d


def _find_wn_ffs_idx(edata, wn_ffs, sidx, eidx):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type wn_ffs: float
    :type sidx: int
    :type eidx: int
    :rtype: int
    """

    _sidx, _eidx = edata.ncrt_search_sidx, eidx
    if (sidx - _sidx > setting.INTV2HOUR
        and max(edata.merged_sus[_sidx:sidx]) - min(edata.merged_sus[_sidx:sidx]) > 10):
        _sidx = sidx

    for idx in range(_sidx, 0, -1):
        if edata.merged_sus[idx] >= wn_ffs - 5:
            _sidx = idx
        else:
            break

    wh = np.where(edata.merged_sus[_sidx:] >= wn_ffs)[0]
    if any(wh):
        _sidx = wh[0] + _sidx

    wn_ffs_idx = _eidx
    for idx, _u in enumerate(edata.merged_sus[_sidx:_eidx]):
        if _u < wn_ffs:
            continue
        wn_ffs_idx = idx + _sidx
        break

    wn_ffs_idx = _adjust_with_qdata(edata.qus, edata.sus, wn_ffs_idx)

    if wn_ffs_idx < sidx:
        wn_ffs_idx = sidx

    return wn_ffs_idx


def _continuous_regions(data):
    """

    :type data: numpy.ndarray
    :rtype: list[(int, int)]
    """
    wh_diffs = data[1:] - data[0:-1]
    wh_diffs[wh_diffs == 1] = 0
    iszero = np.concatenate(([0], np.equal(wh_diffs, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    zero_ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    res = []
    for zr in zero_ranges:
        sidx, eidx = zr[0], zr[1]
        res.append((sidx, eidx))

    return res


def _adjust_with_qdata(qdata, sdata, target_idx):
    """

    :type qdata: numpy.ndarray
    :type sdata: numpy.ndarray
    :type target_idx: int
    :rtype: int
    """
    logger = getLogger(__name__)

    stick = None
    qu = qdata[target_idx]
    for idx in range(target_idx, 0, -1):
        cu = qdata[idx]
        if cu != qu :
            stick = target_idx
            break

    if not stick:
        return target_idx

    for tidx in range(stick, stick+setting.INTV15MIN):
        if sdata[tidx] >= qu:
            return tidx

    # never reaches to here
    logger.debug('Adjust Point %d -> %d !!' % (target_idx, stick))
    return stick


def _adjust_with_qdata_origin(qdata, sdata, target_idx):
    """

    :type qdata: numpy.ndarray
    :type sdata: numpy.ndarray
    :type target_idx: int
    :rtype: int
    """
    logger = getLogger(__name__)

    stick = None
    qu = qdata[target_idx]
    for idx in range(target_idx, 0, -1):
        cu = qdata[idx]
        if cu != qu :
            stick = target_idx
            break

    if not stick:
        return target_idx

    for tidx in range(stick, stick+setting.INTV1HOUR):
        if sdata[tidx] >= qu:
            return tidx

    # never reaches to here
    logger.debug('Adjust Point %d -> %d !!' % (target_idx, stick))
    return stick



def _chart(edata, qus, qks):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type qus:  numpy.ndarray
    :type qks:  numpy.ndarray
    """
    if not DEBUG_MODE:
        return

    infra = ncrtes.get_infra()
    output_path = infra.get_path('ncrtes/ut', create=True)

    plt.figure(facecolor='white', figsize=(16, 8))
    ax1 = plt.subplot(111)
    ax1.plot(edata.us, c='#aaaaaa')
    ax1.plot(edata.ks, c='#90A200')
    # ax1.plot(edata.qus, c='r')
    # ax1.plot(edata.qks, c='#C2CC34')
    ax1.plot(qus, c='#22950E')
    ax1.axhline(y=edata.target_station.s_limit, c='b')
    ax1.axhline(y=edata.ncrt_search_uth, c='k')
    ax1.axhline(y=edata.may_recovered_speed, c='k')

    ax1.axvline(x=edata.ncrt_search_sidx, c='#0078CC', lw=2)
    ax1.axvline(x=edata.ncrt_search_eidx, c='#0078CC', lw=2)

    plt.title('%s (%s, s_limit=%d)' % (
        edata.target_station.station_id,
        edata.target_station.corridor.name,
        edata.target_station.s_limit
    ))

    plt.grid()
    plt.legend()
    plt.show()
    filename = '%s.png' % edata.target_station.station_id
    # plt.savefig(os.path.join(output_path, filename))
    plt.show()

    filename = '%s.xlsx' % edata.target_station.station_id
    wb = xlsxwriter.Workbook(os.path.join(output_path, filename))
    ws = wb.add_worksheet('data')
    ws.write_column(0, 0, ['Time'] + edata.snow_event.data_period.get_timeline(as_datetime=False))
    ws.write_column(0, 1, ['Density'] + edata.ks.tolist() )
    ws.write_column(0, 2, ['Speed'] + edata.us.tolist() )
    ws.write_column(0, 3, ['QK'] + qks.tolist() )
    ws.write_column(0, 4, ['QU'] + qus.tolist() )
    if edata.normal_func and edata.normal_func.is_valid():
        klist = list(range(5, 100))
        ulist = edata.normal_func.daytime_func.recovery_speeds(klist)
        ws.write_column(0, 5, ['NormalK'] + klist )
        ws.write_column(0, 6, ['NormalU'] + ulist )
    wb.close()
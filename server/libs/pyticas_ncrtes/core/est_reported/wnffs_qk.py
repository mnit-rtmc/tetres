# -*- coding: utf-8 -*-

import numpy as np

from pyticas_ncrtes.core import setting, data_util
from pyticas_ncrtes.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

DEBUG_MODE = True
CONGESTED_SPEED = 30
FFS_K = setting.FFS_K

def determine(edata, **kwargs):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :return: wetnormal-ffs
    :rtype: bool, float
    """
    logger = getLogger(__name__)

    logger.debug('>>>>>> Determine Wet-Normal FFS : Q-K Mode')

    if not _check(edata):
        logger.debug(' - data is not valid')
        logger.debug('<<<<<< End of Wet-Normal FFS Determination')
        return False, None

    over_uth_point = _over_uth_point(edata)
    uth = edata.ncrt_search_uth
    mink, maxk = kwargs.get('mink', 5), kwargs.get('maxk', FFS_K)

    wn_ffss, wn_ffs_idxs = _wn_ffss(edata, over_uth_point, mink=mink, maxk=maxk)

    # print('wn_ffs_idxs=', wn_ffs_idxs)
    # print('wn_ffss=', wn_ffss)

    # check wn-ffs values
    if not any(wn_ffss) or len(wn_ffss) < 5:
        logger.debug('WN-FFSs are not valid (1)')
        logger.debug('<<<<<< End of Wet-Normal FFS Determination')
        return False, None

    min_idx, max_idx, s_wn_ffss, q_wn_ffss = _minmax_wn_ffs(edata, wn_ffss, wn_ffs_idxs, over_uth_point)

    # check if daytime-lowk or nighttime mode should be performed
    # if density is too low for linear-regression with Q-K
    if _is_low_k_case(edata, uth, wn_ffss, wn_ffs_idxs, over_uth_point, min_idx, max_idx, s_wn_ffss, q_wn_ffss):
        logger.debug('WN-FFSs are not valid (2)')
        logger.debug('<<<<<< End of Wet-Normal FFS Determination')
        return False, None

    # check if pattern is strange
    if _strange_pattern(s_wn_ffss):
        logger.debug('WN-FFSs are not valid. Data pattern seems wrong (4)')
        logger.debug('<<<<<< End of Wet-Normal FFS Determination')
        return False, None


    # determine Q-K data range, which is expected as there is wet-normal
    ssidx, seidx, ttks, ttqs, ttus = _qk_data_range(edata, uth,
                                                    wn_ffss, wn_ffs_idxs,
                                                    over_uth_point,
                                                    min_idx, max_idx, s_wn_ffss, q_wn_ffss,
                                                    mink=mink,
                                                    maxk=maxk,
                                                    n_limit=10)

    # check if Q-K data range is found
    if ssidx is None:
        logger.debug('Q-K data range are not identified!')
        logger.debug('<<<<<< End of Wet-Normal FFS Determination')
        return False, None

    logger.debug('Q-K data range : (%d, %d) ' % (ssidx, seidx))

    # add results
    edata.ncrt_qk_sidx = ssidx
    edata.ncrt_qk_eidx = seidx

    # determine `wn_ffs` with Q-K data
    wn_ffs, cfunc = _find_ffs(ttks, ttqs, maxk)

    # check if `wn_ffs` is too low and density is too low
    if (wn_ffs is None or wn_ffs < uth or wn_ffs < np.mean(ttus) * 0.7):
        logger.debug('The found WN-FFS is not valid (too low) : %s' % wn_ffs)
        wn_ffs = max(edata.qus[ssidx:seidx])
        #_chart(edata, wn_ffs, ssidx, seidx, wn_ffss, wn_ffs_idxs, ttks, ttqs, cfunc, uth)
        #logger.debug('<<<<<< End of Wet-Normal FFS Determination')
        #return False, None

    # find the time point when speed reaches to WN-FFS
    edata.wn_ffs_idx = _find_wn_ffs_idx(edata, wn_ffs)
    edata.wn_ffs = wn_ffs

    _check_recovered_at_lost(edata)

    logger.debug('WN-FFS is found : %.2f at %d' % (wn_ffs, edata.wn_ffs_idx))
    logger.debug('<<<<<< End of Wet-Normal FFS Determination')


    _chart2(edata)

    # if DEBUG_MODE:
    #     import matplotlib.pyplot as plt
    #     fig = plt.figure()
    #     plt.plot(edata.merged_sus, label='merged_sus', c='b')
    #     plt.plot(edata.us, label='us', c='#888888')
    #     plt.plot(edata.ks, label='ks', c='#E0E0E0')
    #     plt.axhline(y=wn_ffs)
    #     plt.axvline(x=edata.wn_ffs_idx)
    #     plt.axvline(x=ssidx, c='r')
    #     plt.axvline(x=seidx, c='r')
    #     plt.ylim(ymin=0, ymax=90)
    #     plt.legend()
    #     plt.grid()
    #     plt.show()
    #
    _chart(edata, wn_ffs, ssidx, seidx, wn_ffss, wn_ffs_idxs, ttks, ttqs, cfunc, uth)

    return True, wn_ffs


def _check(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :return: wetnormal-ffs
    :rtype: bool, float
    """
    if not edata.ncrt_search_sidx or not edata.worst_ratio_idx:
        return False
    return True


def _over_uth_point(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: int
    """
    over_uth_point = edata.ncrt_search_sidx
    # move start-point to increase-start-point
    for idx in range(over_uth_point, edata.search_start_idx, -1):
        if edata.sus[idx] > edata.sus[idx-1]:
            over_uth_point = idx
        else:
            break
    return over_uth_point


def _wn_ffss(edata, over_uth_point, **kwargs):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type over_uth_point: int
    :type kwargs:
    :rtype: list[float], list[int]
    """
    logger = getLogger(__name__)

    mink, maxk = kwargs.get('mink', 5), kwargs.get('maxk', FFS_K)
    wn_ffss = []
    idxs = []
    # to_idx = min(over_uth_point + 10 * setting.INTV1HOUR, len(edata.us) - setting.INTV1HOUR)

    to_idx = min(over_uth_point + 6 * setting.INTV1HOUR, len(edata.us) - setting.INTV1HOUR)
    snow_end_index = edata.snow_event.snow_end_index
    to_idx = max(snow_end_index + setting.INTV3HOUR, to_idx)
    if edata.sks[to_idx] > maxk:
        wh = np.where(edata.sks[to_idx:] < maxk)
        if any(wh[0]):
            to_idx = min(to_idx + wh[0][0] + setting.INTV1HOUR, len(edata.sus)-1)

    logger.debug('Data Range to Find WN-FFSs : %d - %d' % (over_uth_point, to_idx))
    # import matplotlib.pyplot as plt
    # from pyticas_ncrtes.core.nsrf.nsr_func import fitting

    for ssidx in range(over_uth_point, to_idx, setting.INTV15MIN):

        sidx, eidx = ssidx, min(ssidx + setting.INTV1HOUR, len(edata.us) - 1)
        tks, tqs, tus = edata.ks[sidx:eidx], edata.qs[sidx:eidx], edata.us[sidx:eidx]

        # fig = plt.figure()
        # plt.scatter(tks, tqs)
        # plt.xlim(xmin=0, xmax=100)
        # plt.ylim(ymin=0, ymax=1500)
        # if len(tks) < 10:
        #     print('_find_ffs() : number of data < 10')
        #     return None, None
        # func = lambda x, a: a * x
        # _, popts, _, cfunc = fitting.curve_fit(func, tks, tqs, [1])
        #
        #
        # krange = list(range(1, 50))
        # plt.plot(krange, [ cfunc(_k) for _k in krange], c='r')
        # plt.suptitle('%d - %d (%s)' % (sidx, eidx, popts[0]))
        # plt.grid()
        # plt.show()

        wh = np.where((tks < maxk) & (tks > mink))
        ttks, ttqs, tus = tks[wh], tqs[wh], tus[wh]
        if not any(ttks):
            continue

        qk = {_k: ttqs[idx] for idx, _k in enumerate(ttks)}
        ttks, ttqs = _filter_qk(qk)

        if not any(ttks):
            continue

        wn_ffs, cfunc = _find_ffs(ttks, ttqs, maxk)

        if wn_ffs:
            wn_ffss.append(wn_ffs)
            idxs.append(ssidx)

    if any(wn_ffss):
        logger.debug('MaxWN-FFS=%.1f, RecoveredU=%.1f' % (max(wn_ffss), max(edata.qus[to_idx-setting.INTV1HOUR:to_idx])))
    else:
        logger.debug('WN-FFS` are not found')
        return [], []

    may_recovered_u = edata.may_recovered_speed
    max_wn_ffss = max(wn_ffss)
    if (any(wn_ffss)
        and not may_recovered_u < max_wn_ffss
        and max(edata.qus[to_idx-setting.INTV1HOUR:to_idx]) - max(wn_ffss) > 5):
        logger.debug('WN-FFS is not collected until reaching to normal-speed')
        return [], []

    return wn_ffss, idxs



def _wn_ffss2(edata, over_uth_point, **kwargs):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type over_uth_point: int
    :type kwargs:
    :rtype: list[float], list[int]
    """
    logger = getLogger(__name__)

    mink, maxk = kwargs.get('mink', 5), kwargs.get('maxk', FFS_K)
    wn_ffss = []
    idxs = []
    # to_idx = min(over_uth_point + 10 * setting.INTV1HOUR, len(edata.us) - setting.INTV1HOUR)

    to_idx = min(over_uth_point + 6 * setting.INTV1HOUR, len(edata.us) - setting.INTV1HOUR)
    snow_end_index = edata.snow_event.snow_end_index
    to_idx = max(snow_end_index + setting.INTV3HOUR, to_idx)
    if edata.sks[to_idx] > maxk:
        wh = np.where(edata.sks[to_idx:] < maxk)
        if any(wh[0]):
            to_idx = min(to_idx + wh[0][0] + setting.INTV1HOUR, len(edata.sus)-1)

    logger.debug('Data Range to Find WN-FFSs with U-T : %d - %d' % (over_uth_point, to_idx))
    # import matplotlib.pyplot as plt
    # from pyticas_ncrtes.core.nsrf.nsr_func import fitting

    for ssidx in range(over_uth_point, to_idx, setting.INTV15MIN):

        sidx, eidx = ssidx, min(ssidx + setting.INTV1HOUR, len(edata.us) - 1)
        tks, tqs, tus = edata.ks[sidx:eidx], edata.qs[sidx:eidx], edata.us[sidx:eidx]

        # fig = plt.figure()
        # plt.scatter(tks, tqs)
        # plt.xlim(xmin=0, xmax=100)
        # plt.ylim(ymin=0, ymax=1500)
        # if len(tks) < 10:
        #     print('_find_ffs() : number of data < 10')
        #     return None, None
        # func = lambda x, a: a * x
        # _, popts, _, cfunc = fitting.curve_fit(func, tks, tqs, [1])
        #
        #
        # krange = list(range(1, 50))
        # plt.plot(krange, [ cfunc(_k) for _k in krange], c='r')
        # plt.suptitle('%d - %d (%s)' % (sidx, eidx, popts[0]))
        # plt.grid()
        # plt.show()

        wh = np.where((tks < maxk))
        ttks, ttqs, ttus = tks[wh], tqs[wh], tus[wh]
        if not any(ttks):
            continue

        wn_ffs = np.mean(ttus)
        wn_ffss.append(wn_ffs)
        idxs.append(ssidx)

    if any(wn_ffss):
        logger.debug('MaxWN-FFS=%.1f, RecoveredU=%.1f' % (max(wn_ffss), max(edata.qus[to_idx-setting.INTV1HOUR:to_idx])))
    else:
        logger.debug('WN-FFS` are not found')
        return [], []

    may_recovered_u = edata.may_recovered_speed
    max_wn_ffss = max(wn_ffss)
    if (any(wn_ffss)
        and not may_recovered_u < max_wn_ffss
        and max(edata.qus[to_idx-setting.INTV1HOUR:to_idx]) - max(wn_ffss) > 5):
        logger.debug('WN-FFS is not collected until reaching to normal-speed')
        return [], []

    return wn_ffss, idxs

def _minmax_wn_ffs(edata, wn_ffss, wn_ffs_idxs, over_uth_point, **kwargs):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type wn_ffss: list[float]
    :type wn_ffs_idxs: list[int]
    :type over_uth_point: int
    :rtype: int, int, numpy.ndarray, numpy.ndarray
    """
    logger = getLogger(__name__)

    change_threshold = kwargs.get('change_threshold', 0.5)
    smoothing_window, stepping_size = kwargs.get('sw', 11), kwargs.get('ss', 3)


    # s_wn_ffss = np.array(data_util.smoothing(wn_ffss, smoothing_window))
    # q_wn_ffss = np.array(data_util.stepping(s_wn_ffss, stepping_size))

    s_wn_ffss = np.array(data_util.smooth(wn_ffss, smoothing_window))
    q_wn_ffss = np.array(data_util.stepping(s_wn_ffss, stepping_size))
    s_wn_ffss = running_mean(q_wn_ffss, 3)

    maxu_limit = edata.may_recovered_speed

    to_idx = len(s_wn_ffss) -1
    for idx in range(len(s_wn_ffss)-1, 0, -1):
        if s_wn_ffss[idx] > maxu_limit:
            to_idx = idx
        else:
            break

    max_idx = np.argmax(q_wn_ffss[:to_idx+1]).item()
    maxu = q_wn_ffss[max_idx]

    logger.debug('MaxU-Limit : %.2f, ToIdx : %d / %d, MaxIdx : %d, MaxU : %.2f'
                 % (maxu_limit, to_idx,
                    len(s_wn_ffss)-1, max_idx, maxu))

    #max_idx = np.argmax(q_wn_ffss).item()
    #maxu = q_wn_ffss[max_idx]

    _max_idx = max_idx
    # adjust `max_idx` using `q_wn_ffss`
    for idx in range(max_idx, 0, -1):
        cu = q_wn_ffss[idx]
        if maxu - cu < 1:
            _max_idx = idx
        else:
            break

    # check quantization effect...
    real_max_idx = np.argmax(wn_ffss)
    if _max_idx < real_max_idx and (max(wn_ffss[_max_idx:real_max_idx+1]) - min(wn_ffss[_max_idx:real_max_idx+1]) < 5):
        max_idx = _max_idx

    # adjust `max_idx` using `s_wn_ffss`
    for idx in range(max_idx, to_idx):
        cv, nv = wn_ffss[idx], wn_ffss[idx + 1]
        if nv - cv < change_threshold:
            break
        max_idx = idx

    if max_idx > 0:
        min_idx = np.argmin(s_wn_ffss[:max_idx]).item()
    else:
        min_idx = 0

    return min_idx, max_idx, s_wn_ffss, q_wn_ffss


def _is_low_k_case(edata, uth, wn_ffss, wn_ffs_idxs, over_uth_point,
                   min_idx, max_idx, s_wn_ffss, q_wn_ffss):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type uth: float
    :type wn_ffss: list[float]
    :type wn_ffs_idxs: list[int]
    :type over_uth_point: int
    :type min_idx: int
    :type max_idx: int
    :type s_wn_ffss: numpy.ndarray
    :type q_wn_ffss: numpy.ndarray
    :rtype: int, float, bool
    """
    kth = 7
    rth = 0.9
    margin = setting.INTV30MIN
    data_idx_at_maxu = wn_ffs_idxs[max_idx]
    k_at_maxu = np.mean(edata.sks[data_idx_at_maxu-margin:data_idx_at_maxu])

    if k_at_maxu > kth:
        return False

    highu = edata.may_recovered_speed
    highu_data_idx = None
    for idx, _wn_ffs in enumerate(s_wn_ffss):
        if _wn_ffs > highu:
            highu_data_idx = wn_ffs_idxs[idx]
            break

    if highu_data_idx and np.mean(edata.sks[highu_data_idx-margin:highu_data_idx]) > kth:
        return False

    return True


def _strange_pattern(s_wn_ffss):
    """

    :type s_wn_ffss: numpy.ndarray
    :rtype: bool
    """
    midx = int(len(s_wn_ffss) / 2)
    return np.mean(s_wn_ffss[:midx]) - np.mean(s_wn_ffss[midx:]) > 5


def _qk_data_range(edata, uth, wn_ffss, wn_ffs_idxs, over_uth_point,
                   min_idx, max_idx, s_wn_ffss, q_wn_ffss, **kwargs):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type uth: float
    :type wn_ffss: list[float]
    :type wn_ffs_idxs: list[int]
    :type over_uth_point: int
    :type min_idx: int
    :type max_idx: int
    :type s_wn_ffss: numpy.ndarray
    :type q_wn_ffss: numpy.ndarray
    :rtype: bool, int, int, list[float], list[int], list[int]
    """

    logger = getLogger(__name__)

    mink, maxk, n_limit = kwargs.get('mink', 5), kwargs.get('maxk', FFS_K), kwargs.get('n_limit', 10)

    may_recovered_speed = edata.may_recovered_speed

    logger.debug('MinIdx in WN-FFSs : %d' % min_idx)
    logger.debug('MaxIdx in WN-FFSs : %d' % max_idx)
    logger.debug('MaxWN-FFS:%s, MinWN-FFS:%s' % (max(s_wn_ffss), min(s_wn_ffss)))

    # if recovered from the beginning
    if max_idx == 0 or max_idx == min_idx or max(s_wn_ffss) - min(s_wn_ffss) < 5:
        logger.debug('=> case 1 : recovered from the beginning directly (maxidx=%d, minidx=%d, max=%.2f, min=%.2f)'
                     % (max_idx, min_idx, wn_ffss[max_idx], wn_ffss[min_idx]))
        midx = 0
        if s_wn_ffss[0] > max(uth, edata.target_station.s_limit):
            logger.debug('  -> high speed from the beginning')
            midx = 0
            sidx, eidx = wn_ffs_idxs[midx], max(wn_ffs_idxs[max_idx], min(wn_ffs_idxs[midx] + setting.INTV1HOUR, edata.n_data-1))
        else:
            real_max_idx = np.argmax(wn_ffss).item()
            midx = int((min_idx + real_max_idx) / 2)
            sidx, eidx = wn_ffs_idxs[midx], min(wn_ffs_idxs[real_max_idx], edata.n_data-1)
            if eidx - sidx < setting.INTV1HOUR:
                eidx = sidx + setting.INTV1HOUR

        logger.debug(' -> midx=%d, may_recovered_speed=%.1f, sidx=%d, eidx=%d'
                     % (midx, may_recovered_speed, sidx, eidx))

        not_avaliable = _check_recovered_after_congestion1(edata, sidx, eidx, wn_ffs_idxs, wn_ffss, n_limit, mink, maxk)

        if not_avaliable:
            logger.debug('recovered after congestion')
            return None, None, None, None, None

        mink = 0
        ssidx, seidx, ttks, ttqs, ttus = _make_sure_n_data(edata, sidx, eidx, n_limit, mink, maxk)
        logger.debug('  -> (ssidx, seidx) = (%s, %s)' % (ssidx, seidx))
        return ssidx, seidx, ttks, ttqs, ttus

    _from_idx = min_idx
    _wn_ffss, _wn_ffs_idxs = s_wn_ffss[min_idx:max_idx + 1], wn_ffs_idxs[min_idx:max_idx + 1]

    if len(_wn_ffss) < 3:
        return None, None, None, None, None

    logger.debug('N of _WN_FFSS = %d' % len(_wn_ffss))
    sidx, eidx = -1, -1

    # find vertex point
    up_vertex_idx, d_to_up_vertex, _, _ = _find_vertex(_wn_ffs_idxs, _wn_ffss, find_under=False, offset=min_idx)
    dn_vertex_idx, d_to_dn_vertex, _, _ = _find_vertex(_wn_ffs_idxs, _wn_ffss, find_under=True, offset=min_idx)

    logger.debug('UpVertexIdx=%s, DtoUpVertex=%s' % (up_vertex_idx, d_to_up_vertex))
    logger.debug('DnVertexIdx=%s, DtoDnVertex=%s' % (dn_vertex_idx, d_to_dn_vertex))

    if dn_vertex_idx >= 0 and up_vertex_idx > dn_vertex_idx or up_vertex_idx <= 0:
        _wn_ffss, _wn_ffs_idxs = s_wn_ffss[dn_vertex_idx:max_idx + 1], wn_ffs_idxs[dn_vertex_idx:max_idx + 1]
        _wn_ffss2, _wn_ffs_idxs2 = [], []

        if any(_wn_ffs_idxs):
            _from_idx = dn_vertex_idx
            up_vertex_idx, d_to_up_vertex, _, _ = _find_vertex(_wn_ffs_idxs, _wn_ffss,
                                                               find_under=False, offset=dn_vertex_idx)

            _wn_ffss2, _wn_ffs_idxs2 = s_wn_ffss[up_vertex_idx:max_idx + 1], wn_ffs_idxs[up_vertex_idx:max_idx + 1]

        if any(_wn_ffs_idxs2):
            _from_idx2 = up_vertex_idx
            up_vertex_idx2, d_to_up_vertex2, _, _ = _find_vertex(_wn_ffs_idxs2, _wn_ffss2,
                                                               find_under=False, offset=up_vertex_idx)

            if d_to_up_vertex2 > 2:
                up_vertex_idx = up_vertex_idx2
                d_to_up_vertex = d_to_up_vertex2
                _from_idx = up_vertex_idx

            logger.debug('Updated UpVertexIdx=%s, DtoUpVertex=%s' % (up_vertex_idx, d_to_up_vertex))

    if any(_wn_ffss) and (up_vertex_idx < 0 or (up_vertex_idx >= 0 and d_to_up_vertex < 1)):
        speeds, frequency = _kde(_wn_ffss)
        max_freq_idx = np.argmax(frequency).item()
        wh = np.where(_wn_ffss > speeds[max_freq_idx])
        logger.debug('Max-Frequency Speed in KDE : %s' % speeds[max_freq_idx])

        if any(wh[0]):
            up_vertex_idx = wh[0][0] + _from_idx
            logger.debug('Updated UpVertexIdx=%s (with KDE)' % up_vertex_idx)
        else:
            logger.debug('Updated UpVertexIdx=0 (recovered from the beginning)')
            up_vertex_idx = _from_idx

    if up_vertex_idx < 0:
        logger.debug('UpVertexIdx is not found : set to %s' % _from_idx)
        up_vertex_idx = _from_idx

    real_max_idx = max(max_idx, np.argmax(wn_ffss).item())
    sidx = wn_ffs_idxs[up_vertex_idx]
    _eidx = wn_ffs_idxs[real_max_idx]
    if _eidx - sidx > setting.INTV2HOUR:
        _eidx = wn_ffs_idxs[max_idx]

    eidx = int(max(_eidx, min(wn_ffs_idxs[up_vertex_idx] + setting.INTV1HOUR, len(edata.us))))

    sidx = np.argmin(edata.merged_sus[sidx:eidx]).item() + sidx

    not_avaliable, ssidx, seidx, ttks, ttqs, ttus = _check_recovered_after_congestion(edata, sidx, eidx, wn_ffs_idxs, wn_ffss, n_limit, mink, maxk)


    if not_avaliable:
        return None, None, None, None, None

    # if eidx < sidx:
    #     logger.debug('No Available WN-FFSs (4)')
    #     return None, None, None, None, None
    #
    # if sidx >= 0:
    #     logger.debug('Data Range : (%d, %d)' % (sidx, eidx))
    # else:
    #     return None, None, None, None, None
    #
    # if max_idx is not None:
    #     logger.debug('MaxWNFFSIdx : idx=%d, u=%.2f' % (wn_ffs_idxs[max_idx], wn_ffss[max_idx]))
    # if min_idx is not None:
    #     logger.debug('MinWNFFSIdx : idx=%d, u=%.2f' % (wn_ffs_idxs[min_idx], wn_ffss[min_idx]))

    return ssidx, seidx, ttks, ttqs, ttus

    # return _make_sure_n_data(edata, sidx, eidx, n_limit, mink, maxk, n_try=0, to_limit=to_limit)


def _check_recovered_at_lost(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype:
    """
    sus, qus = _qdata(edata.merged_sus)
    wn_ffs = edata.wn_ffs
    wn_ffs_idx = edata.wn_ffs_idx
    worst_u = qus[edata.worst_ratio_idx]
    print('=->', wn_ffs, worst_u)
    if wn_ffs - worst_u < 5:
        recovered_idx = np.argmax(qus[wn_ffs_idx:wn_ffs_idx+setting.INTV2HOUR]).item() + wn_ffs_idx
        for idx, qu in enumerate(qus[wn_ffs_idx:]):
            if qu - worst_u < 3:
                continue
            recovered_idx = idx + wn_ffs_idx
            print('found---->recovered idx:', recovered_idx)
            break
        print('recovered idx:', recovered_idx)
        edata.wn_ffs = np.mean(edata.merged_sus[recovered_idx-setting.INTV15MIN:recovered_idx+setting.INTV15MIN]).item()
        edata.wn_ffs_idx = _find_wn_ffs_idx(edata, edata.wn_ffs, recovered_idx-setting.INTV15MIN, edata.n_data)
        edata.is_recovered_at_lost = True
        print('update wn_ffs : ', edata.wn_ffs, wn_ffs_idx, '->', edata.wn_ffs_idx)


def _qdata(data, sw=31, ss=3):
    """

    :type data: numpy.ndarray
    :type sw: int
    :type ss: int
    :rtype: numpy.ndarray, numpy.ndarray
    """
    sdata = data_util.smooth(data, sw)
    qdata = data_util.stepping(sdata, ss)
    sdata = qdata
    # sdata = data_util.smooth(qdata, sw2)

    sdata = [ round(v, 2) for v in sdata ]
    qdata = [ round(v, 2) for v in qdata ]

    return np.array(sdata), np.array(qdata)



def _find_ffs(ks, qs, kth, n_try=0):
    """

    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type kth: float
    :type n_try: int
    :rtype: float, function
    """
    from pyticas_ncrtes.core.nsrf.nsr_func import fitting
    wh = np.where(ks < kth)
    ttks = ks[wh]
    ttqs = qs[wh]
    if n_try == 0 and len(ttks) < 10:
        return None, None
    func = lambda x, a: a * x
    _, popts, _, cfunc = fitting.curve_fit(func, ttks, ttqs, [1])

    if n_try == 0:
        _fu = popts[0]
        _ttks, _ttqs = [], []
        for idx, _k in enumerate(ttks):
            _u = ttqs[idx] / _k
            if _fu - _u < 5:
                _ttks.append(ttks[idx])
                _ttqs.append(ttqs[idx])
        if any(_ttks) and len(_ttks) != len(ttks):
            return _find_ffs(np.array(_ttks), np.array(_ttqs), kth, n_try+1)

    # import matplotlib.pyplot as plt
    # fig = plt.figure(facecolor='white', figsize=(16, 8))
    # plt.scatter(ttks, ttqs)
    # krange = list(range(1, 50))
    # plt.plot(krange, [ cfunc(_k) for _k in krange], c='r')
    # plt.ylim(ymin=0, ymax=2000)
    # plt.grid()
    # plt.legend()
    # plt.show()


    return popts[0], cfunc



def _find_wn_ffs_idx(edata, wn_ffs, sidx=None, eidx=None):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type wn_ffs: float
    :type sidx: int
    :type eidx: int
    :rtype: int
    """
    if not sidx:
        sidx = edata.search_start_idx
        eidx = edata.ncrt_search_eidx

    sidx_candidates = [int(sidx)] + edata.uk_change_point
    for _sidx in reversed(sorted(sidx_candidates)):
        if _sidx < eidx:
            sidx = _sidx
            break

    wn_ffs_idx = None

    for idx in range(sidx, eidx):
        if edata.merged_sus[idx] < wn_ffs - 5:
            continue

        tus = edata.merged_sus[idx:eidx]
        tks = edata.merged_sks[idx:eidx]
        wh = np.where( (tks < FFS_K) & (tus < wn_ffs - 5))[0]
        if len(wh) > setting.INTV1HOUR:
            continue

        wn_ffs_idx = idx
        for tidx in range(idx, eidx):
            tus = edata.merged_sus[tidx:tidx+setting.INTV30MIN]
            if edata.merged_sus[tidx] > wn_ffs - 5 and np.mean(tus) >= wn_ffs:
                wn_ffs_idx = tidx
                break
        break

    if not wn_ffs_idx:
        wn_ffs_idx = np.where(edata.merged_sus[sidx:eidx] >= wn_ffs)[0][0]

    wh = np.where(edata.merged_sus[wn_ffs_idx:wn_ffs_idx+setting.INTV30MIN] >= wn_ffs)[0]
    if any(wh):
        wn_ffs_idx = wh[0] + wn_ffs_idx

    wn_ffs_idx = _adjust_with_qdata(edata.qus, edata.sus, wn_ffs_idx)

    if wn_ffs_idx < sidx:
        wn_ffs_idx = sidx

    return wn_ffs_idx



def _find_wn_ffs_idx_origin(edata, wn_ffs):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type wn_ffs: float
    :rtype: int
    """

    _sidx, _eidx = edata.ncrt_search_sidx, edata.ncrt_qk_eidx
    if (edata.ncrt_qk_sidx - _sidx > setting.INTV2HOUR
        and max(edata.merged_sus[_sidx:edata.ncrt_qk_sidx]) - min(edata.merged_sus[_sidx:edata.ncrt_qk_sidx]) > 10):
        _sidx = edata.ncrt_qk_sidx

    for idx in range(_sidx, 0, -1):
        if edata.merged_sus[idx] >= wn_ffs - 5:
            _sidx = idx
        else:
            break

    _sidx = np.where(edata.merged_sus[_sidx:] >= wn_ffs)[0][0] + _sidx

    wn_ffs_idx = _eidx
    for idx, _u in enumerate(edata.merged_sus[_sidx:_eidx]):
        if _u < wn_ffs:
            continue
        wn_ffs_idx = idx + _sidx
        break

    wn_ffs_idx = _adjust_with_qdata(edata.qus, edata.sus, wn_ffs_idx)

    return wn_ffs_idx



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


def _filter_qk(qk, **kwargs):
    """ filtering noise of U-K plain

    :type qk: dict[float, float]
    :rtype: numpy.ndarray, numpy.ndarray
    """
    ks = np.array(sorted(qk.keys()))
    qs = np.array([qk[k] for k in ks])

    k_range = kwargs.get('k_range', 2)
    m = kwargs.get('m', 1.96)
    n_th = kwargs.get('n_threshold', 0)

    _ks, _qs = [], []
    # filter u-noise
    for idx, k in enumerate(ks):
        q = qs[idx]
        _avg, _stddev, _data = data_util.avg_y_of_around_x(ks, qs, k, k_range)
        if _avg and len(_data) <= 3:
            continue
        if not _avg or abs(q - _avg) > m * _stddev or len(_data) < n_th:
            continue

        _ks.append(k)
        _qs.append(q)

    return np.array(_ks), np.array(_qs)


def running_mean(x, N):
    n_data = len(x)
    y = np.zeros((n_data,))
    for ctr in range(n_data):
         y[ctr] = np.sum(x[ctr:(ctr+N)])
    res = y/N
    sidx = n_data-np.floor(N/2)-1
    res[sidx:] = res[sidx-1]
    return res


def _check_recovered_after_congestion1(edata, sidx, eidx, wn_ffs_idxs, wn_ffss, n_limit, mink, maxk):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type sidx: int
    :type eidx: int
    :type wn_ffs_idxs: list[int]
    :type wn_ffss: list[float]
    :type n_limit: int
    :type mink: float
    :type maxk: float
    :rtype: bool, bool
    """
    # move `sidx` to congested area
    _sidx = sidx - setting.INTV1HOUR
    _sidx = np.argmin(edata.merged_sus[_sidx:eidx]).item() + _sidx

    if edata.merged_sus[_sidx] > CONGESTED_SPEED:
        return False

    usidx, ueidx = _under_duration(edata.merged_sus, CONGESTED_SPEED, _sidx)

    # not too congested
    if ueidx - usidx < setting.INTV1HOUR:
        return False

    if edata.worst_ratio_idx >= _sidx:
        return False

    sus_from_widx = edata.merged_sus[edata.worst_ratio_idx:_sidx]
    tmp_recovered_idx = np.argmax(sus_from_widx) + edata.worst_ratio_idx


    if edata.merged_sus[tmp_recovered_idx] < CONGESTED_SPEED:
        return False # recovered from worst to normal condition directly

    ssidx = edata.snow_event.snow_start_index
    if usidx > ssidx + setting.INTV1HOUR:
        if min(edata.merged_sus[ssidx:usidx-setting.INTV1HOUR]) > edata.ncrt_search_uth:
            return False
        if edata.srst and usidx < edata.srst + setting.INTV3HOUR:
            return False


    if min(edata.merged_sus[sidx:eidx]) < CONGESTED_SPEED:
        _decide_wn2_reduction_interval(edata, eidx)
    else:
        _decide_wn2_reduction_interval(edata, sidx)

    return True


def _check_recovered_after_congestion(edata, sidx, eidx, wn_ffs_idxs, wn_ffss, n_limit, mink, maxk):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type sidx: int
    :type eidx: int
    :type wn_ffs_idxs: list[int]
    :type wn_ffss: list[float]
    :type n_limit: int
    :type mink: float
    :type maxk: float
    :rtype: bool, bool, int, int, numpy.ndarray, numpy.ndarray, numpy.ndarray,
    """
    logger = getLogger(__name__)

    tsus = edata.merged_sus[max(eidx-setting.INTV30MIN, 0):min(eidx+setting.INTV30MIN, edata.n_data)]
    tsks = edata.merged_sks[max(eidx-setting.INTV30MIN, 0):min(eidx+setting.INTV30MIN, edata.n_data)]
    wh = np.where(tsks < FFS_K)
    u_at_eidx = np.mean(tsus[wh])

    tsus = edata.merged_sus[max(sidx-setting.INTV30MIN, 0):min(sidx+setting.INTV30MIN, edata.n_data)]
    tsks = edata.merged_sks[max(sidx-setting.INTV30MIN, 0):min(sidx+setting.INTV30MIN, edata.n_data)]
    wh = np.where(tsks < FFS_K)
    u_at_sidx = np.mean(tsus[wh])

    to_limit = None
    ru_th = edata.may_recovered_speed

    ssidx, seidx, ttks, ttqs, ttus = None, None, None, None, None
    is_updated = False

    # check if there is congested area between `sidx` and `eidx`
    if u_at_eidx > ru_th and not is_updated:
        wh = np.where(np.array(wn_ffs_idxs) >= eidx)
        if any(wh[0]):
            wfi_idx = wh[0][0]
            logger.debug('Check congestion between sidx and eidx : %d - %d (wfi_idx=%d)' % (sidx, eidx, wfi_idx))
            for idx in range(wfi_idx, 0, -1):
                cur_idx, next_idx = wn_ffs_idxs[idx-1], wn_ffs_idxs[idx]
                if sidx > cur_idx:
                    break
                if next_idx - cur_idx > setting.INTV2HOUR and np.mean(edata.merged_sus[cur_idx:next_idx]) < CONGESTED_SPEED:
                    logger.debug(' -> update eidx : (%d, %d) -> (%d, %d)' % (sidx, eidx, sidx, cur_idx))
                    eidx = cur_idx
                    to_limit = next_idx
                    is_updated = True
                    ssidx, seidx, ttks, ttqs, ttus = _make_sure_n_data(edata, sidx, eidx, n_limit, mink, maxk, n_try=0, to_limit=to_limit)
                    if ssidx is None:
                        _decide_wn2_reduction_interval(edata, next_idx)
                    break

    # check if there is congested area before `sidx` when speed is already recovered at `sidx`
    if not is_updated and u_at_sidx > ru_th:
        wh = np.where(np.array(wn_ffs_idxs) >= sidx)
        if any(wh[0]):
            wfi_idx = wh[0][0]
            logger.debug('Check congestion before sidx : %d (wfi_idx=%d)' % (sidx, wfi_idx))
            for idx in range(wfi_idx, 0, -1):
                cur_idx, next_idx = wn_ffs_idxs[idx-1], wn_ffs_idxs[idx]
                if sidx - next_idx > setting.INTV2HOUR:
                    break
                if next_idx - cur_idx > setting.INTV2HOUR and np.mean(edata.merged_sus[cur_idx:next_idx]) < CONGESTED_SPEED:
                    # it is already recovered before congestion
                    if wn_ffss[idx-1] >= ru_th:
                        logger.debug(' -> update eidx : (%d, %d) -> (%d, %d)' % (sidx, eidx, cur_idx, cur_idx))
                        sidx = eidx = cur_idx
                        to_limit = next_idx
                        is_updated = True
                        ssidx, seidx, ttks, ttqs, ttus = _make_sure_n_data(edata, sidx, eidx, n_limit, mink, maxk, n_try=0, to_limit=to_limit)
                        if ssidx is None:
                            edata.should_wn_uk_without_ffs = True
                        break
                    else:
                        logger.debug('No Available WN-FFSs (3)')
                        # return False, sidx, eidx, to_limit
                        _decide_wn2_reduction_interval(edata, next_idx)

                        return True, None, None, None, None, None

    if ssidx is None:
        ssidx, seidx, ttks, ttqs, ttus = _make_sure_n_data(edata, sidx, eidx, n_limit, mink, maxk, n_try=0, to_limit=to_limit)

    return False, ssidx, seidx, ttks, ttqs, ttus


def _make_sure_n_data(edata, sidx, eidx, n_limit, mink, maxk, n_try=0, to_limit=None):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type sidx: int
    :type eidx: int
    :type n_limit: int
    :type mink: float
    :type maxk: float
    :rtype: int, int, list[float], list[int], list[int]
    """
    # make sure there is more than `n_limit` data points during data collecting time interval
    ttks, ttqs, tus = [], [], []
    _eidx = eidx
    for idx in range(sidx + setting.INTV15MIN, len(edata.us) - setting.INTV15MIN, setting.INTV15MIN):
        if _eidx - sidx < setting.INTV15MIN:
            _eidx = idx
            continue

        if to_limit and idx > to_limit:
            break

        if to_limit:
            _eidx = min(_eidx, to_limit)

        tks, tqs, tus = edata.ks[sidx:_eidx], edata.qs[sidx:_eidx], edata.us[sidx:_eidx]
        wh = np.where((tks < maxk) & (tks > mink) & (tqs > 360))
        ttks, ttqs, tus = tks[wh], tqs[wh], tus[wh]
        qk = {_k: ttqs[idx] for idx, _k in enumerate(ttks)}
        ttks, ttqs = _filter_qk(qk)
        if len(ttks) > n_limit:
            break
        _eidx = idx
        ttks, ttqs, tus = [], [], []

    if not any(ttks) or len(ttks) < n_limit:
        return None, None, None, None, None

    eidx = _eidx

    return sidx, eidx, ttks, ttqs, tus


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


def _kde(data, step=0.5):
    """
    :type data: Union(list, numpy.ndarray)
    :type step: float
    :rtype: numpy.ndarray, numpy.ndarray
    """
    data = np.array(data)
    if max(data) - min(data) < 3:
        return np.array([np.mean(data)]), np.array([1])

    from scipy import stats
    kernel = stats.gaussian_kde(data)
    data_range = np.arange(min(data), max(data), step)
    res = kernel.evaluate(data_range)
    res = data_util.smooth(res, 5)
    res = np.array(res)

    if DEBUG_MODE:
        # print(data_range)
        # print(res)
        try:
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(16, 9), dpi=100, facecolor='white')
            ax1, ax2 = plt.subplot(121), plt.subplot(122)
            ax1.plot(data_range, res, c='b', marker='o')
            ax2.plot(data)
            plt.grid()
            fig.tight_layout()
            fig.subplots_adjust(top=0.92)
            plt.show()
        except:
            pass

    return data_range, res


def _under_duration(us, uth, target_idx):
    """

    :type us: numpy.ndarray
    :type uth: float
    :type target_idx: int
    :rtype: (int, int)
    """
    prev_idx = target_idx
    for idx in range(target_idx, 0, -1):
        if us[idx] > uth:
            break
        prev_idx = idx

    next_idx = target_idx
    for idx in range(target_idx, len(us)):
        if us[idx] > uth:
            break
        next_idx = idx
    return (prev_idx, next_idx)


def _decide_wn2_reduction_interval(edata, after_congested_idx):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type after_congested_idx: int
    :rtype:
    """
    tmp_recovered_u_th = 20
    edata.should_wn_uk_without_ffs = True
    _midx = max(after_congested_idx - setting.INTV1HOUR, 0)
    midx = np.argmin(edata.merged_sus[_midx:after_congested_idx]).item() + _midx
    uth = max(tmp_recovered_u_th, edata.merged_sus[midx]+5)
    usidx, ueidx = _under_duration(edata.merged_sus, uth, midx)
    sidx, eidx = max(usidx - setting.INTV1HOUR, 0), min(usidx + setting.INTV1HOUR, edata.n_data-1)
    maxu_idx = np.argmax(edata.merged_sus[sidx:eidx]).item() + sidx
    raw_maxu_idx = np.argmax(edata.us[sidx:eidx]).item() + sidx

    if edata.normal_ratios[maxu_idx] < 0.8:
        getLogger(__name__).debug('Temporary Recovered Area is not recovered according to Normal Ratio (maxu_idx=%d, r=%f)'
                                  % (maxu_idx, edata.normal_ratios[maxu_idx]))
        edata.should_wn_uk_without_ffs = False
        return

    edata.wn2_interval_sidx = maxu_idx
    edata.wn2_interval_eidx = maxu_idx
    for idx in range(maxu_idx, edata.n_data):
        if edata.merged_sus[idx] < tmp_recovered_u_th:
            break
        edata.wn2_interval_eidx = idx

    sidx, eidx = max(after_congested_idx - setting.INTV1HOUR, 0), min(after_congested_idx + setting.INTV1HOUR, edata.n_data-1)
    edata.wn2_after_congestion_idx = np.argmax(edata.merged_sus[sidx:eidx]).item() + sidx

    if edata.merged_sus[after_congested_idx] < edata.target_station.s_limit:
        for idx in range(after_congested_idx, edata.n_data-1):
            cu, nu = edata.merged_sus[idx], edata.merged_sus[idx+1]
            if cu > edata.target_station.s_limit - 5 and cu > nu:
                edata.wn2_after_congestion_idx = np.argmax(edata.merged_sus[sidx:eidx]).item() + sidx
                break

    print('wn2_interval (%d - %d), after_congestion_idx=%d' % (maxu_idx, usidx, edata.wn2_after_congestion_idx))


def _chart(edata, wn_ffs, ssidx, seidx, wn_ffss, wn_ffs_idxs, ttks, ttqs, cfunc, uth):
    if not DEBUG_MODE:
        return

    import matplotlib.pyplot as plt

    if ttks is not None:
        fig = plt.figure(facecolor='white', figsize=(16, 8))
        plt.scatter(ttks, ttqs)
        krange = list(range(1, 50))
        plt.plot(krange, [cfunc(_k) for _k in krange], c='r')
        plt.ylim(ymin=0, ymax=2000)
        plt.grid()
        plt.legend()

    fig = plt.figure(facecolor='white', figsize=(16, 8))
    plt.plot(wn_ffs_idxs, wn_ffss, marker='x', c='g')
    s_wn_ffss = np.array(data_util.smooth(wn_ffss, 11))
    q_wn_ffss = np.array(data_util.stepping(s_wn_ffss, 3))
    q_wn_ffss = running_mean(q_wn_ffss, 3)
    plt.plot(wn_ffs_idxs, s_wn_ffss, marker='.', c='r')
    plt.plot(wn_ffs_idxs, q_wn_ffss, marker='.', c='b')
    plt.ylim(ymin=0, ymax=70)
    plt.grid()
    plt.legend()
    try:
        plt.suptitle('%s (SL=%d, FFS=%.2f, Uth=%.2f, WN-FFS=%s, DRange(%d, %d))'
                     % (edata.target_station.station_id,
                        edata.target_station.s_limit,
                        edata.normal_func.daytime_func.get_FFS(),
                        uth if uth else -1,
                        wn_ffs if wn_ffs else -1,
                        ssidx if ssidx else -1, seidx if seidx else -1))
    except:
        plt.suptitle('%s (SL=%d)' % (edata.target_station.station_id, edata.target_station.s_limit))
    plt.show()


def _chart2(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type qus:  numpy.ndarray
    :type qks:  numpy.ndarray
    """
    if not DEBUG_MODE:
        return

    import matplotlib.pyplot as plt

    plt.figure(facecolor='white', figsize=(16, 8))
    ax1 = plt.subplot(111)
    ax1.plot(edata.us, c='#aaaaaa')
    ax1.plot(edata.ks, c='#90A200')
    ax1.plot(edata.qus, c='r')
    ax1.plot(edata.qks, c='#C2CC34')

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
    plt.show()
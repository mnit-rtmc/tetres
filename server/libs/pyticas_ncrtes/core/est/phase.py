# -*- coding: utf-8 -*-


import numpy as np

from pyticas_ncrtes.core import setting, data_util


def determine(edata):
    """

    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    _srst(edata)

    if not edata.ncrt:
        return

    _lst(edata)
    _sist(edata)
    _pst(edata)


def _sist(edata):
    """ Speed Reduction Start Time

    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    # edata.ncrt = 203
    CONGESTED_SPEED = 30
    intv30min = setting.INTV30MIN
    intv1h = setting.INTV1HOUR
    # ncrt, qus, sus = edata.ncrt, edata.qus, edata.sus
    qus = edata.qus
    ncrt, sus = edata.ncrt, data_util.smooth(edata.us, setting.SW_1HOUR)
    if not ncrt:
        return

    if sus[ncrt] < CONGESTED_SPEED:
        return

    sist = edata.lst

    # move backward
    for idx in range(ncrt, 0, -1):
        if qus[idx] - qus[idx - 1] >= -1:
            sist = idx
        else:
            break

    # move forward
    for idx in range(sist, ncrt):
        if qus[idx + 1] - qus[idx] >= 1:
            break
        else:
            sist = idx

    # find minimum speed
    sidx, eidx = max(0, sist - intv30min), min(sist + intv30min, len(qus) - 1)
    edata.sist = np.argmin(sus[sidx:eidx]).item() + sidx

    # minimum speed between sist candidate and ncrt
    if edata.sist and edata.ncrt and edata.ncrt - edata.sist > intv30min:
        edata.sist = np.argmin(sus[edata.sist:edata.ncrt]).item() + edata.sist

    # sist cannot be early than lst
    if edata.lst and edata.sist:
        edata.sist = max(edata.lst, edata.sist)

    # sist cannot be later than ncrt
    if edata.sist >= edata.ncrt:
        edata.sist = None


def _srst(edata):
    """ Speed Reduction Start Time

    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    intv30min = setting.INTV30MIN
    intv1h = setting.INTV1HOUR
    night_time_limit = intv1h
    ratios = edata.ratios
    if ratios is None:
        return
        
    night_ratios = edata.night_sratios


    # find minimum and maximum ratio
    ssidx = edata.snow_event.snow_start_index
    seidx = edata.snow_event.snow_end_index
    widx = ssidx + setting.INTV1HOUR
    max_ratio = min(max(ratios[:widx]), 1)

    tus, tks = edata.sus[ssidx:seidx], edata.sks[ssidx:seidx]
    wh = np.where((tks > 10) & (tus > 30))[0]
    if not any(wh):
        return

    min_ratio = min(ratios[wh])
    rth = max(max_ratio - 0.1, min_ratio + 0.05)

    night_rth = 0.85
    sus = edata.sus
    qus = edata.qus
    n_data = len(ratios)

    start_idx = 0
    for idx in range(n_data - 1):
        if qus[idx + 1] - qus[idx] >= -2:
            start_idx = idx + 1
        else:
            break

    # print('# start idx : ', start_idx)
    # print('# rth : ', rth)

    # find reduction interval
    in_reduction = 0
    for idx in range(start_idx, n_data - night_time_limit):
        if night_ratios[idx] is not None:
            if night_ratios[idx + night_time_limit] is None:
                continue
            nonone_night_ratios = np.nonzero(night_ratios[idx:idx + night_time_limit])[0]
            if (max(nonone_night_ratios) < night_rth and night_ratios[idx] > night_ratios[idx + night_time_limit]):
                in_reduction = idx
                break
        else:
            if (max(ratios[idx:idx + intv30min]) < rth and sus[idx] > sus[idx + intv30min]):
                in_reduction = idx
                break

    # print('# in_reduction : ', in_reduction)
    search_start_idx = ssidx - intv30min

    # move forward if there's speed drop valley and peak-speed is similar with srst candidate
    srst = in_reduction
    for _ in range(10):
        if search_start_idx >= in_reduction:
            continue
        maxqu_sidx = np.argmax(qus[search_start_idx:in_reduction]).item() + search_start_idx
        maxqu_eidx = maxqu_sidx
        for idx in range(maxqu_sidx, n_data):
            if qus[maxqu_sidx] == qus[idx]:
                maxqu_eidx = idx
            else:
                break
        srst = np.argmax(sus[maxqu_sidx:maxqu_eidx + 1]).item() + maxqu_sidx
        sidx = np.argmin(sus[srst:srst + intv30min + 1]).item() + srst
        if in_reduction - sidx > intv30min:
            next_maxu_idx = np.argmax(sus[sidx:in_reduction]).item() + sidx
            # print('> srst=%d, next_max_idx=%d, diff=%f, valley=%f' % (srst, next_maxu_idx, edata.sus[srst] - edata.sus[next_maxu_idx], max(edata.sus[sidx:next_maxu_idx+1]) - min(edata.sus[sidx:next_maxu_idx+1])))
            if ((sus[srst] < sus[next_maxu_idx] or sus[srst] - sus[next_maxu_idx] < 5)
                and max(sus[sidx:next_maxu_idx + 1]) - min(sus[sidx:next_maxu_idx + 1]) > 5):
                search_start_idx = np.argmin(sus[srst:next_maxu_idx + 1]).item() + srst
            else:
                break
        else:
            break

    # move forward if speed level is similar
    prev_srst = srst
    u_at_srst = sus[srst]
    for idx in range(srst, n_data):
        avgu = np.mean(edata.us[idx:idx + intv30min])
        if u_at_srst - avgu < 5:
            # print(' -> move : %d -> %d' % (prev_srst, idx))
            srst = idx
        else:
            break

    # check speed level difference between srst and losted time
    lost_idx = in_reduction
    for idx in range(in_reduction, lost_idx):
        if sus[idx] > sus[idx + 1]:
            lost_idx = idx
        else:
            break
    eidx = min(lost_idx + intv30min * 2, n_data - 1)
    lost_idx = np.argmin(sus[lost_idx:eidx + 1]).item() + lost_idx

    # if speed drop is very little...
    if abs(sus[srst] - sus[lost_idx]) < 5:
        srst = None

    # print('=> ', srst)
    edata.srst = srst


def _lst(edata):
    """ Lowest Speed Time

    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    sidx = edata.snow_event.snow_start_index
    eidx = edata.ncrt

    try:
        sus, sks = edata.sus[sidx:eidx + 1], edata.sks[sidx:eidx + 1]
        lst = np.argmin(sus) + sidx
        edata.lst = lst
    except:
        print('=> error to find lst: ', edata.target_station.station_id, sidx, eidx)


def _pst(edata):
    """ Lowest Speed Time

    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """

    if edata.sist:
        sidx = edata.sist if edata.sus[edata.sist] < edata.target_station.s_limit else edata.lst
    else:
        sidx = edata.lst

    if not sidx:
        return

    eidx = edata.n_data - setting.INTV1HOUR

    edata.pst = _reaching_point(edata.sus,
                                edata.target_station.s_limit,
                                sidx, eidx)


def _reaching_point(data, target_speed, search_from, search_to, t_intv=setting.INTV1HOUR, try_alt=False, op='gt'):
    """

    :type data: numpy.ndarray
    :type target_speed: float
    :type search_from:  int
    :type search_to:  int
    :type t_intv: int
    :type try_alt: bool
    :rtype: int
    """
    search_to = min(search_to, len(data))
    for idx in range(search_from, search_to):
        to = min(idx + t_intv, search_to)
        tus = data[idx:to]
        avgu = np.mean(tus)

        # check drop-again
        wh = np.where(data[idx:search_to] < target_speed - 5)[0]
        if len(wh) > setting.INTV1HOUR:
            continue

        if ((op == 'gt' and data[idx] >= target_speed and avgu >= target_speed)
            or (op == 'lt' and data[idx] <= target_speed and avgu <= target_speed)):
            return idx

    if try_alt:
        # find just the first over-target-speed point
        if op == 'gt':
            wh = np.where(data[search_from:search_to] >= target_speed)
        else:
            wh = np.where(data[search_from:search_to] <= target_speed)

        if any(wh[0]):
            return int(wh[0][0]) + search_from

    return None

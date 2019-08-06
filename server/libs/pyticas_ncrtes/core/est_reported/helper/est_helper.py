# -*- coding: utf-8 -*-
from pyticas_ncrtes.core import setting, data_util

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import numpy as np
import matplotlib.pyplot as plt

from pyticas_ncrtes.core.est.helper import nighttime_helper as nh


# def minute_to_interval(minute):
#     return (minute * 60) / setting.DATA_INTERVAL
#
#
# def minute_to_smoothing_window(minute):
#     return setting._window(minute_to_interval(minute))


def find_speed_change_point(edata, aks, aus, normal_ffs, **kwargs):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :param aks:
    :type aks: numpy.ndarray
    :param aus:
    :type aus: numpy.ndarray
    :param normal_ffs:
    :type normal_ffs: float
    """
    LOW_K = kwargs.get('low_k', 10)
    W = kwargs.get('window_size', 10)
    SW = kwargs.get('smoothing_window_size', 11)
    U_DIFF_THRESHOLD = kwargs.get('u_diff_threshold', 8)
    K_DIFF_THRESHOLD = kwargs.get('k_diff_threshold', 5)

    BIG_K_DIFF_THRESHOLD = kwargs.get('big_k_diff_threshold', 10)

    search_limit_idx = edata.snow_event.snow_end_index + setting.INTV2HOUR

    paks, naks, udiffs, kdiffs, pmaxks, pminks, nmaxks, nminks, nuss = [], [], [], [], [], [], [], [], []
    for idx in range(W, len(aks)-W):
        if idx >= search_limit_idx:
            break

        pks, pus, nks, nus = aks[idx-W:idx], aus[idx-W:idx], aks[idx+1:idx+W+1], aus[idx+1:idx+W+1]
        pak, pau, nak, nau = np.mean(pks), np.mean(pus), np.mean(nks), np.mean(nus)
        nuss.append(nau)
        udiffs.append(nau - pau)
        kdiffs.append(nak - pak)
        paks.append(pak)
        naks.append(nak)
        pmaxks.append(max(pks))
        pminks.append(min(pks))
        nmaxks.append(max(nks))
        nminks.append(min(nks))

    udiffs, kdiffs = np.array(udiffs), np.array(kdiffs)
    sudiffs = data_util.smooth(udiffs, SW)
    maxpoints = data_util.max_points(sudiffs)

    w2 = int(W / 2)
    cps = []
    for mp in maxpoints:
        # print('real_mp=', real_mp, ', real_mp + W = ', real_mp+W, ', is_night=', edata.night_ratios[mp])
        # print('  -> check1 : '
        #       ,mp < w2
        #       ,mp > len(udiffs)-w2
        #       ,paks[mp] < LOW_K
        #       ,naks[mp] < LOW_K
        #       ,edata.night_ratios[mp] is None
        #       ,((paks[mp] < LOW_K and naks[mp] < LOW_K) and edata.night_ratios[mp] is None))

        if (mp < w2
            or mp > len(udiffs)-w2
            or ((paks[mp] < LOW_K and naks[mp] < LOW_K) and edata.night_ratios[mp] is not None)):
            # or ((paks[mp] < LOW_K or naks[mp] < LOW_K))):
            #or (paks[mp] < LOW_K or naks[mp] < LOW_K)):
            continue

        real_mp = np.argmax(udiffs[mp-w2:mp+w2]).item() + (mp-w2)
        pu = np.mean(aus[real_mp-W:real_mp]).item()

        # print('  -> check : ', real_mp+W,
        #       edata.qus[real_mp+W+W] < normal_ffs*0.9
        #     ,udiffs[real_mp] > U_DIFF_THRESHOLD
        #     ,-K_DIFF_THRESHOLD < kdiffs[real_mp] < K_DIFF_THRESHOLD
        #     ,pmaxks[real_mp] - pminks[real_mp] < BIG_K_DIFF_THRESHOLD
        #     ,nmaxks[real_mp] - nminks[real_mp] < BIG_K_DIFF_THRESHOLD
        #     ,pmaxks[real_mp] - nminks[real_mp] < BIG_K_DIFF_THRESHOLD
        #     ,abs(pu - nuss[real_mp]) > U_DIFF_THRESHOLD)

        if (udiffs[real_mp] > U_DIFF_THRESHOLD
            and edata.qus[real_mp+W] < normal_ffs*0.9
            and -K_DIFF_THRESHOLD < kdiffs[real_mp] < K_DIFF_THRESHOLD
            and pmaxks[real_mp] - pminks[real_mp] < BIG_K_DIFF_THRESHOLD
            and nmaxks[real_mp] - nminks[real_mp] < BIG_K_DIFF_THRESHOLD
            and pmaxks[real_mp] - nminks[real_mp] < BIG_K_DIFF_THRESHOLD
            and abs(pu - nuss[real_mp]) > U_DIFF_THRESHOLD):
            cps.append(real_mp + W)
        # if (udiffs[real_mp] > U_DIFF_THRESHOLD
        #     and -K_DIFF_THRESHOLD < kdiffs[real_mp] < K_DIFF_THRESHOLD
        #     and pmaxks[real_mp] - pminks[real_mp] < BIG_K_DIFF_THRESHOLD
        #     and nmaxks[real_mp] - nminks[real_mp] < BIG_K_DIFF_THRESHOLD
        #     and pmaxks[real_mp] - nminks[real_mp] < BIG_K_DIFF_THRESHOLD):
        #     cps.append(real_mp + W)


    # import matplotlib.pyplot as plt
    # w = W
    # fig = plt.figure(figsize=(18, 4), dpi=100, facecolor='white')
    # plt.plot([0]*w + udiffs.tolist() + [0]*w, label='udiffs')
    # plt.plot([0]*w + sudiffs.tolist() + [0]*w, label='sudiffs')
    # plt.plot([0]*w + kdiffs.tolist() + [0]*w, label='kdiffs')
    #
    # for cp in cps:
    #     plt.axvline(x=cp, c='r')
    #
    # plt.tight_layout()
    # plt.legend()
    # plt.grid()

    return cps



def find_speed_reduction_in_same_k(edata, **kwargs):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    # 2013-01-27, I-35W NB, S34
    LOW_K = kwargs.get('low_k', 10)
    U_DIFF_THRESHOLD = kwargs.get('u_diff_threshold', 8)
    K_DIFF_THRESHOLD = kwargs.get('k_diff_threshold', 5)
    default_Kt = kwargs.get('default_kt', 25)
    kt = edata.normal_func.daytime_func.get_Kt() if edata.normal_func else default_Kt
    if not kt:
        kt = default_Kt

    snow_end_idx = edata.snow_event.time_to_index(edata.snow_event.snow_end_time)
    search_limit_idx = snow_end_idx + setting.SW_2HOURS

    sw = setting.SW_1HOUR
    sus = data_util.smooth(edata.aus, sw)
    sks = data_util.smooth(edata.aks, sw)
    night_us = edata.night_us
    minmax = data_util.local_minmax_points(sus)

    res = []
    for idx in range(1, len(minmax)):
        pidx, cidx = minmax[idx - 1], minmax[idx]
        pu, cu = sus[pidx], sus[cidx]
        pk, ck = sks[pidx], sks[cidx]

        if cidx >= search_limit_idx:
            break

        # skip nighttime
        if (pk < LOW_K and ck < LOW_K and night_us[cidx] is not None and night_us[pidx] is not None):
            continue

        # skip high-k
        if pk > kt or ck > kt:
            continue

        if (pu - cu >= U_DIFF_THRESHOLD and ck - pk <= K_DIFF_THRESHOLD
            and not _is_temporary_drop(cidx, edata, 30, 0.8)):
            res.append([pidx, cidx])

    return res


def find_speed_recovery_in_same_k(edata, **kwargs):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    LOW_K = kwargs.get('low_k', 10)
    U_DIFF_THRESHOLD = kwargs.get('u_diff_threshold', 10)
    K_DIFF_THRESHOLD = kwargs.get('k_diff_threshold', 8)
    default_Kt = kwargs.get('default_kt', 25)

    kt = edata.normal_func.daytime_func.get_Kt() if edata.normal_func else default_Kt
    if not kt:
        kt = default_Kt

    snow_end_idx = edata.snow_event.time_to_index(edata.snow_event.snow_end_time)
    search_limit_idx = snow_end_idx + setting.SW_2HOURS

    sw = setting.SW_1HOUR
    sus = data_util.smooth(edata.aus, sw)
    sks = data_util.smooth(edata.aks, sw)
    night_us = edata.night_us
    minmax = data_util.local_minmax_points(sus)

    res = []
    for idx in range(1, len(minmax)):
        pidx, cidx = minmax[idx - 1], minmax[idx]
        pu, cu = sus[pidx], sus[cidx]
        pk, ck = sks[pidx], sks[cidx]

        if cidx >= search_limit_idx:
            break

        # skip nighttime
        if (pk < LOW_K and ck < LOW_K and night_us[cidx] is not None and night_us[pidx] is not None):
            continue

        # skip high-k
        if pk > kt or ck > kt:
            continue

        if (cu - pu >= U_DIFF_THRESHOLD and pk - ck <= K_DIFF_THRESHOLD):
            res.append([pidx, cidx])

    return res


def worst_ratio_point(edata, ratios=None, default_Kt=25):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :param ratios:
    :type ratios:
    :rtype: int
    """
    CONGESTED_SPEED = 30
    LOW_K = 5
    snow_sidx, snow_eidx = (edata.snow_event.time_to_index(edata.snow_event.snow_start_time),
                            edata.snow_event.time_to_index(edata.snow_event.snow_end_time))

    snow_sidx = max(snow_sidx, snow_eidx - setting.INTV1HOUR*24)

    wn_ratios = edata.normal_ratios[snow_sidx:snow_eidx] if ratios is None else ratios[snow_sidx:snow_eidx]
    sus, sks = edata.sus[snow_sidx:snow_eidx], edata.sks[snow_sidx:snow_eidx]
    kt = edata.normal_func.daytime_func.get_Kt() if edata.normal_func else default_Kt
    if not kt:
        kt = default_Kt

    tindices = np.where( (sus > CONGESTED_SPEED) & (sks > LOW_K) & (sks < kt))
    if not any(tindices[0]):
        tindices = np.where( (sus > CONGESTED_SPEED) & (sks > LOW_K))
    if not any(tindices[0]):
        tindices = (list(range(len(wn_ratios))), list)

    target_ratios = wn_ratios[tindices[0]]
    midx = np.argmin(target_ratios).item()

    widx = tindices[0][midx] + snow_sidx
    sidx = max(widx-setting.INTV30MIN, 0)
    eidx = min(widx+setting.INTV30MIN, edata.n_data-1)

    return np.argmin(edata.merged_sus[sidx:eidx]) + sidx



def  find_nighttime_snowing(edata, **kwargs):
    """
    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: list[int]
    """
    nighttime_patterns = nh.nighttime_pattern(edata)
    drops1 = _find_nighttime_snowing_by_ratio_drop(edata, nighttime_patterns, **kwargs)
    drops2 = _find_nighttime_snowing_by_speed_pattern(edata, nighttime_patterns, **kwargs)
    drops = sorted(list(set(drops1 + drops2)))

    # TODO: fix this code...
    snow_end_idx = edata.snow_event.snow_end_index
    to_idx = snow_end_idx + setting.INTV2HOUR

    return [ idx for idx in drops if idx < to_idx ]

def _find_nighttime_snowing_by_speed_pattern(edata, nighttime_patterns, **kwargs):
    """
    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type nighttime_patterns: list[pyticas_ncrtes.core.etypes.NighttimePatterns]
    :rtype: list[int]
    """
    res = []
    night_ratios = edata.night_sratios

    for nighttime_pattern in nighttime_patterns:
        if not nighttime_pattern.patterns:
            continue
        last_seg = nighttime_pattern.patterns[-1]
        if last_seg.is_recovered:
            continue

        if not _has_ratio_drop_after(last_seg.eidx, edata):
            continue

        # set reduction interval index
        TREND_STABLE = nh.NighttimePatterns.TREND_STABLE

        found = False
        # find real reduction hill start point
        for ppt_idx in range(len(nighttime_pattern.patterns)-2, 0, -1):
            ppt = nighttime_pattern.patterns[ppt_idx]
            if ppt.speed_trend != TREND_STABLE:
                found = True
                min_idx = np.argmin(night_ratios[ppt.sidx:last_seg.eidx]) + ppt.sidx
                # print(' > nighttime reduction (2-1): ', min_idx)
                res.append(min_idx)
                break

        if not found:
            # print(' > nighttime reduction (2-2): ', last_seg.eidx)
            res.append(last_seg.eidx)

    return res


def _has_ratio_drop_after(tidx, edata, time_limit=setting.INTV2HOUR, rth=0.8):
    """

    :param tidx:
    :type tidx: int
    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    tidx, time_limit = int(tidx), int(time_limit)
    ratios = edata.normal_ratios[tidx:tidx+time_limit]

    min_idx, min_ratio = np.argmin(ratios), min(ratios)
    if min_ratio < rth:
        return True
    return False


def _is_temporary_drop_during_nighttime(tidx, edata, nighttime_patterns, time_limit=setting.INTV30MIN, rth=0.8):
    """

    :param tidx:
    :type tidx: int
    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :param nighttime_patterns:
    :type nighttime_patterns: list[pyticas_ncrtes.core.etypes.NighttimePatterns]
    """
    nighttime_ratios = edata.night_sratios
    sidx, eidx = int(max(tidx - time_limit, 0)), int(min(tidx + time_limit, len(nighttime_ratios)-1))
    if not (sidx < tidx < eidx):
        return False
    prev_max = max(np.nonzero(nighttime_ratios[sidx:tidx])[0])
    next_max = max(np.nonzero(nighttime_ratios[tidx:eidx])[0])
    return prev_max >= rth and next_max >= rth


def _is_temporary_drop(tidx, edata, time_limit=setting.INTV30MIN, rth=0.8):
    """

    :type tidx: int
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    ratios = edata.normal_ratios
    sidx, eidx = int(max(tidx - time_limit, 0)), int(min(tidx + time_limit, len(ratios)-1))
    prev_max = max(np.nonzero(ratios[sidx:tidx])[0])
    next_max = max(np.nonzero(ratios[tidx:eidx])[0])
    return prev_max >= rth and next_max >= rth


def _find_nighttime_snowing_by_ratio_drop(edata, nighttime_patterns, **kwargs):
    """
    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type nighttime_patterns: list[pyticas_ncrtes.core.etypes.NighttimePatterns]
    :rtype: list[int]
    """
    res = []
    nighttime_drop_ratio_threshold = kwargs.get('nighttime_drop_ratio_threshold', 0.1)
    nighttime_ratios = edata.night_ratios
    nighttime_avg_us = edata.night_us
    nighttime_sus = edata.sus_for_night
    s_limit = edata.target_station.s_limit
    wn_ffs = edata.wn_ffs if edata.wn_ffs else s_limit - 5
    u_limit = min(wn_ffs, s_limit)

    TREND_STABLE = nh.NighttimePatterns.TREND_STABLE
    TREND_RECOVERY = nh.NighttimePatterns.TREND_RECOVERY
    TREND_REDUCTION = nh.NighttimePatterns.TREND_REDUCTION

    for nighttime_pattern in nighttime_patterns:

        for pt_idx, pt in enumerate(nighttime_pattern.patterns):

            # only for reduction interval
            if pt.speed_trend in [TREND_RECOVERY, TREND_STABLE]:
                continue

            # set reduction interval index
            hill_sidx, hill_eidx = pt.sidx, pt.eidx

            # find real reduction hill start point
            for ppt_idx in range(pt_idx, 0, -1):
                ppt = nighttime_pattern.patterns[ppt_idx]
                if ppt.speed_trend == TREND_RECOVERY:
                    break
                if nighttime_sus[pt.sidx] - 5 > nighttime_sus[ppt.sidx]:
                    break
                if ppt.speed_trend == TREND_REDUCTION:
                    hill_sidx = ppt.sidx

            # find real reduction hill end point
            for npt_idx in range(pt_idx, len(nighttime_pattern.patterns)):
                npt = nighttime_pattern.patterns[npt_idx]
                if npt.speed_trend == TREND_RECOVERY:
                    break
                if nighttime_sus[pt.eidx] + 5 < nighttime_sus[npt.eidx]:
                    break
                if npt.speed_trend == TREND_REDUCTION:
                    hill_eidx = npt.eidx


            sr, er = nighttime_ratios[hill_sidx], nighttime_ratios[hill_eidx]

            # big ratio drop
            if (sr - er > nighttime_drop_ratio_threshold*2
                and er < 0.8
                and nighttime_sus[hill_eidx] < u_limit
                and not _is_temporary_drop_during_nighttime(pt.eidx, edata, nighttime_patterns)): # 2012-12-09, S33
                # print(' > nighttime reduction (1): ', pt.eidx)
                res.append(pt.eidx)
                continue

            # if nighttime_sus[pt.sidx] < nighttime_sus[pt.eidx] or nighttime_avg_us[pt.sidx] - nighttime_avg_us[pt.eidx] > 5:
            #     continue

            # ratio drop during recovery interval of normal-avg-nighttime-speed
            if (sr - er > nighttime_drop_ratio_threshold
                and nighttime_sus[hill_eidx] < u_limit
                and (not nighttime_pattern.patterns[-1].is_recovered or er < 0.7)
                and not _is_temporary_drop_during_nighttime(pt.eidx, edata, nighttime_patterns)):
                # print(' > nighttime reduction (2): ', pt.eidx)
                res.append(pt.eidx)
    return res



def find_nighttime_snowing_v1(edata, **kwargs):
    """
    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: list[int]
    """
    nighttime_patterns = nh.nighttime_pattern(edata)
    res = []
    ratio_threshold = kwargs.get('ratio_threshold', 0.9)
    nighttime_drop_ratio_threshold = kwargs.get('nighttime_drop_ratio_threshold', 0.1)
    nighttime_ratios = edata.night_ratios
    nighttime_avg_us = edata.night_us
    nighttime_sus = edata.sus_for_night
    s_limit = edata.target_station.s_limit
    wn_sratios = edata.wn_sratios
    wn_ffs = edata.wn_ffs if edata.wn_ffs else s_limit - 5
    u_limit = min(wn_ffs, s_limit)
    # print('# _find_nighttime_snowing')
    for nighttime_pattern in nighttime_patterns:
        for pt in nighttime_pattern.patterns:
            if nighttime_sus[pt.sidx] < nighttime_sus[pt.eidx] or nighttime_avg_us[pt.sidx] - nighttime_avg_us[pt.eidx] > 5:
                # print(' -> skip : ', pt)
                continue
            hill_sidx, hill_eidx = pt.sidx, pt.eidx
            sr, er = nighttime_ratios[hill_sidx], nighttime_ratios[hill_eidx]
            # if wn_sratios is not None:
            #     print('   - check hill : ', (hill_sidx, hill_eidx), (sr, er), (nighttime_sus[hill_eidx], wn_sratios[hill_eidx]))
            #     print('         >> ', (sr - er > nighttime_drop_ratio_threshold), (nighttime_sus[hill_eidx] < u_limit), (wn_sratios[hill_eidx] < ratio_threshold))

            if (sr - er > nighttime_drop_ratio_threshold
                and nighttime_sus[hill_eidx] < u_limit
                and not nighttime_pattern.patterns[-1].is_recovered):
                #and wn_sratios[hill_eidx] < ratio_threshold):
                res.append(pt.eidx)
    return res

def find_stable_ratio_sections(ratios, stable_duration_limit):
    """

    :param ratios:
    :type ratios: numpy.ndarray
    :param stable_duration_limit:
    :type stable_duration_limit: int
    :return:
    :rtype: list[[int, int, float]
    """

    diffs = ratios[1:] - ratios[:-1]
    iszero = np.concatenate(([0], np.equal(diffs, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    stable_ranges = np.where(absdiff == 1)[0].reshape(-1, 2)

    res = []
    for sidx, eidx in stable_ranges:
        if (eidx - sidx) < stable_duration_limit:
            continue
        res.append([sidx, eidx, np.mean(ratios[sidx:eidx+1])])

    return res

def get_histogram(data, xmin=0, normed=True):
    res = np.histogram(data, bins=list(range(xmin, 200, 5)), normed=normed)
    counts = list(res[0])
    bins = list(res[1][1:])
    # smoothed = data_util.gaussian_filter(counts, N=3)
    return bins, counts


def show_histogram(data, edata, additional_title=''):
    long_title = '%s (%s[s_limit=%d, label=%s], %s)%s' % (
        edata.snow_event.snow_period.get_date_string(),
        edata.target_station.station_id,
        edata.target_station.s_limit,
        edata.target_station.label,
        edata.target_station.corridor.name,
        additional_title)

    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor='white')
    ax1, ax2 = plt.subplot(121), plt.subplot(122)
    _k_bins, _k_hist = get_histogram(data)
    ax1.plot(_k_bins, _k_hist, c='b', marker='o')
    ax2.plot(data)
    plt.grid()
    fig.suptitle(long_title)
    fig.tight_layout()
    fig.subplots_adjust(top=0.92)
    plt.show()


def show_histogram_kde(data, edata, additional_title=''):
    from scipy import stats
    import matplotlib.pyplot as plt

    kernel = stats.gaussian_kde(data, bw_method=0.1)
    data_range = list(range(int(min(data)), int(max(data))))
    res = np.array(kernel.evaluate(data_range))
    res = data_util.smooth(res, 11)
    long_title = '%s (%s[s_limit=%d, label=%s], %s)%s' % (
        edata.snow_event.snow_period.get_date_string(),
        edata.target_station.station_id,
        edata.target_station.s_limit,
        edata.target_station.label,
        edata.target_station.corridor.name,
        additional_title)

    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor='white')
    ax1, ax2 = plt.subplot(121), plt.subplot(122)
    ax1.plot(data_range, res, c='b', marker='o')
    ax2.plot(data)
    plt.grid()
    fig.suptitle(long_title)
    fig.tight_layout()
    fig.subplots_adjust(top=0.92)
    plt.show()


    # ffs_limit = nsr_func.station.s_limit + 20
    # if ffs >= ffs_limit:
    #     log.info('> %s : Freeflow Speed is too high. It might have detector calibration problem' % tsi.station_id)
    #     return False


    return True

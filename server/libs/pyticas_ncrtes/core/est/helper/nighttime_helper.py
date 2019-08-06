# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import numpy as np

from pyticas_ncrtes.core import setting, data_util

LOW_K_AREA = 10
NIGHTTIME_RECOVERED_RATIO = 0.9

class NighttimePattern(object):
    def __init__(self, speed_trend, sidx, eidx, is_recovered, ratios):
        """

        :type speed_trend: int
        :type sidx: int
        :type eidx: int
        :type is_recovered: bool
        :type ratios: list[float]
        """
        self.idx = -1
        self.speed_trend = speed_trend
        self.sidx = sidx
        self.eidx = eidx
        self.is_recovered = is_recovered
        self.speed_trend_raw = speed_trend
        self.ratios = ratios

    def is_recovery(self):
        return self.speed_trend_raw == NighttimePatterns.TREND_RECOVERY

    def __repr__(self):
        return ('<NighttimePattern sidx=%d, eidx=%d, speed_trend=%d is_recovered=%s>'
                % (self.sidx, self.eidx, self.speed_trend, self.is_recovered))

    def __str__(self):
        return self.__repr__()

class NighttimePatterns(object):

    LITTLE_DROP = 5
    RECOVERED_RATIO = 0.9
    TREND_STABLE = 0
    TREND_RECOVERY = 1
    TREND_REDUCTION = -1

    PT_FULLY_RECOVERED = 1
    PT_RECOVERING_DURING_WHOLE_NIGHT = 2
    PT_REACH_TO_NORMAL = 3
    PT_RECOVERING_BUT_NOT_RECOVERED = 4
    PT_LOOSING_DURING_WHOLE_NIGHT = -1
    PT_LOOSING_AT_END_OF_NIGHT_AND_KEEP_LOOSING = -2
    PT_LOOSING_AT_END_OF_NIGHT = -3
    PT_UNKNOWN = 99

    def __init__(self, npatterns, edata):
        """

        :type npatterns: list[NighttimePattern]
        :type edata: ESTData
        """
        self.patterns = npatterns
        self.edata = edata
        for idx, pt in enumerate(self.patterns):
            pt.idx = idx

    def get_indices(self):
        """
        :rtype: (int, int)
        """
        return (self.patterns[0].sidx, self.patterns[-1].eidx)

    def patterns_before_recovered(self):
        """

        :rtype: (NighttimePattern, int, list[int], list[NighttimePattern])
        """
        recovered = []
        for _p in self.patterns:
            if _p.is_recovered:
                recovered.append(_p)
            else:
                recovered = []

        last_recovered = recovered[0] if recovered else None
        last_trend = self.TREND_RECOVERY
        trs = [ _p.speed_trend for _p in self.patterns ]
        pts = self.patterns

        if not last_recovered:
            last_trend = trs[-1]
            if last_trend == 0:
                not_stables = [ _t for _t in reversed(trs) if _t != self.TREND_STABLE ]
                if not_stables:
                    last_trend = not_stables[0]
                else:
                    last_trend = self.patterns[-1].speed_trend_raw
        else:
            trs = [ _p.speed_trend for _p in self.patterns if _p.sidx <= last_recovered.sidx]
            pts = [ _p for _p in self.patterns if _p.sidx <= last_recovered.sidx]

        return last_recovered, last_trend, trs, pts


    def recovery_pattern(self):

        last_recovered, last_trend, trs, pts = self.patterns_before_recovered()

        # no reduction and speed level is high
        if self.TREND_REDUCTION not in trs and self.patterns[-1].is_recovered:
            return self.PT_FULLY_RECOVERED

        # no reduction in rate and speed level is not high
        elif self.TREND_REDUCTION not in trs:
            return self.PT_RECOVERING_DURING_WHOLE_NIGHT

        # there's reduction in rate, but recovered at end of nighttime
        elif last_trend == self.TREND_RECOVERY and self.patterns[-1].is_recovered:
            return self.PT_REACH_TO_NORMAL

        # there's reduction in rate, but recovering at end of nighttime (not fully)
        elif last_trend == self.TREND_RECOVERY and not self.patterns[-1].is_recovered:
            return self.PT_RECOVERING_BUT_NOT_RECOVERED

        # continuously reduction in rate during nighttime
        elif self.TREND_RECOVERY not in trs:
            return self.PT_LOOSING_DURING_WHOLE_NIGHT

        # continuously reduction in rate during nighttime
        elif (last_trend == self.TREND_REDUCTION
              and not self.patterns[-1].is_recovered and not self.has_recoverying_before_peak()):
            return self.PT_LOOSING_AT_END_OF_NIGHT_AND_KEEP_LOOSING

        # continuously reduction during nighttime
        elif last_trend == self.TREND_REDUCTION and not self.patterns[-1].is_recovered:
            return self.PT_LOOSING_AT_END_OF_NIGHT

        return self.PT_UNKNOWN


    def has_recoverying_before_peak(self):
        s_limit = self.edata.target_station.s_limit
        eidx = self.patterns[-1].eidx
        if eidx > len(self.edata.sus) - setting.SW_1HOUR:
            return False

        _sus, _sks = self.edata.sus[eidx:], self.edata.sks[eidx:]
        wh_highk = np.where(_sks > 20)
        if not any(wh_highk[0]):
            return False
        sus, sks = _sus[:wh_highk[0][0]], _sks[:wh_highk[0][0]]

        # minmax_idxs = np.diff(np.sign(np.diff(sus))).nonzero()[0].tolist()
        # minmax = [0] + minmax_idxs + [len(sus) - 1]
        #
        # for idx in range(1, len(minmax)):
        #     pu, nu = sus[idx-1], sus[idx]
        #     if pu < nu:
        #         return True
        #
        # return False

        if max(sus) > s_limit - 5:
            return True

        return False



    def recovered_point(self):
        pass

    def __repr__(self):
        return ('<NighttimePatterns sidx=%d, eidx=%d, patterns=%d>'
                % (self.patterns[0].sidx, self.patterns[-1].eidx, len(self.patterns)))

    def __str__(self):
        return self.__repr__()


SAME_UK_GROUP_U_DISTANCE_THRESHOLD = 5


def find_recovery_point_during_night(g, night_patterns, uk_groups, edata):
    """
    :type g: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :type night_patterns: list[pyticas_ncrtes.core.etypes.NighttimePatterns]
    :type uk_groups: list[pyticas_ncrtes.core.etypes.UKTrajectoryGroup]
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :return:
    """
    # if this function is called, it means that aleady recovered after this nighttime

    night_pattern = find_nighttime_pattern_for_nighttime_group(night_patterns, g)
    if not night_pattern:
        return False, None

    # if it is "recovering all night",
    # then find recovery point during nighttime
    if _is_all_night_recovering(night_pattern, edata):

        if _is_recovered_at_end_of_nighttime(night_pattern, edata):
            print('> all night recovering and recovered at end of nighttime')
            return _determine_recovered_point_during_nighttime(g, night_pattern, uk_groups, edata)
        else:
            print('> all night recovering and NOT recovered at end of nighttime')
            return _determine_recovered_point_after_nighttime(night_pattern, uk_groups, edata)

    # elif it is "recovered before night" and no "drop-by-snowing" during nighttime,
    # then skip it
    if _is_recovered_before_ngihttime(night_pattern, edata) and not _has_drop_by_snow_during_nighttime(night_pattern, edata):
        return False, None

    # elif it is "loosing all night"
    if _is_all_night_loosing(night_pattern, edata):
        return False, None

    # else, find recovery point during nighttime
    print('> else case')
    return _determine_recovered_point_during_nighttime(g, night_pattern, uk_groups, edata)


def find_nighttime_pattern_for_nighttime_group(night_patterns, nighttime_group):
    """

    :type night_patterns: list[NighttimePatterns]
    :type nighttime_group: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :return:
    """
    g_sidx = nighttime_group.edges[0].start_point.sidx
    g_eidx = nighttime_group.edges[-1].end_point.eidx
    for _night_pattern in reversed(night_patterns):
        (sidx, eidx) = _night_pattern.get_indices()
        if not (g_sidx > eidx or g_eidx < sidx):
            return _night_pattern
    return None


def find_group_for_nighttime_pattern(tidx, uk_groups):
    """

    :type tidx: int
    :type uk_groups: list[pyticas_ncrtes.core.etypes.UKTrajectoryGroup]
    :return:
    """
    for g in uk_groups:
        if g.edges[0].start_point.sidx < tidx < g.edges[-1].end_point.eidx:
            return g
    return None


def _nighttime_section_has_max_speed_increase(night_pattern, edata):
    """

    :type night_pattern: pyticas_ncrtes.core.etypes.NighttimePatterns
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: (int, int)
    """
    max_u_increase_start, max_u_increase_end, max_u_increase = -1, -1, -1
    for pt in night_pattern.patterns:
        if pt.speed_trend != NighttimePatterns.TREND_RECOVERY:
            continue
        sidx, eidx = pt.sidx, pt.eidx
        sus = edata.lsus[sidx:eidx+1]
        minu, maxu = min(sus), max(sus)
        u_increase = maxu - minu
        if max_u_increase < u_increase:
            max_u_increase = u_increase
            max_u_increase_start = sidx
            max_u_increase_end = eidx
    if max_u_increase_start > 0:
        return (max_u_increase_start, max_u_increase_end)
    return (-1, -1)


def _nighttime_last_recovery(night_pattern, edata):
    """

    :type night_pattern: pyticas_ncrtes.core.etypes.NighttimePatterns
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: (int, int)
    """
    for pt in reversed(night_pattern.patterns):
        if pt.speed_trend != NighttimePatterns.TREND_RECOVERY:
            continue
        return (pt.sidx, pt.eidx)

    return (-1, -1)


def _nighttime_section_to_reach_normal(night_pattern, edata):
    """

    :type night_pattern: pyticas_ncrtes.core.etypes.NighttimePatterns
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: ([int, int], [int, int])
    """
    before_updated = [-1, -1]
    last_recovered = [-1, -1]
    last_recovered_pt = None
    for pt in night_pattern.patterns:
        if pt.speed_trend != NighttimePatterns.TREND_RECOVERY and not pt.is_recovered:
            last_recovered = [-1, -1]
            last_recovered_pt = None
            continue

        if last_recovered[0] < 0 and pt.is_recovered:
            last_recovered = [pt.sidx, pt.eidx]
            last_recovered_pt = pt
            # return (pt.sidx, pt.eidx)

    if last_recovered_pt:

        before_updated = list(last_recovered)

        for idx in range(last_recovered_pt.sidx, last_recovered_pt.eidx+1):
            if edata.night_ratios[idx] >= setting.NIGHTTIME_RECOVERED_RATIO:
                last_recovered[1] = idx
                break

        for pt in reversed(night_pattern.patterns[:last_recovered_pt.idx]):
            if pt.speed_trend == NighttimePatterns.TREND_STABLE or pt.speed_trend == NighttimePatterns.TREND_RECOVERY:
                last_recovered[0] = pt.sidx
            else:
                break

        if last_recovered[1] - last_recovered[0] > 1:
            last_recovered[0] = last_recovered[0] + np.argmin(edata.llsus[last_recovered[0]:last_recovered[1]])

        if last_recovered[1] - last_recovered[0] > 1:
            last_recovered[1] = last_recovered[0] + np.argmax(edata.llsus[last_recovered[0]:last_recovered[1]])


    return before_updated, last_recovered


def _is_all_night_recovering(night_pattern, edata):
    """

    :type night_pattern: pyticas_ncrtes.core.etypes.NighttimePatterns
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: (int, int)
    """
    # retrieve nighttime patterns before the first recovered section
    # which is after the last not-recovered section
    last_recovered, last_trend, trs, pts = night_pattern.patterns_before_recovered()

    if (pts[0].speed_trend not in [ NighttimePatterns.TREND_RECOVERY, NighttimePatterns.TREND_STABLE ]
        or not last_recovered):
        return False

    sus = edata.sus
    us_at_minmax = [sus[pts[0].sidx], sus[pts[0].eidx]]
    for pt in pts:
        idx = pt.eidx
        u = sus[idx]
        if u < min(us_at_minmax) and not pt.is_recovery():
            return False
        us_at_minmax.append(u)

    # is_the_case = False
    # up_gaps, down_gaps = [], []
    # for pt in pts:
    #     if pt.is_recovery():
    #         up_gaps.append(edata.sus[pt.eidx] - edata.sus[pt.sidx])
    #     else:
    #         down_gaps.append(edata.sus[pt.sidx] - edata.sus[pt.eidx])
    #
    # max_down_gap = max(down_gaps) if down_gaps else -1
    # max_up_gap = max(up_gaps) if up_gaps else -1
    return True


def _is_recovered_at_end_of_nighttime(night_pattern, edata):
    """

    :type night_pattern: pyticas_ncrtes.core.etypes.NighttimePatterns
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: (int, int)
    """
    # retrieve nighttime patterns before the first recovered section
    # which is after the last not-recovered section
    last_recovered, last_trend, trs, pts = night_pattern.patterns_before_recovered()
    return (last_recovered != None)


def _is_all_night_loosing(night_pattern, edata):
    """

    :type night_pattern: pyticas_ncrtes.core.etypes.NighttimePatterns
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: (int, int)
    """
    # retrieve nighttime patterns before the first recovered section
    # which is after the last not-recovered section
    last_recovered, last_trend, trs, pts = night_pattern.patterns_before_recovered()

    if NighttimePatterns.TREND_RECOVERY not in trs:
        return True

    # continuously reduction in rate during nighttime
    if (last_trend == NighttimePatterns.TREND_REDUCTION
          and not night_pattern.patterns[-1].is_recovered and not night_pattern.has_recoverying_before_peak()):
        return True

    # continuously reduction during nighttime
    if last_trend == NighttimePatterns.TREND_REDUCTION and not night_pattern.patterns[-1].is_recovered:
        return True

    return False


def _is_recovered_before_ngihttime(night_pattern, edata):
    """

    :type night_pattern: pyticas_ncrtes.core.etypes.NighttimePatterns
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: (int, int)
    """
    last_recovered, last_trend, trs, pts = night_pattern.patterns_before_recovered()

    # nighttime is over speed_limit
    sus = edata.llsus[pts[0].sidx:pts[-1].eidx]
    if min(sus) > edata.target_station.s_limit:
        return True

    # the first section is recovered
    if pts[0].is_recovered:
        return True

    return False


def _has_drop_by_snow_during_nighttime(night_pattern, edata):
    """

    :type night_pattern: pyticas_ncrtes.core.etypes.NighttimePatterns
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: (int, int)
    """
    last_recovered, last_trend, trs, pts = night_pattern.patterns_before_recovered()
    sus = edata.sus
    for pt in pts:
        if pt.is_recovery():
            continue
        gap = sus[pt.sidx] - sus[pt.eidx]
        # gap_ratio = pt.ratios[0] - pt.ratios[-1]
        if gap > SAME_UK_GROUP_U_DISTANCE_THRESHOLD:
            return True
    return False


def _determine_recovered_point_during_nighttime(g, night_pattern, uk_groups, edata):
    """

    :type g: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :type night_pattern: pyticas_ncrtes.core.etypes.NighttimePatterns
    :type uk_groups: list[pyticas_ncrtes.core.etypes.UKTrajectoryGroup]
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: bool, (int, int)
    """
    print('# _determine_recovered_point_during_nighttime()')
    # recovered during nighttime
    (osidx, oeidx), (sidx, eidx) = _nighttime_section_to_reach_normal(night_pattern, edata)
    print(' > _nighttime_section_to_reach_normal() : ', (sidx, eidx))
    if sidx < 0:
        # (sidx, eidx) = _nighttime_section_has_max_speed_increase(night_pattern, edata)
        # print(' > _nighttime_section_has_max_speed_increase() : ', (sidx, eidx))
        (sidx, eidx) = _nighttime_last_recovery(night_pattern, edata)
        print(' > _nighttime_last_recovery() : ', (sidx, eidx))

    if osidx == night_pattern.patterns[0].sidx and osidx < g.edges[0].start_point.sidx:
        _g = find_group_for_nighttime_pattern(sidx - 1, uk_groups)
        if _g and _g.is_recovery:
            return False, (sidx, eidx)

    if (sidx == eidx):
        return False, (sidx, eidx)

    return True, (sidx, eidx)


def _determine_recovered_point_after_nighttime(night_pattern, uk_groups, edata):
    """

    :type night_pattern: pyticas_ncrtes.core.etypes.NighttimePatterns
    :type uk_groups: list[pyticas_ncrtes.core.etypes.UKTrajectoryGroup]
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: (int, int)
    """
    print('# _determine_recovered_point_after_nighttime()')
    # recovered after nighttime
    start_idx = night_pattern.patterns[-1].eidx
    for idx, _u in enumerate(edata.night_us[start_idx:]):
        if _u is None:
            start_idx = start_idx + idx
            break

    _sus, _sks = edata.sus[start_idx+1:], edata.sks[start_idx+1:]
    minmax = data_util.local_minmax_points(_sus)
    start_point = start_idx
    max_point = start_idx + minmax[-1]
    for idx in range(1, len(minmax)):
        pu, nu = _sus[minmax[idx-1]], _sus[minmax[idx]]
        if pu < nu:
            start_point = start_idx + minmax[idx-1]
            max_point = start_idx + minmax[idx]
            break

    g = find_group_for_nighttime_pattern(max_point, uk_groups)
    if g:
        max_point = g.edges[0].start_point.sidx

    # max_point = start_idx + minmax[-1]
    # for idx in range(1, len(minmax)):
    #     pu, nu = _sus[minmax[idx-1]], _sus[minmax[idx]]
    #     # until find big-drop...
    #     if pu - nu > SAME_UK_GROUP_U_DISTANCE_THRESHOLD:
    #         max_point = start_idx + minmax[idx-1]
    #         break

    return True, (start_point, max_point)
    # return True, (night_pattern.patterns[-1].sidx, max_point)


def find_nighttime_pattern(night_patterns, peak_reduction_group):
    """

    :type night_patterns: list[NighttimePatterns]
    :type peak_reduction_group: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :return:
    """
    g_sidx = peak_reduction_group.edges[0].start_point.sidx
    for _night_pattern in reversed(night_patterns):
        (sidx, eidx) = _night_pattern.get_indices()
        if g_sidx > sidx and g_sidx - eidx < setting.SW_4HOURS * 2:
            return _night_pattern
    return None


def nighttime_pattern(edata):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: list[NighttimePatterns]
    """
    segs = nighttime_segments(edata)
    patterns = []
    for (sidx, eidx) in segs:
        patterns.append(_nighttime_u_change_pattern(sidx, eidx, edata))
    return patterns


def nighttime_segments(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: list[(int, int)]
    """
    segments = []
    seg_start_idx = -1

    idx = 0
    for idx, u in enumerate(edata.night_us):
        if u is not None:
            if seg_start_idx < 0:
                seg_start_idx = idx
        else:
            if seg_start_idx >= 0:
                segments.append((seg_start_idx, idx - 1))
                seg_start_idx = -1

    if seg_start_idx >= 0:
        segments.append((seg_start_idx, edata.n_data-1))

    return segments


def _nighttime_u_change_pattern(sidx, eidx, edata):
    """
    :type sidx: int
    :type eidx: int
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: NighttimePatterns
    """
    nus = edata.night_us[sidx:eidx+1]
    sus = edata.sus_for_night[sidx:eidx+1]
    nks = edata.night_ks[sidx:eidx+1]
    sks = edata.sks_for_night[sidx:eidx+1]

    wh_lowk = np.where(sks < LOW_K_AREA)
    if any(wh_lowk[0]):
        _sidx, _eidx = wh_lowk[0][0], wh_lowk[0][-1]
        nus = nus[:_eidx+1]
        sus = sus[:_eidx+1]
        nks = nks[:_eidx+1]
        sks = sks[:_eidx+1]
        eidx = sidx + _eidx

    diffs = nus - sus
    ratios = sus / nus

    minmax = data_util.local_minmax_points(diffs)

    LITTLE_DROP = NighttimePatterns.LITTLE_DROP
    RECOVERED_RATIO = NighttimePatterns.RECOVERED_RATIO
    TREND_STABLE = NighttimePatterns.TREND_STABLE
    TREND_RECOVERY = NighttimePatterns.TREND_RECOVERY
    TREND_REDUCTION = NighttimePatterns.TREND_REDUCTION

    segs = []
    """:type: list[NighttimePattern] """

    for idx in range(1, len(minmax)):
        _sidx, _eidx = minmax[idx-1], minmax[idx]
        _ratios = ratios[_sidx:_eidx+1].tolist()

        if abs(diffs[_eidx] - diffs[_sidx]) < LITTLE_DROP:
            if segs and segs[-1].speed_trend == TREND_STABLE:
                segs[-1].eidx= sidx + _eidx
                segs[-1].is_recovered = np.mean(ratios[segs[-1].sidx-sidx:_eidx]) > RECOVERED_RATIO
                segs[-1].ratios = segs[-1].ratios + _ratios[1:]
            else:
                segs.append(NighttimePattern(TREND_STABLE, sidx+_sidx, sidx+_eidx, np.mean(ratios[_sidx:_eidx+1]) > RECOVERED_RATIO, _ratios)) # stable
        elif diffs[_sidx] > diffs[_eidx]:
            segs.append(NighttimePattern(TREND_RECOVERY, sidx+_sidx, sidx+_eidx, ratios[_eidx] > RECOVERED_RATIO, _ratios)) # recovery
        else:
            segs.append(NighttimePattern(TREND_REDUCTION, sidx+_sidx, sidx+_eidx, ratios[_eidx] > RECOVERED_RATIO, _ratios)) # reduction

        segs[-1].speed_trend_raw = 1 if diffs[_sidx] > diffs[_eidx] else -1

    return NighttimePatterns(segs, edata)



def _nighttime_u_change_pattern_v1(sidx, eidx, edata):
    """
    :type sidx: int
    :type eidx: int
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: NighttimePatterns
    """
    nus = edata.night_us[sidx:eidx+1]
    sus = edata.sus_for_night[sidx:eidx+1]
    nks = edata.night_ks[sidx:eidx+1]
    sks = edata.sks_for_night[sidx:eidx+1]

    wh_lowk = np.where(sks < LOW_K_AREA)
    if any(wh_lowk[0]):
        _sidx, _eidx = wh_lowk[0][0], wh_lowk[0][-1]
        nus = nus[:_eidx+1]
        sus = sus[:_eidx+1]
        nks = nks[:_eidx+1]
        sks = sks[:_eidx+1]
        eidx = sidx + _eidx

    diffs = nus - sus
    ratios = sus / nus

    minmax = data_util.local_minmax_points(diffs)

    LITTLE_DROP = NighttimePatterns.LITTLE_DROP
    RECOVERED_RATIO = NighttimePatterns.RECOVERED_RATIO
    TREND_STABLE = NighttimePatterns.TREND_STABLE
    TREND_RECOVERY = NighttimePatterns.TREND_RECOVERY
    TREND_REDUCTION = NighttimePatterns.TREND_REDUCTION

    segs = []
    """:type: list[NighttimePattern] """

    for idx in range(1, len(minmax)):
        _sidx, _eidx = minmax[idx-1], minmax[idx]
        _ratios = ratios[_sidx:_eidx+1].tolist()

        if abs(diffs[_eidx] - diffs[_sidx]) < LITTLE_DROP:
            if segs and segs[-1].speed_trend == TREND_STABLE:
                segs[-1].eidx= sidx + _eidx
                segs[-1].is_recovered = np.mean(ratios[segs[-1].sidx-sidx:_eidx]) > RECOVERED_RATIO
                segs[-1].ratios = segs[-1].ratios + _ratios[1:]
            else:
                segs.append(NighttimePattern(TREND_STABLE, sidx+_sidx, sidx+_eidx, np.mean(ratios[_sidx:_eidx+1]) > RECOVERED_RATIO, _ratios)) # stable
        elif diffs[_sidx] > diffs[_eidx]:
            segs.append(NighttimePattern(TREND_RECOVERY, sidx+_sidx, sidx+_eidx, ratios[_eidx] > RECOVERED_RATIO, _ratios)) # recovery
        else:
            segs.append(NighttimePattern(TREND_REDUCTION, sidx+_sidx, sidx+_eidx, ratios[_eidx] > RECOVERED_RATIO, _ratios)) # reduction

        segs[-1].speed_trend_raw = 1 if diffs[_sidx] > diffs[_eidx] else -1

    return NighttimePatterns(segs, edata)

def has_nighttime(g, edata):
    """

    :type g: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :return:
    """
    sidx, eidx = g.edges[0].start_point.sidx, g.edges[-1].end_point.eidx
    is_night = []
    for idx in range(sidx, eidx):
        if edata.night_us[idx] is not None:
            is_night.append(idx)
    return len(is_night) >= setting.SW_4HOURS


def recovery_interval_at_a_point(tidx, ratios, sratios):
    """

    :type tidx: int
    :type ratios: numpy.ndarray
    :type sratios: numpy.ndarray
    :rtype: (int, int)
    """
    return _recovery_start_point(tidx, ratios, sratios), _recovery_end_point(tidx, ratios, sratios)


def _recovery_start_point(tidx, ratios, sratios, interval_margin=10):
    """

    :type tidx: int
    :type ratios: numpy.ndarray
    :type sratios: numpy.ndarray
    :type interval_margin: int
    :rtype: [int, int]
    """
    stick = None
    for idx in range(tidx-1, 0, -1):
        if sratios[idx] is None:
            stick = idx + 1
            break

        if sratios[idx + 1] < sratios[idx]:
            stick = idx + 1
            break

    if not stick:
        stick = 0

    for idx in range(stick, tidx):
        if sratios[stick] != sratios[idx]:
            stick = idx - 1
            break

    if stick == tidx:
        return stick

    stick = max(stick - interval_margin, 0)

    for idx in range(stick, tidx):
        if ratios[idx] is not None:
            stick = idx
            break

    for idx in range(tidx, stick):
        if ratios[idx] is not None:
            tidx = idx
            break

    print(stick, tidx, ratios[stick:tidx])

    return stick + np.argmin(ratios[stick:tidx])


def _recovery_end_point(tidx, ratios, sratios, interval_margin=10):
    """

    :type tidx: int
    :type ratios: numpy.ndarray
    :type sratios: numpy.ndarray
    :type interval_margin: int
    :rtype: [int, int]
    """
    stick = None
    for idx in range(tidx+1, len(sratios)):
        if sratios[idx] is None:
            stick = idx - 1
            break
        if sratios[idx] < sratios[idx - 1]:
            stick = idx - 1
            break

    if not stick:
        stick = len(ratios) - 1

    for idx in range(stick, tidx, -1):
        if sratios[idx] is None:
            break
        if sratios[stick] != sratios[idx]:
            stick = idx + 1
            break

    stick = min(stick + interval_margin, len(sratios) - 1)

    for idx in range(stick, tidx, -1):
        if ratios[idx] is not None:
            stick = idx
            break

    for idx in range(tidx, stick):
        if ratios[idx] is not None:
            tidx = idx
            break



    return tidx + np.argmax(ratios[tidx:stick])



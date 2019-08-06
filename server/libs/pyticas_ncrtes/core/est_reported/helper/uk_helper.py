# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import math
import numpy as np

VERTICAL_SLOP = 3  # 2 = when speed changes as 15 and density changes as 5
SAME_UK_GROUP_U_DISTANCE_THRESHOLD = 5
SAME_UK_GROUP_K_DISTANCE_THRESHOLD = 10
UK_TRACKING_DISTANCE_THRESHOLD = 5  # 7.07
SMALL_UK_GROUP_THRESHOLD = 2
LINEAR_LINE_DEGREE_THRESHOLD = 80 #22.5
STABLE_SPEED_THRESHOLD = 3
STABLE_TIME_THRESHOLD = 60 # in minute
LOW_K = 10
SAME_K_LIMIT = 5


def is_vertical_down_edge(edge):
    """

    :type edge: pyticas_ncrtes.core.etypes.UKTrajectoryEdge
    :rtype: bool
    """
    if (edge.is_recovery or edge.contain_nighttime()):
        return False
    pr, cr = edge.start_point, edge.end_point
    pck, pcu, cck, ccu = pr.center_k, pr.center_u, cr.center_k, cr.center_u
    slope = (ccu - pcu) / (cck - pck)
    is_vertical = (slope > VERTICAL_SLOP or slope < -VERTICAL_SLOP)
    if is_vertical and pcu - ccu > SAME_UK_GROUP_U_DISTANCE_THRESHOLD:
        return True
    else:
        return False


def is_vertical_edge(edge):
    """

    :type edge: pyticas_ncrtes.core.etypes.UKTrajectoryEdge
    :rtype: bool
    """
    (mink, maxk), (minu, maxu) = edge.minmax()
    if maxk < LOW_K:
        return False
    pr, cr = edge.start_point, edge.end_point
    pck, pcu, cck, ccu = pr.center_k, pr.center_u, cr.center_k, cr.center_u
    slope = (ccu - pcu) / (cck - pck)
    is_vertical = (slope > VERTICAL_SLOP or slope < -VERTICAL_SLOP)
    if is_vertical and abs(pcu - ccu) > SAME_UK_GROUP_U_DISTANCE_THRESHOLD:
        return True
    else:
        return False


def get_direction_change_angle(e1, e2):
    """

    :type e1: pyticas_ncrtes.core.etypes.UKTrajectoryEdge
    :type e2: pyticas_ncrtes.core.etypes.UKTrajectoryEdge
    :rtype: float
    """
    if e1.start_point.sidx < e2.start_point.sidx:
        return get_angle_among_3points(e1.start_point, e1.end_point, e2.end_point)
    else:
        return get_angle_among_3points(e2.start_point, e2.end_point, e1.end_point)


def get_angle_among_3points(p0, p1, p2):
    """
    :type p0: pyticas_ncrtes.core.etypes.UKTrajectoryPoint
    :type p1: pyticas_ncrtes.core.etypes.UKTrajectoryPoint
    :type p2: pyticas_ncrtes.core.etypes.UKTrajectoryPoint
    :rtype: float
    """
    points = np.array([[p0.center_k, p0.center_u], [p1.center_k, p1.center_u], [p2.center_k, p2.center_u]])
    L1 = points[1] - points[0]
    L2 = points[2] - points[1]
    e1, e2 = L1, -L2
    num = np.dot(e1, e2)
    denom = np.linalg.norm(e1) * np.linalg.norm(e2)
    degree = 180 - np.arccos(num/denom) * 180 / np.pi
    return degree


def is_overlapped(e1, e2):
    """
    :type e1: Union(pyticas_ncrtes.core.etypes.UKTrajectoryEdge, pyticas_ncrtes.core.etypes.UKTrajectoryGroup)
    :type e2: Union(pyticas_ncrtes.core.etypes.UKTrajectoryEdge, pyticas_ncrtes.core.etypes.UKTrajectoryGroup)
    :rtype: bool
    """
    (mink1, maxk1), (minu1, maxu1) = e1.minmax()
    (mink2, maxk2), (minu2, maxu2) = e2.minmax()
    return not (maxk1 < mink2 + 1 or mink1 > maxk2 - 1)


def is_over(host_edge, guest_edge):
    """
    :type host_edge: Union(pyticas_ncrtes.core.etypes.UKTrajectoryEdge, pyticas_ncrtes.core.etypes.UKTrajectoryGroup)
    :type guest_edge: Union(pyticas_ncrtes.core.etypes.UKTrajectoryEdge, pyticas_ncrtes.core.etypes.UKTrajectoryGroup)
    :rtype: bool
    """
    (mink, maxk), (minu, maxu) = overlapped_area(host_edge, guest_edge)
    if mink is None:
        return False
    mk = (mink + maxk) / 2
    return host_edge.u_at_k(mk) > guest_edge.u_at_k(mk)


def overlapped_area(e1, e2):
    """
    :type e1: Union(pyticas_ncrtes.core.etypes.UKTrajectoryEdge, pyticas_ncrtes.core.etypes.UKTrajectoryGroup)
    :type e2: Union(pyticas_ncrtes.core.etypes.UKTrajectoryEdge, pyticas_ncrtes.core.etypes.UKTrajectoryGroup)
    :rtype: ((float, float), (float, float))
    """
    if not is_overlapped(e1, e2):
        return (None, None), (None, None)
    (mink1, maxk1), (minu1, maxu1) = e1.minmax()
    (mink2, maxk2), (minu2, maxu2) = e2.minmax()

    return (max(mink1, mink2), min(maxk1, maxk2)), (max(minu1, minu2), min(maxu1, maxu2))


def uk_abs_diffs(e1, e2):
    """
    :type e1: Union(pyticas_ncrtes.core.etypes.UKTrajectoryEdge, pyticas_ncrtes.core.etypes.UKTrajectoryGroup)
    :type e2: Union(pyticas_ncrtes.core.etypes.UKTrajectoryEdge, pyticas_ncrtes.core.etypes.UKTrajectoryGroup)
    :rtype: list[float], list[float]
    """
    udiffs, kdiffs = uk_diffs(e1, e2)
    if udiffs is None:
        return None, None
    return [ abs(_u) for _u in udiffs ], [ abs(_k) for _k in kdiffs ]


def uk_diffs(e1, e2):
    """
    :type e1: Union(pyticas_ncrtes.core.etypes.UKTrajectoryEdge, pyticas_ncrtes.core.etypes.UKTrajectoryGroup)
    :type e2: Union(pyticas_ncrtes.core.etypes.UKTrajectoryEdge, pyticas_ncrtes.core.etypes.UKTrajectoryGroup)
    :rtype: list[float], list[float]
    """
    (mink, maxk), (minu, maxu) = overlapped_area(e1, e2)
    if mink is None:
        return None, None
    udiffs = []
    step = min(0.5, (maxk - mink) / 5)
    if step > 0:
        for k in np.arange(mink, maxk, step):
            u1 = e1.u_at_k(k)
            u2 = e2.u_at_k(k)
            if not u1 or not u2 or u1 == u2:
                continue
            udiffs.append(u1 - u2)

    kdiffs = []
    step = min(0.5, (maxu - minu) / 5)
    if step > 0:
        for u in np.arange(minu, maxu, step):
            k1 = e1.k_at_u(u)
            k2 = e2.k_at_u(u)
            if not k1 or not k2 or k1 == k2:
                continue
            kdiffs.append(k1 - k2)
    return udiffs, kdiffs


def distance_from_point_to_edge(p, g):
    """
    :type p: pyticas_ncrtes.core.etypes.UKTrajectoryPoint
    :type g: pyticas_ncrtes.core.etypes.UKTrajectoryEdge
    :rtype: float
    """
    (mink, maxk), (minu, maxu) = g.minmax()
    step = min(0.5, (maxk - mink) / 3)

    dists = []
    for k in np.arange(mink, maxk, step):
        u = g.u_at_k(k)
        d = math.sqrt((p.center_k - k) ** 2 + (p.center_u - u) ** 2)
        dists.append(d)

    return min(dists)


def has_overlapped_edge(g):
    """

    :type g: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :return:
    """
    for pidx in range(len(g.edges)-1):
        for nidx in range(pidx+1, len(g.edges)):
            pe, ce = g.edges[pidx], g.edges[nidx]
            if is_overlapped(pe, ce):
                return True
    return False



def has_near_ks(pg, ng):
    """
    :type pg: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :type ng: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :rtype: bool
    """
    pp1, pp2, np1, np2 = pg.edges[0].start_point, pg.edges[-1].end_point, ng.edges[0].start_point, ng.edges[-1].end_point
    maxu = max(pp1.center_u, pp2.center_u, np1.center_u, np2.center_u)
    minu = min(pp1.center_u, pp2.center_u, np1.center_u, np2.center_u)

    for u in np.arange(maxu, minu, -0.5):
        pk = pg.k_at_u(u)
        nk = ng.k_at_u(u)
        if not pk or not nk:
            continue
        if abs(pk - nk) > SAME_K_LIMIT:
            return False

    return True


def is_under_recovery(pg, cg, groups):
    """
    :type pg: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :type cg: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :type groups: list[UKTrajectoryGroup]
    :rtype: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    """
    if (not pg.is_recovery or cg.is_recovery
        or pg.contain_nighttime() or cg.contain_nighttime()):
        return None

    pp, cp = pg.edges[0].start_point, cg.edges[-1].end_point
    found = False
    if pp.center_k >= cp.center_k:
        _u = pg.u_at_k(cp.center_k)
        if _u is not None and cp.center_u < _u:
            found = True
    else:
        _u = cg.u_at_k(pp.center_k)
        if _u is not None and pp.center_u > _u:
            found = True

    if not found:
        return None

    # check u-k range
    if has_near_ks(pg, cg):
        return None

    return cg


def is_recovery_over_reduction(pg, cg, groups):
    """
    :type pg: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :type cg: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :type groups: list[UKTrajectoryGroup]
    :rtype: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    """
    if (pg.is_recovery or not cg.is_recovery
        or pg.contain_nighttime() or cg.contain_nighttime()):
        return None

    pp, cp = pg.edges[0].start_point, cg.edges[-1].end_point
    found = False
    if pp.center_k >= cp.center_k:
        _u = pg.u_at_k(cp.center_k)
        if _u is not None and cp.center_u > _u:
            found = True
    else:
        _u = cg.u_at_k(pp.center_k)
        if _u is not None and pp.center_u < _u:
            found = True

    if not found:
        return None

    # check u-k range
    if has_near_ks(pg, cg):
        return None

    return cg



def is_vertical_down(pg, cg, groups):
    """
    :type pg: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :type cg: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :type groups: list[UKTrajectoryGroup]
    :rtype: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    """
    if (cg.is_recovery or cg.contain_nighttime()):
        return None
    pr, cr = cg.edges[0].start_point, cg.edges[-1].end_point
    pck, pcu, cck, ccu = pr.center_k, pr.center_u, cr.center_k, cr.center_u
    slope = (ccu - pcu) / (cck - pck)
    is_vertical = (slope > VERTICAL_SLOP or slope < -VERTICAL_SLOP)
    if is_vertical and pcu - ccu > 5:
        return cg
    else:
        return None


def is_vertical_up(pg, cg):
    """
    :type pg: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :type cg: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :rtype: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    """
    if (not cg.is_recovery or cg.contain_nighttime()):
        return None
    pr, cr = cg.edges[0].start_point, cg.edges[-1].end_point
    pck, pcu, cck, ccu = pr.center_k, pr.center_u, cr.center_k, cr.center_u
    slope = (ccu - pcu) / (cck - pck)
    is_vertical = (slope > VERTICAL_SLOP or slope < -VERTICAL_SLOP)
    if is_vertical and ccu - pcu > 5:
        return cg
    else:
        return None


def is_up_to_right(pg, cg):
    """
    :type pg: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :type cg: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :rtype: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    """
    if (not cg.is_recovery or cg.contain_nighttime()):
        return None
    pr, cr = cg.edges[0].start_point, cg.edges[-1].end_point
    pck, pcu, cck, ccu = pr.center_k, pr.center_u, cr.center_k, cr.center_u
    slope = (ccu - pcu) / (cck - pck)
    is_right_up = ( slope >= 0 )
    if is_right_up:
        return cg
    else:
        return None


def is_down_to_left(pg, cg):
    """
    :type pg: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :type cg: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    :rtype: pyticas_ncrtes.core.etypes.UKTrajectoryGroup
    """
    if (cg.is_recovery or cg.contain_nighttime()):
        return None
    pr, cr = cg.edges[0].start_point, cg.edges[-1].end_point
    pck, pcu, cck, ccu = pr.center_k, pr.center_u, cr.center_k, cr.center_u
    slope = (ccu - pcu) / (cck - pck)
    is_left_down = ( slope >= 0 )
    if is_left_down:
        return cg
    else:
        return None



class UKTrajectoryPoint(object):
    def __init__(self, idx, sidx, eidx, ks, us, edata):
        """

        :type idx: int
        :type sidx: int
        :type eidx: int
        :type ks: numpy.ndarray
        :type us: numpy.ndarray
        :type edata: pyticas_ncrtes.core.etypes.ESTData
        """
        self.idx = idx
        self.sidx = sidx
        self.eidx = eidx
        self.ks = ks
        self.us = us
        self.edata = edata
        self.center_k, self.center_u = self._center_point()
        # self.distance_to_normal = None
        # self.distance_to_normal = self._minimum_distance_to_normal()
        self.in_nighttime = self._in_nighttime()
        self.mink, self.maxk, self.minu, self.maxu = min(self.ks), max(self.ks), min(self.us), max(self.us)
        self.length = len(self.ks)
        self.minutes = (self.length * edata.snow_event.interval) / 60.0

    def _center_point(self):
        """

        :rtype: (float, float)
        """
        return np.mean(self.ks), np.mean(self.us)

    def _in_nighttime(self):
        """

        :rtype: bool
        """
        night_ratios = self.edata.night_ratios[self.sidx:self.eidx + 1]
        nonzeros = np.nonzero(night_ratios)
        return len(nonzeros[0]) > 0

    def __repr__(self):
        return ('<UKTrajectoryPoint idx=%d interval=(%d-%d) center=(%.2f, %.2f)>'
                % (self.idx, self.sidx, self.eidx, self.center_k, self.center_u))

    def __str__(self):
        return self.__repr__()


class UKTrajectoryEdge(object):
    def __init__(self, idx, start_point, end_point):
        """

        :type idx: int
        :type start_point: UKTrajectoryPoint
        :type end_point: UKTrajectoryPoint
        """
        self.idx = idx
        self.start_point = start_point
        self.end_point = end_point
        self.group = -1
        self.update_trend()
        self.has_overlapped = False
        self.tag = None
        self.is_fixed = False

    def update_trend(self):
        # pd, cd = self.end_point.distance_to_normal, self.start_point.distance_to_normal
        # self.rate_to_normal = (pd - cd) if pd is not None else None
        self.is_recovery = (self.start_point.center_u < self.end_point.center_u)
        self.is_k_increase = (self.start_point.center_k < self.end_point.center_k)

    def is_vertical(self):
        (mink, maxk), (minu, maxu) = self.minmax()
        return maxk - mink < 2

    def u_at_k(self, k):
        pp, cp = self.start_point, self.end_point
        if (pp.center_k <= k and k <= cp.center_k) or (pp.center_k >= k and k >= cp.center_k):
            return data_util.get_value_on_line(k, pp.center_u, cp.center_u, pp.center_k, cp.center_k)
        return None

    def k_at_u(self, u):
        pp, cp = self.start_point, self.end_point
        if (pp.center_u <= u and u <= cp.center_u) or (pp.center_u >= u and u >= cp.center_u):
            return data_util.get_value_on_line(u, pp.center_k, cp.center_k, pp.center_u, cp.center_u)
        return None

    def slope(self):
        """
        :rtype: float
        """
        return self.line_func()[0]

    def line_func(self):
        """
        :rtype: (float, float)
        """
        pr, cr = self.start_point, self.end_point
        pck, pcu, cck, ccu = pr.center_k, pr.center_u, cr.center_k, cr.center_u
        a = (ccu - pcu) / (cck - pck)
        b = -a * pck + pcu
        return (a, b)

    def minmax(self):
        """

        :rtype: ((float, float), (float, float))
        """
        ks = [self.start_point.center_k, self.end_point.center_k]
        us = [self.start_point.center_u, self.end_point.center_u]

        return (min(ks), max(ks)), (min(us), max(us))

    def contain_nighttime(self):
        return self.start_point.in_nighttime or self.end_point.in_nighttime

    def __repr__(self):
        return (
            '<UKTrajectoryEdge idx=%d group=%d points=(%d-%d) interval=(%d-%d) points=[(%.1f, %.1f), (%.1f, %.1f)] tag="%s" is_recovery=%s>'
            % (
            self.idx, self.group, self.start_point.idx, self.end_point.idx, self.start_point.sidx, self.end_point.eidx,
            self.start_point.center_k, self.start_point.center_u, self.end_point.center_k, self.end_point.center_u,
            self.tag, self.is_recovery))

    def __str__(self):
        return self.__repr__()


class UKTrajectoryGroup(object):
    def __init__(self, idx, edges, tag=None, is_fixed=False):
        """

        :type idx: int
        :type edges: list[UKTrajectoryEdge]
        :type tag: str
        :type is_fixed: bool
        """
        self.idx = idx
        self.edges = edges
        self.is_recovery = (edges[0].start_point.center_u < edges[-1].end_point.center_u)
        self.tag = tag
        self.is_fixed = is_fixed
        for _e in self.edges:
            _e.tag = tag
            _e.is_fixed = is_fixed

    def get_points(self):
        """
        :rtype: list[UKTrajectoryPoint]
        """
        points = []
        for edge in self.edges:
            points.append(edge.start_point)
        points.append(self.edges[-1].end_point)
        return points

    def get_all_ksus(self):
        """
        :rtype: (numpy.ndarray, numpy.ndarray)
        """
        ks, us = [], []
        edata = self.edges[0].start_point.edata
        sidx, eidx = self.edges[0].start_point.sidx, self.edges[-1].end_point.eidx
        return edata.ks[sidx:eidx], edata.us[sidx:eidx]

    def minmax(self):
        """
        :rtype: ((float, float), (float, float))
        """
        minks, maxks, minus, maxus = [], [], [], []
        for _e in self.edges:
            (mink, maxk), (minu, maxu) = _e.minmax()
            minks.append(mink)
            maxks.append(maxk)
            minus.append(minu)
            maxus.append(maxu)
        return (min(minks), max(maxks)), (min(minus), max(maxus))

    def u_at_k(self, k, method='avg'):
        us = []
        for _e in self.edges:
            _u = _e.u_at_k(k)
            if _u is not None:
                us.append(_u)
        if us:
            if method == 'avg':
                return np.mean(us)
            elif method == 'min':
                return min(us)
            elif method == 'max':
                return max(us)
        else:
            return None

    def k_at_u(self, u, method='avg'):
        ks = []
        for _e in self.edges:
            _k = _e.k_at_u(u)
            if _k is not None:
                ks.append(_k)
        if ks:
            if method == 'avg':
                return np.mean(ks)
            elif method == 'min':
                return min(ks)
            elif method == 'max':
                return max(ks)
        else:
            return None

    def contain_nighttime(self):
        """

        :rtype: bool
        """
        for _e in self.edges:
            if _e.contain_nighttime():
                return True
        return False

    def __repr__(self):
        return (
            '<UKTrajectoryGroup idx=%d edges=(%d, %d) points=(%d-%d) interval=(%d-%d) tag="%s">'
            % (self.idx, self.edges[0].idx, self.edges[-1].idx,
               self.edges[0].start_point.idx, self.edges[-1].end_point.idx,
               self.edges[0].start_point.sidx, self.edges[-1].end_point.eidx,
               self.tag
               ))

    def __str__(self):
        return self.__repr__()
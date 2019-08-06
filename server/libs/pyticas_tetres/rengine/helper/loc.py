# -*- coding: utf-8 -*-

import sys

from pyticas import route
from pyticas.logger import getLogger
from pyticas.rn import geo
from pyticas.tool import distance as distutil
from pyticas_tetres.ttypes import LOC_TYPE

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

def location(host, guest):
    """

    :type host: pyticas.ttypes.Route
    :type guest: pyticas.ttypes.Route
    :rtype: (pyticas_tetres.ttypes.LOC_TYPE, float, float)
    """

    logger = getLogger(__name__)

    s1 = host.rnodes[0]
    e1 = host.rnodes[-1]
    s2 = guest.rnodes[0]
    e2 = guest.rnodes[-1]

    # distance map from the most upstream of corridor
    # for a route through multiple corridor
    corrs1 = route.corridors(host)
    corrs2 = route.corridors(guest)
    corrs = corrs1 if len(corrs1) >= len(corrs2) else corrs2
    mmap = {}
    last_mp = 0
    for corr in corrs:
        t_mmap = geo.get_mile_point_map(corr.rnodes)
        for rn_name, mp in t_mmap.items():
            t_mmap[rn_name] = mp + last_mp
        last_mp = t_mmap[corr.rnodes[-1].name]
        mmap.update(t_mmap)

    s1mp = mmap.get(s1.name, None)
    e1mp = mmap.get(e1.name, None)
    s2mp = mmap.get(s2.name, None)
    e2mp = mmap.get(e2.name, None)

    if None in [s1mp, e1mp, s2mp, e2mp]:
        #logger.warn('Could not make distance map for %s and %s' % (host, guest))
        return (None, None, None)

    distance = s1mp - s2mp

    if s1mp >= e2mp:
        return (LOC_TYPE.UP, distance, e2mp-s1mp)

    if e1mp <= s2mp:
        return (LOC_TYPE.DOWN, distance, s2mp - e1mp)

    if s1mp <= s2mp and e1mp >= e2mp:
        return (LOC_TYPE.INSIDE, distance, 0)

    if s1mp >= s2mp and e1mp <= e2mp:
        return (LOC_TYPE.WRAP, distance, 0)

    if s1mp >= s2mp and e1mp >= e2mp and s1mp <= e2mp:
        return (LOC_TYPE.UP_OVERLAPPED, distance, 0)

    if s1mp <= s2mp and e1mp <= e2mp and e1mp >= s2mp:
        return (LOC_TYPE.DOWN_OVERLAPPED, distance, 0)


    logger.warn('Could not decide location type for %s and %s' % (host, guest))

    return (None, None, None)


def location_by_coordinate(r, lat, lon):
    """ calculate distance from the most upstream rnode to the given coordinates

    **Limitation :**
    it supports calculation of the location on the same corridor
    which the most upstream rnode belongs

    :type r: pyticas.ttypes.Route
    :type lat: float
    :type lon: lon
    :rtype: float
    """
    upstream_rnode = r.rnodes[0]
    corr = upstream_rnode.corridor
    (upnode, dnnode) = geo.find_updown_rnodes(lat, lon, corr.rnodes, d_limit=1)
    if not upnode:
        return False

    f_done = False

    # check to downstream
    dist = distutil.distance_in_mile_with_coordinate(upnode.lat, upnode.lon, lat, lon)
    cur_node = upstream_rnode
    for next_node in geo.iter_to_downstream(upstream_rnode):
        dist += distutil.distance_in_mile(cur_node, next_node)
        if upnode == next_node:
            f_done = True
            break
        cur_node = next_node

    if not f_done:
        # check to upstream
        dist = distutil.distance_in_mile_with_coordinate(dnnode.lat, dnnode.lon, lat, lon)
        cur_node = upstream_rnode
        for next_node in geo.iter_to_upstream(upstream_rnode):
            dist += distutil.distance_in_mile(cur_node, next_node)
            if dnnode == next_node:
                f_done = True
                break
            cur_node = next_node
        if f_done:
            dist = -1 * dist

    if f_done:
        return dist
    else:
        return False



def minimum_distance(r, lat, lon):
    """

    :type r: pyticas.ttypes.Route
    :type lat: float
    :type lon: lon
    :rtype: float
    """
    min_distance = sys.maxsize
    for rn in r.rnodes:
        d = distutil.distance_in_mile_with_coordinate(rn.lat, rn.lon, lat, lon)
        if d < min_distance:
            min_distance = d
    return min_distance
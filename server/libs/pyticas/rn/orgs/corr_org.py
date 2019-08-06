# -*- coding: utf-8 -*-
import pyticas.tool.distance

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import re
import sys

from pyticas.ttypes import CorridorObject
from pyticas.tool.distance import distance_in_mile_with_coordinate
from pyticas.rn.geo import find_updown_rnodes

def create_corridor(corr, CORRIDOR_CACHE):
    """ create CorridorObject and cache it in memory
    """
    route = corr.get('route')
    direction = corr.get('dir', 'All')
    corrKey = CorridorObject.corr_key(route, direction)
    corrObject = CorridorObject({
        'name' : corrKey,
        'route' : route,
        'dir' : direction, 
        'rnodes' : [],
        'stations' : [],
        'station_rnode' : {},
        'rnode_station' : {},
        'entrances' : [],
        'exits' : [],
        'intersections' : [],     
        'interchanges' : [],
        'accesses' : [],
    })
    CORRIDOR_CACHE[corrKey] = corrObject
    return corrObject

def add_rnode(corr, rnode):
    """ add rnode to CorridorObject according to rnode type
    :type corr: CorridorObject
    :type rnode: pyticas.ttypes.RNodeObject
    """
    corr.rnodes.append(rnode)
    rnode.corridor = corr
    if rnode.is_station():
        corr.stations.append(rnode)
        corr.station_rnode[rnode.station_id ] = rnode
        corr.rnode_station[rnode.name] = rnode
    elif rnode.is_entrance():
        corr.entrances.append(rnode)
    elif rnode.is_exit():
        corr.exits.append(rnode)
    elif rnode.is_intersection():
        corr.intersections.append(rnode)
    elif rnode.is_interchange():
        corr.interchanges.append(rnode)
    elif rnode.is_access():
        corr.accesses.append(rnode)


def remove_rnode(corr, rnode):
    """

    :type corr: CorridorObject
    :type rnode: pyticas.ttypes.RNodeObject
    :return:
    """
    if rnode in corr.rnodes:
        corr.rnodes.remove(rnode)
    if rnode in corr.entrances:
        corr.entrances.remove(rnode)
    if rnode in corr.exits:
        corr.exits.remove(rnode)
    if rnode in corr.intersections:
        corr.intersections.remove(rnode)
    if rnode in corr.interchanges:
        corr.interchanges.remove(rnode)
    if rnode in corr.accesses:
        corr.accesses.remove(rnode)

def find_close_rnode(lat, lon, RNODE_CACHE, **kwargs):
    corridor_name = kwargs.get('cooridor_name', None)
    min_dist = sys.maxsize
    min_rnode = None
    for rnode in RNODE_CACHE.values():
        if corridor_name and corridor_name not in rnode.corridor.name:
            continue
        d = distance_in_mile_with_coordinate(lat, lon, rnode.lat, rnode.lon)
        if d < min_dist:
            min_dist = d
            min_rnode = rnode
    return min_rnode

def add_camera(camObject, corr_name, CORRIDOR_CACHE, RNODE_CACHE):
    """ find corridor having given camObject and link camObject to the station

    :type camObject: pyticas.ttypes.CameraObject
    :type corr_name: str
    :type CORRIDOR_CACHE: dict[str, pyticas.ttypes.CorridorObject]
    :type RNODE_CACHE: dict[str, pyticas.ttypes.RNodeObject]
    :return:
    """

    # retrieve corridor and add dmsObject to dms list of the corridor
    corrObject = CORRIDOR_CACHE.get(corr_name)

    if corrObject == None:
        m = re.search(r'\((.*?)\)', corr_name)
        if m:
            origin_corr_name = corr_name.replace(' {0}'.format(m.group(0)), '')
        else:
            origin_corr_name = corr_name
        close_rnode = find_close_rnode(camObject.lat, camObject.lon, RNODE_CACHE, cooridor_name=origin_corr_name)
        if close_rnode:
            corrObject = CORRIDOR_CACHE.get(close_rnode.corridor.name)
        if not corrObject:
            return
    if corrObject.cameras == None:
        corrObject.cameras = []

    corrObject.cameras.append(camObject)
    camObject.corridor = corrObject

    # make links among dmsObject and stations
    stations = [ st for st in corrObject.stations ]

    if not stations:
        return

    up_node, dn_node = find_updn_stations(camObject.lat, camObject.lon, stations)
    camObject.up_station = up_node
    camObject.down_station = dn_node
    if up_node:
        up_node.down_camera.append(camObject)
    if dn_node:
        dn_node.up_camera.append(camObject)

    # if (not up_node and dn_node) or (up_node and not dn_node):
    #     print('=> ', camObject.name, up_node, dn_node)

def add_dms(dmsObject, corr_name, CORRIDOR_CACHE):
    """ find corridor having given dmsObject and link dmsObject to the station
    """

    # retrieve corridor and add dmsObject to dms list of the corridor
    corrObject = CORRIDOR_CACHE.get(corr_name)
    if corrObject == None:
        return
    if corrObject.dmss == None:
        corrObject.dmss = []

    corrObject.dmss.append(dmsObject)
    dmsObject.corridor = corrObject
    # make links among dmsObject and stations
    stations = [ st for st in corrObject.stations ]

    if not stations:
        return

    up_node, dn_node = find_updn_stations(dmsObject.lat, dmsObject.lon, stations)
    dmsObject.up_station = up_node
    dmsObject.down_station = dn_node
    if up_node:
        up_node.down_dmss.append(dmsObject)
    if dn_node:
        dn_node.up_dmss.append(dmsObject)

    # if (not up_node and dn_node) or (up_node and not dn_node):
    #     print('=> ', dmsObject.name, up_node, dn_node)
    # else:
    #     print('=> ', dmsObject.name, up_node, dn_node)

def link_rnodes(corrObject):
    """ construct geometry link among rnodes
    """
    rnodes = corrObject.rnodes
    nrnodes = len(rnodes)

    def _find_up_node(func, cur_idx):
        for idx in range(cur_idx-1, 0, -1):
            if getattr(rnodes[idx], func)():
                return rnodes[idx]
        return None

    def _find_dn_node(func, cur_idx):
        for idx in range(cur_idx+1, nrnodes):
            if getattr(rnodes[idx], func)():
                return rnodes[idx]
        return None

    for idx in range(nrnodes):
        cur_rnode = rnodes[idx]
        cur_rnode.up_rnode = _find_up_node('is_rnode', idx)
        cur_rnode.up_station = _find_up_node('is_station', idx)
        cur_rnode.up_entrance = _find_up_node('is_entrance', idx)
        cur_rnode.up_exit = _find_up_node('is_exit', idx)
        cur_rnode.down_rnode = _find_dn_node('is_rnode', idx)
        cur_rnode.down_station = _find_dn_node('is_station', idx)
        cur_rnode.down_entrance = _find_dn_node('is_entrance', idx)
        cur_rnode.down_exit = _find_dn_node('is_exit', idx)


def find_updn_stations(lat, lon, rnodes):
    """

    :type lat: float
    :type lon: float
    :type rnodes: list[pyticas.ttypes.RNodeObject]
    :return:
    """
    return find_updown_rnodes(lat, lon, rnodes)

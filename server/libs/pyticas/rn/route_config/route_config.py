# -*- coding: utf-8 -*-
import math

from pyticas.infra import Infra
from pyticas.logger import getDefaultLogger
from pyticas.rn.route_config.const import VIRTUAL_NODE_DISTANCE
from pyticas.tool import distance as distutil
from pyticas.ttypes import RouteConfigNodeSet, RouteConfig

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def create_route_config(rnodes, **kwargs):
    """
    :type rnodes: list[pyticas.ttypes.RNodeObject]
    :rtype: pyticas.ttypes.RouteConfig
    """
    infra_cfg_date = kwargs.get('infra_cfg_date', None)
    infra = kwargs.get('infra', Infra.get_infra(infra_cfg_date))
    (rns, orns) = infra.geo.opposite_rnodes(rnodes)
    rc = RouteConfig()
    rc.infra_cfg_date = infra.cfg_date
    rc.add_nodes(rns, orns)
    organize(rc)
    return rc


def find_nodeset_by_rnode(rc, rnode, direction_n):
    """
    :type rc: pyticas.ttypes.RouteConfig
    :type rnode: pyticas.ttypes.RNodeObject
    :type direction_n: int
    :rtype: RouteConfigNodeSet
    """
    for node_set in rc.node_sets:
        rc_node = getattr(node_set, 'node%d' % direction_n)
        if not rc_node.is_virtual() and rc_node.rnode.name == rnode.name:
            return node_set
    return None


def find_nodeset_by_detector(rc, det, direction_n):
    """
    :type rc: pyticas.ttypes.RouteConfig
    :type det: pyticas.ttypes.DetectorObject
    :type direction_n: int
    :rtype: RouteConfigNodeSet
    """
    for node_set in rc.node_sets:
        rc_node = getattr(node_set, 'node%d' % direction_n)
        if not rc_node.is_virtual() and det.name in [ d.name for d in rc_node.rnode.detectors ]:
            return node_set
    return None


def remove_virtual_nodesets(rc):
    """
    :type rc: pyticas.ttypes.RouteConfig
    """
    for vnode in [node_set for node_set in rc.node_sets if node_set.is_virtual()]:
        rc.node_sets.remove(vnode)


def get_rc_nodes(rc, n_direction):
    """
    :type rc: RouteConfig
    :type n_direction: int
    :return:
    """
    return [getattr(node_set, "node{}".format(n_direction), None) for node_set in rc.node_sets]


def get_max_lanes(rc, n_direction):
    """
    :type rc: RouteConfig
    :type n_direction: int
    :return:
    """
    return max([node.lanes for node in get_rc_nodes(rc, n_direction)])


def get_max_mile_point(rc):
    """
    :type rc: RouteConfig
    :return:
    """
    return max(rc.node_sets[-1].mile_point, rc.node_sets[0].mile_point)


def organize(rc):
    """
    :type rc: RouteConfig
    :rtype: RouteConfig
    """
    if [node_set for node_set in rc.node_sets if node_set.node1.is_virtual() and node_set.node2.is_virtual()]:
        # already organized
        return rc

    _set_lane_types(rc.node_sets)

    new_nodesets = []
    acc_distance = 0
    (up_corr1, dn_corr1, up_corr2, dn_corr2) = (None, None, None, None)

    def _dn_corridor(start_idx, node_index):
        for ridx in range(start_idx+1, len(rc.node_sets)):
            node = getattr(rc.node_sets[ridx], 'node%d' % node_index, None)
            if node and node.rnode:
                return node.rnode.corridor
        return None

    def _up_corridor(start_idx, node_index):
        for ridx in range(start_idx-1, 0, -1):
            node = getattr(rc.node_sets[ridx], 'node%d' % node_index, None)
            if node and node.rnode:
                return node.rnode.corridor
        return None


    for ridx in range(len(rc.node_sets) - 1):

        up_nodeset = rc.node_sets[ridx]
        dn_nodeset = rc.node_sets[ridx + 1]

        # calculate distance and mile point
        d = _calc_distance(up_nodeset, dn_nodeset)
        acc_distance += d
        mile_point = round(acc_distance, 1)
        dn_nodeset.mile_point = mile_point
        dn_nodeset.acc_distance = acc_distance
        new_nodesets.append(up_nodeset)

        # prepare lane info
        up_lanes1 = _up_lanes(rc.node_sets, ridx, 1)
        up_lanes2 = _up_lanes(rc.node_sets, ridx, 2)
        dn_lanes1 = _dn_lanes(rc.node_sets, ridx + 1, 1)
        dn_lanes2 = _dn_lanes(rc.node_sets, ridx + 1, 2)

        up_lanes1 = up_lanes1 or dn_lanes1
        up_lanes2 = up_lanes2 or dn_lanes2
        dn_lanes1 = dn_lanes1 or up_lanes1
        dn_lanes2 = dn_lanes2 or up_lanes2

        # prepare corridor info
        up_corr1 = _up_corridor(ridx, 1)
        dn_corr1 = _dn_corridor(ridx, 1)
        up_corr1 = up_corr1 or dn_corr1
        dn_corr1 = dn_corr1 or up_corr1

        up_corr2 = _up_corridor(ridx, 2)
        dn_corr2 = _dn_corridor(ridx, 2)
        up_corr2 = up_corr2 or dn_corr2
        dn_corr2 = dn_corr2 or up_corr2

        # set corridor to `RouteConfigNode` that does not have corridor value (in case of rnode == None)
        if not up_nodeset.node2.corridor:
            up_nodeset.node2.corridor = up_corr2
        if not dn_nodeset.node2.corridor:
            dn_nodeset.node2.corridor = dn_corr2
        if not up_nodeset.node1.corridor:
            up_nodeset.node1.corridor = up_corr1
        if not dn_nodeset.node1.corridor:
            dn_nodeset.node1.corridor = dn_corr1

        # add virtual node
        n_v = round(dn_nodeset.mile_point - up_nodeset.mile_point - VIRTUAL_NODE_DISTANCE, 1)
        n_13 = int(math.floor(n_v / 3.0 * 10)) if n_v >= 0.3 else 0
        n_2 = int((n_v * 10.0) - 2 * n_13)

        (vmp, vad) = _add_vnode(new_nodesets, n_13, up_nodeset.mile_point, acc_distance, up_lanes1, up_lanes2,
                                up_nodeset,
                                up_corr1, up_corr2)
        (vmp, vad) = _add_vnode(new_nodesets, n_2, vmp, vad, up_lanes1, up_lanes2, up_nodeset, up_corr1, up_corr2)
        (vmp, vad) = _add_vnode(new_nodesets, n_13, vmp, vad, dn_lanes1, dn_lanes2, dn_nodeset, dn_corr1, dn_corr2)

    new_nodesets.append(rc.node_sets[-1])

    rc.node_sets = new_nodesets
    return rc


def reverse(rc):
    """
    :type rc: RouteConfig
    :rtype: RouteConfig
    """
    max_mp = get_max_mile_point(rc)
    for node in rc.node_sets:
        node.mile_point = round(max_mp - node.mile_point, 1)
        node.node2, node.node1 = node.node1, node.node2
    rc.node_sets.reverse()
    return rc


def print_rc(rc):
    """
    :type rc: RouteConfig
    :return:
    """
    logger = getDefaultLogger(__name__)
    logger.debug("*" * 10)
    logger.debug("RouteConfig")
    for idx, node_set in enumerate(rc.node_sets):
        logger.debug('%2d > %2.1f > %s' % (idx, node_set.mile_point, _node_to_str(node_set)))
    logger.debug("*" * 10)


def _add_vnode(new_data, n, mp, ad, lanes1, lanes2, data_node, corr1, corr2):
    """
    :type new_data: list[RouteConfigNode]
    :type n: int
    :type mp: float
    :type ad: float
    :type lanes1: int
    :type lanes2: int
    :type data_node: RouteConfigNodeSet
    :type corr1: pyticas.ttypes.CorridorObject
    :type corr2: pyticas.ttypes.CorridorObject
    :return:
    """
    for idx in range(n):
        mile_point = round(mp + (0.1 * (idx + 1)), 1)
        acc_distance = ad + (0.1 * (idx + 1))
        vnode = RouteConfigNodeSet(None, None, mp=mile_point, ad=acc_distance, ln1=lanes1, ln2=lanes2)
        vnode.node1.node_config = data_node.node1.node_config.clone()
        vnode.node2.node_config = data_node.node2.node_config.clone()
        vnode.node1.node_config.ramp_opened = 0
        vnode.node2.node_config.ramp_opened = 0
        vnode.node1.corridor = corr1
        vnode.node2.corridor = corr2
        new_data.append(vnode)
    return mp + (0.1 * n), ad + (0.1 * n)


def _up_lanes(node_sets, uidx, rn):
    """
    :type node_sets: list[RouteConfigNodeSet]
    :type uidx: int
    :type rn: int
    :rtype: int
    """
    for tidx in range(uidx, -1, -1):
        rc_node = getattr(node_sets[tidx], 'node{}'.format(rn))
        if rc_node.lanes:
            return rc_node.lanes
        if rc_node.is_station():
            return rc_node.rnode.lanes
    return None


def _dn_lanes(node_sets, didx, rn):
    """
    :type node_sets: list[RouteConfigNodeSet]
    :type didx: int
    :type rn: int
    :rtype: int
    """
    for tidx in range(didx, len(node_sets)):
        rc_node = getattr(node_sets[tidx], 'node{}'.format(rn))
        if rc_node.lanes:
            return rc_node.lanes
        if rc_node.is_station():
            return rc_node.rnode.lanes
    return None


def _dtype(det):
    """
    :type det: pyticas.ttypes.DetectorObject
    :return:
    """
    if det.is_auxiliary_lane():
        return 'A'
    elif det.is_shoulder_lane():
        return 'S'
    elif det.is_HOVT_lane():
        return 'H'
    return ''


def _nearby_station(node_sets, nidx, rn):
    """
    :type node_sets: list[RouteConfigNodeSet]
    :type nidx: int
    :type rn: int
    :rtype: pyticas.ttypes.RNodeObject
    """
    min_dist = 99999
    min_st = None
    target_rc_node = getattr(node_sets[nidx], 'node{}'.format(rn))
    if not target_rc_node.rnode:
        target_rc_node = getattr(node_sets[nidx], 'node{}'.format(1 if rn == 2 else 2))
    for idx, node_set in enumerate(node_sets):
        rc_node = getattr(node_set, 'node{}'.format(rn))
        if rc_node.is_station():
            dist = distutil.distance_in_mile(rc_node.rnode, target_rc_node.rnode)
            if dist < min_dist:
                min_dist = dist
                min_st = rc_node.rnode
    return min_st


def _lane_types(rnode):
    """
    :type rnode: pyticas.ttypes.RNodeObject
    :rtype: list[str]
    """
    types = {}
    for det in rnode.detectors:
        if det.lane not in types or not types[det.lane]:
            types[det.lane] = _dtype(det)
    return list(types.values())


def _set_lane_types(node_sets):
    """
    :type node_sets: list[RouteConfigNodeSet]
    """
    for nidx, rc_node in enumerate(node_sets):
        if rc_node.node1.is_station():
            rc_node.node1.node_config.lane_types = _lane_types(rc_node.node1.rnode)
        else:
            near_station = _nearby_station(node_sets, nidx, 1)
            rc_node.node1.node_config.lane_types = _lane_types(near_station)
        rc_node.node1.lanes = len(rc_node.node1.node_config.lane_types)

        if rc_node.node2.is_station():
            rc_node.node2.node_config.lane_types = _lane_types(rc_node.node2.rnode)
        else:
            near_station = _nearby_station(node_sets, nidx, 2)
            rc_node.node2.node_config.lane_types = _lane_types(near_station)
        rc_node.node2.lanes = len(rc_node.node2.node_config.lane_types)


def _calc_distance(up_nodeset, dn_nodeset):
    """
    :type up_nodeset: RouteConfigNodeSet
    :type dn_nodeset: RouteConfigNodeSet
    """
    median_width = 0.015
    # <--?--?--  (direction 2)
    # ---S--S--> (direction 1)
    if up_nodeset.node1.rnode and dn_nodeset.node1.rnode:
        return distutil.distance_in_mile(up_nodeset.node1.rnode, dn_nodeset.node1.rnode)
    # <--S--S--  (direction 2)
    # ---?X--X?--> (direction 1)
    elif up_nodeset.node2.rnode and dn_nodeset.node2.rnode:
        return distutil.distance_in_mile(up_nodeset.node2.rnode, dn_nodeset.node2.rnode)
    # <--S--X--  (direction 2)
    # ---X--S--> (direction 1)
    elif up_nodeset.node2.rnode and dn_nodeset.node1.rnode:
        d_tmp = distutil.distance_in_mile(up_nodeset.node2.rnode, dn_nodeset.node1.rnode)
        return math.sqrt(math.pow(d_tmp, 2) - math.pow(median_width, 2))
    # <--X--S--  (direction 2)
    # ---S--X--> (direction 1)
    elif up_nodeset.node1.rnode and dn_nodeset.node2.rnode:
        d_tmp = distutil.distance_in_mile(up_nodeset.node1.rnode, dn_nodeset.node2.rnode)
        return math.sqrt(math.pow(d_tmp, 2) - math.pow(median_width, 2))


def _node_to_str(node_set):
    """
    :type node_set: RouteConfigNodeSet
    """

    def _s(rc_node):
        """
        :type rc_node: pyticas.ttypes.RouteConfigNode
        :rtype: str
        """
        rnode = rc_node.rnode
        if not rnode:
            return 'NONE (%s)' % (rc_node.corridor.name if rc_node.corridor else 'None')

        if rnode.is_station():
            return '%15s (%10s, %d, %d)' % (
                rnode.station_id, rnode.name, node_set.node1.lanes, len(node_set.node1.node_config.lane_types))
        elif rnode.is_entrance():
            return '%15s (%10s, %d, %d)' % (
                'E:' + rnode.label, rnode.name, node_set.node1.lanes, len(node_set.node1.node_config.lane_types))
        elif rnode.is_exit():
            return '%15s (%10s, %d, %d)' % (
                'X:' + rnode.label, rnode.name, node_set.node1.lanes, len(node_set.node1.node_config.lane_types))
        return 'NONE'

    return _s(node_set.node1) + ' | ' + _s(node_set.node2)

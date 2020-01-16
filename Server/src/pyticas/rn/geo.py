# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.logger import getDefaultLogger
from pyticas.tool import distance as distutil
import math
from collections import namedtuple

def iter_to_downstream(rn, filter=None, break_filter=None, break_after_filter=None):
    """ Yield `RNodeObject` from `rn.down_rnode` to the most downstream of the corridor

    Note:
        start and end rnodes will be included

    Arguments:
        * filter: return if `RNodeObject` is passed by `filter`
        * break_filter: break iteration if `RNodeObject` is passed by `break_filter`

    :type rn: pyticas.ttypes.RNodeObject
    :type filter: function
    :type break_filter: function
    :yield: pyticas.ttypes.RNodeObject
    """
    to_be_breaked = False
    cur_node = rn
    while cur_node.down_rnode:
        cur_node = cur_node.down_rnode
        if break_filter and break_filter(cur_node):
            break
        if to_be_breaked:
            break
        if break_after_filter and break_after_filter(cur_node):
            to_be_breaked = True
        if not filter or filter(cur_node):
            yield cur_node


def iter_to_upstream(rn, filter=None, break_filter=None, break_after_filter=None):
    """ Yield `RNodeObject` from `rn.up_rnode` to the most upstream of the corridor

    Note:
        start and end rnodes will be included

    Arguments:
        * filter: return if `RNodeObject` is passed by `filter`
        * break_filter: break iteration if `RNodeObject` is passed by `break_filter`

    :type rn: pyticas.ttypes.RNodeObject
    :type filter: function
    :type break_filter: function
    :yield: pyticas.ttypes.RNodeObject
    """
    to_be_breaked = False
    cur_node = rn
    while cur_node.up_rnode:
        cur_node = cur_node.up_rnode
        if break_filter and break_filter(cur_node):
            break
        if to_be_breaked:
            break
        if break_after_filter and break_after_filter(cur_node):
            to_be_breaked = True
        if not filter or filter(cur_node):
            yield cur_node

def get_length(rnodes):
    """ returns length of the given section

    :type rnodes: list[pyticas.ttypes.RNodeObject]
    :rtype: float
    """
    return [ miles for ridx, rn, miles in get_mile_points(rnodes) ][-1]

def get_mile_points(rnodes):
    """ returns index, rnode object and mile point

    :type rnodes: list[pyticas.ttypes.RNodeObject]
    :rtype: collections.Iterable[int, pyticas.ttypes.RNodeObject, float]
    """
    def _calculate_epsilon(v):
        if v != 0:
            return v * 0.0000001
        else:
            return 0.0000001

    miles = 0.0
    prevRn = None
    n_points_keys = {}
    for ridx, rn in enumerate(rnodes):
        if prevRn != None:
            m = distutil.distance_in_mile(prevRn, rn)
            miles += m
        while (str(miles) in n_points_keys.keys()):
            miles += _calculate_epsilon(miles)
        n_points_keys[str(miles)] = rn.name
        prevRn = rn
        yield ridx, rn, miles

def get_mile_point_map(rnodes):
    """ return mile point map as dict[rnode_name, mile_point]

    :type rnodes: list[pyticas.ttypes.RNodeObject]
    :return: dict[RNodeObject.name, mile point]
    :rtype: dict[str, float]
    """
    mile_points_map = {}
    for idx, rnode, miles in get_mile_points(rnodes):
        mile_points_map[rnode.name] = miles
    return mile_points_map

def between_rnodes(rn1, rn2):
    """ Return rnode list between the given two rnodes except `rn1` and `rn2`

    :type rn1: pyticas.ttypes.RNodeObject
    :type rn2: pyticas.ttypes.RNodeObject
    :rtype: list[pyticas.ttypes.RNodeObject]
    """
    rnodes = []
    cur_rnode = rn1
    f_end = False
    while True:
        drn = cur_rnode.down_rnode
        if not drn:
            break
        cur_rnode = drn

        if cur_rnode.name == rn2.name:
            f_end = True
            break

        if cur_rnode.n_type and not (cur_rnode.is_station() and not cur_rnode.detectors):
            rnodes.append(cur_rnode)

    if not f_end: return []

    return rnodes

def ordered_by_distance(rnode, rnode_list, **kwargs):
    """ Return list of `RNodeObject` and distance to the given `rnode`

    :type rnode: pyticas.ttypes.RNodeObject
    :type rnode_list: list[pyticas.ttypes.RNodeObject]
    :return: list[(RNodeObject, DistanceInMile)]
    :rtype: list[(pyticas.ttypes.RNodeObject, float)]
    """
    logger = getDefaultLogger(__name__)
    d_limit = kwargs.get('d_limit', None)
    dists = {}
    # logger.debug('ordered_by_distance(): make rnode and distance list : target_rnode=%s, d_limit=%s' %
    #               (str([rnode.station_id, rnode.name, rnode.label, rnode.n_type]), str(d_limit)))

    for rn in rnode_list:
        if ((rn.is_station() and not rn.detectors) or
                (not rn.is_ramp() and not rn.station_id) or
                not rn.n_type):
            continue
        d = distutil.distance_in_mile(rnode, rn)
        # logger.debug('ordered_by_distance(): distance to %s = %f' % ( str([rn.station_id, rn.name, rn.label, rn.n_type]), d))
        if d_limit and d > d_limit:
            continue
        dists[d] = rn
    if dists:
        return [(dists[d], d) for d in sorted(dists)]
    else:
        return None

def nearby_rnode(lat, lon, rnodes, d_limit=1):
    """

    :type lat: float
    :type lon: float
    :type rnodes: list[pyticas.ttypes.RNodeObject]
    :type d_limit: float
    :rtype: pyticas.ttypes.RNodeObject, float
    """
    min_dist = 999999
    min_dist_rnode = None
    for rn in rnodes:
        d = distutil.distance_in_mile_with_coordinate(lat, lon, rn.lat, rn.lon)
        if d < min_dist and d <= d_limit:
            min_dist = d
            min_dist_rnode = rn
    return min_dist_rnode, min_dist


def find_updown_rnodes(lat, lon, rnodes, d_limit=1):
    """

    :type lat: float
    :type lon: float
    :type rnodes: list[pyticas.ttypes.RNodeObject]
    :type d_limit: float
    :rtype: (pyticas.ttypes.RNodeObject, pyticas.ttypes.RNodeObject)
    """
    nb_node, nb_dist = nearby_rnode(lat, lon, rnodes, d_limit)
    if not nb_node:
        return None, None

    if len(rnodes) < 2:
        return None, None

    nb_index = rnodes.index(nb_node)
    if nb_index > 0:
        ref_node = rnodes[nb_index-1]
    else:
        ref_node = rnodes[nb_index+1]


    Point = namedtuple('Point', ['x', 'y'])

    # find algle 'p0 -> p1 -> p2'
    p0 = Point(x=lat, y=lon)
    p1 = Point(x=nb_node.lat, y=nb_node.lon)
    p2 = Point(x=ref_node.lat, y=ref_node.lon)
    a = (p1.x - p0.x)**2 + (p1.y - p0.y)**2
    b = (p1.x - p2.x)**2 + (p1.y - p2.y)**2
    c = (p2.x - p0.x)**2 + (p2.y - p0.y)**2
    angle = math.acos((a+b-c) / math.sqrt(4*a*b)) * (180 / math.pi)

    if nb_index > 0:
        if angle <= 90:
            return ref_node, nb_node
        else:
            return nb_node, rnodes[nb_index+1] if nb_index < len(rnodes)-1 else None
    else:
        if angle <= 90:
            return nb_node, ref_node
        else:
            return None, nb_node


def angle_of_rnodes(rn1, rn2, rn3):
    """ Retuern angle of (rn1rn2 and rn2rn3)
    
    :type rn1: pyticas.ttypes.RNodeObject
    :type rn2: pyticas.ttypes.RNodeObject
    :type rn3: pyticas.ttypes.RNodeObject
    :rtype: float 
    """
    return _calculate_angle((rn1.lat, rn1.lon), (rn2.lat, rn2.lon), (rn3.lat, rn3.lon))


def _calculate_angle(p0, p1, p2):
    """ Retuern angle of (p0p1 and p1p2)
    
    :type p0: (float, float) 
    :type p1: (float, float)
    :type p2: (float, float)
    :rtype: float 
    """
    a = (p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2
    b = (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2
    c = (p2[0] - p0[0]) ** 2 + (p2[1] - p0[1]) ** 2
    return math.acos((a + b - c) / math.sqrt(4 * a * b)) * 180 / math.pi


class Geo(object):

    def __init__(self, infra):
        """
        :type infra: pyticas.infra.Infra
        """
        self.infra = infra

    def nearby_rnode(self, lat, lon, rnodes, d_limit=1):
        """

        :type lat: float
        :type lon: float
        :type rnodes: list[pyticas.ttypes.RNodeObject]
        :type d_limit: float
        :rtype: pyticas.ttypes.RNodeObject, float
        """
        return nearby_rnode(lat, lon, rnodes, d_limit)

    def find_updown_rnodes(self, lat, lon, rnodes, d_limit=1):
        """

        :type lat: float
        :type lon: float
        :type rnodes: list[pyticas.ttypes.RNodeObject]
        :type d_limit: float
        :rtype: (pyticas.ttypes.RNodeObject, pyticas.ttypes.RNodeObject)
        """
        return find_updown_rnodes(lat, lon, rnodes, d_limit)


    def update_corridor_connections(self):
        d_limit = 1

        for corr in self.infra.corridors.values():
            if corr.is_CD() or not corr.dir:
                continue
            for target_corr in self.infra.corridors.values():

                if (corr == target_corr or
                    target_corr.is_CD() or
                    target_corr == self.find_opposite_corridor(corr.name)):
                    continue

                conns = {}

                for idx, ext in enumerate(corr.exits):

                    connected = self.infra.get_rnode(ext.forks[0]) if ext.forks else None

                    if connected and not connected.is_entrance():
                        continue

                    # directly connected according to `metro_config.xml`
                    if connected and connected.corridor.name == target_corr.name:
                        conns[1] = (ext, connected)
                        break

                    # ext is connected to `CD` corridor
                    elif connected and connected.is_CD_entrance():
                        # logger.debug('find_exit_to(): try to find exit from CD')
                        (cd_exit, cd_ent) = self._exit_from_CD(connected, target_corr, d_limit=d_limit)
                        if cd_ent:
                            conns[2] = (ext, cd_ent)
                    else:
                        # try to check it is connected (not connected by `metro_config.xml`)
                        connected = self.is_estimated_exit_connected_to(ext, target_corr)
                        if connected:
                            conns[3] = (ext, connected)

                if conns:
                    key = sorted(conns.keys())[0]
                    (ext, ent) = conns[key]
                    ext.connected_to[ent.corridor.name] = ent
                    ent.connected_from[ext.corridor.name] = ext


    def find_opposite_corridor(self, corridor_name, **kwargs):
        """ Return opposite direction corridor of the given corridor

        Example:
            >>> corr = find_opposite_corridor('I-35E NB')
            >>> print(corr.name)
            I-35E SB
            >>>

        :type corridor_name: str
        :rtype: pyticas.ttypes.CorridorObject
        """
        corr = self.infra.get_corridor_by_name(corridor_name)
        opps = {'EB': 'WB',
                'WB': 'EB',
                'NB': 'SB',
                'SB': 'NB'}
        opposing_dir = opps.get(corr.dir, None)
        if not opposing_dir:
            return None

        return self.infra.get_corridor(corr.route, opposing_dir)

    def find_nearby_opposite_rnodes(self, rnode, **kwargs):
        """ Return rnode list with distance in mile located in opposite direction corridor

            Note:
                The list is ordered by distance in ASC

            **Optional parameters**

            * n_type : find rnodes by the given n_type
                - 'RNode' for stations, entrances and exits
                - 'Station' for only stations
                - 'Entrance' for only entrances
                - 'Exit' for only exits
                - 'Camera' for only camera
                - 'DMS' for only DMS
            * d_limit : find rnodes that are within the given distance limit

            **Example**
            ::
                >>> rns = find_nearby_opposite_rnodes('S40', n_type='Station', d_limit=0.5)
                >>> for (rn, dist) in rns:
                ...     print(rn.corridor.name, rn.station_id, rn.name, dist)
                I-35W (SB) S27 rnd_88025 0.17125980644973224
                I-35W (SB) S1606 rnd_95760 0.31665272907751346
                >>>

        :type rnode: pyticas.ttypes.RNodeObject
        :return: list[(NearbyStationInOppositeDirection, DistanceInMile)]
        :rtype: list[(pyticas.ttypes.RNodeObject, float)]
        """
        target_type = kwargs.get('n_type', 'Station')
        attr_name = {'Station': 'stations',
                     'Entrance': 'entrances',
                     'Exit': 'exits',
                     'RNode': 'rnodes',
                     'Camera': 'cameras',
                     'DMS': 'dmss'}
        if not attr_name.get(target_type, None):
            return None
        opposite_corridor = self.find_opposite_corridor(rnode.corridor.name)
        dists = self.ordered_by_distance(rnode, getattr(opposite_corridor, attr_name[target_type]), **kwargs)
        return dists


    def opposite_rnodes(self, rnodes, **kwargs):
        """ Return two list that one is rnode list and the other is opposite-direction rnode list

        Note:
            each rnode list can contain `None` if there is no opposite-direction rnode within `d_limit`

        :type rnodes: list[pyticas.ttypes.RNodeObject]
        :rtype: (list[pyticas.ttypes.RNodeObject], list[pyticas.ttypes.RNodeObject])
        """
        logger = getDefaultLogger(__name__)
        # logger.debug('opposite_rnodes(): make rnode list of the current corridor and the opposite direction')
        d_limit = kwargs.get('d_limit', 0.1)
        d_limit2 = kwargs.get('d_limit2', 0.05)
        n_type = kwargs.get('n_type', 'RNode')

        # find rnodes in the opposite direction within d_limit
        prev_corr = None
        segments = []
        sub_seg = None
        for ridx, rn in enumerate(rnodes):
            if rn.corridor != prev_corr:
                sub_seg = []
                segments.append(sub_seg)
            sub_seg.append(rn)
            prev_corr = rn.corridor

        orns = []
        for seg in segments:
            orn_s = orn_e = None
            for ridx, rn in enumerate(seg):
                nearbys = self.find_nearby_opposite_rnodes(rn, n_type=n_type, d_limit=d_limit)
                if not nearbys or not nearbys[0]:
                    continue
                if not orn_s:
                    orn_s = nearbys[0][0]

                if nearbys[0][1] < d_limit2:
                    orn_e = nearbys[0][0]

            # rnode list in the opposite direction
            seg_orns = ([orn_s]
                        + [rn for rn in self.iter_to_upstream(orn_s,
                                                         lambda rn: rn.is_ramp() or (rn.station_id and rn.detectors),
                                                         lambda rn: rn.name == orn_e.name)]
                        + [orn_e])

            orns.extend(seg_orns)

        # logger.debug('opposite_rnodes(): rnodes ---')
        # for rn in rnodes:
        #     logger.debug('opposite_rnodes():   ' + str([rn.n_type, rn.station_id, rn.name, rn.label]))
        #
        # logger.debug('opposite_rnodes(): opposite rnodes ---')
        # for rn in orns:
        #     logger.debug('opposite_rnodes():   ' + str([rn.n_type, rn.station_id, rn.name, rn.label]))

        def _nearby(trn, orns):
            """ Return rnode and distance with minimum distance to `trn`

            :type trn: pyticas.ttypes.RNodeObject
            :type orns: list[pyticas.ttypes.RNodeObject]
            :rtype: (RNodeObject, float)
            """
            min_dist = 9999
            min_rn = None
            for rn in orns:
                d = distutil.distance_in_mile(trn, rn)
                if d < min_dist:
                    min_dist = d
                    min_rn = rn
            if min_dist <= d_limit:
                return min_rn, min_dist
            else:
                return None, None

        n_rnodes = len(rnodes)
        n_orns = len(orns)

        # logger.debug('opposite_rnodes(): find synced points')
        synced = []
        for rn_idx, rn in enumerate(rnodes):
            orn, d_rn = _nearby(rn, orns) if rn else (None, None)
            if orn:
                nearby_orn, d_orn = _nearby(orn, rnodes) if rn else (None, None)
                if rn == nearby_orn:
                    # logger.debug('opposite_rnodes():  synced : %s -- %s' % (str([rn.n_type, rn.station_id, rn.name, rn.label]),
                    #                                      str([orn.n_type, orn.station_id, orn.name, orn.label])))
                    synced.append((rn, orn))

        res = []
        cur_rn_idx = 0
        cur_orn_idx = 0
        for sidx, (rn, orn) in enumerate(synced):
            rn_idx = rnodes.index(rn)
            orn_idx = orns.index(orn)

            # logger.debug(' cur_rn_idx=%d, rn_idx=%d, cur_orn_idx=%d, orn_idx=%d' % (cur_rn_idx, rn_idx, cur_orn_idx, orn_idx))

            should_add_rns = (cur_rn_idx < rn_idx)
            should_add_orns = (cur_orn_idx < orn_idx)

            if should_add_rns and should_add_orns:

                t_rn_idx = cur_rn_idx
                t_orn_idx = cur_orn_idx

                while t_rn_idx < rn_idx and t_orn_idx < orn_idx:
                    d_rn2rn_next = distutil.distance_in_mile(rnodes[t_rn_idx], rnodes[rn_idx]) if t_rn_idx > 0 else 0
                    d_orn2orn_next = distutil.distance_in_mile(orns[t_orn_idx], orns[orn_idx]) if t_orn_idx > 0 else 0
                    if d_rn2rn_next < d_orn2orn_next:
                        res.append([None, orns[t_orn_idx]])
                        t_orn_idx += 1
                    else:
                        res.append([rnodes[t_rn_idx], None])
                        t_rn_idx += 1

                if t_rn_idx < rn_idx:
                    res.extend([[rnodes[idx], None] for idx in range(t_rn_idx, rn_idx)])

                if t_orn_idx < orn_idx:
                    res.extend([[None, orns[idx]] for idx in range(t_orn_idx, orn_idx)])

            elif should_add_rns:
                res.extend([[rnodes[idx], None] for idx in range(cur_rn_idx, rn_idx)])
            elif should_add_orns:
                res.extend([[None, orns[idx]] for idx in range(cur_orn_idx, orn_idx)])

            res.append([rn, orn])
            cur_rn_idx = rn_idx + 1
            cur_orn_idx = orn_idx + 1

        if cur_rn_idx < n_rnodes:
            res.extend([[rnodes[idx], None] for idx in range(cur_rn_idx, n_rnodes)])
        elif cur_orn_idx < n_orns:
            res.extend([[None, orns[idx]] for idx in range(cur_orn_idx, n_orns)])


        fixed = []
        n_res = len(res)
        if n_res > 3:
            sidx = 0
            while sidx < n_res-2:
                rn1, orn1 = res[sidx]
                rn2, orn2 = res[sidx+1]
                rn3, orn3 = res[sidx+2]


                if rn1 == None and orn3 == None:
                    """
                  <---orn1---orn2----x----
                  ----x----rn2-----rn3------>
                  """
                    d = distutil.distance_in_mile(orn1, rn3)
                    if d < 0.15:
                        fixed.append([rn2, orn1])
                        fixed.append([rn3, orn2])
                        sidx += 3
                        continue

                elif orn1 == None and rn3 == None:
                    """
                  <----x----orn2----orn3----
                  ----rn1--rn2------x------>
                  """
                    d = distutil.distance_in_mile(rn1, orn3)
                    if d < 0.15:
                        fixed.append([rn1, orn2])
                        fixed.append([rn2, orn3])
                        sidx += 3
                        continue

                # elif ((rn1 != None and rn1.is_station())
                #       and (not rn2 or not rn2.is_station())
                #       and (not orn1 or not orn1.is_station())
                #       and (orn2 != None and orn2.is_station())):
                #
                #     d = distutil.distance_in_mile(rn2 or rn1, orn1 or orn2)
                #     if d < 0.15:
                #         fixed.append([None, orn1])
                #         fixed.append([rn1, orn2])
                #         fixed.append([rn2, None])
                #         sidx += 3
                #         continue
                #
                # elif ((rn2 != None and rn2.is_station())
                #       and (not rn1 or not rn1.is_station())
                #       and (not orn2 or not orn2.is_station())
                #       and (orn1 != None and orn1.is_station())):
                #
                #     d = distutil.distance_in_mile(rn1 or rn2, orn2 or orn1)
                #     if d < 0.15:
                #         fixed.append([rn1, None])
                #         fixed.append([rn2, orn1])
                #         fixed.append([None, orn2])
                #         sidx += 3
                #         continue

                fixed.append([rn1, orn1])
                sidx += 1

            for tidx in range(sidx, n_res):
                fixed.append(res[tidx])
        else:
            fixed = res

        # fixed = [ (v[0], v[1]) for v in fixed if v[0] and v[1] ]

        return ([r[0] for r in fixed],
                [r[1] for r in fixed])


    def find_exit_to(self, rn, corr, **kwargs):
        """ Return tuple of exit and the connected entrance to the given corridor

        Note:
            iterate from the given `rn` to downstream only

        :type rn: pyticas.ttypes.RNodeObject
        :type corr: pyticas.ttypes.CorridorObject
        :rtype: (pyticas.ttypes.RNodeObject, pyticas.ttypes.RNodeObject)
        """
        logger = getDefaultLogger(__name__)
        # logger.debug('find_exit_to(): find exit to the corridor %s' % corr.name)
        d_limit = kwargs.get('d_limit', 2)
        cur_node = rn

        while cur_node.down_exit:
            cur_node = cur_node.down_exit
            connected_ent = self.is_connected_to(cur_node, corr, d_limit=d_limit)
            if connected_ent:
                return cur_node, connected_ent

        # logger.debug('find_exit_to(): Could not find by regular way....let\'s try something...')
        cur_node = rn
        while cur_node.down_exit:
            cur_node = cur_node.down_exit
            connected_ent = self.is_estimated_exit_connected_to(cur_node, corr, d_limit=d_limit)
            #logger.debug('-> find nearby entrance : target_exit=%s' % str([cur_node.name, cur_node.label]))
            if connected_ent:
                return (cur_node, connected_ent)
        return (None, None)

    def is_connected_to(self, ext, corr, **kwargs):
        """ Return tuple of exit and the connected entrance to the given corridor
            if the given `ext` is connected to the corridor

        Note:
            iterate from the given `rn` to downstream only

        :type ext: pyticas.ttypes.RNodeObject
        :type corr: pyticas.ttypes.CorridorObject
        :rtype: pyticas.ttypes.RNodeObject
        """
        logger = getDefaultLogger(__name__)
        d_limit = kwargs.get('d_limit', 1)

        connected = self.infra.get_rnode(ext.forks[0]) if ext.forks else None

        # logger.debug('find_exit_to(): cur_exit=%s, connected=%s' % (str([ext.label, ext.name]),
        #                                               str([connected.label, connected.name]) if connected else ''))
        if connected and not connected.is_entrance():
            return None

        # case1 : connected to the target corridor
        if connected and connected.corridor.name == corr.name:
            # logger.debug('find_exit_to():     : found')
            return connected

        # case2 : connected to the CD
        if connected and connected.is_CD_entrance():
            # logger.debug('find_exit_to(): try to find exit from CD')
            (cd_exit, cd_ent) = self._exit_from_CD(connected, corr, d_limit=d_limit)
            if cd_ent: return cd_ent

        # some rnode is not CD type but connected to other corridor (e.g. I-35WN to I-494WB)
        if ' CD ' in ext.label or (connected and connected.is_CD_entrance()):
            # logger.debug('find_exit_to(): try to find nearby entrance (not connected by forks)')
            connected_ent = self.find_nearby_entrance(ext, corr, d_limit=d_limit)
            if connected_ent:
                return connected_ent

        return None

    def _exit_from_CD(self, rn, corr, **kwargs):
        """ Return tuple of exit and entrance, which are connection from CD to the given corridor

        :type rn: pyticas.ttypes.RNodeObject
        :type corr: pyticas.ttypes.CorridorObject
        :rtype: (pyticas.ttypes.RNodeObject, pyticas.ttypes.RNodeObject)
        """
        if not rn.corridor.is_CD():
            return (None, None)

        cur_node = rn
        while cur_node.down_rnode:
            cur_node = cur_node.down_rnode
            if cur_node.is_exit() and cur_node.forks:
                connected = self.infra.get_rnode(cur_node.forks[0])
                dist = distutil.distance_in_mile(rn, connected)
                if dist > kwargs.get('d_limit', 1):
                    return (None, None)
                if connected.corridor.is_CD():
                    return self._exit_from_CD(connected, corr)
                if connected.corridor.name == corr.name:
                    return (cur_node, connected)
        return (None, None)

    def is_estimated_exit_connected_to(self, ext, corr, **kwargs):
        """ Return tuple of exit and the connected entrance to the given corridor
            if the given `ext` is estimated that it is connected to the corridor

        **Note**:
            This function estimates the connection from exit to other corridor.
            It can be used in the case of that there's no connection according to the `metro_config.xml`
            but there is connection in real world


        :type ext: pyticas.ttypes.RNodeObject
        :type corr: pyticas.ttypes.CorridorObject
        :rtype: pyticas.ttypes.RNodeObject
        """
        d_limit = kwargs.get('d_limit', 1)

        def _is_exit_to_other_corridor(ext):
            """
            :type ext: pyticas.ttypes.RNodeObject
            :return:
            """
            if ext.forks:
                return True

            for corr in self.infra.get_corridors():
                if corr.route in ext.label and corr.dir in ext.label:
                    return True

            return False

        if _is_exit_to_other_corridor(ext):
            connected_ent = self.find_nearby_entrance(ext, corr, d_limit=d_limit)
            if connected_ent:
                return connected_ent

        return None

    def find_nearby_entrance(self, ext, corr, **kwargs):
        """ Return entrance in the given corridor near by the given exit

        :type ext: pyticas.ttypes.RNodeObject
        :type corr: pyticas.ttypes.CorridorObject
        :rtype: pyticas.ttypes.RNodeObject
        """
        logger = getDefaultLogger(__name__)
        # logger.debug('find_nearby_entrance(): target_exit=%s, target_corridor=%s' %
        #              (str([ext.name, ext.label]), corr.name))

        if not ext.is_exit():
            raise ValueError('The first parameter must be exit')

        ents_info = self.ordered_by_distance(ext,
                                        [rn for rn in corr.entrances],
                                        d_limit=kwargs.get('d_limit', 1))
        if not ents_info:
            return None

        for (ent, dist) in ents_info:
            # logger.debug('find_nearby_entrance(): checking connected entrance : %s (ext corridor=%s, %s)' %
            #              (str([ent.name, ent.label]), ext.corridor.route, ext.corridor.dir))

            if ((ext.corridor.route in ent.label and ext.corridor.dir in ent.label)
                or ('CD' in ent.label and corr.route in ent.label and corr.dir in ent.label)):
                # logger.debug('find_nearby_entrance():    : found')
                return ent

        return None

    def iter_to_downstream(self, rn, filter=None, break_filter=None, break_after_filter=None):
        """ Yield `RNodeObject` from `rn.down_rnode` to the most downstream of the corridor

        Note:
            start and end rnodes will be included

        Arguments:
            * filter: return if `RNodeObject` is passed by `filter`
            * break_filter: break iteration if `RNodeObject` is passed by `break_filter`

        :type rn: pyticas.ttypes.RNodeObject
        :type filter: function
        :type break_filter: function
        :yield: pyticas.ttypes.RNodeObject
        """
        for irn in iter_to_downstream(rn, filter, break_filter, break_after_filter):
            yield irn

    def iter_to_upstream(self, rn, filter=None, break_filter=None, break_after_filter=None):
        """ Yield `RNodeObject` from `rn.up_rnode` to the most upstream of the corridor

        Arguments:
            * filter: return if `RNodeObject` is passed by `filter`
            * break_filter: break iteration if `RNodeObject` is passed by `break_filter`

        :type rn: pyticas.ttypes.RNodeObject
        :type filter: function
        :type break_filter: function
        :yield: pyticas.ttypes.RNodeObject
        """
        for irn in iter_to_upstream(rn, filter, break_filter, break_after_filter):
            yield irn

    def get_length(self, rnodes):
        """ returns length of the given section

        :type rnodes: list[pyticas.ttypes.RNodeObject]
        :rtype: float
        """
        return [ miles for ridx, rn, miles in get_mile_points(rnodes) ][-1]

    def get_mile_points(self, rnodes):
        """ returns index, rnode object and mile point

        :type rnodes: list[pyticas.ttypes.RNodeObject]
        :rtype: collections.Iterable[int, pyticas.ttypes.RNodeObject, float]
        """
        return get_mile_points(rnodes)

    def get_mile_point_map(self, rnodes):
        """ return mile point map as dict[rnode_name, mile_point]

        :type rnodes: list[pyticas.ttypes.RNodeObject]
        :return: dict[RNodeObject.name, mile point]
        :rtype: dict[str, float]
        """
        return get_mile_point_map(rnodes)

    def between_rnodes(self, rn1, rn2):
        """ Return rnode list between the given two rnodes except `rn1` and `rn2`

        :type rn1: pyticas.ttypes.RNodeObject
        :type rn2: pyticas.ttypes.RNodeObject
        :rtype: list[pyticas.ttypes.RNodeObject]
        """
        return between_rnodes(rn1, rn2)

    def ordered_by_distance(self, rnode, rnode_list, **kwargs):
        """ Return list of `RNodeObject` and distance to the given `rnode`

        :type rnode: pyticas.ttypes.RNodeObject
        :type rnode_list: list[pyticas.ttypes.RNodeObject]
        :return: list[(RNodeObject, DistanceInMile)]
        :rtype: list[(pyticas.ttypes.RNodeObject, float)]
        """
        return ordered_by_distance(rnode, rnode_list, **kwargs)

    def angle_of_rnodes(self, rn1, rn2, rn3):
        """
        
        :type rn1: pyticas.ttypes.RNodeObject
        :type rn2: pyticas.ttypes.RNodeObject
        :type rn3: pyticas.ttypes.RNodeObject
        :rtype: float 
        """
        return self.calculate_angle((rn1.lat, rn1.lon), (rn2.lat, rn2.lon), (rn3.lat, rn3.lon))


    def calculate_angle(self, p0, p1, p2):
        """ Retuern angle of (p0p1 and p1p2)
        
        :type p0: (float, float) 
        :type p1: (float, float)
        :type p2: (float, float)
        :rtype: float 
        """
        return _calculate_angle(p0, p1, p2)

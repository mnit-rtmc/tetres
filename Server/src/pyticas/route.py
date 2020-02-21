# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import os
import uuid

from pyticas import ticas
from pyticas.infra import Infra
from pyticas.logger import getDefaultLogger
from pyticas.rc import route_config
from pyticas.rn.geo import between_rnodes, iter_to_downstream, get_mile_points
from pyticas.tool import util, json
from pyticas.ttypes import Route

logger = getDefaultLogger(__name__)


def create_route(srn_name, ern_name, name='', desc='', **kwargs):
    """ Return `Route` that is from `srn_name` to `ern_name`

    :param srn_name: start rnode name
    :type srn_name: str
    :param ern_name: end rnode name
    :type ern_name: str
    :type name: str
    :type desc: str
    :rtype: pyticas.ttypes.Route
    """
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if not name:
        name = 'Route @ %s' % (now)
    if not desc:
        desc = 'Route created at %s ' % now

    infra = kwargs.get('infra', Infra.get_infra())
    r = Route(name, desc)
    r.infra_cfg_date = infra.cfg_date

    start_rnode = infra.get_rnode(srn_name)
    end_rnode = infra.get_rnode(ern_name)

    r.rnodes.append(start_rnode)
    betweens = infra.geo.between_rnodes(start_rnode, end_rnode)

    # if not betweens and start_rnode.name == end_rnode.name:
    #     raise ValueError(('Cannot find end of section in creating route. ',
    #                       'Make sure start and end rnode information : {0} - {1}'.format(srn_name, ern_name)))

    r.rnodes.extend([rn for rn in betweens])
    r.rnodes.append(end_rnode)

    return r


def create_mc_route(srn_erns, name='', desc='', **kwargs):
    """ Return multi-corridor `Route`

    :param srn_erns: list of (start_rnode_name, end_rnode_name)
    :type srn_erns: list[(str, str)]
    :type name: str
    :type desc: str
    :return:
    """
    routes = []
    for (srn_name, ern_name) in srn_erns:
        r = create_route(srn_name, ern_name)
        if not r:
            return None
        routes.append(r)
    return merge_routes(routes)


def merge_routes(routes):
    """ Merge routes

    :param routes: list of [Route]
    :type routes: list[Route]
    :rtype: Route
    """
    mr = merge_two_routes(routes[0], routes[1])
    if len(routes) <= 2:
        return mr
    for r in routes[2:]:
        mr = merge_two_routes(mr, r)
        if not mr:
            return None

    return mr


def merge_two_routes(r1, r2):
    """ Merge two routes

    :type r1: Route
    :type r2: Route
    :rtype: Route
    """

    def find_exit_to(rn, corr):
        for ext in iter_to_downstream(rn, lambda x: x.is_exit()):
            if corr.name in ext.connected_to:
                return ext, ext.connected_to.get(corr.name)
        return None, None

    r1_end = r1.rnodes[-1]
    r2_start = r2.rnodes[0]
    mr = r1.clone()
    if r1_end.corridor == r2_start.corridor:
        rnodes = between_rnodes(r1_end, r2_start)
        mr.rnodes.extend(rnodes)
        mr.rnodes.extend(r2.rnodes)
        return mr
    else:
        (ext, ent) = find_exit_to(r1_end, r2_start.corridor)
        if ext:
            rnodes_btw_r1_and_ext = between_rnodes(r1_end, ext)
            rnodes_btw_ent_and_r2 = between_rnodes(ent, r2_start)
            mr.rnodes.extend(rnodes_btw_r1_and_ext)
            mr.rnodes.extend([ext, ent])
            mr.rnodes.extend(rnodes_btw_ent_and_r2)
            mr.rnodes.extend(r2.rnodes)
            return mr

    logger.warn('Could not merge two routes : %s ~ %s and %s ~ %s' % (str([r1.rnodes[0].station_id, r1.rnodes[0].name]),
                                                                      str([r1.rnodes[-1].station_id,
                                                                           r1.rnodes[-1].name]),
                                                                      str([r2.rnodes[0].station_id, r2.rnodes[0].name]),
                                                                      str([r2.rnodes[-1].station_id,
                                                                           r2.rnodes[-1].name])))
    return None


def load_routes():
    """
    :rtype: list[Route]
    """
    routes = []
    for file in util.file_list(ticas.get_path('route')):
        r = load_route(file)
        if r:
            routes.append(r)
    return routes


def load_route_by_name(route_name):
    """
    :type route_name: str:
    :rtype: Route
    """
    return load_route(get_file_path(route_name))


def load_route(filepath):
    """
    :type filepath: str
    :rtype: Route
    """
    if not os.path.exists(filepath):
        return None

    r = json.loads(util.get_file_contents(filepath))
    if isinstance(r, Route):
        return r
    else:
        return None


def save_route(r, **kwargs):
    """
    :type r: Route
    """
    r_json = json.dumps(r)
    filepath = get_file_path(r.name, **kwargs)
    overwrite = kwargs.get('overwrite', False)
    if not overwrite and os.path.exists(filepath):
        return False
    util.save_file_contents(filepath, r_json)
    return os.path.exists(filepath)


def delete_route(route_name):
    filepath = get_file_path(route_name)
    if not os.path.exists(filepath):
        return False, 'Not exists'
    os.unlink(filepath)
    if os.path.exists(filepath):
        return False, 'Fail to delete'
    else:
        return True, 'Deleted'


def exists(route_name):
    return os.path.exists(get_file_path(route_name))


def opposite_route(r):
    """
    :type r: Route
    :rtype: Route
    """
    orns = []
    if not hasattr(r, 'cfg') or not r.cfg:
        # r.cfg = route_config.create_route_config(r.rnodes, infra_cfg_date=r.rnodes[0].infra_cfg_date)
        r.cfg = route_config.create_route_config(r.rnodes)

    for ns in r.cfg.node_sets:
        if ns.node2.rnode:
            orns.append(ns.node2.rnode)
    opposite_route = Route(name='Opposite Direction of %s' % r.name, desc=r.desc)
    opposite_route.rnodes = list(reversed(orns))
    opposite_route.infra_cfg_date = opposite_route.rnodes[0].infra_cfg_date
    return opposite_route


def get_file_path(route_name, **kwargs):
    """
    :type route_name: str
    :rtype: str
    """
    name_based = kwargs.get('name_based', True)
    if name_based:
        uid = uuid.uuid3(uuid.NAMESPACE_DNS, route_name)
    else:
        uid = uuid.uuid4()

    name = str(uid)
    filepath = os.path.join(ticas.get_path('route'), name)
    if not name_based and os.path.exists(filepath):
        return get_file_path(route_name, **kwargs)

    return os.path.join(ticas.get_path('route'), name)


def center_coordinates(r):
    """ Return (lat, lon)
    :type r: Route
    :rtype: (float, float)
    """
    route_length = max([mp for ridx, rn, mp in get_mile_points(r.rnodes)])
    center = route_length / 2.0
    prev_rn = None
    for ridx, rn, mp in get_mile_points(r.rnodes):
        if mp > center:
            return (prev_rn.lat + rn.lat) / 2, (prev_rn.lon + rn.lon) / 2
        prev_rn = rn
    raise Exception('Could not determine center adjust')


def corridors(r):
    """

    :type r: pyticas.ttypes.Route
    :return:
    """
    corrs = []
    for rn in r.rnodes:
        if rn.corridor not in corrs:
            corrs.append(rn.corridor)
    return corrs


def print_route(r):
    """
    :type r: Route
    """
    logger.debug("*" * 10)
    logger.debug("Route")
    for ridx, rn in enumerate(r.rnodes):
        logger.debug('RN #%2d > %s : %d' % (ridx, _s(rn), rn.lanes))
    logger.debug("*" * 10)


def _s(rnode):
    """
    :type rnode: pyticas.ttypes.RNodeObject
    :rtype: str
    """
    if not rnode: return 'NONE'

    if rnode.is_station():
        return '%18s (%10s)' % (rnode.station_id, rnode.name)
    elif rnode.is_entrance():
        return '%18s (%10s)' % ('E:' + rnode.label, rnode.name)
    elif rnode.is_exit():
        return '%18s (%10s)' % ('X:' + rnode.label, rnode.name)
    return 'NONE'

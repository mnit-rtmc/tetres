# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_server.logger import getLogger
from pyticas.infra import Infra
from pyticas.tool import json
from pyticas.ttypes import  Route

def json2route(json_str):
    """ convert json to `Route` object from TICAS client

    :type json_str: str
    :rtype: Route
    """

    tmp = json.loads(json_str)

    r = Route(tmp.name, tmp.desc)
    if not hasattr(tmp, 'cfg'):
        tmp.cfg = None
    if not hasattr(tmp, 'rnodes'):
        tmp.rnodes = []
    r.cfg = tmp.cfg
    r.rnodes = tmp.rnodes
    route_setup(r)

    return r

def route_setup(r):
    """ initialize `Route` converted from json
        (`rnode` and `corridor` must be connected to their instances)

    :type r: ROute
    :return:
    """
    logger = getLogger(__name__)

    infra = Infra.get_infra()
    rnodes = []
    for ridx, rn in enumerate(r.rnodes):
        rnode_object = infra.get_rnode(rn)
        if rnode_object is None:
            logger.warn('rnode is not found : %s' % rn)
            continue
        rnodes.append(rnode_object)

    r.rnodes = rnodes

    if hasattr(r, 'cfg') and r.cfg:
        for nidx, ns in enumerate(r.cfg.node_sets):
            if hasattr(ns.node1, 'rnode') and ns.node1.rnode:
                r.cfg.node_sets[nidx].node1.rnode = infra.get_rnode(ns.node1.rnode)
            else:
                r.cfg.node_sets[nidx].node1.rnode = None

            if hasattr(ns.node2, 'rnode') and ns.node2.rnode:
                r.cfg.node_sets[nidx].node2.rnode = infra.get_rnode(ns.node2.rnode)
            else:
                r.cfg.node_sets[nidx].node2.rnode = None

            try:
                ns.node1.corridor = infra.get_corridor_by_name(ns.node1.corridor)
                ns.node2.corridor = infra.get_corridor_by_name(ns.node2.corridor)
            except AttributeError as ex:
                raise ex

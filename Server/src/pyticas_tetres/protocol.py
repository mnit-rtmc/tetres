# -*- coding: utf-8 -*-
from pyticas import route, rc
from pyticas.tool import json
from pyticas.tool.json import loads as json_loads
from pyticas_tetres.ttypes import WorkZoneInfo, TTRouteInfo

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_server.util import route_setup


def json2sei(json_str):
    sei = json.loads(json_str)
    sei.set_years()
    return sei


def json2snei(json_str):
    return json.loads(json_str)


def json2snmi(json_str):
    snmi = json.loads(json_str)
    if not hasattr(snmi, '_snowevent'):
        setattr(snmi, '_snowevent', None)
    if not hasattr(snmi, '_snowroute'):
        setattr(snmi, '_snowroute', None)
    return snmi


def json2ttri(json_str):
    """ convert json to `pyticas_tetres.types.TTRouteInfo` object from TICAS client

    :type json_str: str
    :rtype: TTRouteInfo
    """

    tmp = json.loads(json_str)
    if not hasattr(tmp.route, 'cfg'):
        tmp.route.cfg = None
    route_setup(tmp.route)
    return tmp


def json2wzi(wzi_json):
    """ convert json to `pyticas_tetres.types.WorkZoneInfo` from TICAS client

    :type wzi_json: str
    :rtype: pyticas_tetres.ttypes.WorkZoneInfo
    """
    wzi = json_loads(wzi_json)

    assert isinstance(wzi, WorkZoneInfo)

    if hasattr(wzi, 'route1'):
        route_setup(wzi.route1)
    else:
        wzi.route1 = None

    if hasattr(wzi, 'route2'):
        route_setup(wzi.route2)
    else:
        wzi.route2 = None

    # wzi.years = wzi.years_string(wzi.str2datetime(wzi.start_time).year, wzi.str2datetime(wzi.end_time).year)
    # if wzi.route1 or wzi.route2:
    #     wzi.corridors = wzi.corridor_string([wzi.route1, wzi.route2])
    # else:
    #     wzi.corridors = ''

    return wzi


def json2wzgi(json_str):
    return json.loads(json_str)


def json2route_wise_moe_parameters(json_str):
    return json.loads(json_str)


def json2snri(json_str):
    """ convert json to `pyticas_tetres.types.SnowRouteInfo` object from TICAS client

    :type json_str: str
    :rtype: SnowRouteInfo
    """

    info = json.loads(json_str)
    if info.route1 and not hasattr(info.route1, 'cfg'):
        info.route1.cfg = None
    route_setup(info.route1)
    route2 = route.opposite_route(info.route1)
    cfg2 = info.route1.cfg.clone()
    rc.route_config.reverse(cfg2)
    route2.cfg = cfg2
    info.route2 = route2
    info.route1.name = 'route1 - %s' % info.route1.rnodes[0].corridor.name
    info.route1.desc = ''
    info.route2.name = 'route2 - %s' % info.route2.rnodes[0].corridor.name
    info.route2.desc = ''
    return info

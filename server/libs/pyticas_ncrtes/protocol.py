# -*- coding: utf-8 -*-
"""
pyticas_ncrtes.protocol
========================

- module to convert JSON string from client to data types in `pyticas_ncrtes.itypes`

"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.tool import json
from pyticas.tool.json import loads as json_loads
from pyticas_server.util import route_setup


def json2snei(json_str):
    """

    :type json_str: str
    :rtype: pyticas_ncrtes.itypes.SnowEventInfo
    """
    return json.loads(json_str)


def json2snri(json_str):
    """

    :type json_str: str
    :rtype: pyticas_ncrtes.itypes.SnowRouteInfo
    """
    snri = json_loads(json_str)

    if hasattr(snri, 'route1'):
        route_setup(snri.route1)
    else:
        snri.route1 = None

    if hasattr(snri, 'route2'):
        route_setup(snri.route2)
    else:
        snri.route2 = None

    return snri


def json2snrgi(json_str):
    """ convert json

    :type json_str: str
    :rtype: pyticas_ncrtes.itypes.SnowRouteGroupInfo
    """
    return json.loads(json_str)


def json2ts(json_str):
    """

    :param json_str:
    :type json_str:
    :return:
    :rtype: pyticas_ncrtes.itypes.TargetStationInfo
    """
    return json.loads(json_str)

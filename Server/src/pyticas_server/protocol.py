# -*- coding: utf-8 -*-
from pyticas.infra import Infra

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.tool import json
from pyticas.ttypes import Route
from pyticas_server.util import route_setup

MSG_SUCCESS = 'success'
MSG_INVALID_REQUEST = 'invalid request'
CODE_SUCCESS = 1
CODE_FAIL = -1
CODE_ERROR = -2

def response(code, message, obj=None, only_name=True, **kwargs):
    jdata = {'code': code, 'message': message}
    jdata['obj'] = obj
    return json.dumps(jdata, only_name=only_name, indent=4)

def response_success(obj=None, only_name=True, **kwargs):
    msg = kwargs.get('message', MSG_SUCCESS)
    return response(CODE_SUCCESS, msg, obj, only_name)

def response_fail(message):
    return response(CODE_FAIL, message, None, False)

def response_error(message):
    return response(CODE_ERROR, message, None, False)

def response_invalid_request(**kwargs):
    msg = kwargs.get('message', MSG_INVALID_REQUEST)
    return response(CODE_ERROR, msg, None, False)


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

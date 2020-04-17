# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from functools import wraps

from flask import request

from pyticas_server import protocol as prot
from pyticas_tetres import cfg


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_auth():
            return authenticate()
        return f(*args, **kwargs)

    return decorated


def check_auth():
    """
    :rtype: bool
    """
    return (not cfg.USE_WHITELIST) or request.remote_addr in cfg.ADMIN_IP_ADDRESSES


def authenticate():
    return prot.response_invalid_request(message='Could not verify your access level for that URL (from admin_auth)')

# -*- coding: utf-8 -*-
"""
snowevent.py
~~~~~~~~~~~~~~

this module handles the request from `operating-condition data input > road condition during snow event tab` of `admin client`

"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres import api_urls_admin
from pyticas_tetres.api_base import TeTRESApi
from pyticas_tetres.da.actionlog import ActionLogDataAccess
from pyticas_tetres.da.snowevent import SnowEventDataAccess
from pyticas_tetres.protocol import json2snei


def register_api(app):
    TeTRESApi(app, ActionLogDataAccess.DT_SNOWEVENT, json2snei, SnowEventDataAccess, {
        'insert': (api_urls_admin.SNE_INSERT, ['POST']),
        'list': (api_urls_admin.SNE_LIST, ['GET']),
        'list_by_year': (api_urls_admin.SNE_LIST_BY_YEAR, ['POST']),
        'get_by_id': (api_urls_admin.SNE_GET, ['POST']),
        'update': (api_urls_admin.SNE_UPDATE, ['POST'], ['start_time', 'end_time']),
        'delete': (api_urls_admin.SNE_DELETE, ['POST']),
        'years': (api_urls_admin.SNE_YEARS, ['GET']),
    }, requires_auth=True).register()

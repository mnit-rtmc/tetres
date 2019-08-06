# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres import api_urls_admin
from pyticas_tetres.api_base import TeTRESApi
from pyticas_tetres.da.actionlog import ActionLogDataAccess
from pyticas_tetres.da.specialevent import SpecialEventDataAccess
from pyticas_tetres.protocol import json2sei


def register_api(app):
    TeTRESApi(app, ActionLogDataAccess.DT_SPECIALEVENT, json2sei, SpecialEventDataAccess, {
        'insert': (api_urls_admin.SE_INSERT, ['POST']),
        'list': (api_urls_admin.SE_LIST, ['GET']),
        'list_by_year': (api_urls_admin.SE_LIST_BY_YEAR, ['POST']),
        'get_by_id': (api_urls_admin.SE_GET, ['POST']),
        'update': (api_urls_admin.SE_UPDATE, ['POST'], ['start_time', 'end_time', 'lat', 'lon', 'attendance']),
        'delete': (api_urls_admin.SE_DELETE, ['POST']),
        'years': (api_urls_admin.SE_YEARS, ['GET']),
    }, requires_auth=True).register()

# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_ncrtes import api_urls
from pyticas_ncrtes.api_base import NCRTESApi
from pyticas_ncrtes.da.snowevent import SnowEventDataAccess
from pyticas_ncrtes.protocol import json2snei


def register_api(app):
    NCRTESApi(app, 'snow_event', json2snei, SnowEventDataAccess, {
        'insert': (api_urls.SNE_INSERT, ['POST']),
        'list': (api_urls.SNE_LIST, ['GET']),
        'list_by_year': (api_urls.SNE_LIST_BY_YEAR, ['POST']),
        'get_by_id': (api_urls.SNE_GET, ['POST']),
        'update': (api_urls.SNE_UPDATE, ['POST']),
        'delete': (api_urls.SNE_DELETE, ['POST']),
        'ymds': (api_urls.SNE_YEARS, ['GET']),
    }).register()

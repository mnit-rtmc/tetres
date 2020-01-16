# -*- coding: utf-8 -*-
"""
wz_group.py
~~~~~~~~~~~~~~

this module handles the request from `operating-condition data input > workzone tab` of `admin client`

- corresponding API client in the admin client : `edu.umn.natsrl.tetres.admin.api.WorkzoneGroupClient`
- data information classes

    - `edu.umn.natsrl.tetres.admin.api.WorkzoneGroupClient`

"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres import api_urls_admin
from pyticas_tetres.api_base import TeTRESApi
from pyticas_tetres.da.actionlog import ActionLogDataAccess
from pyticas_tetres.da.wz_group import WZGroupDataAccess
from pyticas_tetres.protocol import json2wzgi


def register_api(app):
    TeTRESApi(app, ActionLogDataAccess.DT_WORKZONE_GROUP, json2wzgi, WZGroupDataAccess, {
        'insert': (api_urls_admin.WZ_GROUP_INSERT, ['POST']),
        'update': (api_urls_admin.WZ_GROUP_UPDATE, ['POST']),
        'list': (api_urls_admin.WZ_GROUP_LIST, ['GET']),
        'list_by_year': (api_urls_admin.WZ_GROUP_LIST_BY_YEAR, ['POST']),
        'get_by_name': (api_urls_admin.WZ_GROUP_GET, ['POST']),
        'delete': (api_urls_admin.WZ_GROUP_DELETE, ['POST']),
        'years': (api_urls_admin.WZ_GROUP_YEARS, ['GET']),
    }, requires_auth=True).register()

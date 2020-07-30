# -*- coding: utf-8 -*-
"""
wz_group.py
~~~~~~~~~~~~~~

this module handles the request from `operating-condition data input > workzone tab` of `admin client`

- corresponding API client in the admin client : `edu.umn.natsrl.tetres.admin.api.WorkzoneGroupClient`
- data information classes

    - `edu.umn.natsrl.tetres.admin.api.WorkzoneGroupClient`

"""
from pyticas_tetres.da.route_wise_moe_parameters import RouteWiseMOEParametersDataAccess

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres import api_urls_admin
from pyticas_tetres.api_base import TeTRESApi
from pyticas_tetres.da.actionlog import ActionLogDataAccess
from pyticas_tetres.protocol import json2route_wise_moe_parameters


def register_api(app):
    TeTRESApi(app, ActionLogDataAccess.DT_ROUTE_WISE_MOE_PARAMETERS, json2route_wise_moe_parameters,
              RouteWiseMOEParametersDataAccess, {
                  'insert': (api_urls_admin.RW_MOE_PARAM_INSERT, ['POST']),
                  'list': (api_urls_admin.RW_MOE_PARAM_LIST, ['GET']),
              }, requires_auth=True).register()

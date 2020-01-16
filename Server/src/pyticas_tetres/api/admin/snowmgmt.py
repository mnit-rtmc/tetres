# -*- coding: utf-8 -*-
"""
snowmgmt.py
~~~~~~~~~~~~~~

this module handles the request from `operating-condition data input > road condition during snow event tab` of `admin client`

"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from flask import request

from pyticas_server import protocol as prot
from pyticas_tetres import api_urls_admin
from pyticas_tetres.admin_auth import requires_auth
from pyticas_tetres.api_base import TeTRESApi
from pyticas_tetres.da.actionlog import ActionLogDataAccess
from pyticas_tetres.da.snowevent import SnowEventDataAccess
from pyticas_tetres.da.snowmgmt import SnowMgmtDataAccess
from pyticas_tetres.da.snowroute import SnowRouteDataAccess
from pyticas_tetres.protocol import json2snmi


def register_api(app):
    TeTRESApi(app, ActionLogDataAccess.DT_SNOWMGMT, json2snmi, SnowMgmtDataAccess, {
        'insert': (api_urls_admin.SNM_INSERT, ['POST']),
        'insert_all': (api_urls_admin.SNM_INSERT_ALL, ['POST']),
        'update': (api_urls_admin.SNM_UPDATE, ['POST'], ['lane_lost_time', 'lane_regain_time']),
        'delete': (api_urls_admin.SNM_DELETE, ['POST']),
    }, requires_auth=True).register()

    @app.route(api_urls_admin.SNM_LIST, methods=['POST'])
    @requires_auth
    def tetres_snow_mgmt_list():
        snowevent_id = request.form.get('snowevent_id')
        mgmt_list = []
        snowMgmtDA = SnowMgmtDataAccess()
        snowRouteDA = SnowRouteDataAccess(session=snowMgmtDA.get_session())  # use the same session
        snowEventDA = SnowEventDataAccess(session=snowMgmtDA.get_session())  # use the same session

        for snmm in snowMgmtDA.search([('sevent_id', snowevent_id)], as_model=True):
            snmi = snowMgmtDA.da_base.to_info(snmm)
            snmi._snowroute = snowRouteDA.da_base.to_info(snmm._snowroute)
            snmi._snowevent = snowEventDA.da_base.to_info(snmm._snowevent)
            mgmt_list.append(snmi)

        snowMgmtDA.close_session()

        return prot.response_success({'list': mgmt_list})

# -*- coding: utf-8 -*-
"""
snowroute.py
~~~~~~~~~~~~~~

this module handles the request from `operating-condition data input > road condition during snow event tab` of `admin client`

"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from flask import request

from pyticas import route, rc
from pyticas_server import protocol as prot
from pyticas_tetres import api_urls_admin
from pyticas_tetres.admin_auth import requires_auth
from pyticas_tetres.api_base import TeTRESApi
from pyticas_tetres.da.actionlog import ActionLogDataAccess
from pyticas_tetres.da.snowroute import SnowRouteDataAccess
from pyticas_tetres.protocol import json2snri


def register_api(app):
    tetresApi = TeTRESApi(app, ActionLogDataAccess.DT_SNOWROUTE, json2snri, SnowRouteDataAccess, {
        'list': (api_urls_admin.SNR_LIST, ['GET']),
        'get_by_id': (api_urls_admin.SNR_GET, ['POST']),
        'delete': (api_urls_admin.SNR_DELETE, ['POST']),
    }, requires_auth=True)
    tetresApi.register()

    @app.route(api_urls_admin.SNR_INSERT, methods=['POST'])
    @requires_auth
    def tetres_snowroute_insert():
        route_json = request.form.get('data')
        info = json2snri(route_json)

        snowRouteDA = SnowRouteDataAccess()

        ex = snowRouteDA.get_by_name(info.name)
        if ex:
            snowRouteDA.close_session()
            return prot.response_fail('already exist')

        route2 = route.opposite_route(info.route1)
        cfg2 = info.route1.cfg.clone()
        rc.route_config.reverse(cfg2)
        route2.cfg = cfg2
        info.route2 = route2
        info.route1.name = 'route1 - %s' % info.route1.rnodes[0].corridor.name
        info.route1.desc = ''
        info.route2.name = 'route2 - %s' % info.route2.rnodes[0].corridor.name
        info.route2.desc = ''

        snrm = snowRouteDA.insert(info)
        if not snrm:
            snowRouteDA.close_session()
            return prot.response_fail('Fail to insert data')

        snowRouteDA.commit()

        tetresApi.add_actionlog(ActionLogDataAccess.INSERT,
                                snowRouteDA.get_tablename(),
                                snrm.id,
                                ActionLogDataAccess.data_description(ActionLogDataAccess.DT_SNOWROUTE, snrm),
                                handled=False,
                                dbsession=snowRouteDA.get_session())

        inserted_id = snrm.id

        snowRouteDA.close_session()

        return prot.response_success(obj=inserted_id)

    @app.route(api_urls_admin.SNR_UPDATE, methods=['POST'])
    @requires_auth
    def tetres_snowroute_update():
        id = request.form.get('id')
        route_json = request.form.get('data')

        snowRouteDA = SnowRouteDataAccess()

        ex = snowRouteDA.get_by_id(id)
        if not ex:
            snowRouteDA.close_session()
            return prot.response_invalid_request()

        info = json2snri(route_json)
        is_updated = snowRouteDA.update(id, {'name': info.name, 'description': info.description, 'prj_id': info.prj_id})
        if not is_updated:
            return prot.response_fail('fail to update database')

        if not snowRouteDA.commit():
            return prot.response_fail('fail to update database (commit fail)')

        tetresApi.add_actionlog(ActionLogDataAccess.INSERT,
                                snowRouteDA.get_tablename(),
                                id,
                                ActionLogDataAccess.data_description(ActionLogDataAccess.DT_SNOWROUTE, info),
                                handled=True,
                                dbsession=snowRouteDA.get_session())

        return prot.response_success(id)

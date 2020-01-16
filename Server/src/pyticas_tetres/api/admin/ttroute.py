# -*- coding: utf-8 -*-
"""
ttroute.py
~~~~~~~~~~~~~~

this module handles the request from `route configuration tab` of `admin client`

"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from flask import request

from pyticas import route
from pyticas.ttypes import Route
from pyticas_server import protocol as prot
from pyticas_tetres import api_urls_admin
from pyticas_tetres.admin_auth import requires_auth
from pyticas_tetres.api_base import TeTRESApi
from pyticas_tetres.da.actionlog import ActionLogDataAccess
from pyticas_tetres.da.route import TTRouteDataAccess
from pyticas_tetres.protocol import json2ttri, route_setup


def register_api(app):
    TeTRESApi(app, ActionLogDataAccess.DT_TTROUTE, json2ttri, TTRouteDataAccess, {
        'insert': (api_urls_admin.TTROUTE_INSERT, ['POST']),
        'list': (api_urls_admin.TTROUTE_LIST, ['GET']),
        'get_by_id': (api_urls_admin.TTROUTE_GET, ['POST']),
        'update': (api_urls_admin.TTROUTE_UPDATE, ['POST']),
        'delete': (api_urls_admin.TTROUTE_DELETE, ['POST']),
    }, requires_auth=True).register()

    @app.route(api_urls_admin.TTROUTE_OPPOSITE_ROUTE, methods=['POST'])
    @requires_auth
    def tetres_route_opposite_route():
        route_id = request.form.get('id')

        da = TTRouteDataAccess()
        ttri = da.get_by_id(route_id)
        da.close_session()

        route_setup(ttri.route)
        opposite_route = route.opposite_route(ttri.route)
        if not isinstance(opposite_route, Route):
            return prot.response_fail('fail to load_data route configuration file')
        return prot.response_success(opposite_route)



# -*- coding: utf-8 -*-
"""
route.py
~~~~~~~~~~~~~~

this module handles the request from `route configuration tab` of `user client`

- corresponding API client in the admin client : `ticas.tetres.user.api.RouteClient`
"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from flask import request

from pyticas_server import protocol as prot
from pyticas_tetres import api_urls_user
from pyticas_tetres.da.route import TTRouteDataAccess


def register_api(app):
    @app.route(api_urls_user.ROUTE_LIST, methods=['POST'])
    def tetres_user_route_list():
        # retrieven user parameter
        corridor_name = request.form.get('corridor')

        da = TTRouteDataAccess()
        ttris = list(da.list_by_corridor(corridor_name, order_by=('name', 'desc'), window_size=10000))
        da.close_session()

        return prot.response_success({'list': ttris})

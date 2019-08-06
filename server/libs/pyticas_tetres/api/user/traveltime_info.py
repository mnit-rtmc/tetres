# -*- coding: utf-8 -*-
"""
traveltime_info.py
~~~~~~~~~~~~~~

this module handles the request from the public web (it is an experimental)
"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from flask import request

from pyticas.tool import tb
from pyticas_server import protocol as prot
from pyticas_tetres import api_urls_admin
from pyticas_tetres.rengine import traveltime_info


def register_api(app):
    @app.route(api_urls_admin.PI_ROUTE_LIST, methods=['GET', 'POST'])
    def tetres_pi_route_list():
        return prot.response_success(traveltime_info.traveltime_route_list())

    @app.route(api_urls_admin.PI_GET, methods=['POST'])
    def tetres_pi_get():
        route_id = request.form.get('route_id')
        depart_time = request.form.get('depart_time')
        weather_type = request.form.get('weather_type', None)

        try:
            depart_time = datetime.datetime.strptime(depart_time, '%Y-%m-%d %H:%M')
        except:
            return prot.response_fail('depart_time format must be "%Y-%m-%d %H:%M:00"')

        try:
            reliabilites, traveltimes = traveltime_info.traveltime_info(route_id, weather_type, depart_time)
        except Exception as ex:
            tb.traceback(ex)
            return prot.response_fail('fail to extract data for the given route')

        return prot.response_success({'reliabilities': reliabilites, 'traveltimes': traveltimes})

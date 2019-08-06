# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from flask import request

from pyticas import rc
from pyticas import route
from pyticas.ttypes import Route
from pyticas_ncrtes import api_urls
from pyticas_ncrtes.api_base import NCRTESApi
from pyticas_ncrtes.da.snowroute import SnowRouteDataAccess
from pyticas_ncrtes.db.exc import AlreadyExist
from pyticas_ncrtes.itypes import SnowRouteInfo
from pyticas_ncrtes.protocol import json2snri
from pyticas_server import protocol as prot
from pyticas_server.util import json2route


def register_api(app):
    ncrtes_api = NCRTESApi(app, 'snr', json2snri, SnowRouteDataAccess, {
        'delete': (api_urls.SNR_DELETE, ['POST']),
    })
    ncrtes_api.register()

    @app.route(api_urls.SNR_LIST, methods=['POST'])
    def ncrtes_snr_list():
        try:
            snrgi_id = request.form.get('snowroute_group_id')
            snrDA = SnowRouteDataAccess()
            snr_list = snrDA.search([('snowroute_group_id', snrgi_id)])
            snrDA.close()
        except Exception as ex:
            import traceback
            traceback.print_tb(ex)
            raise ex

        return prot.response_success({'list': snr_list})

    @app.route(api_urls.SNR_INSERT, methods=['POST'])
    def ncrtes_snr_insert():
        snr_json = request.form.get('data', None)
        route_json = request.form.get('route', None)
        snri = json2snri(snr_json)
        if route_json:
            return _snr_insert_from_route(snri, route_json)

        return _snr_insert_from_snri(snri)

    @app.route(api_urls.SNR_UPDATE, methods=['POST'])
    def ncrtes_snr_update():
        id = request.form.get('id')
        snr_json = request.form.get('data')

        snrDA = SnowRouteDataAccess()

        ex = snrDA.get_by_id(id)
        if not ex:
            return prot.response_invalid_request()
        info = json2snri(snr_json)
        route2 = route.opposite_route(info.route1)
        cfg2 = info.route1.cfg.clone()
        rc.route_config.reverse(cfg2)
        route2.cfg = cfg2
        info.route2 = route2
        info.route1.name = 'route1 - %s' % info.route1.rnodes[0].corridor.name
        info.route1.desc = ''
        info.route2.name = 'route2 - %s' % info.route2.rnodes[0].corridor.name
        info.route2.desc = ''

        if not isinstance(info.route2, Route):
            return prot.response_fail('fail to load_data route configuration file')
        try:
            snrDA.update(id, info.get_dict(), True)
            ex = snrDA.get_by_id(id)
            return prot.response_success(obj=id)
        except AlreadyExist:
            return prot.response_fail('already exist')

    def _snr_insert_from_snri(snri):
        """
        :type snri: SnowRouteInfo
        """
        if not isinstance(snri, SnowRouteInfo) or not snri.route1 or not snri.route2:
            return prot.response_invalid_request()
        snrDA = SnowRouteDataAccess()

        snri.route1.name = 'route1 - %s' % snri.route1.rnodes[0].corridor.name
        snri.route1.desc = ''
        snri.route2.name = 'route2 - %s' % snri.route2.rnodes[0].corridor.name
        snri.route2.desc = ''

        try:
            snrm = snrDA.insert(snri, autocommit=True)
            return prot.response_success(obj=snrm.id)
        except:
            return prot.response_fail('fail to save snow management route data')

    def _snr_insert_from_route(snri, route_json):
        """
        :type snri: SnowRouteInfo
        :type route_json: str
        """
        route1 = json2route(route_json)
        route2 = route.opposite_route(route1)
        if not isinstance(route2, Route):
            return prot.response_fail('fail to load_data route configuration file')
        cfg2 = route1.cfg.clone()
        route2.cfg = rc.route_config.reverse(cfg2)
        snri.route1 = route1
        snri.route2 = route2
        return _snr_insert_from_snri(snri)

# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from flask import request

from pyticas_ncrtes import api_urls
from pyticas_ncrtes.api_base import NCRTESApi
from pyticas_ncrtes.da.target_station_manual import TargetStationManualDataAccess
from pyticas_ncrtes.protocol import json2ts
from pyticas_server import protocol as prot


def register_api(app):
    ncrtes_api = NCRTESApi(app, 'tsmanual', json2ts, TargetStationManualDataAccess, {
        'insert': (api_urls.MANUAL_TS_INSERT, ['POST']),
        'delete': (api_urls.MANUAL_TS_DELETE, ['POST']),
    })
    ncrtes_api.register()

    @app.route(api_urls.MANUAL_TS_LIST, methods=['POST'])
    def ncrtes_tsmanual_list():
        try:
            corridor_name = request.form.get('corridor_name')
            da = TargetStationManualDataAccess()
            ts_list = da.list_by_corridor(corridor_name)
            da.close()
        except Exception as ex:
            import traceback
            traceback.print_tb(ex)
            raise ex

        return prot.response_success({'list': ts_list})

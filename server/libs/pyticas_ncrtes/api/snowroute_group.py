# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from flask import request

from pyticas import route, rc
from pyticas_server import protocol as prot
from pyticas_ncrtes import api_urls
from pyticas_ncrtes.api_base import NCRTESApi
from pyticas_ncrtes.da.snowroute_group import SnowRouteGroupDataAccess
from pyticas_ncrtes.da.snowroute import SnowRouteDataAccess
from pyticas_ncrtes.protocol import json2snrgi
from sqlalchemy import exc

def register_api(app):
    ncrtes_api = NCRTESApi(app, 'snowroute_group', json2snrgi, SnowRouteGroupDataAccess, {
        'insert': (api_urls.SNR_GROUP_INSERT, ['POST']),
        'list': (api_urls.SNR_GROUP_LIST, ['GET']),
        'list_by_year': (api_urls.SNR_GROUP_LIST_BY_YEAR, ['POST']),
        'get_by_id': (api_urls.SNR_GROUP_GET, ['POST']),
        'delete': (api_urls.SNR_GROUP_DELETE, ['POST']),
        'update': (api_urls.SNR_GROUP_UPDATE, ['POST']),
        'years': (api_urls.SNR_GROUP_YEARS, ['GET']),
    })

    def after_delete(deleted_objs):
        snrDA = SnowRouteDataAccess()
        for snrgi in deleted_objs:
            snr_list = snrDA.search([('snowroute_group_id', snrgi.id)], as_model=True)
            print(snr_list)
            for snri in snr_list:
                snrDA.delete(snri.id, False)
        snrDA.commit()
        snrDA.close()

    ncrtes_api.on_delete_success = after_delete
    ncrtes_api.register()

    @app.route(api_urls.SNR_GROUP_COPY, methods=['POST'])
    def ncrtes_snowroute_group_copy():
        snrg_id = request.form.get('snowroute_group_id')
        snrDA = SnowRouteDataAccess()
        snr_list = snrDA.search([('snowroute_group_id', snrg_id)])
        new_snrgi_id = _insert_snrgi()
        if new_snrgi_id < 0:
            return prot.response_error('cannot copy snow management route group')

        try:
            for snri in snr_list:
                snri.snowroute_group_id = new_snrgi_id
                snri._snowroute_group = None
                snri.id = None
                snrDA.insert(snri, autocommit=False)
        except Exception as ex:
            snrDA.rollback()
            return prot.response_error('cannot copy snow management route group (fail to insert SnowRouteInfo)')

        snrDA.commit()
        snrDA.close()
        return prot.response_success(obj=new_snrgi_id)

    def _insert_snrgi():
        json_data = request.form.get('data')
        obj = json2snrgi(json_data)
        da_instance = SnowRouteGroupDataAccess()
        try:
            model_data = da_instance.insert(obj, autocommit=True)
        except exc.IntegrityError:
            da_instance.close()
            return -1
        except:
            da_instance.close()
            return -1

        inserted_id = model_data.id
        da_instance.commit()
        da_instance.close()

        return inserted_id
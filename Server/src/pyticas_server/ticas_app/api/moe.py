# -*- coding: utf-8 -*-
from pyticas_server.ticas_app import api_urls

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import base64
import json
import os
import uuid

from flask import request

from pyticas import period
from pyticas.infra import Infra
from pyticas.moe import moe
from pyticas.moe import writer
from pyticas.tool import tb
from pyticas_server import protocol as prot
from pyticas_server.protocol import json2route


def register_api(app):
    @app.route(api_urls.MOE_TT, methods=['POST'])
    def moe_tt():
        return _moe(moe.travel_time_md, 'Travel Time')

    @app.route(api_urls.MOE_SPEED, methods=['POST'])
    def moe_speed():
        return _moe(moe.speed_md, 'Station Speed')

    @app.route(api_urls.MOE_DENSITY, methods=['POST'])
    def moe_density():
        return _moe(moe.density_md, 'Station Density')

    @app.route(api_urls.MOE_OCCUPANCY, methods=['POST'])
    def moe_occupancy():
        return _moe(moe.occupancy_md, 'Station Occupancy')

    @app.route(api_urls.MOE_ACCELERATION, methods=['POST'])
    def moe_accel():
        return _moe(moe.acceleration_md, 'Station Acceleration')

    @app.route(api_urls.MOE_AVG_FLOW, methods=['POST'])
    def moe_avg_flow():
        return _moe(moe.average_flow_md, 'Average Lane Flow')

    @app.route(api_urls.MOE_TOTAL_FLOW, methods=['POST'])
    def moe_total_flow():
        return _moe(moe.total_flow_md, 'Total Flow')

    @app.route(api_urls.MOE_VMT, methods=['POST'])
    def moe_vmt():
        return _moe(moe.vmt_md, 'VMT')

    @app.route(api_urls.MOE_LVMT, methods=['POST'])
    def moe_lvmt():
        return _moe(moe.lvmt_md, 'LVMT')

    @app.route(api_urls.MOE_VHT, methods=['POST'])
    def moe_vht():
        return _moe(moe.vht_md, 'VHT')

    @app.route(api_urls.MOE_DVH, methods=['POST'])
    def moe_dvh():
        return _moe(moe.dvh_md, 'DVH')

    @app.route(api_urls.MOE_STT, methods=['POST'])
    def moe_stt():
        return _moe(moe.stt_md, 'Snapshot Travel Time', write_function=writer.write_stt)

    @app.route(api_urls.MOE_SV, methods=['POST'])
    def moe_sv():
        return _moe(moe.sv_md, 'Speed Variations', write_function=writer.write_sv)

    @app.route(api_urls.MOE_CM, methods=['POST'])
    def moe_cm():
        return _moe(moe.cm_md, 'Congested Miles', write_function=writer.write_cm)

    @app.route(api_urls.MOE_CMH, methods=['POST'])
    def moe_cmh():
        return _moe(moe.cmh_md, 'Congested Miles x Hours', write_function=writer.write_cmh)

    @app.route(api_urls.MOE_MRF, methods=['POST'])
    def moe_mrf():
        return _moe(moe.mrf_md, 'Mainline and Ramp Flow Rates', write_function=writer.write_mrf)

    @app.route(api_urls.MOE_RWIS, methods=['POST'])
    def moe_rwis():
        return prot.response_fail('Not Implemented')


def _moe(moe_func, moe_name, **kwargs):
    """

    :type moe_func: callable
    :type moe_name: str
    :return:
    """
    try:
        route_json = request.form.get('route', None)
        periods = request.form.get('periods', None)

        if not route_json or not periods:
            return prot.response_error('Invalid Parameter')

        r = json2route(route_json)

        period_list = []
        for prdinfo in json.loads(periods):
            prd = period.create_period(
                (prdinfo['start_year'], prdinfo['start_month'], prdinfo['start_date'], prdinfo['start_hour'],
                 prdinfo['start_min']),
                (prdinfo['end_year'], prdinfo['end_month'], prdinfo['end_date'], prdinfo['end_hour'],
                 prdinfo['end_min']),
                prdinfo['interval']
            )
            period_list.append(prd)

        tmp_dir = Infra.get_infra().get_path('moe_tmp', create=True)
        uid = str(uuid.uuid4())
        est_file = os.path.join(tmp_dir, '%s.xlsx' % uid)
        res = moe_func(r, period_list)
        write = kwargs.get('write_function', writer.write)
        write(est_file, r, res, **kwargs)

        encoded = None
        with open(est_file, 'rb') as f:
            xlsx_content = f.read()
            encoded = base64.b64encode(xlsx_content)

        if not encoded:
            return prot.response_error('ERROR : %s' % moe_name)

        os.remove(est_file)

        return prot.response_success(obj=encoded.decode('utf-8'))

    except Exception as ex:
        tb.traceback(ex)
        return prot.response_error('ERROR : %s' % moe_name)


def _output_path(sub_dir='', create=True):
    infra = Infra.get_infra()
    if sub_dir:
        output_dir = infra.get_path('moe/%s' % sub_dir, create=create)
    else:
        output_dir = infra.get_path('moe', create=create)

    if create and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        return os.path.abspath(output_dir)

    if os.path.exists(output_dir):
        return os.path.abspath(output_dir)
    else:
        return output_dir

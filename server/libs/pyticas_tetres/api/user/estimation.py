# -*- coding: utf-8 -*-
"""
estimation.py
~~~~~~~~~~~~~~

this module handles the request from `estimation tab` of `user client`

- corresponding API client in the admin client : `ticas.tetres.user.api.WorkzoneGroupClient`
"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os

from flask import request, send_from_directory

from pyticas.tool import json
from pyticas_server import protocol as prot
from pyticas_tetres import api_urls_user
from pyticas_tetres.est import workers
from pyticas_tetres.est.helper import util


def register_api(app):
    @app.route(api_urls_user.ESTIMATION, methods=['POST'])
    def tetres_user_estimation():
        routes = request.form.get('routeIDs')
        param = request.form.get('param')
        route_ids = json.loads(routes)
        eparam = json.loads(param)
        """:type: pyticas_tetres.ttypes.EstimationRequestInfo """
        setattr(eparam, 'travel_time_route', None)

        if not hasattr(eparam, 'oc_param'):
            return prot.response_invalid_request(message="Invalid Request (no oc_param)")

        uid = workers.estimate(route_ids, eparam)

        return prot.response_success({'uid': uid})

    @app.route(api_urls_user.ESTIMATION_RESULT, methods=['POST'])
    def tetres_user_get_result():
        uid = request.form.get('uid')
        if not uid:
            return prot.response_error('invalid request')

        output_path = util.output_path(uid, create=False)
        output_filepath = '%s.zip' % output_path

        # file is ready
        if os.path.exists(output_filepath):
            return prot.response_success('file is ready')

        # process is runninng
        elif os.path.exists(output_path):
            return prot.response_fail('process is running')

        # invalid uid
        else:
            return prot.response_error('invalid uid')

    @app.route(api_urls_user.ESTIMATION_DOWNLOAD, methods=['GET'])
    def tetres_user_download():
        uid = request.args.get('uid')
        if not uid:
            return 'not found : %s' % uid, 404

        output_dir_path = util.output_path()
        output_filepath = '%s.zip' % util.output_path(uid, create=False)

        # file is ready
        if not os.path.exists(output_filepath):
            return 'not found', 404

        return send_from_directory(directory=output_dir_path, filename='%s.zip' % uid)

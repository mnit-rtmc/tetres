# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import base64
import os
import uuid

from flask import request

from pyticas import rc
from pyticas.infra import Infra
from pyticas.tool import tb, json
from pyticas.ttypes import Route
from pyticas_server import protocol as prot
from pyticas_server.protocol import json2route
from pyticas_server.ticas_app import api_urls as api_urls
from pyticas_server.util import route_setup



def register_api(app):
    @app.route(api_urls.ROUTE_FROM_XLSX, methods=['POST', 'GET'])
    def ticas_route_from_cfg():
        file_content = request.form.get('xlsxcontent')
        r = rc.loader.load_from_contents(base64.b64decode(file_content))
        if not isinstance(r, Route):
            return prot.response_fail('fail to load_data route configuration file')

        return prot.response_success(obj=r)

    @app.route(api_urls.ROUTE_TO_XLSX, methods=['POST', 'GET'])
    def ticas_route_xlsx_content():
        route_content = request.form.get('route')
        r = json2route(route_content)
        if not r.cfg:
            r.cfg = rc.route_config.create_route_config(r.rnodes)

        try:
            tmp_dir = Infra.get_infra().get_path('tmp', create=True)
            uid = str(uuid.uuid4())
            filepath = os.path.join(tmp_dir, '%s.xlsx' % uid)
            rc.writer.write(filepath, r)
            with open(filepath, 'rb') as f:
                file_content = f.read()
                encoded = base64.b64encode(file_content)
                return prot.response_success(obj=encoded.decode('utf-8'))
        except Exception as ex:
            tb.traceback(ex)
            return prot.response_fail('fail to write route')

    def _json2route(json_str):
        tmp = json.loads(json_str)
        r = Route(tmp.name, tmp.desc)
        if not hasattr(tmp, 'cfg'):
            tmp.cfg = None
        if not hasattr(tmp, 'rnodes'):
            tmp.rnodes = []

        r.cfg = tmp.cfg
        r.rnodes = tmp.rnodes
        route_setup(r)
        return r

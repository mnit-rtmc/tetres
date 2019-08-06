# -*- coding: utf-8 -*-
import base64
import os
import uuid

from pyticas.infra import Infra
from pyticas.rn.route_config import route_config
from pyticas.tool import tb

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from flask import request

from pyticas import rc
from pyticas.ttypes import Route
from pyticas_server import protocol as prot
from pyticas_tetres import api_urls_admin
from pyticas_tetres.admin_auth import requires_auth
from pyticas_server.util import json2route

def register_api(app):
    @app.route(api_urls_admin.ROUTE_FROM_CFG, methods=['POST', 'GET'])
    @requires_auth
    def tetres_admin_route_from_cfg():
        file_content = request.form.get('cfgfile')
        r = rc.loader.load_from_contents(base64.b64decode(file_content))
        if not isinstance(r, Route):
            return prot.response_fail('fail to load_data route configuration file')

        return prot.response_success(r)

    @app.route(api_urls_admin.ROUTE_XLSX, methods=['POST', 'GET'])
    @requires_auth
    def tetres_admin_xlsx_content_from_route():
        route_content = request.form.get('route')
        r = json2route(route_content)
        try:
            tmp_dir = Infra.get_infra().get_path('tmp', create=True)
            uid = str(uuid.uuid4())
            filepath = os.path.join(tmp_dir, '%s.xlsx' % uid)
            if not r.cfg:
                r.cfg = route_config.create_route_config(r.rnodes)
            rc.writer.write(filepath, r)
            with open(filepath, 'rb') as f:
                file_content = f.read()
                encoded = base64.b64encode(file_content)
                return prot.response_success(obj=encoded.decode('utf-8'))
        except Exception as ex:
            tb.traceback(ex)
            return prot.response_fail('fail to write route')

# -*- coding: utf-8 -*-
from pyticas_server import cfg

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from flask import request

from pyticas.tool.json import dumps as jsonify


def register_api(app):
    @app.route('/ticas/ison', methods=['GET'])
    def ticas_is_on():
        return jsonify({'code': 1, 'msg': 'TICAS server is already running!'})

    if cfg.LOCAL_MODE:
        @app.route('/ticas/turnoff', methods=['GET'])
        def ticas_turn_off():
            def shutdown_server():
                func = request.environ.get('werkzeug.server.shutdown')
                if func is None:
                    raise RuntimeError('Not running with the Werkzeug Server')
                func()

            shutdown_server()
            return jsonify({'code': 1})

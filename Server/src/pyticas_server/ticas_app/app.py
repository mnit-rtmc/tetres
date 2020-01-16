# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from flask import make_response

from pyticas.tool.json import dumps as jsonify
from pyticas_server import api
from pyticas_server.logger import getLogger
from pyticas_server import cfg
from pyticas_server.app import TICASApp

class TICASBaseApp(TICASApp):


    def init(self, app):
        """
        :type app: Flask
        """
        @app.errorhandler(400)
        def not_found(error):
            return make_response(jsonify( { 'code' : -1, 'error': 'Bad request' } ), 400)

        @app.errorhandler(404)
        def not_found(error):
            return make_response(jsonify( { 'code' : -1, 'error': 'Not found' } ), 404)

        @app.route('/version', methods = ['GET'])
        def version():
            return api.API_VERSION


    def register_service(self, app):
        """
        :type app: Flask
        """
        logger = getLogger(__name__)
        logger.info('  - registering %s (LOCAL MODE=%s)' % (self.name, cfg.LOCAL_MODE))

        from pyticas_server.ticas_app.api import infra, system, route, moe
        modules = [infra, system, route, moe]

        for module in modules:
            module.register_api(app)

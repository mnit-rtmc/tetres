# -*- coding: utf-8 -*-
"""
pyticas_server.server
======================

server class which is a container of Flask app

"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import socket
import ssl

from flask import Flask
from flask_cors import CORS

from pyticas import ticas
from pyticas.infra import Infra
from pyticas_server import cfg
from pyticas_server.logger import getLogger
from pyticas_server.ticas_app.app import TICASBaseApp


class TICASServer(object):
    def __init__(self, data_path, **kwargs):
        self.data_path = data_path
        self.server = Flask(__name__, static_url_path="")
        CORS(self.server)
        cfg.LOCAL_MODE = kwargs.get('local_mode', cfg.LOCAL_MODE)
        self.apps = [TICASBaseApp("TICAS Base App")]

    def add_app(self, ticas_app):
        """ add application to TICASServer

        :param ticas_app:
        :type ticas_app:
        :return:
        :rtype:
        """
        self.apps.append(ticas_app)

    def start(self, port=None, debug=True, ssl_path=None, **kwargs):
        """ start server

        :type port: int
        :type debug: bool
        :type ssl_path: str
        :rtype:
        """

        logger = getLogger(__name__)
        if not ticas.is_initialized():
            logger.info('initializing TICAS')
            ticas.initialize(self.data_path)
            Infra.get_infra('', download=True)  # load_data recent roadway network

        logger.info('starting PyTICAS Apps')

        # create key and crt for HTTPS
        if ssl_path and len(ssl_path) == 2:
            # ssl_path[0] : `crt` file path
            # ssl_path[1] : `key` file path
            logger.info('creating SSL context...')
            # make_ssl_devcert(os.path.join(ssl_path, 'ssl'), host='localhost') # make dummy ssl
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.load_cert_chain(os.path.join(ssl_path[0]), os.path.join(ssl_path[1]))
        else:
            context = None

        # call init modules
        logger.info('loading init modules...')
        for app in self.apps:
            app.init(self.server)

        logger.info('registering service modules...')
        for app in self.apps:
            app.register_service(self.server)

        # run api web service
        if not port:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # faverolles 12/19/2019: socket change
            # sock.bind(('localhost', 0))
            sock.bind(('0.0.0.0', 0))
            port = sock.getsockname()[1]
            sock.close()

        self.server.run(debug=debug, port=port, ssl_context=context, **kwargs)

        logger.info('program terminated')

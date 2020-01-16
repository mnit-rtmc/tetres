# -*- coding: utf-8 -*-
"""
pyticas_ncrtes.app
===================
- app class used in `pyticas_server.server` module
"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_ncrtes.db import conn
from pyticas_ncrtes.logger import getLogger
from pyticas_server.app import TICASApp


class NCRTESApp(TICASApp):
    DB_INFO = None

    def __init__(self, name, DB_INFO):
        super().__init__(name)
        NCRTESApp.DB_INFO = DB_INFO

    def init(self, server):
        """ initialize application of F

        :type server: flask.Flask
        :rtype:
        """
        conn.connect(NCRTESApp.DB_INFO)
        conn.check_version()

    def register_service(self, server):
        """ register web services to the Flask server

        :type server: flask.Flask
        :rtype:
        """

        logger = getLogger(__name__)
        logger.info('  - registering {}'.format(self.name))

        # import API modules
        from pyticas_ncrtes.api import handlers

        for module in handlers:
            module.register_api(server)

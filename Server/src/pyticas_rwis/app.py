# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import pkgutil
from pyticas_rwis.logger import getLogger
from pyticas_server.app import TICASApp
from pyticas_rwis.db import conn

class RWISApiApp(TICASApp):

    def __init__(self, name, DB_INFO):
        super(RWISApiApp, self).__init__(name)
        self.DB_INFO = DB_INFO

    def init(self, app):
        conn.connect(self.DB_INFO)

    def register_service(self, app):
        logger = getLogger(__name__)
        logger.info('  - registering {}'.format(self.name))

        from pyticas_rwis.api import rwis_service
        modules = [ rwis_service]
        for module in modules:
            module.register_api(app)
        #
        # package = api
        # prefix = package.__name__ + "."
        # for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
        #     module = __import__(modname, fromlist="dummy")
        #     module.register_api(app)
        #
        # for mod in self.load_api_modules(__file__, __name__, 'api'):
        #     mod.register_api(app)

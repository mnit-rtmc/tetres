# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.tool import json
from pyticas_server.app import TICASApp
from pyticas_tetres import rservice, cfg
from pyticas_tetres import ttypes
from pyticas_tetres.db.tetres import conn
from pyticas_tetres.est import workers as user_workers
from pyticas_tetres.logger import getLogger
from pyticas_tetres.sched import worker as admin_worker

if ttypes not in json.TYPE_MODULES:
    json.TYPE_MODULES.append(ttypes)


class TeTRESApp(TICASApp):
    DB_INFO = None
    CAD_DB_INFO = None
    IRIS_DB_INFO = None

    def __init__(self, name, DB_INFO, CAD_DB_INFO=None, IRIS_DB_INFO=None):
        super(TeTRESApp, self).__init__(name)
        self.DB_INFO = DB_INFO
        self.CAD_DB_INFO = CAD_DB_INFO
        self.IRIS_DB_INFO = IRIS_DB_INFO

    def init(self, app):

        conn.connect(self.DB_INFO)
        conn.check_version()

        if self.CAD_DB_INFO:
            from pyticas_tetres.db.cad import conn as cad_conn
            cad_conn.connect(self.CAD_DB_INFO)

        if self.IRIS_DB_INFO:
            from pyticas_tetres.db.iris import conn as iris_conn
            iris_conn.connect(self.IRIS_DB_INFO)

        from pyticas_tetres.util import systemconfig
        systemconfig.initialize_system_config_info()

        rservice.start()
        admin_worker.start(1, self.DB_INFO, self.CAD_DB_INFO, self.IRIS_DB_INFO)
        user_workers.start(cfg.N_WORKERS_FOR_USER_CLIENT, self.DB_INFO, self.CAD_DB_INFO, self.IRIS_DB_INFO)

    def register_service(self, app):
        logger = getLogger(__name__)
        logger.info('  - registering {}'.format(self.name))

        from pyticas_tetres.api import tetres
        from pyticas_tetres.api.admin import (snowmgmt, snowevent, wz_group, specialevent, wz, snowroute, ttroute,
                                              actionlog, route, systemconfig, route_wise_moe_parameters)
        from pyticas_tetres.api.user import traveltime_info

        from pyticas_tetres.api.user import route as user_route
        from pyticas_tetres.api.user import estimation as user_estimation
        from pyticas_tetres.api import data_api

        # faverolles 12/26/2019: Added "api_additions/api_endpoints" to modules to be registered as well
        from api_extension import api_endpoints

        modules = [ttroute, snowevent, snowmgmt, snowroute,
                   specialevent, tetres, wz, wz_group,
                   traveltime_info, user_route, user_estimation, data_api,
                   actionlog, route, systemconfig, api_endpoints, route_wise_moe_parameters]

        for module in modules:
            module.register_api(app)
        #
        # package = api
        # prefix = package.__name__ + "."
        # for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
        #     module = __import__(modname, fromlist="dummy")
        #     module.register_api(app)

        # for mod in self.load_api_modules(__file__, __name__, 'api'):
        #     mod.register_api(app)

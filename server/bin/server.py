# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import sys, os, socket, getopt
import common
import dbinfo
from pyticas import tetresconf

def read_host_ip():
    """ read server host ip from `tetres.conf` file

    :rtype: str
    """
    return tetresconf.get_property('ticas.python_server_host_ip')

if __name__ == '__main__':
    
    port = 5000

    TeTRES_DB_INFO = dbinfo.tetres_db_info()
    CAD_DB_INFO = dbinfo.cad_db_info()
    IRIS_DB_INFO = dbinfo.iris_incident_db_info()

    print('DATA PATH : ', common.DATA_PATH)

    # import required modules
    from pyticas_server.server import TICASServer
    from pyticas_ncrtes.app import NCRTESApp
    from pyticas_tetres.app import TeTRESApp
    from pyticas_rwis.app import RWISApiApp

    from pyticas import ticas
    from pyticas.rn import infra_loader

    data_path = common.DATA_PATH

    # initialize with `DATA_PATH`
    ticas.initialize(data_path)

    # download the new 'metro.config.xml' from TMC
    infra_loader.load_metro('', download=True)

    # create server instance
    ticasServer = TICASServer(data_path, local_mode=False)
    ticasServer.add_app(NCRTESApp("NCRTES: Normal Condition Recovery Time Estimation System", dbinfo.ncrtes_db_info(data_path)))
    ticasServer.add_app(TeTRESApp("TeTRES: Travel Time Reliability Management System", TeTRES_DB_INFO, CAD_DB_INFO, IRIS_DB_INFO))
    # ticasServer.add_app(RWISApiApp("RWIS: RWIS Proxy Server", dbinfo.rwis_db_info()))

    # start server
    ticasServer.start(host=read_host_ip(), port=port, debug=True, use_reloader=False)

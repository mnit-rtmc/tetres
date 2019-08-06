# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_ncrtes.logger import getLogger
from pyticas_ncrtes.db import __DB_VERSION__

def initialize_database():
    logger = getLogger(__name__)
    logger.info('    - initialize database : add default nsr_data')

    from pyticas_ncrtes.db import conn

    conn.engine.execute("INSERT INTO config (name, content) VALUES ('version', '{}')".format(__DB_VERSION__))

    #conn.engine.execute("TRUNCATE incident_type")
    #conn.engine.execute("INSERT INTO incident_type (eventtype, eventtypecode, eventsubtype, eventsubtypecode) VALUES ('FATALITY CRASH', '1054', 'VEHICLE VS ANIMAL', 'ANIMAL')")
    #conn.engine.execute("INSERT INTO incident_type (eventtype, eventtypecode, eventsubtype, eventsubtypecode) VALUES ('FATALITY CRASH2', '10542', 'VEHICLE VS ANIMAL2', 'ANIMAL2')")

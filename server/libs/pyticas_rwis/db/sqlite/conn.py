# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pyticas.ticas import get_path
from pyticas_rwis.logger import getLogger
from pyticas_rwis.db import model

def connect(DB_INFO):
    """
    :rtype: (sqlalchemy.engine.Engine, sqlalchemy.engine.Connection, sqlalchemy.orm.session.Session)
    """
    logger = getLogger(__name__)
    logger.info('    - creating database connection...')
    # for SQLite
    engine = create_engine('sqlite:///' + os.path.join(get_path('db'), DB_INFO['filename']))
    connection = engine.connect()
    model.Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    return (engine, connection, session)



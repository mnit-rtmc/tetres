# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from pyticas.ticas import get_path
from pyticas_ncrtes.logger import getLogger
from pyticas_ncrtes.db import model


def connect(DB_INFO):
    """
    :rtype: (sqlalchemy.engine.Engine, sqlalchemy.engine.Connection, sqlalchemy.orm.scoped_session)
    """
    logger = getLogger(__name__)
    logger.info('creating database connection...')
    # for SQLite
    engine = create_engine('sqlite:///' + os.path.join(get_path('db'), DB_INFO['filename']))
    connection = engine.connect()
    model.Base.metadata.bind = engine
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    return (engine, connection, Session)



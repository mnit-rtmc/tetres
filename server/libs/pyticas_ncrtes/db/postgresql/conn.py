# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from pyticas_ncrtes.logger import getLogger
from pyticas_ncrtes.db import model

def connect(DB_INFO):
    """
    :rtype: (sqlalchemy.engine.Engine, sqlalchemy.engine.Connection, sqlalchemy.orm.scoped_session)
    """
    logger = getLogger(__name__)
    logger.info('creating database connection...')
    connection_string = 'postgresql+pg8000://{}:{}@{}:{}/{}'.format(DB_INFO['user'],
                                                    DB_INFO['passwd'],
                                                    DB_INFO['host'],
                                                    DB_INFO['port'],
                                                    DB_INFO['db_name'])

    engine = create_engine(connection_string, encoding='utf-8')
    connection = engine.connect()
    model.Base.metadata.bind = engine
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    return (engine, connection, Session)
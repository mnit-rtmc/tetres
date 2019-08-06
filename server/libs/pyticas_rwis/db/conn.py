# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_rwis.db import model
from pyticas_rwis.db.postgresql import conn as postgresql_connector
from pyticas_rwis.db.sqlite import conn as sqlite_connector

connection = None
""":type: sqlalchemy.engine.Connection """

Session = None
""":type: sqlalchemy.orm.scoped_session """

session = None
""":type: sqlalchemy.orm.Session """

engine = None
""":type: sqlalchemy.engine.Engine """

def get_session():
    """

    :rtype: sqlalchemy.orm.Session
    """
    return Session()

def connect(DB_INFO):
    global Session, session, engine, connection

    connectors = {
        'sqlite' : sqlite_connector,
        'postgresql' : postgresql_connector
    }

    (engine, connection, Session) = connectors.get(DB_INFO['engine'], 'sqlite').connect(DB_INFO)
    model.Base.metadata.create_all(engine)

def close():
    connection.close()
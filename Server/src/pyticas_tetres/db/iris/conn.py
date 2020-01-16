# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.db.iris.postgresql import conn as postgresql_connector

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

    :rtype: sqlalchemy.orm.session
    """
    return Session()

def connect(DB_INFO):
    global Session, session, engine, connection

    connectors = {
        'postgresql': postgresql_connector
    }
    (engine, connection, Session) = connectors.get(DB_INFO['engine'], 'postgresql').connect(DB_INFO)
    session = Session()

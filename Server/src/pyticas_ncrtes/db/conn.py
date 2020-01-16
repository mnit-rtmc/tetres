# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import ProgrammingError

from pyticas_ncrtes.db import __DB_VERSION__
from pyticas_ncrtes.db import model
from pyticas_ncrtes.db import setup as setup_db
from pyticas_ncrtes.db.postgresql import conn as postgresql_connector
from pyticas_ncrtes.db.sqlite import conn as sqlite_connector

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

    :rtype: sqlalchemy.orm.scoped_session
    """
    return Session()

def connect(DB_INFO):
    global Session, session, engine, connection

    connectors = {
        'sqlite': sqlite_connector,
        'postgresql': postgresql_connector
    }

    if engine:
        engine.dispose()

    (engine, connection, Session) = connectors.get(DB_INFO['engine'], 'sqlite').connect(DB_INFO)

    model.Base.metadata.create_all(engine)
    check_version()
    session = Session()


def check_version():
    try:
        session = get_session()
        versionInfo = session.query(model.Config).filter(model.Config.name == 'version').one()
        if versionInfo.content != __DB_VERSION__:
            raise Exception(
                'Operating ncrtes database version is not matched (old={} vs new={})'.format(versionInfo.content,
                                                                                            __DB_VERSION__))
    except (NoResultFound,ProgrammingError):
        setup_db.initialize_database()

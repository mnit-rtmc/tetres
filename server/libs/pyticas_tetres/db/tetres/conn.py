# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from sqlalchemy.orm.exc import NoResultFound

from pyticas_tetres.db import __DB_VERSION__
from pyticas_tetres.db.tetres import model
from pyticas_tetres.db.tetres import setup as setup_db
from pyticas_tetres.db.tetres.postgresql import conn as postgresql_connector

connection = None
""":type: sqlalchemy.engine.Connection """

Session = None
""":type: sqlalchemy.orm.scoped_session """

engine = None
""":type: sqlalchemy.engine.Engine """

SESSIONS = {}
""":type: dict[str, sqlalchemy.orm.Session]"""


def get_session():
    """

    :rtype: sqlalchemy.orm.session.Session
    """
    return Session()


def connect(DB_INFO):
    global Session, session, engine, connection

    connectors = {
        'postgresql': postgresql_connector
    }

    (engine, connection, Session) = connectors.get(DB_INFO['engine'], 'postgresql').connect(DB_INFO)

    model.Base.metadata.create_all(engine)


def check_version():
    try:
        session = get_session()
        versionInfo = session.query(model.Config).filter(model.Config.name == 'version').one()
        if versionInfo.content != __DB_VERSION__:
            raise Exception(
                'Operating TTRMS database version is not matched (old={} vs new={})'.format(versionInfo.content,
                                                                                            __DB_VERSION__))
    except NoResultFound:
        # setup database (default configurations)
        setup_db.initialize_database()

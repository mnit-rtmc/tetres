# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import calendar
import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, VARCHAR, BOOLEAN, DateTime, Float, TypeDecorator, String, Boolean
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base

from pyticas_tetres.db.cad.conn import engine

Base = declarative_base()

def utc2local(utc_time):
    """ convert UTC time string to localized unaware-timezone datetime
    :type utc_time: str or datetime.datetime
    :rtype: datetime.datetime
    """
    if isinstance(utc_time, str):
        utc_time = datetime.datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')
    timestamp = calendar.timegm(utc_time.timetuple())
    return datetime.datetime.fromtimestamp(timestamp)


class LocalDateTime(TypeDecorator):
    impl = DateTime

    def process_result_value(self, value, dialect):
        if value:
            return utc2local(value)
        else:
            return value


class CadeventView(Base):
    __table__ = Table('cadevent_view', Base.metadata,
                      Column('pkey', Integer, primary_key=True),
                      Column('openevent', BOOLEAN, nullable=True),
                      Column('cameranum', Integer, nullable=True),
                      Column('cdts', LocalDateTime(timezone=True), nullable=True),
                      Column('udts', LocalDateTime(timezone=True), nullable=True),
                      Column('xdts', LocalDateTime(timezone=True), nullable=True),
                      Column('eventtype', VARCHAR(255), nullable=True),
                      Column('eventsubtype', VARCHAR(255), nullable=True),
                      Column('classification', VARCHAR(255), nullable=True),
                      Column('iris_class', VARCHAR(255), nullable=True),
                      Column('iris_detail', VARCHAR(255), nullable=True),
                      Column('blocking', BOOLEAN, nullable=True),
                      Column('occupied', BOOLEAN, nullable=True),
                      Column('rollover', BOOLEAN, nullable=True),
                      Column('injury', BOOLEAN, nullable=True),
                      Column('fatal', BOOLEAN, nullable=True),
                      Column('lat', Float, nullable=True),
                      Column('lon', Float, nullable=True),
                      Column('geom', Geometry, nullable=True),
                      Column('earea', VARCHAR(255), nullable=True),
                      Column('ecompl', VARCHAR(255), nullable=True),
                      Column('edirpre', VARCHAR(255), nullable=True),
                      Column('edirsuf', VARCHAR(255), nullable=True),
                      Column('efeanme', VARCHAR(255), nullable=True),
                      Column('efeatyp', VARCHAR(255), nullable=True),
                      Column('xstreet1', VARCHAR(255), nullable=True),
                      Column('xstreet2', VARCHAR(255), nullable=True),
                      )
                      # autoload=True, autoload_with=engine)

class CADIncidentType(Base):
    """

    """
    __tablename__ = 'eventtype'
    pkey = Column(Integer, primary_key=True)
    eventtype = Column(String(80), nullable=False)
    eventsubtype = Column(String(50), nullable=False)
    eventtypecode = Column(String(16), nullable=False)
    eventsubtypecode = Column(String(16), nullable=False)
    classification = Column(String(20), nullable=True)
    iris_class = Column(String(20), nullable=True)
    iris_detail = Column(String(25), nullable=True)
    blocking = Column(Boolean, nullable=True)
    occupied = Column(Boolean, nullable=True)
    rollover = Column(Boolean, nullable=True)
    injury = Column(Boolean, nullable=True)
    fatal = Column(Boolean, nullable=True)
    cars_eventtype = Column(VARCHAR(80), nullable=True)
    cars_eventtypecode = Column(VARCHAR(16), nullable=True)

    def __repr__(self):
        return '<CADIncidentType pkey="%s" eventtype="%s" eventsubtype="%s">' % (self.pkey, self.eventtype, self.eventsubtype)

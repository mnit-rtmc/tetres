# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import calendar

from sqlalchemy import Column, Integer, VARCHAR, BOOLEAN, DateTime, Float, TypeDecorator, Text
from sqlalchemy.ext.declarative import declarative_base

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

class IrisIncident(Base):
    __tablename__ = 'incident_view'
    event_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(16), unique=True, nullable=True)
    event_date = Column(LocalDateTime(timezone=True), nullable=True)
    description = Column(Text, nullable=True)
    road = Column(VARCHAR(20), nullable=True)
    direction = Column(VARCHAR(4), nullable=True)
    impact = Column(VARCHAR(20), nullable=True)
    cleared = Column(BOOLEAN, nullable=True)
    confirmed = Column(BOOLEAN, nullable=True)
    camera = Column(VARCHAR(10), nullable=True)
    lane_type = Column(VARCHAR(12), nullable=True)
    detail = Column(VARCHAR(8), nullable=True)
    replaces = Column(VARCHAR(16), nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)

    def __repr__(self):
        return '<IrisIncident id="%s" name="%s">' % (self.event_id, self.name)

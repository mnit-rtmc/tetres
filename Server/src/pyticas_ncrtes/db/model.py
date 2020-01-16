# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, VARCHAR, Float, Text
from sqlalchemy import DateTime, Date, Boolean, CHAR, UnicodeText, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Config(Base):
    __tablename__ = 'config'
    name = Column(VARCHAR(255), nullable=False, primary_key=True)
    content = Column(Text, nullable=True)

    def get_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content
        }


class SnowEvent(Base):
    """

    """
    __tablename__ = 'snowevent'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    reg_date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    _estimated_ncrts = relationship("EstimatedNCRT", cascade="all, delete-orphan")

    def __repr__(self):
        return '<SnowEvent: {}>'.format(self.id)


class SnowRoute(Base):
    """

    """
    __tablename__ = 'snowroute'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(100), nullable=False)
    description = Column(Text, nullable=True)
    route1 = Column(UnicodeText, nullable=False)
    route2 = Column(UnicodeText, nullable=False)
    reg_date = Column(DateTime, nullable=False, default=datetime.datetime.now)

    snowroute_group_id = Column(Integer, ForeignKey('snowroute_group.id'), nullable=False)
    _snowroute_group = relationship("SnowRouteGroup")
    _estimated_ncrts = relationship("EstimatedNCRT", cascade="all, delete-orphan")
    def __repr__(self):
        return '<SnowRoute: {}>'.format(self.id)


class SnowRouteGroup(Base):
    """

    """
    __tablename__ = 'snowroute_group'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(50), nullable=True)
    region = Column(VARCHAR(50), nullable=True)
    sub_region = Column(VARCHAR(50), nullable=True)
    year = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    reg_date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    _snowroutes = relationship("SnowRoute", cascade="all, delete-orphan")

    def __repr__(self):
        return '<SnowRouteGroup: {}>'.format(self.id)


class EstimatedNCRT(Base):
    """

    """
    __tablename__ = 'estimated_ncrt'
    id = Column(Integer, primary_key=True)
    station_id = Column(VARCHAR(10), nullable=False)
    sroute_id = Column(Integer, ForeignKey('snowroute.id'), nullable=False)
    sevent_id = Column(Integer, ForeignKey('snowevent.id'), nullable=False)
    _snowroute = relationship("SnowRoute")
    _snowevent = relationship("SnowEvent")
    recovery_percent = Column(Float, nullable=False)
    recovery_time = Column(DateTime, nullable=False)
    reg_date = Column(DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return '<EstimatedNCRT: {}>'.format(self.id)


class WinterSeason(Base):
    __tablename__ = 'winterseason'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    year = Column(Integer, nullable=False)
    months = Column(Text, nullable=False)

    def __repr__(self):
        return '<WinterSeason name="%s" year=%s>' % (self.name, self.year)



class NormalData(Base):
    __tablename__ = 'normal_data'
    winterseason_id = Column(Integer, ForeignKey('winterseason.id'), nullable=False)
    _winterseason = relationship("WinterSeason")
    id = Column(Integer, primary_key=True)
    station_id = Column(VARCHAR(10), nullable=False)
    data = Column(UnicodeText, nullable=False)

    def __repr__(self):
        return '<NormalData: {}>'.format(self.id)


class NormalFunction(Base):
    __tablename__ = 'normal_funcs'
    winterseason_id = Column(Integer, ForeignKey('winterseason.id'), nullable=False)
    _winterseason = relationship("WinterSeason")
    id = Column(Integer, primary_key=True)
    station_id = Column(VARCHAR(10), nullable=False)
    func = Column(UnicodeText, nullable=False)

    def __repr__(self):
        return '<NormalFunction: {}>'.format(self.id)


class TargetStation(Base):
    """

    """
    __tablename__ = 'target_station'
    id = Column(Integer, primary_key=True)
    winterseason_id = Column(Integer, ForeignKey('winterseason.id'), nullable=False)
    _winterseason = relationship("WinterSeason")
    snowroute_id = Column(Integer, ForeignKey('snowroute.id'), nullable=True)
    snowroute_name = Column(VARCHAR(50), nullable=True)
    _snowroute = relationship("SnowRoute")
    station_id = Column(VARCHAR(10), nullable=False)
    corridor_name = Column(VARCHAR(50), nullable=False)
    normal_function_id = Column(Integer, ForeignKey('normal_funcs.id'), nullable=True)
    _normal_function = relationship("NormalFunction")

    def __repr__(self):
        return '<TargetStation: {}>'.format(self.station_id)


class TargetLaneConfig(Base):
    """

    """
    __tablename__ = 'target_lane'
    id = Column(Integer, primary_key=True)
    winterseason_id = Column(Integer, ForeignKey('winterseason.id'), nullable=False)
    _winterseason = relationship("WinterSeason")
    station_id = Column(VARCHAR(10), nullable=False)
    corridor_name = Column(VARCHAR(50), nullable=False)
    detectors = Column(VARCHAR(255), nullable=True)

    def __repr__(self):
        return '<TargetLaneConfig: {}>'.format(self.station_id)


class TargetStationManual(Base):
    """

    """
    __tablename__ = 'target_station_manual'
    id = Column(Integer, primary_key=True)
    corridor_name = Column(VARCHAR(20), nullable=False)
    station_id = Column(VARCHAR(20), nullable=False)

    def __repr__(self):
        return '<TargetStationManual: {}>'.format(self.station_id)


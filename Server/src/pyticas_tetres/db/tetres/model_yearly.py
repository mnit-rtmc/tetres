# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import time

from sqlalchemy import Column, Integer
from sqlalchemy import ForeignKey, DateTime, Float, UniqueConstraint, VARCHAR, CHAR, UnicodeText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from pyticas_tetres.db.tetres import conn
from pyticas_tetres.db.tetres.model import WorkZone, Specialevent, SnowManagement, Incident, TTRoute

TTTables = {}
TTWeatherTables = {}
TTWorkzoneTables = {}
TTIncidentTables = {}
TTSnowmgmtTables = {}
TTSpecialeventTables = {}
WeatherTables = {}
NOAATables = {}


def create_year_tables(years):
    """
    :type years: list[int]
    """
    for y in years:
        create_year_table(y)


def create_year_table(year):
    """
    :type year: int
    """

    # inspector = Inspector.from_engine(engine)
    # table_names = inspector.get_table_names()
    # from pyticas_tetres.db.model import Base
    Base = declarative_base(bind=conn.engine)

    # faverolles 10/8/2019 NOTE: MOE
    tt_table = type('TravelTime%d' % year, (Base,), {
        '__tablename__': 'tt_%d' % year,
        'id': Column(Integer, primary_key=True, autoincrement=True),
        'route_id': Column(Integer, ForeignKey(TTRoute.id, ondelete='CASCADE'), nullable=False, index=True),
        'route': relationship(TTRoute, backref=backref('tt_%d' % year)),
        'time': Column(DateTime, nullable=False),
        'tt': Column(Float, nullable=False),
        'vmt': Column(Float, nullable=True),
        'speed': Column(Float, nullable=True),
        'vht': Column(Float, nullable=True),
        'dvh': Column(Float, nullable=True),
        'lvmt': Column(Float, nullable=True),
        'uvmt': Column(Float, nullable=True),
        "cm": Column(Float, nullable=True),
        "cmh": Column(Float, nullable=True),
        "acceleration": Column(Float, nullable=True),
        "meta_data": Column(UnicodeText, nullable=False),

        # 'sv': Column(Float, nullable=True),
        '_tt_weathers': relationship('TTWeather%d' % year, lazy='joined'),
        '_tt_incidents': relationship('TTIncident%d' % year, lazy='joined'),
        '_tt_workzones': relationship('TTWorkzone%d' % year, lazy='joined'),
        '_tt_specialevents': relationship('TTSpecialevent%d' % year, lazy='joined'),
        '_tt_snowmanagements': relationship('TTSnowmgmt%d' % year, lazy='joined'),
        '__table_args__': (UniqueConstraint('route_id', 'time', name='_tt_uc_%d' % year),)
    })
    tt_table.__repr__ = lambda self: \
        '<TravelTime%d id="%d" route_id="%d" time="%s" tt="%.1f" vmt="%.1f" speed="%.1f>' % (
            year, self.id, self.route_id, self.time, self.tt, self.vmt, self.speed)
    tt_table.__str__ = tt_table.__repr__

    noaa_table = type('Noaa%d' % year, (Base,), {
        '__tablename__': 'noaa_weather_%d' % year,
        'id': Column(Integer, primary_key=True, unique=True, autoincrement=True),
        'usaf': Column(VARCHAR(6), nullable=False),
        'wban': Column(VARCHAR(5), nullable=False),
        'dtime': Column(DateTime, nullable=False),
        'precip': Column(Float, nullable=True),
        'precip_type': Column(VARCHAR(4), nullable=True),
        'precip_intensity': Column(VARCHAR(4), nullable=True),
        'precip_qc': Column(VARCHAR(4), nullable=True),
        'visibility': Column(Float, nullable=True),
        'visibility_qc': Column(VARCHAR(4), nullable=True),
        'obscuration': Column(VARCHAR(4), nullable=True),
        'descriptor': Column(VARCHAR(4), nullable=True),
        'air_temp': Column(Float, nullable=True),
        'air_temp_qc': Column(VARCHAR(4), nullable=True),
        'dew_point': Column(Float, nullable=True),
        'dew_point_qc': Column(VARCHAR(4), nullable=True),
        'relative_humidity': Column(Float, nullable=True),
        'wind_dir': Column(Integer, nullable=True),
        'wind_dir_qc': Column(VARCHAR(4), nullable=True),
        'wind_speed': Column(Float, nullable=True),
        'wind_speed_qc': Column(VARCHAR(4), nullable=True),
        'wind_gust': Column(Float, nullable=True),
        'wind_gust_qc': Column(VARCHAR(4), nullable=True),

    })
    noaa_table.__repr__ = lambda self: \
        '<NoaaWeather%d id="%d" usaf="%s" wban="%s" time="%s" precip="%s" precip_type="%s">' % (
            year, self.id, self.usaf, self.wban, self.dtime, self.precip, self.precip_type)
    noaa_table.__str__ = noaa_table.__repr__

    tt_weather_table = type('TTWeather%d' % year, (Base,), {
        '__tablename__': 'tt_weather_%d' % year,
        'id': Column(Integer, primary_key=True, unique=True, autoincrement=True),
        'tt_id': Column(Integer, ForeignKey('tt_%d.id' % year, ondelete='CASCADE'), primary_key=True, index=True),
        '_tt': relationship(tt_table, backref=backref('tt_weather_%d' % year)),
        'weather_id': Column(Integer, ForeignKey('noaa_weather_%d.id' % year, ondelete='CASCADE'), index=True),
        '_weather': relationship(noaa_table, backref=backref('tt_weather_%d' % year)),
        'is_extended': False,
    })
    setattr(tt_weather_table, 'oc_field', 'weather_id')
    tt_weather_table.__repr__ = lambda self: \
        '<TTWeather%d id="%d" tt_id="%d" weather_id="%d" precip="%s" precip_type="%s" precip_intensity="%s">' % (
            year, self.id, self.tt_id, self.weather_id,
            self._weather.precip if self._weather else 'N/A',
            self._weather.precip_type if self._weather else 'N/A',
            self._weather.precip_intensity if self._weather else 'N/A',)
    tt_weather_table.__str__ = tt_weather_table.__repr__

    tt_workzone_table = type('TTWorkzone%d' % year, (Base,), {
        '__tablename__': 'tt_workzone_%d' % year,
        'id': Column(Integer, primary_key=True, unique=True, autoincrement=True),
        'tt_id': Column(Integer, ForeignKey('tt_%d.id' % year, ondelete='CASCADE'), nullable=False, index=True),
        '_tt': relationship(tt_table, backref=backref('tt_workzone_%d' % year)),
        'workzone_id': Column(Integer, ForeignKey(WorkZone.id, ondelete='CASCADE'), nullable=False, index=True),
        '_workzone': relationship(WorkZone),
        'loc_type': Column(Integer, nullable=True),
        'distance': Column(Float, nullable=True),  # in mile
        'off_distance': Column(Float, nullable=True),  # in mile
        'is_extended': False,
    })
    setattr(tt_workzone_table, 'oc_field', 'workzone_id')
    tt_workzone_table.__repr__ = lambda self: \
        '<TTWorkZone%d id="%d" tt_id="%d" workzone_id="%d" loc_type="%d" distance="%.2f" off_distance="%.2f">' % (
            year, self.id, self.tt_id, self.workzone_id, self.loc_type, self.distance, self.off_distance)
    tt_workzone_table.__str__ = tt_workzone_table.__repr__

    tt_specialevent_table = type('TTSpecialevent%d' % year, (Base,), {
        '__tablename__': 'tt_specialevent_%d' % year,
        'id': Column(Integer, primary_key=True, unique=True, autoincrement=True),
        'tt_id': Column(Integer, ForeignKey('tt_%d.id' % year, ondelete='CASCADE'), nullable=False, index=True),
        '_tt': relationship(tt_table, backref=backref('tt_specialevent_%d' % year)),
        'specialevent_id': Column(Integer, ForeignKey(Specialevent.id, ondelete='CASCADE'), nullable=False, index=True),
        '_specialevent': relationship(Specialevent),
        'distance': Column(Float, nullable=False),  # in mile
        'event_type': Column(CHAR, nullable=False),
        'is_extended': False,
    })
    setattr(tt_specialevent_table, 'oc_field', 'specialevent_id')
    tt_specialevent_table.__repr__ = lambda self: \
        '<TTSpecialEvent%d id="%d" tt_id="%d" specialevent_id="%d" distance="%d" event_type="%s">' % (
            year, self.id, self.tt_id, self.specialevent_id, self.distance,
            self.event_type)
    tt_specialevent_table.__str__ = tt_specialevent_table.__repr__

    tt_snowmgmt_table = type('TTSnowmgmt%d' % year, (Base,), {
        '__tablename__': 'tt_snowmgmt_%d' % year,
        'id': Column(Integer, primary_key=True, unique=True, autoincrement=True),
        'tt_id': Column(Integer, ForeignKey('tt_%d.id' % year, ondelete='CASCADE'), nullable=False, index=True),
        '_tt': relationship(tt_table, backref=backref('tt_snowmgmt_%d' % year)),
        'snowmgmt_id': Column(Integer, ForeignKey(SnowManagement.id, ondelete='CASCADE'), nullable=False, index=True),
        '_snowmgmt': relationship(SnowManagement),
        'loc_type': Column(Integer, nullable=True),
        'distance': Column(Float, nullable=True),  # in mile
        'off_distance': Column(Float, nullable=True),  # in mile
        'road_status': Column(Integer, nullable=True),
        'recovery_level': Column(Integer, nullable=True),
        'is_extended': False,
    })
    setattr(tt_snowmgmt_table, 'oc_field', 'snowmgmt_id')
    tt_snowmgmt_table.__repr__ = lambda self: \
        '<TTSnowManagement%d id="%d" tt_id="%d" snowmgmt_id="%d"' \
        ' loc_type="%d" distance="%.2f" off_distance="%.2f" road_status="%d">' % (
            year, self.id, self.tt_id, self.snowmgmt_id,
            self.loc_type, self.distance, self.off_distance, self.road_status)
    tt_snowmgmt_table.__str__ = tt_snowmgmt_table.__repr__

    tt_incident_table = type('TTIncident%d' % year, (Base,), {
        '__tablename__': 'tt_incident_%d' % year,
        'id': Column(Integer, primary_key=True, unique=True, autoincrement=True),
        'tt_id': Column(Integer, ForeignKey('tt_%d.id' % year, ondelete='CASCADE'), nullable=False, index=True),
        '_tt': relationship(tt_table, backref=backref('tt_incident_%d' % year)),
        'incident_id': Column(Integer, ForeignKey(Incident.id, ondelete='CASCADE'), nullable=False, index=True),
        '_incident': relationship(Incident),
        'distance': Column(Float, nullable=True),
        'off_distance': Column(Float, nullable=True),
        'is_extended': False,
    })
    setattr(tt_incident_table, 'oc_field', 'incident_id')
    tt_incident_table.__repr__ = lambda self: \
        '<TTIncidentInfo%d id="%d" tt_id="%d" incident_id="%d" distance="%.2f" off_distance="%.2f">' % (
            year, self.id, self.tt_id, self.incident_id, self.distance, self.off_distance)
    tt_incident_table.__str__ = tt_incident_table.__repr__

    TTTables[year] = tt_table
    TTWeatherTables[year] = tt_weather_table
    TTWorkzoneTables[year] = tt_workzone_table
    TTIncidentTables[year] = tt_incident_table
    TTSnowmgmtTables[year] = tt_snowmgmt_table
    TTSpecialeventTables[year] = tt_specialevent_table
    # WeatherTables[year] = weather_table
    NOAATables[year] = noaa_table

    for _ in range(10):
        try:
            Base.metadata.create_all()
            break
        except Exception as ex:
            # print('=-> exception occured when create yearly table : ', year)
            time.sleep(1)


def get_tt_table(year):
    table = TTTables.get(year, None)
    if not table:
        create_year_table(year)
        table = TTTables.get(year)
    return table


def get_tt_weather_table(year):
    return _yearly_table(TTWeatherTables, year)


def get_tt_workzone_table(year):
    return _yearly_table(TTWorkzoneTables, year)


def get_tt_incident_table(year):
    return _yearly_table(TTIncidentTables, year)


def get_tt_snowmgmt_table(year):
    return _yearly_table(TTSnowmgmtTables, year)


def get_tt_specialevent_table(year):
    return _yearly_table(TTSpecialeventTables, year)


def get_weather_table(year):
    return _yearly_table(WeatherTables, year)


def get_noaa_table(year):
    return _yearly_table(NOAATables, year)


def _yearly_table(tables, year):
    table = tables.get(year, None)
    if not table:
        create_year_table(year)
        table = tables.get(year)
    return table

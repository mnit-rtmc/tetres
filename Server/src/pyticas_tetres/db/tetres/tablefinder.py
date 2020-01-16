# -*- coding: utf-8 -*-
from pyticas_tetres.da.config import ConfigDataAccess

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from sqlalchemy.ext.declarative import declarative_base
from pyticas_tetres.da.route import TTRouteDataAccess
from pyticas_tetres.da.weather import WeatherDataAccess
from pyticas_tetres.da.incident import IncidentDataAccess
from pyticas_tetres.da.wz import WorkZoneDataAccess
from pyticas_tetres.da.wz_group import WZGroupDataAccess
from pyticas_tetres.da.wz_laneconfig import WZLaneConfigDataAccess
from pyticas_tetres.da.wz_feature import WZFeatureDataAccess
from pyticas_tetres.da.specialevent import SpecialEventDataAccess
from pyticas_tetres.da.snowevent import SnowEventDataAccess
from pyticas_tetres.da.snowroute import SnowRouteDataAccess
from pyticas_tetres.da.snowmgmt import SnowMgmtDataAccess
from pyticas_tetres.da.tt import TravelTimeDataAccess
from pyticas_tetres.da.tt_weather import TTWeatherDataAccess
from pyticas_tetres.da.tt_incident import TTIncidentDataAccess
from pyticas_tetres.da.tt_workzone import TTWorkZoneDataAccess
from pyticas_tetres.da.tt_specialevent import TTSpecialeventDataAccess
from pyticas_tetres.da.tt_snowmgmt import TTSnowManagementDataAccess
from pyticas_tetres.da.tod_reliability import TODReliabilityDataAccess

def find_by_tablename(tablename):
    """
    :type tablename: str
    :rtype: sqlalchemy.Table
    """
    Base = declarative_base()
    for c in Base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c
    return None

def get_da_instance_by_tablename(tablename):
    """
    :type tablename: str
    :rtype: pyticas_tetres.da.data_access.DataAccess
    """
    das = [TTRouteDataAccess, IncidentDataAccess, WorkZoneDataAccess, WZGroupDataAccess, WZLaneConfigDataAccess,
           WZFeatureDataAccess, SpecialEventDataAccess, SnowEventDataAccess, SnowRouteDataAccess,
           SnowMgmtDataAccess, TODReliabilityDataAccess, ConfigDataAccess ]

    yearly_das = [ TravelTimeDataAccess, TTWeatherDataAccess, TTIncidentDataAccess, TTWorkZoneDataAccess,
           TTSpecialeventDataAccess, TTSnowManagementDataAccess, WeatherDataAccess ]

    year_part = tablename[-4:]
    year = None

    if year_part.isdigit() and int(year_part) > 10000:
        das = yearly_das
        year = int(year_part)

    for da in das:
        da_instance = da(year) if year else da()
        if da_instance.get_model().__table__.name == tablename:
            return da_instance
        da_instance.close_session()

    return None

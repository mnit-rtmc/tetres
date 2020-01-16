# -*- coding: utf-8 -*-
"""
systemconfig.py
~~~~~~~~~~~~~~

this module handles the request from `system configuration tab` of `admin client`

"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.tool import json
from pyticas_tetres import cfg
from pyticas_tetres.da.config import ConfigDataAccess
from pyticas_tetres.ttypes import SystemConfigInfo


def initialize_system_config_info():
    da = ConfigDataAccess()
    config_data = da.get_by_name(cfg.OPT_NAME_SYSCONFIG)
    if not config_data or not config_data.content:
        syscfg = get_system_config_info()
        da.insert_or_update(cfg.OPT_NAME_SYSCONFIG, json.dumps(syscfg))
        da.commit()
    else:
        syscfg = json.loads(config_data.content)
        cfg.DATA_ARCHIVE_START_YEAR = syscfg.data_archive_start_year
        cfg.DAILY_JOB_OFFSET_DAYS = syscfg.daily_job_offset_days
        cfg.DAILY_JOB_START_TIME = syscfg.daily_job_start_time
        cfg.WEEKLY_JOB_START_WEEKDAY = syscfg.weekly_job_start_day
        cfg.WEEKLY_JOB_START_TIME = syscfg.weekly_job_start_time
        cfg.MONTHLY_JOB_START_DAY = syscfg.monthly_job_start_date
        cfg.MONTHLY_JOB_START_TIME = syscfg.monthly_job_start_time
        cfg.INCIDENT_DOWNSTREAM_DISTANCE_LIMIT = syscfg.incident_downstream_distance_limit
        cfg.INCIDENT_UPSTREAM_DISTANCE_LIMIT = syscfg.incident_upstream_distance_limit
        cfg.WZ_DOWNSTREAM_DISTANCE_LIMIT = syscfg.workzone_downstream_distance_limit
        cfg.WZ_UPSTREAM_DISTANCE_LIMIT = syscfg.workzone_upstream_distance_limit
        cfg.SE_ARRIVAL_WINDOW = syscfg.specialevent_arrival_window
        cfg.SE_DEPARTURE_WINDOW1 = syscfg.specialevent_departure_window1
        cfg.SE_DEPARTURE_WINDOW2 = syscfg.specialevent_departure_window2

        # faverolles 1/12/2020: Adding AdminClient MOE Config Parameters
        cfg.MOE_CRITICAL_DENSITY = syscfg.moe_critical_density
        cfg.MOE_LANE_CAPACITY = syscfg.moe_lane_capacity
        cfg.MOE_CONGESTION_THRESHOLD_SPEED = syscfg.moe_congestion_threshold_speed


    da.close_session()


def get_system_config_info():
    """

    :rtype: pyticas_tetres.ttypes.SystemConfigInfo
    """

    syscfg = SystemConfigInfo()

    syscfg.data_archive_start_year = cfg.DATA_ARCHIVE_START_YEAR

    syscfg.daily_job_offset_days = cfg.DAILY_JOB_OFFSET_DAYS
    syscfg.daily_job_start_time = cfg.DAILY_JOB_START_TIME

    syscfg.weekly_job_start_day = cfg.WEEKLY_JOB_START_WEEKDAY
    syscfg.weekly_job_start_time = cfg.WEEKLY_JOB_START_TIME

    syscfg.monthly_job_start_date = cfg.MONTHLY_JOB_START_DAY
    syscfg.monthly_job_start_time = cfg.MONTHLY_JOB_START_TIME

    syscfg.incident_downstream_distance_limit = cfg.INCIDENT_DOWNSTREAM_DISTANCE_LIMIT
    syscfg.incident_upstream_distance_limit = cfg.INCIDENT_UPSTREAM_DISTANCE_LIMIT

    syscfg.workzone_downstream_distance_limit = cfg.WZ_DOWNSTREAM_DISTANCE_LIMIT
    syscfg.workzone_upstream_distance_limit = cfg.WZ_UPSTREAM_DISTANCE_LIMIT

    syscfg.specialevent_arrival_window = cfg.SE_ARRIVAL_WINDOW
    syscfg.specialevent_departure_window1 = cfg.SE_DEPARTURE_WINDOW1
    syscfg.specialevent_departure_window2 = cfg.SE_DEPARTURE_WINDOW2

    # faverolles 1/12/2020: Adding AdminClient MOE Config Parameters
    syscfg.moe_critical_density = cfg.MOE_CRITICAL_DENSITY
    syscfg.moe_lane_capacity = cfg.MOE_LANE_CAPACITY
    syscfg.moe_congestion_threshold_speed = cfg.MOE_CONGESTION_THRESHOLD_SPEED

    return syscfg


def set_system_config_info(syscfg):
    """

    :rtype: pyticas_tetres.ttypes.SystemConfigInfo
    """
    da = ConfigDataAccess()
    inserted = da.insert_or_update(cfg.OPT_NAME_SYSCONFIG, json.dumps(syscfg))
    if inserted == False or not da.commit():
        da.close_session()
        return False

    prev_syscfg = SystemConfigInfo()
    prev_syscfg.data_archive_start_year = cfg.DATA_ARCHIVE_START_YEAR
    prev_syscfg.daily_job_offset_days = cfg.DAILY_JOB_OFFSET_DAYS
    prev_syscfg.daily_job_start_time = cfg.DAILY_JOB_START_TIME
    prev_syscfg.weekly_job_start_day = cfg.WEEKLY_JOB_START_WEEKDAY
    prev_syscfg.weekly_job_start_time = cfg.WEEKLY_JOB_START_TIME
    prev_syscfg.monthly_job_start_date = cfg.MONTHLY_JOB_START_DAY
    prev_syscfg.monthly_job_start_time = cfg.MONTHLY_JOB_START_TIME
    prev_syscfg.incident_downstream_distance_limit = cfg.INCIDENT_DOWNSTREAM_DISTANCE_LIMIT
    prev_syscfg.incident_upstream_distance_limit = cfg.INCIDENT_UPSTREAM_DISTANCE_LIMIT
    prev_syscfg.workzone_downstream_distance_limit = cfg.WZ_DOWNSTREAM_DISTANCE_LIMIT
    prev_syscfg.workzone_upstream_distance_limit = cfg.WZ_UPSTREAM_DISTANCE_LIMIT
    prev_syscfg.specialevent_arrival_window = cfg.SE_ARRIVAL_WINDOW
    prev_syscfg.specialevent_departure_window1 = cfg.SE_DEPARTURE_WINDOW1
    prev_syscfg.specialevent_departure_window2 = cfg.SE_DEPARTURE_WINDOW2

    # faverolles 1/12/2020: Adding AdminClient MOE Config Parameters
    prev_syscfg.moe_critical_density = cfg.MOE_CRITICAL_DENSITY
    prev_syscfg.moe_lane_capacity = cfg.MOE_LANE_CAPACITY
    prev_syscfg.moe_congestion_threshold_speed = cfg.MOE_CONGESTION_THRESHOLD_SPEED

    cfg.DATA_ARCHIVE_START_YEAR = syscfg.data_archive_start_year
    cfg.DAILY_JOB_OFFSET_DAYS = syscfg.daily_job_offset_days
    cfg.DAILY_JOB_START_TIME = syscfg.daily_job_start_time
    cfg.WEEKLY_JOB_START_WEEKDAY = syscfg.weekly_job_start_day
    cfg.WEEKLY_JOB_START_TIME = syscfg.weekly_job_start_time
    cfg.MONTHLY_JOB_START_DAY = syscfg.monthly_job_start_date
    cfg.MONTHLY_JOB_START_TIME = syscfg.monthly_job_start_time
    cfg.INCIDENT_DOWNSTREAM_DISTANCE_LIMIT = syscfg.incident_downstream_distance_limit
    cfg.INCIDENT_UPSTREAM_DISTANCE_LIMIT = syscfg.incident_upstream_distance_limit
    cfg.WZ_DOWNSTREAM_DISTANCE_LIMIT = syscfg.workzone_downstream_distance_limit
    cfg.WZ_UPSTREAM_DISTANCE_LIMIT = syscfg.workzone_upstream_distance_limit
    cfg.SE_ARRIVAL_WINDOW = syscfg.specialevent_arrival_window
    cfg.SE_DEPARTURE_WINDOW1 = syscfg.specialevent_departure_window1
    cfg.SE_DEPARTURE_WINDOW2 = syscfg.specialevent_departure_window2

    # faverolles 1/12/2020: Adding AdminClient MOE Config Parameters
    cfg.MOE_CRITICAL_DENSITY = syscfg.moe_critical_density
    cfg.MOE_LANE_CAPACITY = syscfg.moe_lane_capacity
    cfg.MOE_CONGESTION_THRESHOLD_SPEED = syscfg.moe_congestion_threshold_speed

    return prev_syscfg

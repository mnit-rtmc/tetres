# -*- coding: utf-8 -*-
"""
systemconfig.py
~~~~~~~~~~~~~~

this module handles the request from `system configuration tab` of `admin client`

"""
from pyticas_tetres.da.route_wise_moe_parameters import RouteWiseMOEParametersDataAccess
from pyticas_tetres.systasks.initial_data_maker import update_moe_values
from pyticas_tetres.util.traffic_file_checker import has_traffic_files

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import threading
from flask import request

from pyticas.tool import json
from pyticas_server import protocol as prot
from pyticas_tetres import api_urls_admin, cfg
from pyticas_tetres.admin_auth import requires_auth
from pyticas_tetres.da.actionlog import ActionLogDataAccess
from pyticas_tetres.da.config import ConfigDataAccess
from pyticas_tetres.db.tetres.model import Config
from pyticas_tetres.logger import getLogger
from pyticas_tetres.sched import scheduler, worker
from pyticas_tetres.systasks import actionlog_processor as actionlog_proc
from pyticas_tetres.ttypes import SystemConfigInfo, RouteWiseMOEParametersInfo
from pyticas_tetres.util import actionlog, systemconfig


def register_api(app):
    @app.route(api_urls_admin.SYSCFG_GET, methods=['GET', 'POST'])
    @requires_auth
    def tetres_syscfg_get():
        syscfg = systemconfig.get_system_config_info()
        return prot.response_success(obj=syscfg)

    @app.route(api_urls_admin.SYSCFG_UPDATE, methods=['POST'])
    @requires_auth
    def tetres_syscfg_update():
        cfginfo_json = request.form.get('cfg', None)
        if not cfginfo_json:
            return prot.response_invalid_request()

        cfginfo = json.loads(cfginfo_json, SystemConfigInfo)

        if not cfginfo or not isinstance(cfginfo, SystemConfigInfo):
            return prot.response_invalid_request()

        for k, v in cfginfo.__dict__.items():
            if k.startswith('_'):
                continue
            if v is None:
                return prot.response_invalid_request()

        prev_syscfg = systemconfig.set_system_config_info(cfginfo)
        if not prev_syscfg:
            return prot.response_fail('fail to update configuration')

        put_task_to_actionlog(prev_syscfg)
        t1 = threading.Thread(target=handle_route_wise_moe_parameters, args=(cfginfo_json,))
        t1.start()
        return prot.response_success()


def handle_route_wise_moe_parameters(config_json_string):
    import json
    config_json = json.loads(config_json_string)
    route_id = config_json.get("reference_tt_route_id")
    if route_id:
        rw_moe_critical_density = config_json.get("rw_moe_critical_density")
        rw_moe_lane_capacity = config_json.get("rw_moe_lane_capacity")
        rw_moe_congestion_threshold_speed = config_json.get("rw_moe_congestion_threshold_speed")
        rw_moe_start_date = config_json.get("rw_moe_start_date")
        rw_moe_end_date = config_json.get("rw_moe_end_date")
        rw_moe_param_info = create_rw_moe_param_object(route_id, rw_moe_critical_density, rw_moe_lane_capacity,
                                                       rw_moe_congestion_threshold_speed, rw_moe_start_date,
                                                       rw_moe_end_date)

        rw_moe_object_id = save_rw_param_object(rw_moe_param_info)
        if has_traffic_files(rw_moe_start_date, rw_moe_end_date):
            try:
                update_moe_values(config_json)
                update_rw_moe_status(rw_moe_object_id, status="Completed")
            except Exception as e:
                print(e)
                update_rw_moe_status(rw_moe_object_id, status="Failed", reason=str(e))
        else:
            update_rw_moe_status(rw_moe_object_id, status="Failed", reason="Missing traffic files for the given time range.")


def update_rw_moe_status(rw_moe_object_id, status="Completed", reason=None):
    rw_da = RouteWiseMOEParametersDataAccess()
    rw_da.update(rw_moe_object_id, {
        "status": status,
        "reason": reason,
        "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    rw_da.commit()
    rw_da.close_session()


def create_rw_moe_param_object(route_id, rw_moe_critical_density, rw_moe_lane_capacity,
                               rw_moe_congestion_threshold_speed, rw_moe_start_date, rw_moe_end_date, status='Running'):
    rw_moe_param_info = RouteWiseMOEParametersInfo()
    rw_moe_param_info.reference_tt_route_id = route_id
    rw_moe_param_info.moe_critical_density = rw_moe_critical_density
    rw_moe_param_info.moe_lane_capacity = rw_moe_lane_capacity
    rw_moe_param_info.moe_congestion_threshold_speed = rw_moe_congestion_threshold_speed
    rw_moe_param_info.start_time = rw_moe_start_date if rw_moe_start_date else None
    rw_moe_param_info.end_time = rw_moe_end_date if rw_moe_end_date else None
    rw_moe_param_info.status = status
    return rw_moe_param_info


def save_rw_param_object(rw_moe_param_info):
    rw_moe_param_info.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rw_da = RouteWiseMOEParametersDataAccess()
    rw_moe_object = rw_da.insert(rw_moe_param_info)
    rw_da.commit()
    _id = rw_moe_object.id
    rw_da.close_session()
    return _id


def put_task_to_actionlog(prev_syscfg):
    """

    :type prev_syscfg: pyticas_tetres.ttypes.SystemConfigInfo
    """
    da_config = ConfigDataAccess()
    syscfg = da_config.get_by_name(cfg.OPT_NAME_SYSCONFIG)
    if not syscfg:
        getLogger(__name__).warning('Cannot find the updated system configuration from `config` table')
        da_config.close_session()
        return

    should_run_actionlog_handler = False
    da_actionlog = ActionLogDataAccess()

    is_data_archive_start_year_extended = False
    is_data_archive_start_year_shrinked = False

    if cfg.DATA_ARCHIVE_START_YEAR != prev_syscfg.data_archive_start_year:
        if cfg.DATA_ARCHIVE_START_YEAR < prev_syscfg.data_archive_start_year:
            is_data_archive_start_year_extended = True
        elif cfg.DATA_ARCHIVE_START_YEAR > prev_syscfg.data_archive_start_year:
            is_data_archive_start_year_shrinked = True

    # cancled already posted action logs
    if is_data_archive_start_year_shrinked or is_data_archive_start_year_extended:
        ex_logs = da_actionlog.search(
            searches=[('target_datatype', ActionLogDataAccess.DT_SYSTEMCONFIG), ('handled', False)],
            op='and',
            cond='match',
            as_model=True)
        for a_log in ex_logs:
            a_log.handled = True
            a_log.handled_date = datetime.datetime.now()
            a_log.status = 'Cancled due to another action'
            a_log.status_updated_date = datetime.datetime.now()

        da_actionlog.commit()

    if is_data_archive_start_year_extended:
        should_run_actionlog_handler = True
        actionlog.add(ActionLogDataAccess.UPDATE,
                      ActionLogDataAccess.DT_SYSTEMCONFIG,
                      Config.__tablename__,
                      syscfg.id,
                      'DATA_ARCHIVE_START_YEAR_EXTENDED: %d -> %d' % (
                          prev_syscfg.data_archive_start_year, cfg.DATA_ARCHIVE_START_YEAR),
                      handled=False)

    elif is_data_archive_start_year_shrinked:
        # add log for re-calculation
        should_run_actionlog_handler = True
        actionlog.add(ActionLogDataAccess.UPDATE,
                      ActionLogDataAccess.DT_SYSTEMCONFIG,
                      Config.__tablename__,
                      syscfg.id,
                      'DATA_ARCHIVE_START_YEAR_SHRINKED: %d -> %d' % (
                          prev_syscfg.data_archive_start_year, cfg.DATA_ARCHIVE_START_YEAR),
                      handled=False)

    if (cfg.INCIDENT_DOWNSTREAM_DISTANCE_LIMIT != prev_syscfg.incident_downstream_distance_limit
            or cfg.INCIDENT_UPSTREAM_DISTANCE_LIMIT != prev_syscfg.incident_upstream_distance_limit):
        should_run_actionlog_handler = True
        actionlog.add(ActionLogDataAccess.UPDATE,
                      ActionLogDataAccess.DT_SYSTEMCONFIG,
                      Config.__tablename__,
                      syscfg.id,
                      ActionLogDataAccess.DT_INCIDENT,
                      handled=False)

    if (cfg.WZ_DOWNSTREAM_DISTANCE_LIMIT != prev_syscfg.workzone_downstream_distance_limit
            or cfg.WZ_UPSTREAM_DISTANCE_LIMIT != prev_syscfg.workzone_upstream_distance_limit):
        should_run_actionlog_handler = True
        actionlog.add(ActionLogDataAccess.UPDATE,
                      ActionLogDataAccess.DT_SYSTEMCONFIG,
                      Config.__tablename__,
                      syscfg.id,
                      ActionLogDataAccess.DT_WORKZONE,
                      handled=False)

    if (cfg.SE_ARRIVAL_WINDOW != prev_syscfg.specialevent_arrival_window
            or cfg.SE_DEPARTURE_WINDOW1 != prev_syscfg.specialevent_departure_window1
            or cfg.SE_DEPARTURE_WINDOW2 != prev_syscfg.specialevent_departure_window2):
        should_run_actionlog_handler = True
        actionlog.add(ActionLogDataAccess.UPDATE,
                      ActionLogDataAccess.DT_SYSTEMCONFIG,
                      Config.__tablename__,
                      syscfg.id,
                      ActionLogDataAccess.DT_SPECIALEVENT,
                      handled=False)

    # restart scheduler
    if (cfg.DAILY_JOB_START_TIME != prev_syscfg.daily_job_start_time
            or cfg.DAILY_JOB_OFFSET_DAYS != prev_syscfg.daily_job_offset_days
            or cfg.WEEKLY_JOB_START_WEEKDAY != prev_syscfg.weekly_job_start_day
            or cfg.WEEKLY_JOB_START_TIME != prev_syscfg.weekly_job_start_time
            or cfg.MONTHLY_JOB_START_DAY != prev_syscfg.monthly_job_start_date
            or cfg.MONTHLY_JOB_START_TIME != prev_syscfg.monthly_job_start_time):
        scheduler.restart()

        if cfg.DAILY_JOB_START_TIME != prev_syscfg.daily_job_start_time:
            actionlog.add(ActionLogDataAccess.UPDATE,
                          ActionLogDataAccess.DT_SYSTEMCONFIG,
                          Config.__tablename__,
                          syscfg.id,
                          'DAILY_JOB_START_TIME is updated : %s -> %s' % (
                              prev_syscfg.daily_job_start_time, cfg.DAILY_JOB_START_TIME),
                          handled=True)

        if cfg.DAILY_JOB_OFFSET_DAYS != prev_syscfg.daily_job_offset_days:
            actionlog.add(ActionLogDataAccess.UPDATE,
                          ActionLogDataAccess.DT_SYSTEMCONFIG,
                          Config.__tablename__,
                          syscfg.id,
                          'DAILY_JOB_OFFSET_DAYS is updated: %s -> %s' % (
                              prev_syscfg.daily_job_offset_days, cfg.DAILY_JOB_OFFSET_DAYS),
                          handled=True)

        if cfg.WEEKLY_JOB_START_WEEKDAY != prev_syscfg.weekly_job_start_day:
            actionlog.add(ActionLogDataAccess.UPDATE,
                          ActionLogDataAccess.DT_SYSTEMCONFIG,
                          Config.__tablename__,
                          syscfg.id,
                          'WEEKLY_JOB_START_WEEKDAY is updated: %s -> %s' % (
                              prev_syscfg.weekly_job_start_day, cfg.WEEKLY_JOB_START_WEEKDAY),
                          handled=True)

        if cfg.WEEKLY_JOB_START_TIME != prev_syscfg.weekly_job_start_time:
            actionlog.add(ActionLogDataAccess.UPDATE,
                          ActionLogDataAccess.DT_SYSTEMCONFIG,
                          Config.__tablename__,
                          syscfg.id,
                          'WEEKLY_JOB_START_TIME is updated: %s -> %s' % (
                              prev_syscfg.weekly_job_start_time, cfg.WEEKLY_JOB_START_TIME),
                          handled=True)

        if cfg.MONTHLY_JOB_START_DAY != prev_syscfg.monthly_job_start_date:
            actionlog.add(ActionLogDataAccess.UPDATE,
                          ActionLogDataAccess.DT_SYSTEMCONFIG,
                          Config.__tablename__,
                          syscfg.id,
                          'MONTHLY_JOB_START_DAY is updated: %s -> %s' % (
                              prev_syscfg.monthly_job_start_date, cfg.MONTHLY_JOB_START_DAY),
                          handled=True)

        if cfg.MONTHLY_JOB_START_TIME != prev_syscfg.monthly_job_start_time:
            actionlog.add(ActionLogDataAccess.UPDATE,
                          ActionLogDataAccess.DT_SYSTEMCONFIG,
                          Config.__tablename__,
                          syscfg.id,
                          'MONTHLY_JOB_START_TIME is updated: %s -> %s' % (
                              prev_syscfg.monthly_job_start_time, cfg.MONTHLY_JOB_START_TIME),
                          handled=True)
        # faverolles 1/22/2020 TODO: Add moe threshold parameters
    if not should_run_actionlog_handler:
        unhandled = da_actionlog.list(target_datatypes=[ActionLogDataAccess.DT_SYSTEMCONFIG], handled=False)
        if unhandled:
            should_run_actionlog_handler = True

    da_actionlog.close_session()
    da_config.close_session()

    # add actionlog handler to the task queue in the worker process
    if should_run_actionlog_handler:
        getLogger(__name__).debug('System configurations are updated and the handler process is posted')
        worker.add_task(actionlog_proc.run)
    else:
        getLogger(__name__).debug('System configurations are updated and the handler process is NOT posted')

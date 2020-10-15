# -*- coding: utf-8 -*-
"""
    ActionLog Processor module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ActionLog is created when administrator client does insert/update/delete actions.
    This module reads those data and performs the corresponding actions.
"""
from pyticas.tool import tb

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas_tetres.cfg import SE_ARRIVAL_WINDOW, SE_DEPARTURE_WINDOW2
from pyticas_tetres.da.actionlog import ActionLogDataAccess
from pyticas_tetres.da.route import TTRouteDataAccess
from pyticas_tetres.da.noaaweather import NoaaWeatherDataAccess
from pyticas_tetres.da.incident import IncidentDataAccess
from pyticas_tetres.da.tt import TravelTimeDataAccess
from pyticas_tetres.da.config import ConfigDataAccess
from pyticas_tetres.db.tetres import tablefinder
from pyticas_tetres.logger import getLogger
from pyticas_tetres.systasks import initial_data_maker

from pyticas import period
from pyticas_tetres import cfg
from pyticas_tetres.da import (route)
from pyticas_tetres.rengine import traveltime, categorization


def run():
    # faverolles 1/16/2020 NOTE: Fired when admin client issues
    #   /tetres/adm/syscfg/update
    """
    :rtype:
    """
    logger = getLogger(__name__)

    OPT_NAME = cfg.OPT_NAME_ACTIONLOG_ID_IN_PROCESSING
    da_config = ConfigDataAccess()
    running_config = da_config.insert_or_update(OPT_NAME, '')
    if running_config is False or not da_config.commit():
        logger.warning('cannot update "%s" option' % OPT_NAME)
        return
    running_config_id = running_config.id

    da_actionlog = ActionLogDataAccess()
    action_logs = da_actionlog.list(start_time=None, handled=False)

    handlers = {
        ActionLogDataAccess.DT_TTROUTE: _handler_ttroute,
        ActionLogDataAccess.DT_INCIDENT: _handler_incident,
        ActionLogDataAccess.DT_WORKZONE: _handler_workzone,
        ActionLogDataAccess.DT_SPECIALEVENT: _handler_specialevent,
        ActionLogDataAccess.DT_SNOWMGMT: _handler_snowmanagement,
        ActionLogDataAccess.DT_SNOWROUTE: _handler_snowroute,
        ActionLogDataAccess.DT_SNOWEVENT: _handler_snowevent,
        ActionLogDataAccess.DT_SYSTEMCONFIG: _handler_systemconfig,
    }

    logger.debug('>>> Doing post-processing of admin actions')

    handled = []

    for action_log in action_logs:

        logger.debug('  - processing for %s ' % action_log)

        key = '%s - %s' % (action_log.target_table, action_log.target_id)

        da_actionlog.update(action_log.id, {'status': ActionLogDataAccess.STATUS_RUNNING,
                                            'status_updated_date': datetime.datetime.now()})

        da_config.update(running_config_id, {'content': action_log.id})
        if not da_config.commit():
            da_config.rollback()
            logger.warning('cannot update "%s" option' % OPT_NAME)

        # skip if the item is already handled (user can modify the same data several times)
        if key in handled and action_log.action_type in [ActionLogDataAccess.INSERT, ActionLogDataAccess.UPDATE]:
            logger.debug('    : skip : already processed')
            da_actionlog.update(action_log.id, {'handled': True,
                                                'handled_date': datetime.datetime.now(),
                                                'status': ActionLogDataAccess.STATUS_DONE,
                                                'status_updated_date': datetime.datetime.now()
                                                })
            da_actionlog.commit()

            da_config.update(running_config_id, {'content': ''})
            da_config.commit()
            continue

        # find insance of data access module
        da = tablefinder.get_da_instance_by_tablename(action_log.target_table)

        if not da:
            da_actionlog.update(action_log.id, {'status': ActionLogDataAccess.STATUS_FAIL,
                                                'reason': 'Database Access module is not found',
                                                'status_updated_date': datetime.datetime.now()})
            da_actionlog.commit()

            da_config.update(running_config_id, {'content': ''})
            da_config.commit()

            logger.warning('    : skip : cannot find database access module (tablename=%s)' % action_log.target_table)
            continue

        # retrieve target item
        item = da.get_data_by_id(action_log.target_id)

        # if item is deleted...
        if not item:
            logger.debug('    : skip : item is not found')
            da_actionlog.update(action_log.id, {'handled': True,
                                                'handled_date': datetime.datetime.now(),
                                                'status': ActionLogDataAccess.STATUS_DONE,
                                                'reason': 'target data is not found',
                                                'status_updated_date': datetime.datetime.now()
                                                })
            da_actionlog.commit()

            da_config.update(running_config_id, {'content': ''})
            da_config.commit()

            continue

        # proceed by data type
        handler = handlers.get(action_log.target_datatype)
        if not handler:
            da_actionlog.update(action_log.id, {'status': ActionLogDataAccess.STATUS_FAIL,
                                                'reason': 'handler for the data not found',
                                                'status_updated_date': datetime.datetime.now()})
            da_actionlog.commit()

            da_config.update(running_config_id, {'content': ''})
            da_config.commit()

            logger.debug('    : skip : handler is not found')
            continue
        try:
            reason = ''
            is_handled = handler(da, item, action_log)
            if isinstance(is_handled, tuple):
                is_handled, reason = is_handled[0], is_handled[1]
        except Exception as ex:
            tb.traceback(ex)
            da_actionlog.update(action_log.id, {'status': ActionLogDataAccess.STATUS_FAIL,
                                                'reason': 'exception occured during processing data',
                                                'status_updated_date': datetime.datetime.now()})
            da_actionlog.commit()

            da_config.update(running_config_id, {'content': ''})
            da_config.commit()

            continue

        if is_handled:
            da_actionlog.update(action_log.id, {'handled': True,
                                                'handled_date': datetime.datetime.now(),
                                                'status': ActionLogDataAccess.STATUS_DONE,
                                                'status_updated_date': datetime.datetime.now()
                                                })
            da_actionlog.commit()
            if key != ActionLogDataAccess.DELETE:
                handled.append(key)
        else:
            da_actionlog.update(action_log.id, {'status': ActionLogDataAccess.STATUS_FAIL,
                                                'reason': reason if reason else 'target data is not handled',
                                                'status_updated_date': datetime.datetime.now()
                                                })
            da_actionlog.commit()

        da_config.update(running_config_id, {'content': ''})
        da_config.commit()

        if not da_actionlog.commit():
            da_actionlog.rollback()
            da_actionlog.close_session()
            logger.debug('  - fail to update %s ' % action_log)
            return

        logger.debug('     : end of processing for %s ' % action_log)

    da_actionlog.close_session()
    da_config.close_session()

    logger.debug('<<< End of post-processing of admin actions')


def _handler_ttroute(da, item, action_log):
    """

    :type da: pyticas_tetres.da.route.TTRouteDataAccess
    :type item: pyticas_tetres.ttypes.TTRouteInfo
    :type action_log: pyticas_tetres.ttypes.ActionLogInfo
    """
    # 1. calculate travel time
    # 2. categorize (all)
    try:
        from pyticas_tetres.util.traffic_file_checker import has_traffic_files
        start = datetime.date(cfg.DATA_ARCHIVE_START_YEAR, 1, 1)
        last_day = datetime.date.today() - datetime.timedelta(days=cfg.DAILY_JOB_OFFSET_DAYS)
        start_date_str, end_date_str = start.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')
        if not has_traffic_files(start_date_str, end_date_str):
            return False, "Missing traffic files for the given time range from {} to {}.".format(start_date_str, end_date_str)
    except Exception as e:
        getLogger(__name__).warning(
            'Exception occured while checking if traffic files exist during handling travel time routes. Error: {}'.format(
                e))
    daily_periods = _get_all_daily_periods()
    cnt = 0
    for prd in daily_periods:
        try:
            inserted_ids = traveltime.calculate_a_route(prd, item)
            if inserted_ids:
                categorization.categorize(item, prd)
                cnt += len(inserted_ids)
        except Exception as ex:
            getLogger(__name__).warning(
                'Exception occured when handling route changes : %s' % tb.traceback(ex, f_print=False))

    return cnt > 0


def _handler_incident(da, item, action_log):
    """

    :type da: pyticas_tetres.da.incident.IncidentDataAccess
    :type item: pyticas_tetres.ttypes.IncidentInfo
    :type action_log: pyticas_tetres.ttypes.ActionLogInfo
    """
    target_date = item.str2datetime(item.cdts)
    prd = _get_period_for_a_day(target_date)
    try:
        _categorize_for_a_day(prd, categorization.incident, incidents=[item])
    except Exception as ex:
        getLogger(__name__).warning(
            'Exception occured when handling incident changes : %s' % tb.traceback(ex, f_print=False))
        return False

    return True


def _handler_workzone(da, item, action_log):
    """

    :type da: pyticas_tetres.da.wz.WorkZoneDataAccess
    :type item: pyticas_tetres.ttypes.WorkZoneInfo
    :type action_log: pyticas_tetres.ttypes.ActionLogInfo
    """
    sdt = item.str2datetime(item.start_time)
    edt = item.str2datetime(item.end_time)
    periods = _get_daily_periods(sdt, edt)
    try:
        for prd in periods:
            _categorize_for_a_day(prd, categorization.workzone, workzones=[item])
        return True
    except Exception as ex:
        getLogger(__name__).warning(
            'Exception occured when handling workzone changes : %s' % tb.traceback(ex, f_print=False))
        return False


def _handler_specialevent(da, item, action_log):
    """

    :type da: pyticas_tetres.da.specialevent.SpecialEventDataAccess
    :type item: pyticas_tetres.ttypes.SpecialEventInfo
    :type action_log: pyticas_tetres.ttypes.ActionLogInfo
    """
    sdt = item.str2datetime(item.start_time)
    edt = item.str2datetime(item.end_time)

    sdt = sdt - datetime.timedelta(minutes=SE_ARRIVAL_WINDOW)
    edt = edt + datetime.timedelta(minutes=SE_DEPARTURE_WINDOW2)

    periods = _get_daily_periods(sdt, edt)

    try:
        for prd in periods:
            _categorize_for_a_day(prd, categorization.specialevent, specialevents=[item])
        return True
    except Exception as ex:
        getLogger(__name__).warning(
            'Exception occured when handling specialevent changes : %s' % tb.traceback(ex, f_print=False))
        return False


def _handler_snowmanagement(da, item, action_log):
    """

    :type da: pyticas_tetres.da.snowmgmt.SnowMgmtDataAccess
    :type item: pyticas_tetres.ttypes.SnowManagementInfo
    :type action_log: pyticas_tetres.ttypes.ActionLogInfo
    """
    sdt = item.str2datetime(item.lane_lost_time)
    edt = item.str2datetime(item.lane_regain_time)
    periods = _get_daily_periods(sdt, edt)

    try:
        for prd in periods:
            _categorize_for_a_day(prd, categorization.snowmgmt, snowmgmts=[item])
        return True
    except Exception as ex:
        getLogger(__name__).warning(
            'Exception occured when handling snow-management changes : %s' % tb.traceback(ex, f_print=False))
        return False


def _handler_snowroute(da, item, action_log):
    """

    :type da: pyticas_tetres.da.snowroute.SnowRouteDataAccess
    :type item: pyticas_tetres.ttypes.SnowRouteInfo
    :type action_log: pyticas_tetres.ttypes.ActionLogInfo
    """
    # do nothing
    return True


def _handler_snowevent(da, item, action_log):
    """

    :type da: pyticas_tetres.da.snowevent.SnowEventDataAccess
    :type item: pyticas_tetres.ttypes.SnowEventInfo
    :type action_log: pyticas_tetres.ttypes.ActionLogInfo
    """
    # do nothing
    return True


def _handler_systemconfig(da, item, action_log):
    """

    :type da: pyticas_tetres.da.config.ConfigDataAccess
    :type item: pyticas_tetres.ttypes.SystemConfigInfo
    :type action_log: pyticas_tetres.ttypes.ActionLogInfo
    """
    ttr_da = TTRouteDataAccess()
    routes = ttr_da.list()
    ttr_da.close_session()

    start_date = datetime.datetime.strptime('%s-01-01' % cfg.DATA_ARCHIVE_START_YEAR, '%Y-%m-%d')
    last_date = datetime.datetime.now() - datetime.timedelta(days=cfg.DAILY_JOB_OFFSET_DAYS)
    daily_periods = _get_daily_periods(start_date, last_date)

    # faverolles 1/16/2020 NOTE: If the AdminClient changes the Archive Start Year parameter
    #  and an entry is made in the action_log database table.
    #  The server will repeatedly rerun initial_data_maker which is also run by (dataloader.py)
    #  until this entry is removed from the database.
    #  The issue is that the entry won't be removed because "target data is not handled" which
    #  i think means "until all traffic data is downloaded" for the archive start year.
    #  This never happens because the traffic data is hundreds of GB's.

    #
    if action_log.data_desc.startswith('DATA_ARCHIVE_START_YEAR_EXTENDED'):
        # calculate travel time data and the related non-traffic data during the extended years
        _, year_change = action_log.data_desc.split(':')
        prev_year, changed_year = year_change.split('->')
        prev_year, changed_year = int(prev_year.strip()), int(changed_year.strip())
        prev_end_date = datetime.datetime.strptime('%s-12-31' % (prev_year - 1), '%Y-%m-%d').date()
        try:
            # faverolles 1/16/2020 NOTE: Why is there no parameter db_info passed
            #  I'm guessing its expected to fail because try-catch maybe?
            from pyticas_tetres.util.traffic_file_checker import has_traffic_files
            start_date_str, end_date_str = start_date.strftime('%Y-%m-%d'), prev_end_date.strftime('%Y-%m-%d')
            if not has_traffic_files(start_date_str, end_date_str):
                return False, "Missing traffic files for the given time range from {} to {}.".format(start_date_str, end_date_str)
            import dbinfo
            initial_data_maker.run(start_date.date(), prev_end_date, db_info=dbinfo.tetres_db_info())
            return True
        except Exception as ex:
            getLogger(__name__).warning(
                'exception occured when handling  SystemConfig - Data Archive Start Year (Extended) : %s'
                % tb.traceback(ex, f_print=False))
            return False

    elif action_log.data_desc.startswith('DATA_ARCHIVE_START_YEAR_SHRINKED'):
        # delete the travel time data and the related non-traffic data during the shrinked years
        _, year_change = action_log.data_desc.split(':')
        prev_year, changed_year = year_change.split('->')
        prev_year, changed_year = int(prev_year.strip()), int(changed_year.strip())
        years = [y for y in range(prev_year, changed_year)]

        for y in years:
            sdt = datetime.datetime.strptime('%s-01-01 00:00:00' % y, '%Y-%m-%d %H:%M:%S')
            edt = datetime.datetime.strptime('%s-12-31 23:59:59' % y, '%Y-%m-%d %H:%M:%S')

            try:
                tt_da = TravelTimeDataAccess(y)
                for a_route in routes:
                    tt_da.delete_range(a_route.id, sdt, edt)
                tt_da.close_session()

                weather_da = NoaaWeatherDataAccess(y)
                weather_da.delete_range(None, None, start_time=sdt, end_time=edt)
                weather_da.commit()
                weather_da.close_session()

                incident_da = IncidentDataAccess()
                incident_da.delete_range_all(start_time=sdt, end_time=edt)
                incident_da.commit()
                incident_da.close_session()
            except Exception as ex:
                getLogger(__name__).warning(
                    'exception occured when handling  SystemConfig - Data Archive Start Year (Shrinked) : %s'
                    % tb.traceback(ex, f_print=False))
                return False

    elif action_log.target_datatype == ActionLogDataAccess.DT_INCIDENT:
        for a_route in routes:
            for prd in daily_periods:
                try:
                    categorization.categorize(a_route, prd, categorizers=[categorization.incident])
                except Exception as ex:
                    getLogger(__name__).warning(
                        'exception occured when handling SystemConfig - Incident Parameters Changes : %s'
                        % tb.traceback(ex, f_print=False))
                    return False

    elif action_log.target_datatype == ActionLogDataAccess.DT_WORKZONE:
        for a_route in routes:
            for prd in daily_periods:
                try:
                    categorization.categorize(a_route, prd, categorizers=[categorization.workzone])
                except Exception as ex:
                    getLogger(__name__).warning(
                        'exception occured when handling SystemConfig - Workzone Parameters Changes : %s'
                        % tb.traceback(ex, f_print=False))
                    return False


    elif action_log.target_datatype == ActionLogDataAccess.DT_SPECIALEVENT:
        for a_route in routes:
            for prd in daily_periods:
                try:
                    categorization.categorize(a_route, prd, categorizers=[categorization.specialevent])
                except Exception as ex:
                    getLogger(__name__).warning(
                        'exception occured when handling SystemConfig - SpecialEvent Parameters Changes : %s'
                        % tb.traceback(ex, f_print=False))
                    return False


    elif action_log.target_datatype == ActionLogDataAccess.DT_SNOWMGMT:
        for a_route in routes:
            for prd in daily_periods:
                try:
                    categorization.categorize(a_route, prd, categorizers=[categorization.snowmgmt])
                except Exception as ex:
                    getLogger(__name__).warning(
                        'exception occured when handling SystemConfig - SnowManagement Parameters Changes : %s'
                        % tb.traceback(ex, f_print=False))
                    return False

    return True


def _get_all_daily_periods():
    # faverolles 1/16/2020 NOTE: always starts at datetime.today
    """
    :rtype: list[pyticas.ttypes.Period]
    """
    first_day = datetime.date(cfg.DATA_ARCHIVE_START_YEAR, 1, 1)
    last_day = datetime.date.today() - datetime.timedelta(days=cfg.DAILY_JOB_OFFSET_DAYS)
    stime = datetime.time(0, 0, 0)
    etime = datetime.time(23, 59, 59)
    return period.create_periods(first_day, last_day,
                                 stime, etime,
                                 cfg.TT_DATA_INTERVAL,
                                 target_days=[0, 1, 2, 3, 4, 5, 6],
                                 remove_holiday=False)


def _get_daily_periods(sdt, edt):
    """
    :type sdt: datetime.datetime
    :type edt: datetime.datetime
    :rtype: list[pyticas.ttypes.Period]
    """
    first_day = sdt.date()
    last_day = edt.date()
    stime = datetime.time(0, 0, 0)
    etime = datetime.time(23, 59, 59)
    return period.create_periods(first_day, last_day,
                                 stime, etime,
                                 cfg.TT_DATA_INTERVAL,
                                 target_days=[0, 1, 2, 3, 4, 5, 6],
                                 remove_holiday=False)


def _get_period_for_a_day(dt):
    """
    :type dt: datetime.datetime
    :rtype:pyticas.ttypes.Period
    """
    date = dt.date()
    stime = datetime.time(0, 0, 0)
    etime = datetime.time(23, 59, 59)
    return period.Period(datetime.datetime.combine(date, stime),
                         datetime.datetime.combine(date, etime),
                         cfg.TT_DATA_INTERVAL)


def _categorize_for_a_day(prd, categorizer, **kwargs):
    """
    :type prd: pyticas.ttypes.Period
    :type categorizer: any
    """
    da_route = route.TTRouteDataAccess()
    route_list = da_route.list()
    for a_route in route_list:
        categorization.categorize(a_route, prd, categorizers=[categorizer], **kwargs)
    da_route.close_session()

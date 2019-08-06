# -*- coding: utf-8 -*-

import csv
import os
import queue
import threading
import time
import traceback

import xlsxwriter

from pyticas.infra import Infra
from pyticas.tool import profile, timeutil
from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core import nsrf, data_util
from pyticas_ncrtes.core.nsrf import cache as nsr_cache
from pyticas_ncrtes.core.nsrf import dryday_finder
from pyticas_ncrtes.core.nsrf import nsr_data, nsr_func
from pyticas_ncrtes.core.util import graph
from pyticas_ncrtes.db import conn
from pyticas_ncrtes.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

# TODO: Update this module

prefix = ''
q_task = queue.Queue()
q_drydays = queue.Queue()
q_detector_checked = queue.Queue()
q_data = queue.Queue()
q_func = queue.Queue()
q_res = queue.Queue()
q_exceptions = queue.Queue()


def run(pid, stations, months, data_path, db_info):
    """ target station identification main process

    Parameters
    ===========
        - pid : process identification for multi-processing
        - stations : station list
        - months : month list
        - data_path : TICAS nsr_data path

    :type pid: int
    :type stations: list[str]
    :type months: list[(int, int)]
    :type data_path : str
    :type db_info: dict
    :return:
    """
    Infra.initialize(data_path)

    if conn.Session == None:
        conn.connect(db_info)

    logger = getLogger(__name__)
    logger.info('starting target station identification')

    # process start time
    stime = time.time()

    th_1 = _create_workers(_worker1_find_drydays, 'worker%d-1-find_drydays' % pid, 3)
    th_2 = _create_workers(_worker2_check_detector, 'worker%d-2-check_detectors' % pid, 6)
    th_3 = _create_workers(_worker3_make_data, 'worker%d-3-make_data' % pid, 12)
    th_4 = _create_workers(_worker4_make_func, 'worker%d-4-make_function' % pid, 12)
    th_5 = _create_workers(_worker5_save_chart, 'worker%d-5-write_chart' % pid, 1)
    th_6 = _create_workers(_worker6_save_result, 'worker%d-6-write_result' % pid, 1)
    th_7 = _create_workers(_worker7_log_exceptions, 'worker%d-7-log_exceptions' % pid, 1)

    _dispatch_stations(pid, stations, months)

    q_task.join()
    q_drydays.join()
    q_detector_checked.join()
    q_data.join()
    q_func.join()
    q_res.join()
    q_exceptions.join()

    _terminate_workers(q_task, th_1)
    _terminate_workers(q_drydays, th_2)
    _terminate_workers(q_detector_checked, th_3)
    _terminate_workers(q_data, th_4)
    _terminate_workers(q_func, th_5)
    _terminate_workers(q_res, th_6)
    _terminate_workers(q_exceptions, th_7)

    etime = time.time()

    logger.info('end of target station identification (elapsed time=%s)' % timeutil.human_time(seconds=(etime - stime)))
    profile.print_prof_data()
    profile.clear_prof_data()


def _write_ncr_data(ncr_data, ncr_func):
    """

    :type ncr_data: pyticas_ncrtes.core.etypes.NSRData
    :type ncr_func: pyticas_ncrtes.core.etypes.NSRFunction
    """
    st_id = ncr_data.daytime_data.station.station_id
    corr_name = ncr_data.daytime_data.station.corridor.name
    months = ncr_data.months
    output_path = _output_path(corr_name, months, '%s - Normal UK.xlsx' % st_id)
    wb = xlsxwriter.Workbook(output_path)
    ws = wb.add_worksheet('nsr_data')

    def _uk(uk):
        k_list = []
        u_list = []
        for k, u in uk.items():
            k_list.append(k)
            u_list.append(u)
        return u_list, k_list

    u_list, k_list = _uk(ncr_data.daytime_data.recovery_uk)
    ws.write_column(0, 0, ['Recovery K'] + k_list)
    ws.write_column(0, 1, ['Recovery U'] + u_list)

    u_list, k_list = _uk(ncr_data.daytime_data.reduction_uk)
    ws.write_column(0, 3, ['Reduction K'] + k_list)
    ws.write_column(0, 4, ['Reduction U'] + u_list)

    if ncr_func and ncr_func.is_valid():
        ncr_func.prepare_functions()
        k_list = [v for v in range(0, 140)]

        # print(' recovery pattern ?? ', ncr_func.daytime_func.recovery_function.valid_state)

        if ncr_func.daytime_func.recovery_function.is_valid():
            u_list = ncr_func.daytime_func.recovery_speeds(k_list)
            ws.write_column(0, 6, ['Recovery Pattern K'] + k_list)
            ws.write_column(0, 7, ['Recovery Pattern U'] + u_list)

        if ncr_func.daytime_func.reduction_function.is_valid():
            u_list = ncr_func.daytime_func.reduction_speeds(k_list)
            ws.write_column(0, 9, ['Reduction Pattern K'] + k_list)
            ws.write_column(0, 10, ['Reduction Pattern U'] + u_list)

        u_list = ncr_func.nighttime_func.get_night_speeds()
        t_list = ncr_func.nighttime_func.get_timeline()
        ws.write_column(0, 12, ['NightTime Timeline'] + t_list)
        ws.write_column(0, 13, ['NightTime Avg Speed'] + u_list)

        ws.write_column(0, 15, ['NightTime Whole Timeline'] + t_list)
        u_list = []
        stddev_list = []
        for tidx in range(0, len(ncr_data.night_data.uss[0])):
            same_time_us = []
            for didx, us in enumerate(ncr_data.night_data.uss):
                if us[tidx] > 0:
                    same_time_us.append(us[tidx])

            _avg, _stddev = data_util.avg_stddev(same_time_us, remove_outlier=True)
            u_list.append(_avg)
            stddev_list.append(_stddev)

        ws.write_column(0, 16, ['NightTime Avg Speed'] + u_list)

        ws.write_column(0, 18, ['NightTime Whole Timeline'] + t_list)
        ws.write_column(0, 19, ['NightTime Stddev'] + stddev_list)

        ws.write_column(0, 21, ['NightTime Whole Timeline'] + t_list)
        for didx, us in enumerate(ncr_data.night_data.uss):
            ws.write_column(0, 22 + didx, [ncr_data.night_data.periods[didx].get_date_string()] + us)

    wb.close()


def _dispatch_stations(pid, stations, months):
    """ target station identification main process

    :type pid: int
    :type stations: list[str]
    :type months: list[(int, int)]
    :return:
    """
    infra = ncrtes.get_infra()
    logger = getLogger(__name__)

    cidx = 0
    for sidx, st_id in enumerate(stations):
        st = infra.get_rnode(st_id)
        if st.is_temp_station() or not st.detectors:
            continue
        cidx += 1
        logger.info('creating task for %s' % st.station_id)
        task = {'pid': pid, 'station': st, 'months': months, 'ncr_data': None, 'ncr_func': None}

        # check cache.py
        ncr_data = nsrf.normal_data(st, months)
        ncr_func = nsrf.normal_function(st, months, normal_data=ncr_data)
        if ncr_data:
            task['ncr_data'] = ncr_data
            if ncr_func:
                try:
                    ncr_func.prepare_functions()
                    task['ncr_func'] = ncr_func
                except:
                    ncr_func = None
                    pass

            if ncr_data and ncr_func:
                try:
                    _write_ncr_data(ncr_data, ncr_func)
                except Exception as ex:
                    logger.warn('Fail to write ncr nsr_data of %s' % ncr_data.station.station_id)
                    task['ncr_data'] = None
                    task['ncr_func'] = None

        q_task.put(task)


def _create_workers(func, name, n):
    """ Create worker threads

    :type func: function
    :type name: str
    :type n: int
    :rtype: list[threading.Thread]
    """
    threads = []
    for i in range(n):
        t = threading.Thread(target=func, args=('%s(%d)' % (name, i + 1),))
        t.start()
        threads.append(t)
    return threads


def _terminate_workers(q, threads):
    """ terminate worker threads

    **How it works**
        by putting `None` in `Queue`, worker is got notification to stop processing

    :type q: queue.Queue
    :type threads: list[threading.Thread]
    """
    for t in range(len(threads) * 10):
        q.put(None)
    for t in threads:
        t.join()
    q.queue.clear()


def _worker1_find_drydays(worker_name):
    """ worker to find dry-days

    **Input/Output Queue**
        - input : q_task
        - output : q_drydays

    :type worker_name: str
    """
    logger = getLogger(__name__)
    while True:

        task = q_task.get()
        if task is None:
            logger.debug('%s > done for all tasks' % (worker_name))
            q_task.task_done()
            break

        logger.debug('%s > fetching task for %s' % (worker_name, task['station'].station_id))
        if task['ncr_data']:
            q_drydays.put(task)
            q_task.task_done()
            continue

        target_station = task['station']
        months = task['months']
        try:
            daytime_periods, weather_sources = dryday_finder.drydays_for_daytime(target_station, months)
        except Exception as ex:
            tb = traceback.format_exc()
            q_exceptions.put(
                {'pid': task['pid'], 'station': task['station'], 'months': task['months'], 'ex': ex, 'tb': tb})
            logger.critical('%s > exception occurred for %s (%s)' % (worker_name, task['station'].station_id, ex))
            logger.critical(tb)
            q_task.task_done()
            continue

        task['daytime_periods'] = daytime_periods
        task['weather_sources'] = weather_sources
        q_drydays.put(task)
        q_task.task_done()
        logger.debug('%s > task done for %s' % (worker_name, task['station'].station_id))


def _worker2_check_detector(worker_name):
    """ worker to find malfunctioned detector by checking volume-occupancy pattern

    **Input/Output Queue**
        - input : q_drydays
        - output : q_detector_checked

    :type worker_name: str
    """
    logger = getLogger(__name__)
    while True:
        task = q_drydays.get()
        if task is None:
            logger.debug('%s > done for all tasks' % (worker_name))
            q_drydays.task_done()
            break

        logger.debug('%s > fetching task for %s' % (worker_name, task['station'].station_id))
        if task['ncr_data']:
            q_detector_checked.put(task)
            q_drydays.task_done()
            continue

        target_station = task['station']
        daytime_periods = task['daytime_periods']

        # try:
        #     task['not_used_detectors'] = validator.multiple_pattern_detectors(target_station, daytime_periods)
        # except Exception as ex:
        #     tb = traceback.format_exc()
        #     q_exceptions.put(
        #         {'pid': task['pid'], 'station': task['station'], 'months': task['months'], 'ex': ex, 'tb': tb})
        #     logger.critical('%s > exception occurred for %s (%s)' % (worker_name, task['station'].station_id, ex))
        #     logger.critical(tb)
        #     q_drydays.task_done()
        #     continue

        q_detector_checked.put(task)
        q_drydays.task_done()
        logger.debug('%s > task done for %s' % (worker_name, task['station'].station_id))


def _worker3_make_data(worker_name):
    """ worker to make normal-day nsr_data (daytime and nighttime nsr_data)

    **Input/Output Queue**
        - input : q_detector_checked
        - output : q_data

    :type worker_name: str
    """
    logger = getLogger(__name__)
    while True:
        task = q_detector_checked.get()
        if task is None:
            logger.debug('%s > done for all tasks' % (worker_name))
            q_detector_checked.task_done()
            break
        logger.debug('%s > fetching task for %s' % (worker_name, task['station'].station_id))
        if task['ncr_data']:
            q_data.put(task)
            q_detector_checked.task_done()
            continue
        target_station = task['station']
        try:
            #
            # (dt_periods, recovery_uk_dt, reduction_uk_dt,
            #  us_all_dt, ks_all_dt, cycles_dt, not_used_det_dt) = daytime_data.collect(target_station,
            #                                                                           task['daytime_periods'],
            #                                                                           DATA_INTERVAL,
            #                                                                           not_used_detectors=task[
            #                                                                               'not_used_detectors'])
            #
            # (night_uss,
            #  night_kss,
            #  night_qss,
            #  night_periods) = nighttime_data.collect(target_station, task['daytime_periods'])
            # logger.info('  - late night nsr_data are collected for %s' % (target_station.station_id))
            #
            # ncr_data = ntypes.NSRData(target_station,
            #                           task['months'],
            #                           ntypes.DaytimeData(target_station, dt_periods, recovery_uk_dt, reduction_uk_dt,
            #                                              us_all_dt,
            #                                              ks_all_dt, cycles_dt, not_used_det_dt),
            #                           ntypes.NighttimeData(target_station, night_uss, night_kss, night_qss,
            #                                                night_periods))
            ncr_data = nsr_data.collect(target_station, task['months'], periods=task['daytime_periods'])
            task['ncr_data'] = ncr_data
            # ncr_cache.dumps_ncr_data(ncr_data, task['months'])

        except Exception as ex:
            tb = traceback.format_exc()
            q_exceptions.put(
                {'pid': task['pid'], 'station': task['station'], 'months': task['months'], 'ex': ex, 'tb': tb})
            logger.critical('%s > exception occurred for %s (%s)' % (worker_name, task['station'].station_id, ex))
            logger.critical(tb)
            q_detector_checked.task_done()
            continue

        q_detector_checked.task_done()
        q_data.put(task)
        logger.debug('%s > task done for %s' % (worker_name, task['station'].station_id))


def _worker4_make_func(name):
    """ worker to make normal recovery/reduction function

    **Input/Output Queue**
        - input : q_data
        - output : q_func and q_res

    :type worker_name: str
    """
    logger = getLogger(__name__)
    while True:
        task = q_data.get()
        if task is None:
            logger.debug('%s > done for all tasks' % (name))
            q_data.task_done()
            break
        logger.debug('%s > fetching task for %s' % (name, task['station'].station_id))
        if not task['ncr_func']:
            try:
                _res = nsr_func.make(task['station'], task['months'], normal_data=task['ncr_data'])
                if not _res:
                    print('-> ', task['months'])
                    q_data.task_done()
                    continue

                ncr_func, ncr_data = _res
                # ncr_func = normal_function.make(task['ncr_data'])
                task['ncr_func'] = ncr_func
                nsr_cache.dumps_function(ncr_func, task['months'])
                task['is_ready'] = True

                try:
                    _write_ncr_data(ncr_data, ncr_func)
                except Exception as ex:
                    logger.warn(
                        'Fail to write ncr nsr_data of %s after creating ncr_func' % ncr_data.station.station_id)
                    task['ncr_data'] = None
                    task['ncr_func'] = None

            except Exception as ex:
                tb = traceback.format_exc()
                q_exceptions.put(
                    {'pid': task['pid'], 'station': task['station'], 'months': task['months'], 'ex': ex, 'tb': tb})
                logger.critical('%s > exception occurred for %s (%s)' % (name, task['station'].station_id, ex))
                logger.critical(tb)
                q_data.task_done()
                continue

        else:
            ncr_func = task['ncr_func']

        if (ncr_func.daytime_func.recovery_function.valid_state.is_valid() or
                ncr_func.daytime_func.reduction_function.valid_state.is_valid()):
            q_res.put({'pid': task['pid'], 'station': task['station'], 'months': task['months']})

        q_data.task_done()
        q_func.put(task)
        logger.debug('%s > task done for %s' % (name, task['station'].station_id))


def _worker5_save_chart(worker_name):
    """ worker to create charts for debugging

    **Input Queue**
        - input : q_func

    :type worker_name: str
    """
    logger = getLogger(__name__)
    while True:
        task = q_func.get()
        if task is None:
            logger.debug('%s > done for all tasks' % (worker_name))
            q_func.task_done()
            break
        logger.debug('%s > fetching task for %s' % (worker_name, task['station'].station_id))
        ncr_data = task['ncr_data']
        """:type: pyticas_ncrtes.ntypes.NSRData """
        ncr_func = task['ncr_func']
        """:type: pyticas_ncrtes.ntypes.NSRFunction """
        station = task['station']
        months = task['months']

        try:
            ncr_func.prepare_functions()

            _save_all_uk(ncr_data, months)

            _save_uk_chart(station,
                           'Daytime-Recovery',
                           ncr_data.daytime_data.recovery_uk,
                           ncr_func.daytime_func.recovery_function.linear_func.get_Kt(),
                           ncr_func.daytime_func.recovery_speed if ncr_func.daytime_func.recovery_function.is_valid() else None,
                           ncr_func.daytime_func.recovery_function.equation() if ncr_func.daytime_func.recovery_function.is_valid() else None,
                           _output_path(station.corridor.name, months,
                                        '%s (Daytime-Recovery, valid_state=%s)' % (
                                            station.station_id,
                                            ncr_func.daytime_func.recovery_function.valid_state.name))
                           )

            _save_uk_chart(station,
                           'Daytime-Reduction',
                           ncr_data.daytime_data.reduction_uk,
                           ncr_func.daytime_func.reduction_function.linear_func.get_Kt(),
                           ncr_func.daytime_func.reduction_speed if ncr_func.daytime_func.reduction_function.is_valid() else None,
                           ncr_func.daytime_func.reduction_function.equation() if ncr_func.daytime_func.reduction_function.is_valid() else None,
                           _output_path(station.corridor.name, months,
                                        '%s (Daytime-Reduction, valid_state=%s)' % (
                                            station.station_id,
                                            ncr_func.daytime_func.reduction_function.valid_state.name)))

            if ncr_func.nighttime_func and ncr_func.nighttime_func.is_valid():
                _save_line_chart(station,
                                 'Nighttime Speed',
                                 ncr_func.nighttime_func.avg_us,
                                 ncr_func.nighttime_func.get_night_speeds(),
                                 ncr_func.nighttime_func.get_curve_depth(),
                                 ncr_func.nighttime_func.get_timeline(),
                                 _output_path(station.corridor.name, months,
                                              '%s (Nighttime)' % (station.station_id)))

        except Exception as ex:
            tb = traceback.format_exc()
            q_exceptions.put(
                {'pid': task['pid'], 'station': task['station'], 'months': task['months'], 'ex': ex, 'tb': tb})
            logger.critical('%s > exception occurred for %s (%s)' % (worker_name, task['station'].station_id, ex))
            logger.critical(tb)
            q_func.task_done()
            continue

        q_func.task_done()
        logger.debug('%s > task done for %s' % (worker_name, task['station'].station_id))


def _worker6_save_result(name):
    """ worker to append target station id to csv file

    **Input/Output Queue**
        - input : q_res

    :type worker_name: str
    """
    logger = getLogger(__name__)
    infra = ncrtes.get_infra()
    output_file = None

    while True:
        task = q_res.get()
        if task is None:
            logger.debug('%s > done for all tasks' % (name))
            q_res.task_done()
            break
        s = task['station']
        logger.debug('%s > fetching task for %s' % (name, s.station_id))

        if not output_file:
            years = ['%d%02d' % (y, m) for (y, m) in task['months']]
            ystr = '-'.join(sorted(years))
            output_path = os.path.join(infra.get_path('ncrtes/%s' % ystr, create=True))
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            output_file = os.path.join(output_path, 'target_stations_%d.csv' % task['pid'])
            if os.path.exists(output_file):
                os.remove(output_file)

        try:
            with open(output_file, 'a') as csvfile:
                wr = csv.writer(csvfile, delimiter=',', lineterminator='\n')
                wr.writerow([s.corridor.route, s.corridor.dir, s.station_id, s.label, s.s_limit, s.lanes, s.lat, s.lon])
        except Exception as ex:
            tb = traceback.format_exc()
            q_exceptions.put(
                {'pid': task['pid'], 'station': task['station'], 'months': task['months'], 'ex': ex, 'tb': tb})
            logger.critical('%s > exception occurred for %s (%s)' % (name, task['station'].station_id, ex))
            logger.critical(tb)
            q_res.task_done()
            continue

        q_res.task_done()
        logger.debug('%s > task done for %s' % (name, s.station_id))


def _worker7_log_exceptions(name):
    """ worker to append exception information to text file

    **Input/Output Queue**
        - input : q_exceptions

    :type worker_name: str
    """
    logger = getLogger(__name__)
    infra = ncrtes.get_infra()
    output_file = None

    while True:
        task = q_exceptions.get()
        if task is None:
            logger.debug('%s > done for all tasks' % (name))
            q_exceptions.task_done()
            break

        s = task['station']

        if not output_file:
            years = ['%d%02d' % (y, m) for (y, m) in task['months']]
            ystr = '-'.join(sorted(years))
            output_path = os.path.join(infra.get_path('ncrtes/%s' % ystr, create=True))
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            output_file = os.path.join(output_path, 'exceptions_%d.csv' % task['pid'])
            if os.path.exists(output_file):
                os.remove(output_file)
        try:
            with open(output_file, 'a') as csvfile:
                csvfile.writelines(
                    'corridor=%s, station=%s, exception=%s' % (s.corridor.name, s.station_id, task['ex']))
                csvfile.writelines(str(task['tb']))
                csvfile.writelines('=======================================================')
                csvfile.writelines('')
            q_exceptions.task_done()

        except Exception as ex:
            tb = traceback.format_exc()
            logger.critical('%s > exception occurred for %s (%s)' % (name, task['station'].station_id, ex))
            logger.critical(tb)
            q_exceptions.task_done()


def _save_uk_chart(station, title, uk, Kt, func, equation, output_file):
    """ write chart image of speed-density

    :type station: pyticas.ttypes.RNodeObject
    :type title: str
    :type uk: dict[float, float]
    :type Kt: float
    :type func: function
    :type equation: str
    :type output_file: str
    :return:
    """
    logger = getLogger(__name__)
    ks = [v for v in sorted(uk.keys())]
    us = [uk[k] for k in ks]
    if not ks or not us:
        logger.info('No Data to make chart : %s, %s' % (station.station_id, title))
        return

    if func:
        ks2 = [k for k in range(int(round(min(ks), 0)), int(round(max(ks), 0)))]
        fus = [func(k) for k in ks2]
        if not ks2 or not fus:
            x = [ks]
            y = [us]
        else:
            x = [ks, ks2]
            y = [us, fus]
    else:
        x = [ks]
        y = [us]

    if func:
        title = '{} ({} on {}, Label={}, Lanes={}, SpeedLimit={})\nFunc : {})'.format(title,
                                                                                      station.station_id,
                                                                                      station.corridor.name,
                                                                                      station.label,
                                                                                      station.lanes,
                                                                                      station.s_limit,
                                                                                      # Kt,
                                                                                      equation)
    else:
        title = '{} ({} on {}, Label={}, Lanes={}, SpeedLimit={}))'.format(title,
                                                                           station.station_id,
                                                                           station.corridor.name,
                                                                           station.label,
                                                                           station.lanes,
                                                                           # Kt,
                                                                           station.s_limit)

    graph.plot_scatter(x, 'density', y, 'speed',  # [None, [Kt_idx]], [None, ['Kt']],
                       labels=["normal-day UK nsr_data", "calibrated function"],
                       xmin=0, xmax=120, ymin=0, ymax=100, s=[5, 10],
                       markers=['o', 'x'],
                       title=title,
                       output_file=output_file)


def _save_line_chart(station, title, us, fus, curve_depth, timeline, output_file):
    """ write chart image of nighttime nsr_data

    :type station: pyticas.ttypes.RNodeObject
    :type title: str
    :type us: list[float]
    :type fus: list[float]
    :type curve_depth: float
    :type timeline: list[str]
    :type output_file: str
    :return:
    """

    def plotter_handler(plt):
        ntimes = [t for idx, t in enumerate(timeline) if idx % 6 == 0]
        loc_times = [idx for idx, t in enumerate(timeline) if idx % 6 == 0]
        plt.xticks(loc_times, ntimes, rotation=90)

    graph.plot_line([us, fus], ['avg speed', 'calibrated function'],
                    s=9,
                    title='{} ({} on {}, Label={}, Lanes={}, SpeedLimit={}, CurveDepth={}))'.format(title,
                                                                                                    station.station_id,
                                                                                                    station.corridor.name,
                                                                                                    station.label,
                                                                                                    station.lanes,
                                                                                                    station.s_limit,
                                                                                                    curve_depth),
                    markers=['', '.'],
                    handler=plotter_handler,
                    output_file=output_file)


def _output_path(corridor_name, months, mode):
    """ return output file path

    :type corridor_name: str
    :type months: list[(int, int)]
    :type mode: str
    :rtype: str
    """
    infra = ncrtes.get_infra()
    years = ['%d%02d' % (y, m) for (y, m) in months]
    ystr = '-'.join(sorted(years))
    return os.path.join(infra.get_path('ncrtes/%s%s/func_charts/%s' % (ystr, prefix, corridor_name), create=True), mode)


def _save_all_uk(ncr_data, months):
    """ save chart image for all dry-day u-k nsr_data

    :type ncr_data: pyticas_ncrtes.core.etypes.NSRData
    :type months: list[(int, int)]
    :return:
    """
    station = ncr_data.station
    amuk = {}
    for idx, ks in enumerate(ncr_data.daytime_data.kss):
        for didx, k in enumerate(ks):
            if k > 0 and ncr_data.daytime_data.uss[idx][didx] > 0:
                amuk[k] = ncr_data.daytime_data.uss[idx][didx]

    _save_uk_chart(station,
                   'Daytime-All UK',
                   amuk,
                   None,
                   None,
                   None,
                   _output_path(station.corridor.name, months,
                                '%s (Daytime-All UK)' % (station.station_id))
                   )

# -*- coding: utf-8 -*-
"""
pyticas_ncrtes.core.etypes
===========================

- data types

"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import collections
import csv
import datetime
import enum
import math

import numpy as np

from pyticas import route
from pyticas.ttypes import Period, Serializable
from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core import setting, data_util
from pyticas_ncrtes.core.nsrf.target import lane
from pyticas_ncrtes.core.setting import LATE_NIGHT_START_TIME, LATE_NIGHT_END_TIME
from pyticas_ncrtes.logger import getLogger


class SnowEvent(object):
    """ snow event including multiple snow-event project
    """

    def __init__(self, stime, etime):
        """

        :type stime: datetime.datetime
        :type etime: datetime.datetime
        """

        self.interval = setting.DATA_INTERVAL
        self.snow_start_time = stime
        self.snow_end_time = etime
        self.estimated_snow_start_time = None
        self.estimated_snow_end_time = None
        self.snow_period = Period(self.snow_start_time, self.snow_end_time, self.interval)
        self._set_data_period()
        self.snow_start_index = self.time_to_index(self.snow_start_time)
        self.snow_end_index = self.time_to_index(self.snow_end_time)

    def _set_data_period(self):
        self.data_period = Period(self.snow_start_time, self.snow_end_time, self.interval)

        extended_end_time = self.snow_end_time + datetime.timedelta(0, setting.EXTEND_END_HOUR * 3600)
        # print('snow_start_time : ', self.snow_start_time)
        # print('snow_end_time : ', self.snow_end_time)
        # print('extended_end_time : ', extended_end_time)

        etime = extended_end_time.time()
        if datetime.time(0, 0, 0) <= etime < datetime.time(3, 0, 0):
            extended_end_time = extended_end_time - datetime.timedelta(days=1)
            extended_end_time = extended_end_time.replace(hour=23, minute=0, second=0)
        elif datetime.time(3, 0, 0) <= etime < datetime.time(15, 0, 0):
            extended_end_time = extended_end_time.replace(hour=12, minute=0, second=0)
        elif datetime.time(15, 0, 0) <= etime < datetime.time(21, 0, 0):
            extended_end_time = extended_end_time.replace(hour=21, minute=0, second=0)

        # print('updated extended_end_time : ', extended_end_time)

        self.data_period.extend_start_hour(setting.EXTEND_START_HOUR)
        self.data_period.extend_end_hour(setting.EXTEND_END_HOUR)
        # self.data_period.end_date = extended_end_time

    def time_to_index(self, dt, ignore_error=False):
        """ return time index of the given datetime
        """
        curTime = self.data_period.start_date
        for idx in range(len(self.data_period.get_timeline())):
            curTime += datetime.timedelta(seconds=self.interval)
            if curTime >= dt:
                return idx

        if ignore_error:
            return -1

        raise Exception('Not found time index for {0} of snow event between {1} ~ {2}'.format(dt,
                                                                                              self.data_period.start_date,
                                                                                              self.data_period.end_date))

    def index_to_time(self, ti, **kwargs):
        """ return time index of the given datetime
        """
        get_string = kwargs.get('as_string', True)
        string_format = kwargs.get('string_format', '%H:%M')
        curTime = self.data_period.start_date
        for idx in range(len(self.data_period.get_timeline())):
            curTime += datetime.timedelta(seconds=self.interval)
            if idx == ti:
                if get_string:
                    return curTime.strftime(string_format)
                else:
                    return curTime
        raise Exception('Not found time index for {0} of {1}'.format(ti, self))


class ReportedEvent(object):
    def __init__(self, prj_id, snow_start_time, snow_end_time, reported_lost_time, reported_regain_time,
                 weather_type=None, precipitation=None):
        """
        :type prj_id: str
        :type snow_start_time: str
        :type snow_end_time: str
        :type reported_lost_time: str
        :type reported_regain_time: str
        :type weather_type: str
        :type precipitation: float
        """
        self.prj_id = prj_id
        self.reported_lost_time = None
        self.reported_regain_time = None

        if '-' in snow_start_time:
            self.snow_start_time = datetime.datetime.strptime(snow_start_time, '%Y-%m-%d %H:%M:%S')
            self.snow_end_time = datetime.datetime.strptime(snow_end_time, '%Y-%m-%d %H:%M:%S')
            self.reported_lost_time = datetime.datetime.strptime(reported_lost_time, '%Y-%m-%d %H:%M:%S')
            self.reported_regain_time = datetime.datetime.strptime(reported_regain_time, '%Y-%m-%d %H:%M:%S')
        else:
            self.snow_start_time = datetime.datetime.strptime(snow_start_time, '%m/%d/%Y %H:%M')
            self.snow_end_time = datetime.datetime.strptime(snow_end_time, '%m/%d/%Y %H:%M')
            try:
                self.reported_lost_time = datetime.datetime.strptime(reported_lost_time, '%m/%d/%Y %H:%M')
                self.reported_regain_time = datetime.datetime.strptime(reported_regain_time, '%m/%d/%Y %H:%M')
            except Exception as ex:
                logger = getLogger(__name__)
                logger.info('Exception parsing reported time : %s' % str(ex))
                pass

        self.snow_start_time = self.snow_start_time.replace(second=0, microsecond=0)
        self.snow_end_time = self.snow_end_time.replace(second=0, microsecond=0)
        if self.reported_lost_time:
            self.reported_lost_time = self.reported_lost_time.replace(second=0, microsecond=0)
            self.reported_regain_time = self.reported_regain_time.replace(second=0, microsecond=0)

        self.weather_type = str(weather_type)
        self.precipitation = float(precipitation) if precipitation else None

    @classmethod
    def load_reported_events(cls, filepath):
        reported_events = {}
        with open(filepath, 'r') as csvfile:
            rd = csv.reader(csvfile, delimiter=',')
            for ridx, row in enumerate(rd):
                if not ridx:
                    continue
                rel = reported_events.get(row[0], [])
                rel.append(ReportedEvent(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
                reported_events[row[0]] = rel
        return reported_events


class SnowRoute(object):
    def __init__(self, region, truck_station, id, id_old, corridor, dir, start_station, end_station,
                 route_description, note):
        self.region = region
        self.truck_station = truck_station
        self.id = id
        self.name = '{0}_{1}'.format(id, dir)
        self.id_old = id_old
        self.corridor = corridor
        self.dir = dir
        self.start_station_id = start_station
        self.end_station_id = end_station
        self.route_description = route_description
        self.note = note
        self._route = None

    def get_route(self, **kwargs):
        if not self._route:
            name = kwargs.get('name', 'NoName')
            desc = kwargs.get('desc', '')
            self._route = route.create_route(self.start_station_id, self.end_station_id, name, desc)
        return self._route


    @classmethod
    def load_snow_routes(cls, route_info_file):
        """

        :type route_info_file: str
        :rtype: list[SnowRoute]
        """
        snow_routes = []
        with open(route_info_file, 'r') as csvfile:
            rd = csv.reader(csvfile, delimiter=',')
            for ridx, row in enumerate(rd):
                if not ridx:
                    continue
                sr = SnowRoute(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[11], row[12])
                snow_routes.append(sr)
                sr = SnowRoute(row[0], row[1], row[2], row[3], row[4], row[8], row[9], row[10], row[11], row[12])
                snow_routes.append(sr)
        return snow_routes

    @classmethod
    def find_route(cls, station, snow_routes):
        """

        :type station: pyticas.ttypes.RNode
        :type snow_routes: list[SnowRoute]
        :rtype: SnowRoute
        """
        if not station or not any(snow_routes):
            return None
        for snow_route in snow_routes:
            r = snow_route.get_route()
            if station in r.rnodes:
                return snow_route
        return None

    def __str__(self):
        return '<SnowRoute name="%s" region="%s" subregion="%s" corridor="%s" start_station="%s" end_station="%s">' % (
            self.name, self.region, self.truck_station, self.corridor, self.start_station_id, self.end_station_id
        )


class ESTData(object):
    RATIO_STEPPING_LEVEL = 0.05
    RATIO_SMOOTHING_SIZE = setting.SW_1HOUR
    SMOOTHING_SIZE_FOR_NIGHTTIME = setting.SW_2HOURS

    def __init__(self, tsi, target_station, sevent, snow_routes, reported, normal_func):
        """
        :type tsi: pyticas_ncrtes.itypes.TargetStationInfo
        :type target_station: pyticas.ttypes.RNodeObject
        :type sevent: pyticas_ncrtes.core.etypes.SnowEvent
        :type snow_routes: list[pyticas_ncrtes.core.etypes.SnowRoute]
        :type reported: dict[str, list[pyticas_ncrtes.core.etypes.ReportedEvent]]
        :type normal_func: pyticas_ncrtes.core.etypes.NSRFunction        
        """
        self.target_station_info = tsi
        self.target_station = target_station
        self.snow_event = sevent
        self.normal_func = None
        """:type: pyticas_ncrtes.core.etypes.NSRFunction"""
        self.months = None
        self.kt = None

        if normal_func:
            self.normal_func = normal_func
            self.months = normal_func.months
            if self.normal_func.is_valid():
                self.kt = self.normal_func.daytime_func.get_Kt()

        self.snow_route = self._get_snow_route(snow_routes)
        self.timeline = sevent.data_period.get_timeline(as_datetime=True)

        # Reported Barelane Regain Times
        self.rps = self._reported_regain_times(reported)
        """:type: list[int]"""

        # Traffic Data

        # original
        self.ks = None
        """:type: numpy.ndarray"""
        self.us = None
        """:type: numpy.ndarray"""
        self.qs = None
        """:type: numpy.ndarray"""

        self.n_data = None
        """:type: int """

        # smoothed
        self.lsus = None
        """:type: numpy.ndarray"""
        self.lsks = None
        """:type: numpy.ndarray"""
        self.lsqs = None
        """:type: numpy.ndarray"""

        self.sus = None
        """:type: numpy.ndarray"""
        self.sks = None
        """:type: numpy.ndarray"""
        self.sqs = None
        """:type: numpy.ndarray"""

        # quantized
        self.qus = None
        """:type: numpy.ndarray"""
        self.qks = None
        """:type: numpy.ndarray"""

        # nighttime data
        self.night_ratios = None
        """:type: numpy.ndarray"""
        self.night_sratios = None
        """:type: numpy.ndarray"""
        self.night_us = None
        """:type: numpy.ndarray"""
        self.night_ks = None
        """:type: numpy.ndarray"""

        # whole_data
        self.wn_ffs = None
        """:type: float """
        self.k_at_wn_ffs = None
        """:type: float """

        self.wn_avg_us = None
        """:type: numpy.ndarray"""

        self.wn_ratios = None
        """:type: numpy.ndarray"""

        self.wn_sratios = None
        """:type: numpy.ndarray"""
        # self.wn_qratios = None
        # """:type: numpy.ndarray"""
        # self.wn_us_boundaries = None
        # """:type: numpy.ndarray"""
        # self.wn_boundary_ratios = None
        # """:type: numpy.ndarray"""

        self.normal_avg_us = None
        """:type: numpy.ndarray"""

        self.normal_ratios = None
        """:type: numpy.ndarray"""

        self.ratios = None
        """:type: numpy.ndarray"""

        self.lsratios = None
        """:type: numpy.ndarray"""

        self.sratios = None
        """:type: numpy.ndarray"""

        # Results
        self.srst = None
        """:type: int"""
        self.lst = None
        """:type: int"""
        self.rst = None
        """:type: int"""
        self.ncrt = None
        """:type: int"""

        # Alternatives
        self.pst = None
        """:type: int"""

        # self.sbpst = None # stable_speed_region_before_pst
        # """:type: int"""
        #
        # self.sapst = None # stable_speed_region_after_pst
        # """:type: int"""

        self.snowday_ffs = None
        """:type: float"""

        self.nfrt = None
        """:type: int"""

        self.ncrt_type = None
        """:type: int"""

        self.sist = None
        """:type: int"""

        self.own_ncrt = None
        """:type: int"""

        # self.worst_ratio_idx = None
        # """:type: int"""

        # self.adata = None
        # """:type: AnalysisData """

        self.additional = {}

        # self.estimated_nighttime_snowing = []
        # """:type: list[int] """
        # self.uk_change_point = []
        # """:type: list[int] """
        # self.reduction_by_snow = []
        # """:type: list[int] """
        #
        # self.search_start_idx = None
        # """:type: int"""

        self.ncrt_search_uth = None
        """:type: float"""

        self.ncrt_search_rth = None
        """:type: float"""

        self.ncrt_search_sidx = None
        """:type: int"""

        self.ncrt_search_eidx = None
        """:type: int"""

        # self.ncrt_qk_sidx = None
        # """:type: int"""
        #
        # self.ncrt_qk_eidx = None
        # """:type: int"""

        self.wn_ffs_idx = None
        """:type: int"""

        self.should_wn_uk_without_ffs = False
        """:type: bool"""

        self.wn2_interval_sidx = None
        """:type: int"""

        self.wn2_interval_eidx = None
        """:type: int"""

        self.wn2_after_congestion_idx = None
        """:type: int"""

        self.snowday_ffs = None
        """:type: float """

        self.normal_ffs = None
        """:type: float """

        self.may_recovered_speed = None
        """:type: float """

        # self.is_recovered_at_lost = False

        # flags
        self.is_loaded = False
        # self.is_finished = False

    def prepare_data(self, detectors=None):
        loaded = self._load(detectors=detectors)
        if not loaded:
            return False

        self.is_loaded = True

        return True

    def _load(self, detectors=None):
        """

        :param detectors:
        :type detectors: list[pyticas.ttypes.DetectorObject]
        :return:
        :rtype:
        """
        logger = getLogger(__name__)
        infra = ncrtes.get_infra()
        rdr = infra.rdr
        prd = self.snow_event.data_period
        if not detectors:
            dc, valid_detectors = lane.get_detector_checker(self.target_station)
        else:
            dc, valid_detectors = lambda det: (det in detectors), detectors

        us = np.array(rdr.get_speed(self.target_station, prd, dc).data)
        ks = np.array(rdr.get_density(self.target_station, prd, dc).data)
        qs = np.array(rdr.get_average_flow(self.target_station, prd, dc).data)

        if infra.is_missing(us):
            logger.warning('[%s] Preparing data data missing' % self.target_station.station_id)
            return False

        self.ks, self.us, self.qs = self._interpolate_missing(ks, us, qs)

        self.ks, self.us = data_util.fix_rapid_fluctuation(self.ks, self.us)

        self.n_data = len(self.ks)

        # night time with None nsr_data
        if self.normal_func is not None:
            self.normal_func.prepare_functions()
            self.night_us = np.array(
                self.normal_func.nighttime_func.speeds(self.snow_event.data_period.get_timeline(as_datetime=True)))
            self.night_ks = np.array(
                self.normal_func.nighttime_func.densities(self.snow_event.data_period.get_timeline(as_datetime=True)))

            self.sus_for_night = data_util.smooth(self.us, setting.SW_2HOURS)
            self.sks_for_night = data_util.smooth(self.ks, setting.SW_2HOURS)

            night_ratios = []
            for idx in range(0, len(self.sus_for_night)):
                if self.night_us[idx]:
                    cur_ratio = self.sus_for_night[idx] / self.night_us[idx]
                else:
                    cur_ratio = None
                night_ratios.append(cur_ratio)

            self.night_ratios = np.array(night_ratios)
            self.night_sratios = np.array(night_ratios)

            from pyticas_ncrtes.core.est.helper import nighttime_helper as nh
            segs = nh.nighttime_segments(self)
            for (sidx, eidx) in segs:
                # self.night_ratios[sidx:eidx+1] = data_util.smooth(self.night_ratios[sidx:eidx+1], setting.SMOOTHING_SIZE_FOR_NIGHTTIME)
                self.night_sratios[sidx:eidx + 1] = np.array(
                    data_util.stepping(self.night_ratios[sidx:eidx + 1], self.RATIO_STEPPING_LEVEL))

        else:
            self.night_ratios = np.array([None] * len(self.ks))
            self.night_sratios = np.array([None] * len(self.ks))
            self.night_us = np.array([None] * len(self.ks))

        # smoothing

        self.lsus = data_util.smooth(self.us, setting.SW_1HOUR)
        self.lsks = data_util.smooth(self.ks, setting.SW_1HOUR)
        self.lsqs = data_util.smooth(self.qs, setting.SW_1HOUR)

        self.sus = data_util.smooth(self.us, setting.SW_2HOURS)
        self.sks = data_util.smooth(self.ks, setting.SW_2HOURS)
        self.sqs = data_util.smooth(self.qs, setting.SW_2HOURS)

        self.qus = np.array(data_util.stepping(self.sus, 5))
        self.qks = np.array(data_util.stepping(self.sks, 3))

        merged_sus, merged_sks = self.sus.tolist(), self.sks.tolist()
        for idx, nu in enumerate(self.night_us):
            if nu is not None:
                merged_sks[idx] = self.sks_for_night[idx]
                merged_sus[idx] = self.sus_for_night[idx]
        # self.merged_sus = np.array(merged_sus)
        # self.merged_sks = np.array(merged_sks)

        # aggregated
        # self.aks, self.aus = data_util.adaptive_aggregation(self.ks, self.us, 3, 5)

        if self.normal_func and self.normal_func.is_valid():
            self.normal_func.daytime_func.prepare_functions()
            uk_function = self.normal_func.daytime_func.get_uk_function()
            self.normal_avg_us = np.array(uk_function.speeds(self.lsks))
            prev_not_none, next_not_none = None, None
            for idx in range(len(self.normal_avg_us)):
                if self.normal_avg_us[idx] is None:
                    for tidx in range(idx, self.n_data):
                        if self.normal_avg_us[tidx] is not None:
                            next_not_none = self.normal_avg_us[tidx]
                            break
                    self.normal_avg_us[idx] = np.nanmean([prev_not_none, next_not_none])
                else:
                    prev_not_none = self.normal_avg_us[idx]

            self.normal_ratios = self.sus / self.normal_avg_us

        return True

    def make_wet_normal_pattern(self, wn_ffs, k_at_ffs):
        uk_function = self.normal_func.daytime_func.get_uk_function()

        self.wn_ffs = wn_ffs
        self.k_at_wn_ffs = k_at_ffs

        if uk_function.is_valid() and self.us is not None:
            uk_function._wn_uk = None
            uk_function.make_wetnormal_uk(wn_ffs, k_at_ffs)

            # import matplotlib.pyplot as plt
            # wn_uk = uk_function._wn_uk
            # _ks = list(range(5, 80))
            # _us = uk_function.speeds(_ks)
            # plt.plot(_ks, _us)
            # plt.plot(_ks, uk_function.wet_normal_speeds(_ks))
            # plt.scatter(self.sks, self.sus)
            # plt.show()

            self.wn_avg_us = np.array(uk_function.wet_normal_speeds(self.lsks))
            self.wn_ratios = (self.sus / self.wn_avg_us)
            self.wn_sratios = np.array(data_util.smooth(self.wn_ratios, self.RATIO_SMOOTHING_SIZE))
            self.wn_qratios = np.array(data_util.stepping(self.wn_sratios, self.RATIO_STEPPING_LEVEL))

    def make_wet_normal_pattern_without_wnffs(self):
        uk_function = self.normal_func.daytime_func.get_uk_function()
        if not uk_function.is_valid():
            return

        target_ks = self.ks[self.wn2_interval_sidx:self.wn2_interval_eidx+1]
        target_us = self.us[self.wn2_interval_sidx:self.wn2_interval_eidx+1]

        _ks, _us = [], []
        for idx, _k in enumerate(target_ks):
            _avg, _stddev, _arounds = data_util.avg_y_of_around_x(target_ks, target_us, _k, 2)
            if any(_arounds):
                _ks.append(_k)
                _us.append(_avg)
        target_ks, target_us = np.array(_ks), np.array(_us)

        wh = np.where(target_ks > 10)
        target_us = target_us[wh]
        target_ks = target_ks[wh]

        recovered_k = self.sks[self.wn2_after_congestion_idx]
        recovered_u = min(self.sus[self.wn2_after_congestion_idx], self.normal_func.daytime_func.get_FFS())

        self.wn_ffs = recovered_u
        self.k_at_wn_ffs = max(recovered_k, self.normal_func.daytime_func.get_Kf())

        uk_function._wn_uk = None
        uk_function.make_wetnormal_uk_without_wnffs(target_ks, target_us, recovered_k, recovered_u)

        self.wn_avg_us = np.array(uk_function.wet_normal_speeds(self.lsks))
        self.wn_ratios = (self.sus / self.wn_avg_us)
        self.wn_sratios = np.array(data_util.smooth(self.wn_ratios, self.RATIO_SMOOTHING_SIZE))
        self.wn_qratios = np.array(data_util.stepping(self.wn_sratios, self.RATIO_STEPPING_LEVEL))


    def _interpolate_missing(self, ks, us, qs):
        """

        :type ks: numpy.ndarray
        :type us: numpy.ndarray
        :type qs: numpy.ndarray
        :rtype: (numpy.ndarray, numpy.ndarray, numpy.ndarray)
        """
        n_data = len(us)
        for idx, u in enumerate(us):
            k = ks[idx]
            if u < 0 or k < 0:
                pidx = np.where(us[:idx] > 0)[0][-1] if idx > 0 else np.where(us > 0)[0][-1]
                wh_n = np.where(us[idx + 1:] > 0) if idx < n_data - 1 else np.where(us > 9999)
                if wh_n[0].any():
                    nidx = wh_n[0][0]
                else:
                    nidx = np.where(us > 1)[0][-1]
                us[idx] = (us[pidx] + us[nidx]) / 2
                ks[idx] = (ks[pidx] + ks[nidx]) / 2
                qs[idx] = (qs[pidx] + qs[nidx]) / 2
        return ks, us, qs

    def _reported_regain_times(self, reported):
        """
        :type reported: dict[str, list[ReportedEvent]]
        :rtype: list[int]
        """
        self.reported_events = []
        """:type: list[ReportedEvent] """
        if self.snow_route:
            self.reported_events = reported.get(self.snow_route.id, [])

        if self.reported_events:
            attr = []
            for rep in self.reported_events:
                try:
                    attr.append(int(self.snow_event.time_to_index(rep.reported_regain_time)))
                except:
                    pass
            return attr
        else:
            return []

    def _get_snow_route(self, sroutes):
        """
        :type sroutes: list[SnowRoute]
        :rtype: SnowRoute
        """
        if not any(sroutes):
            return None
        for sr in sroutes:
            r = sr.get_route()
            if self.target_station in r.rnodes:
                return sr
        return None


class DaytimeData(Serializable):
    def __init__(self, target_station, periods, recovery_uk, not_congested_periods, not_congested_uk):
        """

        :type target_station: pyticas.ttypes.RNodeObject
        :type periods: list[pyticas.ttypes.Period]
        :type recovery_uk: dict[float, float]
        :type not_congested_periods: list[pyticas.ttypes.Period]
        :type not_congested_uk: dict[float, float]
        """
        self.station = target_station
        self.periods = periods
        self.recovery_uk = recovery_uk
        self.not_congested_periods = not_congested_periods
        self.not_congested_uk = not_congested_uk

    def __unserialized__(self):
        if self.recovery_uk:
            self.recovery_uk = {float(k): v for k, v in self.recovery_uk.items()}
        if self.not_congested_uk:
            self.not_congested_uk = {float(k): v for k, v in self.not_congested_uk.items()}

    def __str__(self):
        return '<%s station="%s">' % (self.__class__.__name__, self.station.station_id)

    def __repr__(self):
        return self.__str__()


class NighttimeData(Serializable):
    def __init__(self, target_station, avg_us, avg_ks, periods):
        """

        :type target_station: pyticas.ttypes.RNodeObject
        :type avg_us: list[float]
        :type avg_ks: list[float]
        :type periods: list[pyticas.ttypes.Period]
        """
        self.station = target_station
        self.avg_us = avg_us
        self.avg_ks = avg_ks
        self.periods = periods

    def __str__(self):
        return '<%s station="%s">' % (self.__class__.__name__, self.station.station_id)

    def __repr__(self):
        return self.__str__()


class NSRData(Serializable):
    def __init__(self, target_station, months, daytime_data, night_data, det_names):
        """

        :type target_station: pyticas.ttypes.RNodeObject
        :type months: list[(int, int)]
        :type daytime_data: DaytimeData
        :type night_data: NighttimeData
        :type det_names: list[str]
        """
        self.station = target_station
        self.months = months
        self.daytime_data = daytime_data
        self.night_data = night_data
        self.det_names = det_names

    def __str__(self):
        return '<%s station="%s">' % (self.__class__.__name__, self.station.station_id)

    def __repr__(self):
        return self.__str__()


class NighttimeFunction(Serializable):

    SMOOTHING_SIZE = 41

    def __init__(self, avg_us, avg_ks, start_time, end_time, interval):
        """

        :type avg_us: list[float]
        :type avg_ks: list[float]
        :type start_time: Union(datetime.time, None)
        :type end_time: Union(datetime.time, None)
        :type interval: int
        :return:
        """
        self.avg_us = avg_us
        self.avg_ks = avg_ks
        self.start_time = start_time
        self.end_time = end_time
        self.interval = interval
        self._func = None
        self._k_func = None

    def is_valid(self):
        return self.avg_us and len(self.avg_us) > 0

    def get_timeline(self):
        """

        :rtype: list[str]
        """
        return [dt.strftime("%H:%M") for dt in self._time_iterator()]

    def _time_iterator(self):
        today = datetime.date.today()
        sdate = datetime.datetime.combine(today - datetime.timedelta(days=1), self.start_time)
        edate = datetime.datetime.combine(today, self.end_time)
        while sdate < edate:
            yield sdate
            sdate += datetime.timedelta(seconds=self.interval)

    def get_curve_depth(self):
        pos_fus = [v for v in self.get_night_speeds() if v and v > 0]
        if pos_fus:
            diff = round(pos_fus[0] - min(pos_fus), 1)
        else:
            diff = 0
        return diff

    def get_night_speeds(self):
        """ returns night-time speeds by nighttime-function

        :return: list[float]
        """
        us = []
        for curdate in self._time_iterator():
            us.append(self.speed(curdate))
        return us

    def prepare_function(self):
        if self._func:
            return

        w = NighttimeFunction.SMOOTHING_SIZE
        target_us = np.array(data_util.smooth(self.avg_us, w))
        target_ks = np.array(data_util.smooth(self.avg_ks, w))

        # nsr_data = data_util.trending(self.avg_us, 6, 1, less_shift=True)
        from_idx = 0
        n_data = len(target_us)
        to_idx = -1

        # if self.stddev_list:
        #     self.stddev_list = data_util.trending(self.stddev_list, 6, 0.5, smoothing_function=data_util.gaussian_filter)
        # else:
        #     self.stddev_list = []

        for idx, d in enumerate(target_us):
            if not idx: continue
            if target_us[idx] < target_us[idx - 1]:
                from_idx = idx
                break

        for idx in range(n_data - 1, -1, -1):
            if not idx or idx == from_idx:
                break
            if target_us[idx] > target_us[idx - 1]:
                to_idx = idx
                break

        if to_idx < 0:
            # speed decreases by morning traffic
            #   while speed is still not fully recovered
            max_d = -1
            left_peak_idx = -1
            x1, y1 = 0, target_us[0]
            x2, y2 = n_data - 1, target_us[-1]

            for idx in range(max(from_idx, 0), n_data):
                y = data_util.get_value_on_line(idx, y1, y2, x1, x2)
                if y > target_us[idx]:
                    d = data_util.distance_to_line(idx, target_us[idx], y1, y2, x1, x2)
                    if d > max_d:
                        left_peak_idx = idx
                        max_d = d

            x1, y1 = left_peak_idx, target_us[left_peak_idx]
            x2, y2 = n_data - 1, target_us[-1]

            max_d = -1
            for idx in range(left_peak_idx, n_data):
                y = data_util.get_value_on_line(idx, y1, y2, x1, x2)
                if y > target_us[idx]:
                    continue
                d = data_util.distance_to_line(idx, target_us[idx], y1, y2, x1, x2)
                if d > max_d:
                    max_d = d
                    to_idx = idx

        # import matplotlib.pyplot as plt
        # print('-> nighttime : ', (from_idx, to_idx), len(data))
        # plt.figure()
        # plt.plot(data, c='k')
        # plt.axvline(x=from_idx+1, c='b')
        # plt.axvline(x=to_idx-1, c='r')
        # plt.ylim(ymin=0)
        # plt.show()

        if to_idx - from_idx < 2:
            from_idx = -1
            to_idx = -1
        else:
            diff = target_us[from_idx] - min(target_us[from_idx + 1:to_idx])
            if diff < 0.01:
                from_idx = -1
                to_idx = -1

        if from_idx < 0 and to_idx < 0:
            wh = np.where(target_ks < 7)
            if any(wh[0]):
                from_idx = wh[0][0]
                to_idx = wh[0][-1]

        def _late_night_speed(x):
            idx = self.nighttime_index(x)
            if idx < 0 or idx < from_idx or idx > to_idx:
                return None
            return target_us[idx]

        def late_night_speed(x):
            if isinstance(x, collections.Iterable):
                return [_late_night_speed(v) for v in x]
            else:
                return _late_night_speed(x)

        def _late_night_density(x):
            idx = self.nighttime_index(x)
            if idx < 0 or idx < from_idx or idx > to_idx:
                return None
            return target_ks[idx]

        def late_night_density(x):
            if isinstance(x, collections.Iterable):
                return [_late_night_density(v) for v in x]
            else:
                return _late_night_density(x)

        self._func = late_night_speed
        self._k_func = late_night_density

    def prepare_function_origin(self):
        if self._func:
            return

        w = int(4 * 60 * (self.interval / 60) + 1)  # 4hour
        data = np.array(data_util.smooth(self.avg_us, w))
        # nsr_data = data_util.trending(self.avg_us, 6, 1, less_shift=True)
        from_idx = 0
        n_data = len(data)
        to_idx = -1

        # if self.stddev_list:
        #     self.stddev_list = data_util.trending(self.stddev_list, 6, 0.5, smoothing_function=data_util.gaussian_filter)
        # else:
        #     self.stddev_list = []

        for idx, d in enumerate(data):
            if not idx: continue
            if data[idx] < data[idx - 1]:
                from_idx = idx
                break

        for idx in range(n_data - 1, -1, -1):
            if not idx or idx == from_idx:
                break
            if data[idx] > data[idx - 1]:
                to_idx = idx
                break

        if to_idx < 0:
            # speed decreases by morning traffic
            #   while speed is still not fully recovered
            max_d = -1
            left_peak_idx = -1
            x1, y1 = 0, data[0]
            x2, y2 = n_data - 1, data[-1]

            for idx in range(max(from_idx, 0), n_data):
                y = data_util.get_value_on_line(idx, y1, y2, x1, x2)
                if y > data[idx]:
                    d = data_util.distance_to_line(idx, data[idx], y1, y2, x1, x2)
                    if d > max_d:
                        left_peak_idx = idx
                        max_d = d

            x1, y1 = left_peak_idx, data[left_peak_idx]
            x2, y2 = n_data - 1, data[-1]

            max_d = -1
            for idx in range(left_peak_idx, n_data):
                y = data_util.get_value_on_line(idx, y1, y2, x1, x2)
                if y > data[idx]:
                    continue
                d = data_util.distance_to_line(idx, data[idx], y1, y2, x1, x2)
                if d > max_d:
                    max_d = d
                    to_idx = idx

        # import matplotlib.pyplot as plt
        # print('-> nighttime : ', (from_idx, to_idx), len(data))
        # plt.figure()
        # plt.plot(data, c='k')
        # plt.axvline(x=from_idx+1, c='b')
        # plt.axvline(x=to_idx-1, c='r')
        # plt.ylim(ymin=0)
        # plt.show()

        if to_idx - from_idx < 2:
            from_idx = -1
            to_idx = -1
        else:
            diff = data[from_idx] - min(data[from_idx + 1:to_idx])
            if diff < 0.01:
                from_idx = -1
                to_idx = -1

        def _late_night_speed(x):
            idx = self.nighttime_index(x)
            if idx < 0 or idx < from_idx or idx > to_idx:
                return None
            return data[idx]

        def late_night_speed(x):
            if isinstance(x, collections.Iterable):
                return [_late_night_speed(v) for v in x]
            else:
                return _late_night_speed(x)

        self._func = late_night_speed

    def nighttime_index(self, dt):
        """
        :type dt: datetime.datetime
        :rtype: int
        """

        dtt = dt.time()
        dth = dtt.hour

        if self.is_late(dt) < 0:
            return -1

        idx = 0
        for curdate in self._time_iterator():
            cur_time = curdate.time()
            if LATE_NIGHT_START_TIME <= dth < LATE_NIGHT_END_TIME and cur_time >= dtt:
                return idx
            else:
                if LATE_NIGHT_START_TIME <= dth < 24 and cur_time >= dtt:
                    return idx
                if 0 <= dth < LATE_NIGHT_END_TIME and 0 <= cur_time.hour < LATE_NIGHT_END_TIME and cur_time >= dtt:
                    return idx
            idx += 1

        return -1

    def speed(self, dt):
        """
        :type dt: datetime.datetime
        :rtype: float:
        """
        return self._func(dt)

    def speeds(self, dts):
        """
        :type dts: list[datetime.datetime]
        :rtype: list[float]:
        """
        return [self._func(dt) for dt in dts]

    def density(self, dt):
        """
        :type dt: datetime.datetime
        :rtype: float:
        """
        return self._k_func(dt)

    def densities(self, dts):
        """
        :type dts: list[datetime.datetime]
        :rtype: list[float]:
        """
        return [self._k_func(dt) for dt in dts]

    def is_late(self, dt):
        """

        :type dt: datetime.datetime
        :return:
        """
        h = -1
        if isinstance(dt, int):
            h = dt
        elif isinstance(dt, str):
            if '-' in dt:
                h = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').time().hour
            else:
                h = datetime.datetime.strptime(dt, '%H:%M:%S').time().hour
        elif isinstance(dt, datetime.datetime):
            h = dt.time().hour
        elif isinstance(dt, datetime.time):
            h = dt.hour
        else:
            raise Exception('Not available parameter!!')

        # 22 - 5
        if LATE_NIGHT_START_TIME <= LATE_NIGHT_END_TIME:
            if LATE_NIGHT_START_TIME <= h < LATE_NIGHT_END_TIME:
                return h
            else:
                return -1
        else:
            if LATE_NIGHT_START_TIME <= h or h < LATE_NIGHT_END_TIME:
                return h
            else:
                return -1


class FitFunction(Serializable):
    def __init__(self, popts, additional, x1=-1, x2=9999):
        """

        :type popts: Union(tuple, None)
        :type additional: dict
        :type x1: float
        :type x2: float
        """
        self.popts = popts
        """:type: (float, float)"""
        self.additional = additional
        self.x1 = x1
        self.x2 = x2

    def is_valid(self):
        return True if self.popts != None and any(self.popts) else False

    def get_function(self):
        func_form = self.__class__.get_fitting_function()
        popts = self.popts if self.popts else ()
        if not popts:
            return None

        def _func(k):
            return func_form(k, *popts)

        return _func

    def get_speed(self, k):
        if self.popts:
            return self.__class__.get_fitting_function()(k, *self.popts)
        else:
            return None

    def equation(self):
        return 'Equation of FitFunction'

    @classmethod
    def get_fitting_function(self):
        raise NotImplementedError("Must override method")

    def __str__(self):
        return '<%s popts="%s" x1="%s" x2="%s">' % (self.__class__.__name__,
                                                    str(self.popts), str(self.x1), str(self.x2))

    def __repr__(self):
        return self.__str__()


class LineFunction(FitFunction):
    def __init__(self, popts, x1, x2):
        super().__init__(popts, {}, x1, x2)

    def get_function(self):
        x1 = self.x1
        x2 = self.x2
        if self.popts == None or not any(self.popts):
            return lambda k: -1
        fit_func = self.__class__.get_fitting_function()

        def _func(k):
            if x1 <= k <= x2:
                return fit_func(k, *self.popts)
            else:
                return None

        return _func

    def equation(self):
        if self.popts:
            return 'LineFunction: u = %.2f * k %s %.2f (%.2f < k <= %.2f)' % (
                self.popts[0],
                '+' if self.popts[1] > 0 else '-',
                abs(self.popts[1]),
                self.x1, self.x2
            )


    @classmethod
    def get_fitting_function(self):
        """
        :rtype: callable
        """
        return lambda x, a, b: a * x + b




class LogFunction(FitFunction):
    @classmethod
    def get_fitting_function(self):
        """
        :rtype: callable
        """
        return lambda x, a, b: 1 + a / (1 + np.exp(x)) ** b

    def equation(self):
        if self.popts:
            return 'LogFunction: u = 1 + %.2f / (1 + exp(k))^%.2f (%.2f < k <= %.2f)' % (
                self.popts[0],
                self.popts[1],
                self.x1, self.x2
            )



class SegmentedFunction(Serializable):
    FUNCTION_SMOOTHING_WINDOW = 151
    RATIO_DROP_AT_KT = 0

    def __init__(self, funcs, Kf, Kt, ffs):
        """

        :type funcs: list[FitFunction]
        :type Kf: Union(float, None)
        :type Kt: Union(float, None)
        :type ffs: Union(float, None)
        """
        self.funcs = funcs
        self.Kf = Kf
        self.Kt = Kt
        self.ffs = ffs
        self.shift = 0
        self._uk = None
        self._wn_uk = None
        self._wn_range_uk = None

    def set_shift(self, shift):
        self.shift = shift

    def serialize(self):
        self._uk = []
        self._wn_uk = []
        self._wn_range_uk = []
        return super().serialize()

    def is_valid(self):
        return any(self.funcs)

    def speed(self, density, uk=None):
        """

        :type density: float
        :type uk: dict[float, float]
        :return:
        """
        if not self.funcs:
            return None

        if not uk and not self._uk:
            self._make_uk()

        uk_data = uk if uk else self._uk

        _k = round(density * 10)

        if _k in uk_data:
            return uk_data[_k]

        if _k <= min(uk_data.keys()):
            return max(uk_data.values())

        if _k >= max(uk_data.keys()):
            return min(uk_data.values())

        print('=> None : ', density, (min(uk_data.keys()), max(uk_data.keys())))

        return None

    def speeds(self, densities, uk=None):
        """

        :type densities: Union[list[float], numpy.ndarray]
        :type uk: dict[float, float]
        :rtype: list[float]
        """
        return [self.speed(k, uk) for k in densities]

    def _make_uk(self):
        _ks, _us = [], []
        for _k in np.arange(0, 300, 0.1):
            _u = None
            for f in self.funcs:
                if f.x1 <= _k <= f.x2:
                    _u = f.get_speed(_k)
                    break

            if _u:
                _ks.append(round(_k * 10))
                _us.append(_u)

        _us = data_util.smooth(_us, self.FUNCTION_SMOOTHING_WINDOW)

        self._uk = {_k: _us[idx] + self._calculate_shift_by_k(_k / 10) for idx, _k in enumerate(_ks)}

    def _calculate_shift_by_k(self, k):
        """
 
        :type k: float
        :rtype: float
        """
        k_limit = 100
        log_func = self.funcs[-1]
        if k <= log_func.x1:
            return self.shift
        if k >= k_limit:
            return 0
        x1 = k - log_func.x1
        x2 = k_limit - log_func.x1
        y2 = abs(self.shift)
        shift_at_k = (x2 - x1) * y2 / x2
        if self.shift > 0:
            return shift_at_k
        else:
            return -shift_at_k

    def _variable_range_uk(self, k1, r1, k2, r2):
        """

        :type k1: float
        :type r1: float
        :type k2: float
        :type r2: float
        :rtype: dict[float, float]
        """
        _ks, _us = [], []

        n_steps = (k2 - k1) * 10
        r_change_rate = (r2 - r1) / n_steps

        for idx, _k in enumerate(np.arange(k1, k2, 0.1)):
            _u = self.speed(_k)
            if _u:
                _ks.append(round(_k * 10))
                _us.append(_u * (r1 + idx * r_change_rate))

        return {_k: _us[idx] for idx, _k in enumerate(_ks)}

    # def make_wetnormal_uk_origin(self, wn_ffs, k_at_ffs):
    #     """
    #     :type wn_ffs: float
    #     :type k_at_ffs: float
    #     """
    #     _Kf = np.floor(self.Kf * 10) / 10
    #     _Kt = np.floor(self.Kt * 10) / 10
    #     k_at_ffs = np.floor(k_at_ffs * 10) / 10
    #
    #     kwn = max(_Kf, k_at_ffs)
    #
    #     # find Ks
    #     Ks = None
    #     for _k in np.arange(kwn, 80, 0.1):
    #         _nu = self.speed(_k)
    #         if _nu and _nu <= wn_ffs:
    #             Ks = _k
    #             break
    #
    #     # initial shift value and change_rate
    #     k_merging = 150
    #     shift = Ks - kwn
    #     steps = (k_merging - kwn) * 10
    #     shift_change_step = shift / steps
    #
    #     # wet_normal uk
    #     wn_uk = {}
    #
    #     # wn_ffs from k=0 to kwn
    #     for _k in np.arange(0, kwn, 0.1):
    #         wn_uk[round(_k * 10)] = wn_ffs
    #
    #     # from k=wn to k_merging
    #     for idx, _k in enumerate(np.arange(kwn, k_merging, 0.1)):
    #         cur_shift = shift - idx * shift_change_step
    #         reversed_shifted_k = _k + cur_shift
    #         wn_uk[round(_k * 10)] = self.speed(reversed_shifted_k)
    #
    #     u_min = min(wn_uk.values())
    #
    #     # after k_merging
    #     for _k in np.arange(k_merging + 0.1, 300, 0.1):
    #         wn_uk[round(_k * 10)] = float(min(u_min, self.speed(_k)))
    #
    #     # smoothing
    #     # _ks = list(sorted(wn_uk.keys()))
    #     # _us = [ wn_uk[_k] for _k in _ks ]
    #     # _us = data_util.smooth(_us, self.FUNCTION_SMOOTHING_WINDOW)
    #     # self._wn_uk = {_k: _us[idx] for idx, _k in enumerate(_ks)}
    #
    #     self._wn_uk = wn_uk
    #
    #
    # def make_wetnormal_uk_second(self, wn_ffs, k_at_ffs):
    #     """
    #     :type wn_ffs: float
    #     :type k_at_ffs: float
    #     """
    #     _Kf = np.floor(self.Kf * 10) / 10
    #     _Kt = np.floor(self.Kt * 10) / 10
    #     k_at_ffs = np.floor(k_at_ffs * 10) / 10
    #
    #     # wet_normal uk
    #     wn_uk = {}
    #
    #     # speed difference at wn_ffs
    #     nu_at_wn_ffs = self.speed(k_at_ffs)
    #     udiff = max(nu_at_wn_ffs - wn_ffs, 0)
    #
    #     for _k in np.arange(0, k_at_ffs, 0.1):
    #         wn_uk[round(_k * 10)] = wn_ffs
    #
    #     if k_at_ffs < _Kt:
    #         for _k in np.arange(k_at_ffs, _Kt, 0.1):
    #             wn_uk[round(_k * 10)] = self.speed(_k) - udiff
    #
    #     kwn = max(_Kt, k_at_ffs)
    #     u_at_kwn = min(wn_uk.values())
    #
    #     # find Ks
    #     Ks = None
    #     for _k in np.arange(kwn, 80, 0.1):
    #         _nu = self.speed(_k)
    #         if _nu and _nu <= u_at_kwn:
    #             Ks = _k
    #             break
    #
    #     # initial shift value and change_rate
    #     k_merging = 150
    #     shift = Ks - kwn
    #     steps = (k_merging - kwn) * 10
    #     shift_change_step = shift / steps
    #
    #     # from kwn to k_merging
    #     for idx, _k in enumerate(np.arange(kwn, k_merging, 0.1)):
    #         cur_shift = shift - idx * shift_change_step
    #         reversed_shifted_k = _k + cur_shift
    #         wn_uk[round(_k * 10)] = self.speed(reversed_shifted_k)
    #
    #     u_min = min(wn_uk.values())
    #
    #     # after k_merging
    #     for _k in np.arange(k_merging + 0.1, 300, 0.1):
    #         wn_uk[round(_k * 10)] = float(min(u_min, self.speed(_k)))
    #
    #     # smoothing
    #     # _ks = list(sorted(wn_uk.keys()))
    #     # _us = [ wn_uk[_k] for _k in _ks ]
    #     # _us = data_util.smooth(_us, self.FUNCTION_SMOOTHING_WINDOW)
    #     # self._wn_uk = {_k: _us[idx] for idx, _k in enumerate(_ks)}
    #
    #     self._wn_uk = wn_uk

    def make_wetnormal_uk(self, wn_ffs, k_at_ffs):
        """
        :type wn_ffs: float
        :type k_at_ffs: float
        """
        _Kf = np.floor(self.Kf * 10) / 10
        _Kt = np.floor(self.Kt * 10) / 10
        k_at_ffs = np.floor(k_at_ffs * 10) / 10

        # wet_normal uk
        wn_uk = {}

        # speed difference at wn_ffs
        nu_at_wn_ffs = self.speed(k_at_ffs)
        udiff = max(nu_at_wn_ffs - wn_ffs, 0)

        for _k in np.arange(0, k_at_ffs, 0.1):
            wn_uk[round(_k * 10)] = wn_ffs

        # if k_at_ffs < _Kt:
        #     for _k in np.arange(k_at_ffs, _Kt, 0.1):
        #         wn_uk[round(_k * 10)] = self.speed(_k) - udiff

        # kwn = max(_Kt, k_at_ffs)
        kwn = k_at_ffs
        u_at_kwn = min(wn_uk.values())

        # find Ks
        Ks = None
        for _k in np.arange(kwn, 80, 0.1):
            _nu = self.speed(_k)
            if _nu and _nu <= u_at_kwn:
                Ks = _k
                break

        # initial shift value and change_rate
        k_merging = 100
        shift = Ks - kwn
        steps = (k_merging - kwn) * 10
        shift_change_step = shift / steps

        # from kwn to k_merging
        for idx, _k in enumerate(np.arange(kwn, k_merging+0.1, 0.1)):
            cur_shift = shift - idx * shift_change_step
            reversed_shifted_k = _k + cur_shift
            wn_uk[round(_k * 10)] = self.speed(reversed_shifted_k)

        u_min = min(wn_uk.values())

        # after k_merging
        for _k in np.arange(k_merging + 0.1, 300, 0.1):
            wn_uk[round(_k * 10)] = float(min(u_min, self.speed(_k)))

        # smoothing
        # _ks = list(sorted(wn_uk.keys()))
        # _us = [ wn_uk[_k] for _k in _ks ]
        # _us = data_util.smooth(_us, self.FUNCTION_SMOOTHING_WINDOW)
        # self._wn_uk = {_k: _us[idx] for idx, _k in enumerate(_ks)}

        self._wn_uk = wn_uk

    def _calculate_wetnormal_shift(self, k, u):
        """
        :type k: float
        :type u: float
        :rtype: float
        """
        if u >= self.speed(k):
            return 0
        for _k in np.arange(k, 200, 0.1):
            _nu = self.speed(_k)
            if _nu and _nu <= u:
                return _k - k
        return None

    def make_wetnormal_uk_without_wnffs(self, target_ks, target_us, recovered_k, recovered_u):
        """
        :type target_ks: numpy.ndarray
        :type target_us: numpy.ndarray
        :type recovered_k: float
        :type recovered_u: float
        """
        recovered_k, recovered_u = round(recovered_k) * 10 / 10, round(recovered_u) * 10 / 10
        shift0 = self._calculate_wetnormal_shift(recovered_k, recovered_u)
        shifts = [ self._calculate_wetnormal_shift(_k, target_us[idx]) for idx, _k in enumerate(target_ks) ]

        maxshift_idx = np.argmax(np.array(shifts)).item()
        maxshift = shifts[maxshift_idx]
        maxshift_k, maxshift_u = round(target_ks[maxshift_idx]) * 10 / 10, round(target_us[maxshift_idx]) * 10 / 10

        # initial shift value and change_rate
        k_merging = 150

        # wet_normal uk
        wn_uk = {}

        # from k=0 to wn_ffs
        for _k in np.arange(0, recovered_k, 0.1):
            wn_uk[round(_k * 10)] = recovered_u

        # from wn_ffs to maxshift
        steps = (maxshift_k - recovered_k) * 10
        shift_change_step = (shift0 - maxshift) / steps
        for idx, _k in enumerate(np.arange(recovered_k, maxshift_k, 0.1)):
            cur_shift = shift0 - idx * shift_change_step
            reversed_shifted_k = _k + cur_shift
            wn_uk[round(_k * 10)] = self.speed(reversed_shifted_k)

        # from maxshift to k_merging
        steps = (k_merging - maxshift_k) * 10
        shift_change_step = maxshift / steps
        for idx, _k in enumerate(np.arange(maxshift_k, k_merging, 0.1)):
            cur_shift = maxshift - idx * shift_change_step
            reversed_shifted_k = _k + cur_shift
            wn_uk[round(_k * 10)] = self.speed(reversed_shifted_k)

        u_min = min(wn_uk.values())

        # after k_merging
        for _k in np.arange(k_merging + 0.1, 300, 0.1):
            wn_uk[round(_k * 10)] = float(min(u_min, self.speed(_k)))

        # smoothing
        _ks = list(sorted(wn_uk.keys()))
        _us = [ wn_uk[_k] for _k in _ks ]
        _ks = [ _k / 10 for _k in _ks]
        # _us = data_util.smooth(_us, self.FUNCTION_SMOOTHING_WINDOW)

        _ks2 = list(sorted(self._uk.keys()))
        _us2 = [ self._uk[_k] for _k in _ks2 ]
        _ks2 = [ _k / 10 for _k in _ks2]

        # import matplotlib.pyplot as plt
        # fig = plt.figure()
        # plt.scatter(_ks, _us)
        # plt.scatter(_ks2, _us2, c='g', marker='^')
        # plt.scatter(target_ks, target_us, marker='x', c='r', lw=2)
        # plt.axvline(x=recovered_k, c='r')
        # plt.axvline(x=maxshift_k, c='g')
        # plt.xlim(xmin=0, xmax=90)
        # plt.ylim(ymin=0, ymax=90)
        # plt.show()

        self._wn_uk = wn_uk
        # self._wn_uk = {_k: _us[idx] for idx, _k in enumerate(_ks)}


    def wet_normal_speed(self, density):
        """

        :type density: float
        :rtype:
        """
        _k = round(density * 10)
        if _k in self._wn_uk:
            return self._wn_uk[_k]

        return None

    def wet_normal_speeds(self, densities):
        """
        :type densities: Union[list[float], numpy.ndarray]
        :rtype: list[float]
        """
        return [self.wet_normal_speed(k) for k in densities]

    @classmethod
    def unserialize(cls, kwargs):
        obj = cls.__new__(cls)
        for k, v in kwargs.items():
            setattr(obj, k, v)

        if not hasattr(obj, 'shift'):
            setattr(obj, 'shift', 0)
        return obj


class DaytimeFunction(Serializable):
    def __init__(self, target_station, recovery_function):
        """

        :type target_station: pyticas.ttypes.RNodeObject
        :type recovery_function: SegmentedFunction
        """
        self.station = target_station
        self.recovery_function = recovery_function
        self.shift = 0

    def set_shift(self, shift):
        self.shift = shift
        if self.recovery_function:
            self.recovery_function.set_shift(shift)

    def prepare_functions(self):
        pass

    def get_uk_function(self):
        """
        :rtype: SegmentedFunction
        """
        return self.recovery_function

    def get_Kt(self):
        """
        :rtype: float
        """
        return self.get_uk_function().Kt

    def get_Kf(self):
        """
        :rtype: float
        """
        return self.get_uk_function().Kf

    def get_FFS(self):
        """
        :rtype: float
        """
        uk_func = self.get_uk_function()
        if uk_func and uk_func.ffs:
            return uk_func.ffs  + self.shift
        else:
            return None

    def recovery_speed(self, density):
        """
        :type density: float
        :rtype: float
        """
        if not self.recovery_function:
            return None
        return self.recovery_function.speed(density)

    def recovery_speeds(self, densities):
        """
        :type densities: list[float]
        :rtype: list[float]
        """
        return [self.recovery_speed(k) for k in densities]

    @classmethod
    def unserialize(cls, kwargs):
        obj = cls.__new__(cls)
        for k, v in kwargs.items():
            setattr(obj, k, v)

        if not hasattr(obj, 'shift'):
            setattr(obj, 'shift', 0)
        return obj

    def __str__(self):
        return '<%s station=%s Kt=%s Kf=%s>' % (
            self.__class__.__name__, self.station.station_id, self.get_Kt(), self.get_Kf())

    def __repr__(self):
        return self.__str__()


class NSRFunction(Serializable):
    def __init__(self, target_station, months, dt_func, nt_func):
        """

        :type target_station: pyticas.ttypes.RNodeObject
        :type months: list[(int, int)]
        :type dt_func: DaytimeFunction
        :type nt_func: NighttimeFunction
        """
        self.station = target_station
        self.months = months
        self.daytime_func = dt_func
        self.nighttime_func = nt_func

    def prepare_functions(self):
        self.daytime_func.prepare_functions()
        self.nighttime_func.prepare_function()

    def is_valid(self):
        return self.daytime_func.recovery_function is not None and self.daytime_func.recovery_function.is_valid()
        # return self.daytime_func.recovery_function.is_valid()

    def recovery_speed(self, k):
        if self.daytime_func.recovery_function.is_valid():
            return self.daytime_func.recovery_speed(k)
        else:
            return None

    def recovery_speeds(self, ks):
        if self.daytime_func.recovery_function.is_valid():
            return self.daytime_func.recovery_speeds(ks)
        else:
            return None

    def nighttime_speed(self, dt):
        return self.nighttime_func.speed(dt)

    def nighttime_speeds(self, dts):
        return self.nighttime_func.speeds(dts)

    def __str__(self):
        return '<%s station="%s">' % (self.__class__.__name__, self.station.station_id)

    def __repr__(self):
        return self.__str__()


class ValidState(enum.Enum):
    VALID = 'valid data'
    NODATA = 'there is no UK data'
    HIGH_FFS = 'free-flow speed is too high'
    # NOFFS = 'FFS cannot be found'
    LOW_MAX_K = 'max density value is too low'
    # HIGH_MIN_U = 'minimum speed is too high'
    SPARSE_K = 'density distribution is too sparse'
    # WIDE_DISTRIBUTED_U = 'multiple pattern is detected'
    NO_FUNC = 'function is not calibrated'

    def is_valid(self):
        return (self == ValidState.VALID)


class NighttimePattern(object):
    def __init__(self, speed_trend, sidx, eidx, is_recovered, ratios):
        """

        :type speed_trend: int
        :type sidx: int
        :type eidx: int
        :type is_recovered: bool
        :type ratios: list[float]
        """
        self.idx = -1
        self.speed_trend = speed_trend
        self.sidx = sidx
        self.eidx = eidx
        self.is_recovered = is_recovered
        self.speed_trend_raw = speed_trend
        self.ratios = ratios

    def is_recovery(self):
        return self.speed_trend_raw == NighttimePatterns.TREND_RECOVERY

    def __repr__(self):
        return ('<NighttimePattern sidx=%d, eidx=%d, speed_trend=%d is_recovered=%s>'
                % (self.sidx, self.eidx, self.speed_trend, self.is_recovered))

    def __str__(self):
        return self.__repr__()


class NighttimePatterns(object):
    LITTLE_DROP = 3
    RECOVERED_RATIO = 0.9
    TREND_STABLE = 0
    TREND_RECOVERY = 1
    TREND_REDUCTION = -1

    PT_FULLY_RECOVERED = 1
    PT_RECOVERING_DURING_WHOLE_NIGHT = 2
    PT_REACH_TO_NORMAL = 3
    PT_RECOVERING_BUT_NOT_RECOVERED = 4
    PT_LOOSING_DURING_WHOLE_NIGHT = -1
    PT_LOOSING_AT_END_OF_NIGHT_AND_KEEP_LOOSING = -2
    PT_LOOSING_AT_END_OF_NIGHT = -3
    PT_UNKNOWN = 99

    def __init__(self, npatterns, edata):
        """

        :type npatterns: list[NighttimePattern]
        :type edata: ESTData
        """
        self.patterns = npatterns
        self.edata = edata
        for idx, pt in enumerate(self.patterns):
            pt.idx = idx

    def get_indices(self):
        """
        :rtype: (int, int)
        """
        return (self.patterns[0].sidx, self.patterns[-1].eidx)

    def patterns_before_recovered(self):
        """

        :rtype: (NighttimePattern, int, list[int], list[NighttimePattern])
        """
        recovered = []
        for _p in self.patterns:
            if _p.is_recovered:
                recovered.append(_p)
            else:
                recovered = []

        last_recovered = recovered[0] if recovered else None
        last_trend = self.TREND_RECOVERY
        trs = [_p.speed_trend for _p in self.patterns]
        pts = self.patterns

        if not last_recovered:
            last_trend = trs[-1]
            if last_trend == 0:
                not_stables = [_t for _t in reversed(trs) if _t != self.TREND_STABLE]
                if not_stables:
                    last_trend = not_stables[0]
                else:
                    last_trend = self.patterns[-1].speed_trend_raw
        else:
            trs = [_p.speed_trend for _p in self.patterns if _p.sidx <= last_recovered.sidx]
            pts = [_p for _p in self.patterns if _p.sidx <= last_recovered.sidx]

        return last_recovered, last_trend, trs, pts

    def recovery_pattern(self):

        last_recovered, last_trend, trs, pts = self.patterns_before_recovered()

        # no reduction and speed level is high
        if self.TREND_REDUCTION not in trs and self.patterns[-1].is_recovered:
            return self.PT_FULLY_RECOVERED

        # no reduction in rate and speed level is not high
        elif self.TREND_REDUCTION not in trs:
            return self.PT_RECOVERING_DURING_WHOLE_NIGHT

        # there's reduction in rate, but recovered at end of nighttime
        elif last_trend == self.TREND_RECOVERY and self.patterns[-1].is_recovered:
            return self.PT_REACH_TO_NORMAL

        # there's reduction in rate, but recovering at end of nighttime (not fully)
        elif last_trend == self.TREND_RECOVERY and not self.patterns[-1].is_recovered:
            return self.PT_RECOVERING_BUT_NOT_RECOVERED

        # continuously reduction in rate during nighttime
        elif self.TREND_RECOVERY not in trs:
            return self.PT_LOOSING_DURING_WHOLE_NIGHT

        # continuously reduction in rate during nighttime
        elif (last_trend == self.TREND_REDUCTION
              and not self.patterns[-1].is_recovered and not self.has_recoverying_before_peak()):
            return self.PT_LOOSING_AT_END_OF_NIGHT_AND_KEEP_LOOSING

        # continuously reduction during nighttime
        elif last_trend == self.TREND_REDUCTION and not self.patterns[-1].is_recovered:
            return self.PT_LOOSING_AT_END_OF_NIGHT

        return self.PT_UNKNOWN

    def has_recoverying_before_peak(self):
        s_limit = self.edata.target_station.s_limit
        eidx = self.patterns[-1].eidx
        if eidx > len(self.edata.sus) - setting.SW_1HOUR:
            return False

        _sus, _sks = self.edata.sus[eidx:], self.edata.sks[eidx:]
        wh_highk = np.where(_sks > 20)
        if not any(wh_highk[0]):
            return False
        sus, sks = _sus[:wh_highk[0][0]], _sks[:wh_highk[0][0]]

        # minmax_idxs = np.diff(np.sign(np.diff(sus))).nonzero()[0].tolist()
        # minmax = [0] + minmax_idxs + [len(sus) - 1]
        #
        # for idx in range(1, len(minmax)):
        #     pu, nu = sus[idx-1], sus[idx]
        #     if pu < nu:
        #         return True
        #
        # return False

        if max(sus) > s_limit - 5:
            return True

        return False

    def recovered_point(self):
        pass

    def __repr__(self):
        return ('<NighttimePatterns sidx=%d, eidx=%d, patterns=%d>'
                % (self.patterns[0].sidx, self.patterns[-1].eidx, len(self.patterns)))

    def __str__(self):
        return self.__repr__()


class Hill(object):
    def __init__(self, idx, sidx, eidx, ks, us, sks, sus):
        self.idx = idx
        self.sidx = sidx
        self.eidx = eidx
        self.trend_u = 1 if sus[0] < sus[-1] else -1
        self.trend_k = 1 if sks[0] < sks[-1] else -1
        self.ks = ks
        """:type: numpy.ndarray """
        self.us = us
        """:type: numpy.ndarray """
        self.sus = sus
        """:type: numpy.ndarray """
        self.sks = sks
        """:type: numpy.ndarray """

        self.normal_range_us = None
        """:type: numpy.ndarray """

        self.getting_closer_to_normal = -1
        """:type: Union(bool, int)"""

        self.update()

    def update(self):
        sorted_idxs = np.argsort(self.sks)
        self.ssks = self.sks[sorted_idxs]
        """:type: numpy.ndarray """
        self.ssus = self.sus[sorted_idxs]
        """:type: numpy.ndarray """

        sorted_idxs = np.argsort(self.sus)
        self.ssks_by_u = self.sks[sorted_idxs]
        """:type: numpy.ndarray """
        self.ssus_by_u = self.sus[sorted_idxs]
        """:type: numpy.ndarray """

    def is_increasing(self):
        return self.trend_u > 0

    def is_decreasing(self):
        return self.trend_u < 0

    def is_overlapped_to(self, other):
        """

        :type other: Hill
        :rtype: bool, int
        """
        kmin, kmax = self.k_range()
        okmin, okmax = other.k_range()

        if okmax < kmin or okmin > kmax:
            return False, None

        max_k = min(kmax, okmax)
        min_k = max(kmin, okmin)

        status = None
        if max_k - min_k > 1:
            middle_k = int((max_k + min_k) / 2)
            u1 = self.u_at_k(middle_k)
            u2 = other.u_at_k(middle_k)
            if u1 - u2 > 1:
                status = 1
            elif u1 - u2 < -1:
                status = -1
            else:
                status = 0

        return True, status

    def k_range(self):
        return int(math.ceil(min(self.sks))), int(math.floor(max(self.sks)))

    def u_range(self):
        return int(math.ceil(min(self.sus))), int(math.floor(max(self.sus)))

    def u_at_k(self, k):
        """ the value on the line that connects two points of (k1, u1) and (k2, u2)

        :type k: float
        :rtype: float
        """
        if k in self.sks:
            return self.sus[np.where(self.sks == k)[0]][0]

        over_idx = [idx for idx, tk in enumerate(self.ssks) if tk > k]
        if not over_idx or over_idx[0] >= len(self.ssks) - 1:
            return None

        # if not f_use_avg:
        pidx = over_idx[0] - 1
        nidx = pidx + 1
        u1, k1, u2, k2 = self.ssus[pidx], self.ssks[pidx], self.ssus[nidx], self.ssks[nidx]
        u = ((u2 - u1) / (k2 - k1)) * (k - k1) + u1
        return u

    def k_at_u(self, u):
        """

        :type u: float
        :rtype: float
        """
        if not any(self.sks) or not any(self.sus):
            return None

        if u in self.sus:
            k = self.sks[np.where(self.sus == u)[0]]
            return k

        under_idx = [idx for idx, tu in enumerate(self.ssus_by_u) if tu < u]
        if not under_idx or under_idx[0] >= len(self.ssus_by_u) - 1:
            return None
        pidx = under_idx[0] - 1
        nidx = pidx + 1
        u1, k1, u2, k2 = self.ssus_by_u[pidx], self.ssks_by_u[pidx], self.ssus_by_u[nidx], self.ssks_by_u[nidx]

        return (u - u1) / ((u2 - u1) / (k2 - k1)) + k1

    def is_little_hill(self, kth=1, uth=1):
        """
        :type kth: float
        :type uth: float
        :rtype: bool
        """
        (kmin, kmax), (umin, umax) = self.k_range(), self.u_range()

        if kmax - kmin < kth and umax - umin < uth:
            return True
        return False

    def clone(self):
        """
        :rtype: Hill
        """
        h = Hill(self.idx, self.sidx, self.eidx, self.ks, self.us, self.sks, self.sus)
        h.ssks = self.ssks
        h.ssus = self.ssus
        h.ssks_by_u = self.ssks_by_u
        h.ssus_by_u = self.ssus_by_u
        return h

    def info(self):
        return 'Hill[%d](%d-%d)' % (self.idx, self.sidx, self.eidx)

    def __repr__(self):
        return '<Hill idx="%d" sidx="%d" eidx="%d" trend="%d"/>' % (
            self.idx, self.sidx, self.eidx, self.trend_u
        )
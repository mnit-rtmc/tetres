# -*- coding: utf-8 -*-

"""  Detector Data Reader module

    - this module read traffic data using ``det_reader_raw`` module
    - collected data is packed to list for the given time duration
"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas import cfg
from pyticas.dr import det_reader_raw
from pyticas.ttypes import TrafficType
from pyticas.tool.cache import lru_cache


class DetectorDataReader(object):

    def __init__(self):
        pass
    
    @lru_cache
    def get_volume(self, det, prd):
        """
        :type det: pyticas.ttypes.DetectorObject
        :type prd: Period
        :rtype: list[float]
        """
        return self._set_interval(self._get_volume(det, prd), prd, TrafficType.volume)

    @lru_cache
    def _get_volume(self, det, prd):
        """
        :type det: pyticas.ttypes.DetectorObject
        :type prd: Period
        :rtype: list[float]
        """
        return self._check_max(det_reader_raw.read(det.name, prd, TrafficType.volume), cfg.MAX_VOLUME)

    @lru_cache
    def get_scan(self, det, prd):
        """
        :type det: pyticas.ttypes.DetectorObject
        :type prd: Period
        :rtype: list[float]
        """
        return self._set_interval(self._get_scan(det, prd), prd, TrafficType.scan)

    @lru_cache
    def _get_scan(self, det, prd):
        """
        :type det: pyticas.ttypes.DetectorObject
        :type prd: Period
        :rtype: list[float]
        """
        return self._check_max(det_reader_raw.read(det.name, prd, TrafficType.scan), cfg.MAX_SCANS)

    @lru_cache
    def get_density(self, det, prd):
        """
        :type det: pyticas.ttypes.DetectorObject
        :type prd: Period
        :rtype: list[float]
        """
        return self._set_interval(self._get_density(det, prd), prd, TrafficType.density)

    @lru_cache
    def _get_density(self, det, prd):
        """
        :type det: pyticas.ttypes.DetectorObject
        :type prd: Period
        :rtype: list[float]
        """
        scan_data = self._get_scan(det, prd)
        _density = []
        for i, c in enumerate(scan_data):
            if c <= 0:
                k = -1
            else:
                k = float(c) / cfg.MAX_SCANS * cfg.FEET_PER_MILE / det.get_field_length()
            _density.append(k)
        return _density

    @lru_cache
    def get_flow(self, det, prd):
        """
        :type det: pyticas.ttypes.DetectorObject
        :type prd: Period
        :rtype: list[float]
        """
        return self._set_interval(self._get_flow(det, prd), prd, TrafficType.flow)

    @lru_cache
    def _get_flow(self, det, prd):
        q = []
        volume_data = self._get_volume(det, prd)
        for i, v in enumerate(volume_data):
            if v == cfg.MISSING_VALUE:
                q.append(cfg.MISSING_VALUE)
            else:
                q.append(volume_data[i] * cfg.SAMPLES_PER_HOUR)
        return q

    @lru_cache
    def get_speed(self, det, prd):
        """
        :type det: pyticas.ttypes.DetectorObject
        :type prd: Period
        :rtype: list[float]
        """
        return self._get_speed(det, prd)

    @lru_cache
    def _get_speed(self, det, prd):
        """
        :type det: pyticas.ttypes.DetectorObject
        :type prd: Period
        :rtype: list[float]
        """
        if det.is_wavetronics():
            return self._check_max(det_reader_raw.read(det.name, prd, TrafficType.speed_wavetronics), cfg.MAX_SCANS)

        u = []
        q = self.get_flow(det, prd)
        k = self.get_density(det, prd)

        for i in range(len(q)):
            if any(k) == False or k[i] <= 0 or q[i] == cfg.MISSING_VALUE:
                speed = cfg.MISSING_VALUE
            else:
                speed = min(q[i] / k[i], cfg.MAX_SPEED)
            u.append(speed)

        return u

    @lru_cache
    def get_occupancy(self, det, prd):
        """
        :type det: pyticas.ttypes.DetectorObject
        :type prd: Period
        :rtype: list[float]
        """
        return self._set_interval(self._get_occupancy(det, prd), prd, TrafficType.occupancy)

    @lru_cache
    def _get_occupancy(self, det, prd):
        """
        :type det: pyticas.ttypes.DetectorObject
        :type prd: Period
        :rtype: list[float]
        """
        c = self._get_scan(det, prd)
        _occupancy = []
        for i in range(len(c)):
            if c[i] == cfg.MISSING_VALUE:
                _occupancy.append(cfg.MISSING_VALUE)
            else:
                _occupancy.append(float(c[i]) / cfg.MAX_SCANS * 100)
        return _occupancy

    def _set_interval(self, data, prd, traffic_type):
        ret = []
        freq = prd.interval // cfg.DETECTOR_DATA_INTERVAL
        for i in range(0, len(data), freq):
            data_sum = 0.0
            valid_count = 0
            next_itr = len(data) if (i + freq) > len(data) else (i + freq)

            for j in range(i, next_itr):
                v = data[j]
                if v >= 0:
                    data_sum += v
                    valid_count += 1
                #elif traffic_type.interval_function_name == "density_with_station":
                #    valid_count += 1

            if valid_count > 0 and data_sum >= 0:
                ret.append(traffic_type.interval_function(data_sum, valid_count, freq))
            else:
                ret.append(cfg.MISSING_VALUE)
        return ret

    def _check_max(self, data, maximum):
        for i in range(len(data)):
            data[i] = data[i] if data[i] < maximum else -1
        return data

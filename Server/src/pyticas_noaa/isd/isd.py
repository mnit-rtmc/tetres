# -*- coding: utf-8 -*-

import datetime

from pyticas.tool import distance
from pyticas_noaa.isd.isdreader import download as _download_data
from pyticas_noaa.isd.isdreader import parse as _read_station_data
from pyticas_noaa.isd.isdstations import download_isd_stations as _download_isd_stations
from pyticas_noaa.isd.isdstations import load_isd_stations as _load_isd_stations

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

"""
ISD (Integrated Surface Data) module
"""

SAME_TIMERANGE_IN_MINUTE = 60


def get_station_list(state='MN', station_filter=None, redownload=False):
    """
    :type state: str
    :type station_filter: function
    :type redownload: bool
    :rtype: list[pyticas_noaa.isd.isdtypes.ISDStation]
    """
    station_list_file = _download_isd_stations(redownload=redownload)
    if not station_list_file:
        return []
    return _load_isd_stations(station_list_file, state, station_filter=station_filter)


def find_nearby_station(lat, lon, dt, station_list):
    """
    :type lat: float
    :type lon: float
    :type dt: datetime.date
    :type station_list: list[pyticas_noaa.isd.isdtypes.ISDStation]
    :return: list of (distance, ISDStation) tuple from nearby station
    :rtype: list[(float, pyticas_noaa.isd.isdtypes.ISDStation)]
    """
    res = []
    for st in station_list:
        if st.begin > dt or st.end < dt:
            continue
        d = distance.distance_in_mile_with_coordinate(lat, lon, st.lat, st.lon)
        res.append((d, st))
    return sorted(res, key=lambda item: item[0])


def get_station_by_wban(wban):
    """
    :type wban: int or str
    :rtype: pyticas_noaa.isd.isdtypes.ISDStation
    """
    wban = str(wban)
    for isd_station in get_station_list():
        if isd_station.wban == wban:
            return isd_station
    return None


def get_data(isd_station, prd):
    """
    :type isd_station: pyticas_noaa.isd.isdtypes.ISDStation
    :type prd: pyticas.ttypes.Period
    :rtype: list[pyticas_noaa.isd.isdtypes.ISDData]
    """
    cur_date = prd.start_date.replace(hour=0, minute=0, second=0)
    delta = datetime.timedelta(hours=24)
    res = []
    while cur_date <= prd.end_date:
        a_day_data = get_day_data(isd_station, cur_date.year, cur_date.month, cur_date.day)
        if a_day_data:
            for isd_data in a_day_data:
                if prd.start_date <= isd_data.time() <= prd.end_date:
                    res.append(isd_data)
        cur_date += delta
    return res


def get_day_data(isd_station, year, month, day):
    """
    :type isd_station: pyticas_noaa.isd.isdtypes.ISDStation
    :type year: int or str
    :type month: int or str
    :type day: int or str
    :rtype: Generator: pyticas_noaa.isd.isdtypes.ISDData
    """
    current_year = datetime.datetime.now().year
    YEAR_COL = 15
    filepath1, filepath2, filepath3 = None, None, None

    if month == 1 and day == 1:
        filepath1 = _download_data(isd_station.usaf, isd_station.wban, year - 1)
    filepath2 = _download_data(isd_station.usaf, isd_station.wban, year)
    # Next year's data not available. Say, current date is 11/24/2020. How will we get 2021's data?
    if month == 12 and day == 31 and year + 1 <= current_year:
        filepath3 = _download_data(isd_station.usaf, isd_station.wban, year + 1)
        if not filepath3:
            return iter([])

    if not filepath2:
        return iter([])

    filepaths = [filepath1, filepath2, filepath3]
    filepaths = [fpath for fpath in filepaths if fpath]

    def _filter(isd_data):
        """
        :type isd_data: pyticas_noaa.isd.isdtypes.ISDData
        :rtype: bool
        """
        sdt = datetime.datetime(year, month, day, 0, 0, 0)
        edt = datetime.datetime(year, month, day, 23, 59, 59)
        return sdt <= isd_data.time() <= edt

    def _line_filter(line):
        line_year = int(line[YEAR_COL:YEAR_COL + 4])
        line_month = int(line[YEAR_COL + 4:YEAR_COL + 6])
        line_day = int(line[YEAR_COL + 6:YEAR_COL + 8])
        if line_year != year or line_month != month or line_day not in [day - 1, day, day + 1]:
            return False
        else:
            return True

    return _read_station_data(filepaths, _filter, _line_filter)


def get_year_data(isd_station, year):
    """
    :type isd_station: pyticas_noaa.isd.isdtypes.ISDStation
    :type year: int or str
    :rtype: Generator: pyticas_noaa.isd.isdtypes.ISDData
    """
    current_year = datetime.datetime.now().year
    YEAR_COL = 15
    filepath1 = _download_data(isd_station.usaf, isd_station.wban, year - 1)
    filepath2 = _download_data(isd_station.usaf, isd_station.wban, year)
    filepath3 = None
    # Next year's data not available. Say, current date is 11/24/2020. How will we get 2021's data?
    if year + 1 <= current_year:
        filepath3 = _download_data(isd_station.usaf, isd_station.wban, year + 1)
        if not filepath3:
            return iter([])

    if not filepath2:
        return iter([])

    filepaths = [filepath1, filepath2, filepath3]
    filepaths = [fpath for fpath in filepaths if fpath]

    def _filter(isd_data):
        """
        :type isd_data: pyticas_noaa.isd.isdtypes.ISDData
        :rtype: bool
        """
        return isd_data.time().year == year

    def _line_filter(line):
        line_year = int(line[YEAR_COL:YEAR_COL + 4])
        line_month = int(line[YEAR_COL + 4:YEAR_COL + 6])
        line_day = int(line[YEAR_COL + 6:YEAR_COL + 8])
        if line_year != year and not ((line_month == 12 and line_day == 31) or (line_month == 1 and line_day == 1)):
            return False
        else:
            return True

    return _read_station_data(filepaths, _filter, _line_filter)


def apply_interval(isddata_list, prd):
    """
    :type isddata_list: list[pyticas_noaa.isd.isdtypes.ISDData]
    :type prd: pyticas.ttypes.Period
    :rtype: list[pyticas_noaa.isd.isdtypes.ISDData]
    """
    datetimes = [isddata.time() for isddata in isddata_list]
    timelines = prd.get_timeline(as_datetime=True)

    def _find_data(fdt, cur_idx):
        """
        :type fdt: datetime.datetime
        :type cur_idx: int
        :rtype: float
        """
        for idx in range(cur_idx, len(datetimes)):
            dt = datetimes[idx]
            if dt >= fdt:
                return idx, isddata_list[idx]

        diff = isddata_list[-1].time() - fdt
        if diff.seconds > SAME_TIMERANGE_IN_MINUTE * 60:
            return -1, None
        return len(isddata_list) - 1, isddata_list[-1]

    res = []
    cur_idx = 0
    for fdt in timelines:
        cur_idx, isddata = _find_data(fdt, cur_idx)
        res.append(isddata)
    return res

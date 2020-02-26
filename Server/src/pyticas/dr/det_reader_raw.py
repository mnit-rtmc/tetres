# -*- coding: utf-8 -*-


""" Detector Raw Data Reader module

    - this module read traffic data archive files on IRIS server
    - server URL is specified ``pyticas.config.mn.TRAFFIC_DATA_URL``
    - traffic data is downloaded and cached into local disk (``DATA_PATH/cache``)
"""
import global_settings
from pyticas.tool import http

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import os

from pyticas import cfg, logger
from pyticas.ticas import get_path

MAX_TRY_NUM = 3
CACHE_TYPE_DET = 'det'
CACHE_TYPE_FAIL = 'fail'

logging = logger.getDefaultLogger(__name__)


def _path():
    PATHS = {
        CACHE_TYPE_DET: os.path.join(get_path('cache'), 'det'),
        CACHE_TYPE_FAIL: os.path.join(get_path('cache'), 'fail')
    }
    for v in PATHS.values():
        if not os.path.exists(v):
            try:
                os.mkdir(v)
            except FileExistsError:
                pass

    return PATHS


def _cache_path(cache_type, det_name, date, traffic_type):
    PATHS = _path()
    """ return cache path according to cache_type ('fail', 'det'), but if not exists, create directory """
    cache_path = os.path.join(PATHS[cache_type],
                              str(date.year),
                              '{0}{1:02}{2:02}'.format(date.year, date.month, date.day))
    try:
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
    except:
        pass
    return os.path.join(cache_path, '{0}{1}'.format(det_name, traffic_type.extension))


def _convert_to_list(binData, traffic_type):
    """ convert binary data to list """
    import array
    if not binData or len(binData) == 0:
        return []

    data = []
    ar = array.array("b")

    # `fromstring` has been deprecated
    # ar.fromstring(binData)

    ar.frombytes(binData)

    itr = iter(ar)
    for v in itr:

        if traffic_type.sample_size == 2:
            nextValue = next(itr)
            value = ((v << 8) & 0x0000ff00) + (nextValue & 0x000000ff)
        else:
            value = v

        if value < 0:
            value = cfg.MISSING_VALUE
        data.append(value)

    return data


def _save_file_to_cache(det_name, date, bin_data, traffic_type):
    cache_path = _cache_path(CACHE_TYPE_DET, det_name, date, traffic_type)
    with open(cache_path, 'wb') as cfile:
        cfile.write(bin_data)


def _read_cached_data_file(det_name, date, trafficType):
    """ fetch cached data from db """
    cache_path = _cache_path(CACHE_TYPE_DET, det_name, date, trafficType)
    if not os.path.exists(cache_path):
        return None
    with open(cache_path, 'rb') as cfile:
        return cfile.read()


def _load(det_name, year, month, day, traffic_type, missing_data):
    # faverolles 1/18/2020: Reworked the downloading operation
    #   No longer saves all of the "fail" files
    #   Checks if global option to download data files is "TRUE"
    """ Return raw data of the detector as list """
    if det_name is None:
        raise Exception("Detector number must be passed")

    dirname = str(year) + str(month).zfill(2) + str(day).zfill(2)
    remote_file = cfg.TRAFFIC_DATA_URL + '/' + str(year) + '/' + dirname + '/' + det_name + traffic_type.extension
    date = datetime.date(year, month, day)
    data = _read_cached_data_file(det_name, date, traffic_type)

    if data is not None:
        return _convert_to_list(data, traffic_type)

    if global_settings.DOWNLOAD_TRAFFIC_DATA_FILES:
        print(f"Downloading traffic data file [{remote_file}]")
        try:
            with http.get_url_opener(remote_file, timeout=30) as res:
                bin_data = res.read()
                data = _convert_to_list(bin_data, traffic_type)
                if not data:
                    return missing_data
                _save_file_to_cache(det_name, date, bin_data, traffic_type)
                return data
        except Exception as e:
            print(f"Exception downloading traffic data(file=[{remote_file}], reason=[{str(e)}]")
            return missing_data

    return missing_data


def read(det_name, prd, traffic_type):
    """ read detector data according to period and traffic_type """

    # faverolles 1/16/2020 NOTE: _read() is the entry point to _loadByDate()
    #  which is the only entry point to _load() which downloads traffic data files.
    #  A Period is passed which contains the dates to download data for.
    #  Correct fix is to find everywhere that a period is called for a time after the stop date.
    #  Hack fix is to just not download the detector file in _load()

    start_date = prd.start_date
    end_date = prd.end_date

    day_count = ((datetime.date(end_date.year, end_date.month, end_date.day)
                  - datetime.date(start_date.year, start_date.month, start_date.day)).days + 1)
    all_data = []
    interval = cfg.SAMPLES_PER_DAY // traffic_type.samples_per_day * cfg.DETECTOR_DATA_INTERVAL

    start_index = (int)(start_date.hour * 3600 // interval
                        + start_date.minute * 60 // interval)

    end_index = (int)(end_date.hour * 3600 // interval
                      + end_date.minute * 60 // interval
                      + ((day_count - 1) * traffic_type.samples_per_day))

    # faverolles 1/16/2020 NOTE: missing_data is a list of [-1's]
    #   Moved out of _load() to fix recursive initialization of 'missing_data'
    missing_data = [cfg.MISSING_VALUE] * cfg.SAMPLES_PER_DAY

    for date in (start_date + datetime.timedelta(n) for n in range(day_count)):
        all_data += _load(det_name, date.year, date.month, date.day, traffic_type, missing_data)

    clip = all_data[start_index:end_index]

    del all_data
    return clip

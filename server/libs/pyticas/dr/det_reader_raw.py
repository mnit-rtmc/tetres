# -*- coding: utf-8 -*-

""" Detector Raw Data Reader module

    - this module read traffic data archive files on IRIS server
    - server URL is specified ``pyticas.cfg.TRAFFIC_DATA_URL``
    - traffic data is downloaded and cached into local disk (``DATA_PATH/cache``)
"""
from pyticas.tool import http

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import time
import os

from urllib import error as url_error
from pyticas import cfg, logger
from pyticas.ticas import get_path

MAX_TRY_NUM = 3
CACHE_TYPE_DET = 'det'
CACHE_TYPE_FAIL = 'fail'

logging = logger.getDefaultLogger(__name__)

def _path():

    PATHS = {
             CACHE_TYPE_DET : os.path.join(get_path('cache'), 'det'),
             CACHE_TYPE_FAIL : os.path.join(get_path('cache'), 'fail')
    }
    for v in PATHS.values():
        if not os.path.exists(v):
            try:
                os.mkdir(v)
            except FileExistsError:
                pass

    return PATHS

def read(det_name, prd, traffic_type):
    """ read detector data according to period and traffictype """
    return _read([det_name, prd, traffic_type])

def _read(args):
    """ protected real data read function """
    det_name, period, trafficType = args

    start_date = period.start_date
    end_date = period.end_date
    
    day_count = ((datetime.date(end_date.year, end_date.month, end_date.day)
                  - datetime.date(start_date.year, start_date.month, start_date.day)).days + 1)
    allData = []
    interval = cfg.SAMPLES_PER_DAY // trafficType.samples_per_day * cfg.DETECTOR_DATA_INTERVAL

    start_index = (int)(start_date.hour * 3600 // interval
                        + start_date.minute * 60 // interval)

    end_index = (int)(end_date.hour * 3600 // interval
                      + end_date.minute * 60 // interval
                      + ((day_count - 1) * trafficType.samples_per_day))
        
    for date in (start_date + datetime.timedelta(n) for n in range(day_count)):
        allData += _loadByDate(det_name, date, trafficType)

    clip = allData[start_index:end_index]

    del allData
    return clip

def _loadByDate(det_name, date, traffic_type):
    """ load_data data from web or cached db """
    return _load(det_name, date.year, date.month, date.day, traffic_type)

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

def _is_failed(det, date, traffic_type):
    return os.path.exists(_cache_path(CACHE_TYPE_FAIL, det, date, traffic_type))

def _load(det_name, year, month, day, traffic_type, only_download=False, n_try=1):

    """ Return raw data of the detector as list """
    if det_name == None:
        raise Exception("Detector number must be passed")

    missing_data = [cfg.MISSING_VALUE] * cfg.SAMPLES_PER_DAY
    date = datetime.date(year, month, day)
    data = _cached_data(det_name, date, traffic_type)

    if data != None:
        return _convert_to_list(data, traffic_type) if only_download == False else None
    
    # not cached, check if failed detector
    if _is_failed(det_name, date, traffic_type):
        #logging.debug("Detector " + det_name + " is failed detector")
        return missing_data if only_download == False else None
        
    dirname = str(year) + str(month).zfill(2) + str(day).zfill(2);
    remote_file = cfg.TRAFFIC_DATA_URL + '/' + str(year) + '/' + dirname + '/' + det_name + traffic_type.extension

    try:
        if n_try > 1:
            logging.critical('Retrying... (n_try=%d)' % n_try)

        with http.get_url_opener(remote_file, timeout=30) as res:
            binData = res.read()
            data = _convert_to_list(binData, traffic_type)
            if not data:
                return missing_data
            _cache(det_name, date, binData, traffic_type)
            return data

    except url_error.HTTPError as e:
        logging.debug('Could not get the remote file (file={}, reason={}, http_code={})'.format(remote_file, str(e.reason), e.code))
        if e.code == 404:
            open(_cache_path(CACHE_TYPE_FAIL, det_name, date, traffic_type), 'w').close()
        return missing_data if only_download == False else None
    except url_error.URLError as e:
        logging.critical('Could not connect to the server (file={}, reason={})'.format(remote_file, str(e.reason)))
        return missing_data if only_download == False else None
    except ConnectionResetError as e:
        logging.critical('HTTP Connection has been reset. (file={}, reason={})'.format(remote_file, e.errno))
        if n_try <= MAX_TRY_NUM:
            time.sleep(1)
            return _load(det_name, year, month, day, traffic_type, only_download=False, n_try=n_try+1)
        else:
            logging.critical('  - fail to get data')
        return missing_data if only_download == False else None
    except Exception as e:
        logging.critical('Exception occured while downloading traffic data(file={}, reason={})'.format(remote_file, str(e)))
        return missing_data if only_download == False else None



def _convert_to_list(binData, traffic_type):
    """ convert binary data to list """
    import array
    if not binData or len(binData) == 0:
        return []
    
    data = []
    ar = array.array("b")

    # `fromstring` has been deprecated
    #ar.fromstring(binData)

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

def _cache(det_name, date, binData, trafficType):
    cache_path = _cache_path(CACHE_TYPE_DET, det_name, date, trafficType)
    with open(cache_path, 'wb') as cfile:
        cfile.write(binData)
        
def _cached_data(det_name,date, trafficType):
    """ fetch cached data from db """
    cache_path = _cache_path(CACHE_TYPE_DET, det_name, date, trafficType)        
    if os.path.exists(cache_path) == False:
        return None        
    with open(cache_path, 'rb') as cfile:
        return cfile.read()        

from pyticas.ttypes import WeatherSensorData

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import sys
import array
import datetime
import os
import enum
import time

from urllib import request
from urllib import error as url_error

from pyticas import cfg, logger
from pyticas.tool import distance, http
from pyticas.ticas import get_path

MAX_TRY_NUM = 5

_CACHE_TYPE = 'wd_type'
_CACHE_RAIN = 'wd_rain'
_CACHE_FAIL = 'wd_fail'

logging = logger.getDefaultLogger(__name__)

def _path():

    _PATHS = {
        _CACHE_TYPE: os.path.join(get_path('cache'), _CACHE_TYPE),
        _CACHE_RAIN: os.path.join(get_path('cache'), _CACHE_RAIN),
        _CACHE_FAIL: os.path.join(get_path('cache'), _CACHE_FAIL)
    }

    for v in _PATHS.values():
        if not os.path.exists(v):
            try:
                os.mkdir(v)
            except FileExistsError:
                pass

    return _PATHS

class WeatherSensor(enum.Enum):
    WS35W25 = ('WS35W25', 44.8013031052668, -93.290072119722, 'Minnesota River')
    WS94W38 = ('WS94W38', 44.9603328174837, -93.2033227980542, 'T.H.280')
    WS94W40 = ('WS94W40', 44.967214950298, -93.2202504323389, 'Huron St')
    WS94W42 = ('WS94W42', 44.9664425176848, -93.2540917106796, 'Hiawatha Ave')

    def get_name(self):
        return self.name

    def get_lat(self):
        return self.value[1]

    def get_lon(self):
        return self.value[2]

    def get_label(self):
        return self.value[3]


def nearby_sensors(lat, lon):
    """

    :param lat:
    :param lon:
    :rtype: (list[WeatherSensor], list[float])
    """
    sensors = []
    for v in WeatherSensor:
        d = distance.distance_in_mile_with_coordinate(lat, lon, v.get_lat(), v.get_lon())
        sensors.append({'distance' : d, 'sensor' : v})

    sorted_list = sorted(sensors, key=lambda s: s['distance'])
    return [ v['sensor'] for v in sorted_list ], [ v['distance'] for v in sorted_list ]


def get_weather(sensor_name, prd):
    """ return weather information
    
    :type sensor_name: str
    :type prd: Period
    """
    types = _load_data(sensor_name, prd,
                       {'ext': '.pt60', 'sample_size': 1, 'samples_per_day': cfg.SAMPLES_PER_DAY // 2,
                        'cache_type': _CACHE_TYPE})
    rains = _load_data(sensor_name, prd,
                       {'ext': '.pr60', 'sample_size': 2, 'samples_per_day': cfg.SAMPLES_PER_DAY // 2,
                        'cache_type': _CACHE_RAIN})

    return WeatherSensorData(types, rains)


def _load_data(device_name, prd, opt):
    """  load_data data
    
    :type device_name: str
    :type prd: Period
    :type opt: dict
    """
    start_date = prd.start_date
    end_date = prd.end_date

    day_count = (datetime.date(end_date.year, end_date.month, end_date.day) - datetime.date(start_date.year,
                                                                                            start_date.month,
                                                                                            start_date.day)).days + 1
    allData = []
    interval = cfg.SAMPLES_PER_DAY / opt['samples_per_day'] * cfg.DETECTOR_DATA_INTERVAL

    start_index = (int)(start_date.hour * 3600 // interval + start_date.minute * 60 // interval)
    end_index = (int)(
        end_date.hour * 3600 // interval + end_date.minute * 60 // interval + ((day_count - 1) * opt['samples_per_day']))

    for date in (start_date + datetime.timedelta(n) for n in range(day_count)):
        allData += _loadByDate(device_name, date, opt)

    return allData[start_index:end_index]


################################################

def _loadByDate(device_name, date, opt):
    """ load_data data from online or cached """
    return _load(device_name, date.year, date.month, date.day, opt)


def _load(device_name, year, month, day, opt, only_download=False, n_try=1):
    """ Return raw data of the device as list """
    date = datetime.date(year, month, day)
    data = _cached_data(device_name, date, opt)
    if data != None:
        return _convert_to_list(data, opt) if only_download == False else None;

    # not cached, check if failed device
    if _is_failed(device_name, date, opt):
        logging.debug("Device " + str(device_name) + " is failed device")
        return [-1] * (cfg.SAMPLES_PER_DAY) if only_download == False else None

    dirname = str(year) + str(month).zfill(2) + str(day).zfill(2);
    remote_file = cfg.TRAFFIC_DATA_URL + '/' + str(year) + '/' + dirname + '/' + str(device_name) + opt['ext']

    try:
        with http.get_url_opener(remote_file) as res:
            binData = res.read()
    except url_error.HTTPError as e:
        logging.debug('Could not get the weather sensor data (sensor={}, reason={}, http_code={})'.format(device_name, str(e.reason), e.code))
        if e.code == 404:
            open(_cache_path(_CACHE_FAIL, device_name, date, opt), 'w').close()
        return [-1] * (cfg.SAMPLES_PER_DAY) if only_download == False else None
    except url_error.URLError as e:
        logging.critical('Could not connect to weather sensor {} (reason={})'.format(device_name, str(e.reason)))
        return [-1] * (cfg.SAMPLES_PER_DAY) if only_download == False else None
    except ConnectionResetError as e:
        logging.critical('HTTP Connection has been reset. (file={}, reason={})'.format(remote_file, e.errno))
        if n_try <= MAX_TRY_NUM:
            logging.critical('Retrying...')
            time.sleep(1)
            return _load(device_name, year, month, day, opt, only_download=only_download, n_try=n_try+1)
        return [-1] * (cfg.SAMPLES_PER_DAY) if only_download == False else None

    _cache(device_name, date, binData, opt)

    if only_download:
        return

    data = _convert_to_list(binData, opt)

    return data


def _convert_to_list(bin_data, opt):
    """ convert binary data to list """

    data = []
    ar = array.array("b")
    ar.fromstring(bin_data)

    itr = iter(ar)
    for v in itr:
        if opt['sample_size'] == 2:
            nextValue = next(itr)
            if v == -1 and nextValue == -1:
                value = -1
            else:
                value = ((v << 8) & 0x0000ff00) + (nextValue & 0x000000ff)
        else:
            value = v

        data.append(value)

    return data


def _cache_path(cache_type, device_name, date, opt):
    """ return cache path according to cache_type ('fail', 'det'), but if not exists, create directory """
    _PATHS = _path()
    cache_path = os.path.join(_PATHS[cache_type], str(date.year),
                              '{0}{1:02}{2:02}'.format(date.year, date.month, date.day))
    try:
        os.makedirs(cache_path)
    except:
        pass
    return os.path.join(cache_path, '{0}{1}'.format(device_name, opt['ext']))

def _is_failed(device_name, date, opt):
    """ return whether is failed or not """
    return os.path.exists(_cache_path(_CACHE_FAIL, device_name, date, opt))


def _cache(device_name, date, binData, opt):
    """ save binary data to local cache directory """
    cache_path = _cache_path(opt['cache_type'], device_name, date, opt)
    with open(cache_path, 'wb') as cfile:
        cfile.write(binData)


def _cached_data(device_name, date, opt):
    """ fetch cached data """
    cache_path = _cache_path(opt['cache_type'], device_name, date, opt)
    if os.path.exists(cache_path) == False:
        return None
    with open(cache_path, 'rb') as cfile:
        return cfile.read()

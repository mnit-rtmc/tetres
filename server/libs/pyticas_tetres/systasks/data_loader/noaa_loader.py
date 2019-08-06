# -*- coding: utf-8 -*-

from pyticas.tool import timeutil

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import time
from pyticas_noaa.isd import isd
from pyticas_tetres.cfg import TARGET_ISD_STATIONS, STATE
from pyticas_tetres.da import noaaweather
from pyticas_tetres.logger import getLogger


def import_yearly_data(year):
    """

    :type year: int
    :rtype: list[dict]
    """
    logger = getLogger(__name__)
    isd_stations = isd.get_station_list(STATE)
    logger.debug('loading NOAA ISD data for %d' % year)
    res = []
    for (usaf, wban) in TARGET_ISD_STATIONS:
        st = _isd_station(usaf, wban, isd_stations)
        logger.debug(' : ISD station : %s-%s, %s (begin=%s, end=%s)'
                     % (st.usaf, st.wban, st.station_name, st.begin, st.end))

        stime = time.time()
        data_list = list(isd.get_year_data(st, year))

        logger.debug('     -> data loaded: elapsed time=%s' % timeutil.human_time(seconds=(time.time() - stime)))

        stime = time.time()
        is_inserted = _insert_noaa_data(year, usaf, wban, data_list)
        logger.debug('     -> data inserted: elapsed time=%s, inserted=%s' % (
        timeutil.human_time(seconds=(time.time() - stime)), len(data_list)))

        if is_inserted:
            res.append({'usaf': usaf, 'wban': wban, 'loaded': len(data_list)})
        else:
            res.append({'usaf': usaf, 'wban': wban, 'loaded': 0})
    return res


def import_daily_data(dt):
    """

    :type dt: datetime.datetime
    :rtype: list[dict]
    """
    logger = getLogger(__name__)
    isd_stations = isd.get_station_list(STATE)
    logger.debug('loading NOAA ISD data for %s' % dt.strftime('%Y-%m-%d'))
    res = []
    for (usaf, wban) in TARGET_ISD_STATIONS:
        loaded = import_daily_data_for_a_station(dt, usaf, wban, isd_stations)
        res.append(loaded)

    return res


def import_daily_data_for_a_station(dt, usaf, wban, isd_stations=None):
    """

    :type dt: datetime.datetime
    :type usaf: str
    :type wban: str
    :type isd_stations: list
    :rtype: dict
    """
    if not isd_stations:
        isd_stations = isd.get_station_list(STATE)

    year = dt.year
    st = _isd_station(usaf, wban, isd_stations)
    isd_data_list = list(isd.get_day_data(st, dt.year, dt.month, dt.day))
    if not isd_data_list:
        return {'usaf': usaf, 'wban': wban, 'loaded': 0}
    else:
        is_inserted = _insert_noaa_data(year, usaf, wban, isd_data_list)
        if is_inserted:
            return {'usaf': usaf, 'wban': wban, 'loaded': len(isd_data_list)}
        else:
            return {'usaf': usaf, 'wban': wban, 'loaded': 0}


def _insert_noaa_data(year, usaf, wban, isd_data_list):
    """ bulk insertion

    **CAUTION**
    `isd_data_list` must be continous data because existing data will be delete
    `isd_data_list` must contain the same year data

    :type usaf: str
    :type wban: str
    :type isd_data_list: list[pyticas_noaa.isd.isdtypes.ISDData]
    :rtype: bool
    """
    logger = getLogger(__name__)

    if not _delete_existing_noaa_data(usaf, wban, isd_data_list):
        return False

    da = noaaweather.NoaaWeatherDataAccess(year)
    dict_list = [_get_dict(usaf, wban, isd_data) for idx, isd_data in enumerate(isd_data_list)]
    inserted_ids = da.bulk_insert(dict_list, print_exception=True)
    if not inserted_ids or not da.commit():
        logger.warn(' : Exception occured when entering NOAA ISD data')
        return False
    da.close_session()
    return True


def _delete_existing_noaa_data(usaf, wban, isd_data_list):
    """
    :type usaf: str
    :type wban: str
    :type isd_data_list: list[pyticas_noaa.isd.isdtypes.ISDData]
    :rtype: bool
    """
    start_time = isd_data_list[0].time()
    end_time = isd_data_list[-1].time()
    start_year = start_time.year
    end_year = end_time.year

    das = {}
    for year in range(start_year, end_year + 1):
        da = das.get(year, None)
        if da == None:
            da = noaaweather.NoaaWeatherDataAccess(year)
            das[year] = da

        is_deleted = da.delete_range(usaf, wban, start_time, end_time)
        if not is_deleted or not da.commit():
            return False

    for idx, da in das.items():
        da.close_session()

    return True


def _isd_station(usaf, wban, isd_stations):
    """

    :type usaf: str
    :type wban: str
    :type isd_stations: list[pyticas_noaa.isd.isdtypes.ISDStation]
    :rtype: pyticas_noaa.isd.isdtypes.ISDStation
    """
    for st in isd_stations:
        if st.usaf == usaf and st.wban == wban:
            return st
    return None


def _get_dict(usaf, wban, isd_data, pk=None):
    """

    :type isd_data: pyticas_noaa.isd.isdtypes.ISDData
    :rtype: dict
    """
    dictdata = {
        'usaf': usaf,
        'wban': wban,
        'dtime': isd_data.time(),  # .strftime('%Y-%m-%d %H:%M:%S'),
        'precip': isd_data.precipitation(),
        'precip_type': isd_data.precipitation_type()[0],
        'precip_intensity': isd_data.precipitation_intensity()[0],
        'precip_qc': isd_data.precipitation_qc()[0],
        'visibility': isd_data.visibility(),
        'visibility_qc': isd_data.visibility_qc()[0],
        'obscuration': isd_data.obscuration()[0],
        'descriptor': isd_data.descriptor()[0],
        'air_temp': isd_data.air_temp(),
        'air_temp_qc': isd_data.air_temp_qc()[0],
        'dew_point': isd_data.dew_point(),
        'dew_point_qc': isd_data.dew_point_qc()[0],
        'relative_humidity': isd_data.rel_humidity(),
        'wind_dir': isd_data.wind_direction()[0],
        'wind_dir_qc': isd_data.wind_direction_qc()[0],
        'wind_speed': isd_data.wind_speed(),
        'wind_speed_qc': isd_data.wind_speed_qc()[0],
        'wind_gust': isd_data.wind_gust_speed(),
        'wind_gust_qc': isd_data.wind_gust_speed_qc()[0],
    }
    if pk:
        dictdata['id'] = pk
    return dictdata

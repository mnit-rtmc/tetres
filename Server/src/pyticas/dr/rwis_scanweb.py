__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime, enum

from pyticas import cfg, logger
from pyticas.dr.rwis_reader import scanweb_export, scanweb_html
from pyticas.tool import distance
from pyticas.ttypes import RWISSiteInfo

logging = logger.getDefaultLogger(__name__)

class RWIS_READER(enum.Enum):
    SCANWEB_EXPORT = scanweb_export
    SCANWEB_HTML = scanweb_html

def find_nearby_sites(s_lat, s_lon):
    """ return RWIS site list order by distance (from nearest)

    :type s_lat: float
    :type s_lon: float
    :return: RWIS site list
    :rtype: list[RWISSiteInfo]
    """
    sites = []
    for gr in cfg.RWIS_SITE_INFO:
        for st in gr['sites']:
            d = distance.distance_in_mile_with_coordinate(s_lat, s_lon, st['lat'], st['lon'])
            sites.append(RWISSiteInfo({'group_id': gr['id'],
                                       'group_name': gr['name'],
                                       'site_id': st['id'],
                                       'site_name': st['name'],
                                       'lat': st['lat'],
                                       'lon': st['lon'],
                                       'distance_to_target': d}))

    return sorted(sites, key=lambda s: s.distance_to_target)


def get_site_by_id(site_id):
    """ return site information

    :type site_id: str
    :rtype: RWISSiteInfo
    """
    for gr in cfg.RWIS_SITE_INFO:
        for st in gr['sites']:
            if st['id'] == site_id:
                return RWISSiteInfo({'group_id': gr['id'],
                                     'group_name': gr['name'],
                                     'site_id': st['id'],
                                     'site_name': st['name'],
                                     'lat': st['lat'],
                                     'lon': st['lon']})
    return None


def get_all_rwis_sites():
    """ return site information

    :rtype: list[RWISSiteInfo]
    """
    sites = []
    for gr in cfg.RWIS_SITE_INFO:
        for st in gr['sites']:
            sites.append(RWISSiteInfo({'group_id': gr['id'],
                                       'group_name': gr['name'],
                                       'site_id': st['id'],
                                       'site_name': st['name'],
                                       'lat': st['lat'],
                                       'lon': st['lon']}))
    return sites


def get_weather_by_site(group_id, site_id, prd, **kwargs):
    """

    Returns::

        it returns weather data from scan web (rwis.dot.sate.mn.us/scanweb/)
        for the period at the most next district of the given section
        The returned data is a list of dictionary having the following structures

        [
            {'DateTime': '07/07/2014 14:01',
             'Barometric': '',
             'FreezeTemp': '',
             'PvtTemp': '',
             'SfStatus': 'Dry',
             'Salinity': '',
             'PrecipIntensity': '',
             '1hr Accum': '',
             'AirTemp': '85',
             'EndTime': '07/07/2014 05:43',
             'Dewpoint': '63',
             'PrecipType': 'None',
             '24hr Accum': '',
             '6hr Accum': '',
             '3hr Accum': '',
             'Visibility': '',
             'WaterDepth': '',
             'SfTemp': '118.9',
             'RH': '44',
             'PrecipRate': '0',
             'IcePercent': '',
             '10min Accum': '',
             '12hr Accum': '',
             'AvgWindSpeed': '7',
             'Accumulation': '',
             'FrictionIndex': '',
             'ChemFactor': '',
             'PrecipAccumulation': '',
             'GustWindSpeed': '20',
             'WaterDepthIceThickness': '',
             'ChemPercent': '',
             'SubTemp': '77',
             'StartTime': '07/07/2014 05:39',
             'WindDirection': 'W',
             'Conductivity': ''}
              { ...},
              { ...},
              ...
        ]

    :param target_route_or_rnode: section
    :type target_route_or_rnode: ticaslib.section.obj.Section

    :param prd: period
    :type prd: ticaslib.period.obj.Period
    :rtype: pyticas.ttypes.ScanWebData
    """
    start_date, end_date = prd.start_date, prd.end_date
    day_count = (datetime.date(end_date.year, end_date.month, end_date.day) - datetime.date(start_date.year,
                                                                                            start_date.month,
                                                                                            start_date.day)).days + 1

    nocache = kwargs.get('nocache', False)
    dre = kwargs.get('reader', RWIS_READER.SCANWEB_EXPORT)
    if not isinstance(dre, RWIS_READER):
        raise ValueError('Invalid Parameter of reader : reader must be RWIS_READER type')
    data_reader = dre.value

    total_wd = None
    """:type: pyticas.ttypes.ScanWebData """
    for date in (start_date + datetime.timedelta(n) for n in range(day_count)):
        v = data_reader.load_by_date(group_id, site_id, date, nocache=nocache)
        if not v: return None
        if not total_wd:
            total_wd = v
        else:
            total_wd += v

    total_wd.formating()
    total_wd.set_period(prd)

    return total_wd


def _trim_data(wd, prd):
    """

    :type wd: ScanWebData
    :type prd: pyticas.ttypes.Period
    """
    start_date, end_date = prd.start_date, prd.end_date
    mod = prd.interval / 30

    start_index = -1
    end_index = -1
    for idx, dt in enumerate(wd.data.get('DateTime')):
        if '/' in dt:
            dtt = datetime.datetime.strptime(dt, '%m/%d/%Y %H:%M')
        else:
            dtt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        if dtt > start_date and start_index < 0:
            start_index = idx
        if dtt >= end_date:
            end_index = idx
            break
    for field_name, field_data in wd.data.items():
        wd.data[field_name] = field_data[start_index:end_index]

    for field_name, field_data in wd.data.items():
        new_data = [v for idx, v in enumerate(wd.data[field_name]) if idx % mod == 0]
        wd.data[field_name] = new_data


def get_weather(site, prd, **kwargs):
    """
    :type site: RWISSiteInfo
    :type prd: Period
    :rtype: ScanWebData
    """
    return get_weather_by_site(site.group_id, site.site_id, prd, **kwargs)

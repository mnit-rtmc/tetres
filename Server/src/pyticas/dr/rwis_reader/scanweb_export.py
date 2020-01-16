__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import time
import re
from urllib import error as url_error

from pyticas import cfg, logger
from pyticas.dr.rwis_reader import cache as rwis_cache
from pyticas.tool import concurrent, http, tb
from pyticas.ttypes import ScanWebData

logging = logger.getDefaultLogger(__name__)

MAX_TRY_NUM = 3

SRC_TYPE = 'export'

SP_HISTORY_PAGE = 'SfPcHistoryExp.asp'
PC_HISTORY_PAGE = 'PcHistoryExp.asp'
AT_HISTORY_PAGE = 'AtmosOnlyHistoryExp.asp'

"""
This headings is to check csv format in the export page has been changed before parsing
"""
HEADINGS = {
    SP_HISTORY_PAGE: [
        ['Date/Time (CST)', 'SfStatus', 'SfTemp', 'PvtTemp', 'SubTemp', 'FreezeTemp', 'ChemFactor', 'ChemPercent',
         'WaterDepth', 'WaterDepthIceThickness', 'IcePercent', 'Conductivity', 'Salinity', 'FrictionIndex',
         'PrecipType', 'PrecipIntensity', 'Accumulation', 'PrecipRate']],
    PC_HISTORY_PAGE: [
        ['Date/Time (CST)', 'PrecipType', 'PrecipIntensity', 'PrecipRate', 'StartTime', 'EndTime', '10min Accum',
         '1hr Accum', '3hr Accum', '6hr Accum', '12hr Accum', '24hr Accum']],
    AT_HISTORY_PAGE: [
        ['Date/Time (CST)', 'AirTemp', 'RH', 'Dewpoint', 'Barometric', 'AvgWindSpeed', 'GustWindSpeed', 'WindDirection',
         'PrecipType', 'PrecipIntensity', 'PrecipAccumulation', 'PrecipRate'],
        ['Date/Time (CST)', 'AirTemp', 'RH', 'Dewpoint', 'Barometric', 'AvgWindSpeed', 'GustWindSpeed', 'WindDirection',
         'PrecipType', 'PrecipIntensity', 'PrecipAccumulation', 'PrecipRate', 'Visibility' ]
    ]
}


def load_by_date(group_id, site_id, date, **kwargs):
    """  load_data data from web or cached

    :type group_id: str
    :type site_id: str

    :param date: date to extract information
    :type date: datetime.datetime
    """
    date = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
    e_date = date + datetime.timedelta(days=1)

    if not kwargs.get('nocache', False):
        cached_wd = rwis_cache.cached(group_id, site_id, date, src_type=SRC_TYPE)
        if cached_wd != None:
            return cached_wd

    is_ok = False

    # if _is_failed(group_id, site_id, date):
    #    logging.debug('it is failed : {0} / {1}'.format(site_id, date))
    #    return None

    sp_history = None
    pc_history = None
    at_history = None

    cWorker = concurrent.Worker(3)
    for sen_id in range(2):
        cWorker.clear_tasks()
        cWorker.add_task(_read_from_web, SP_HISTORY_PAGE, group_id, site_id, sen_id, date, e_date)
        cWorker.add_task(_read_from_web, PC_HISTORY_PAGE, group_id, site_id, sen_id, date, e_date)
        cWorker.add_task(_read_from_web, AT_HISTORY_PAGE, group_id, site_id, sen_id, date, e_date)
        sp_history, pc_history, at_history = cWorker.run()
        if not sp_history or not pc_history or not at_history:
            continue
        if len(sp_history) > 1 and len(pc_history) > 1 and len(at_history) > 1:
            is_ok = True
            break

    cWorker = None

    if not is_ok:
        rwis_cache.fail(group_id, site_id, date, src_type=SRC_TYPE)
        return None

    if (sp_history[0] not in HEADINGS.get(SP_HISTORY_PAGE) or
                pc_history[0] not in HEADINGS.get(PC_HISTORY_PAGE) or
                at_history[0] not in HEADINGS.get(AT_HISTORY_PAGE)):

        if sp_history[0] not in HEADINGS.get(SP_HISTORY_PAGE):
            print('SfPcHistoryExp Header of the ScanWeb : ' + ', '.join(sp_history[0]))
            print('Expected SfPcHistoryExp Header : ' + ', '.join(HEADINGS.get(SP_HISTORY_PAGE)[0]))

        if pc_history[0] not in HEADINGS.get(PC_HISTORY_PAGE):
            print('PcHistoryExp Header of the ScanWeb : ' + ', '.join(pc_history[0]))
            print('Expected PcHistoryExp Header : ' + ', '.join(HEADINGS.get(PC_HISTORY_PAGE)[0]))

        if at_history[0] not in HEADINGS.get(PC_HISTORY_PAGE):
            print('AtmosOnlyHistoryExp Header of the ScanWeb : ' + ', '.join(at_history[0]))
            print('Expected AtmosOnlyHistoryExp Header : ' + ', '.join(HEADINGS.get(AT_HISTORY_PAGE)[0]))

        raise Exception('RWIS(ExportMode) page format does not match to the RWIS loader')

    sp_fields, sp_data = _convert_to_list(date, sp_history)
    pc_fields, pc_data = _convert_to_list(date, pc_history)
    at_fields, at_data = _convert_to_list(date, at_history)

    # merge without duplicated DataField
    m_fields = sp_fields + pc_fields[1:] + at_fields[1:]

    m_data = [sp_data[idx] + pc_data[idx][1:] + at_data[idx][1:] for idx in range(len(sp_data))]
    wd = ScanWebData(m_fields, m_data)

    rwis_cache.cache(group_id, site_id, date, wd, src_type=SRC_TYPE)

    return wd


def _read_from_web(page_name, group_id, site_id, sen_id, date, e_date, n_try=1):
    """  thread worker to get data from web page

    :param page_name: web page name of scanWeb site
    :type page_name: str

    :type group_id: str
    :type site_id: str

    :param sen_id: sensor id (?), required param for uri request
    :type sen_id: int

    :param date: target date
    :type date: datetime.datetime

    :param date: end date
    :type e_date: datetime.datetime
    """
    remote_file = '{0}{1}?Units=English&Siteid={2}&Senid={3}&HEndDate={4}'.format(cfg.SCANWEB_URL, page_name, site_id,
                                                                                  sen_id,
                                                                                  '{0}%2F{1}%2F{2}'.format(e_date.month,
                                                                                                           e_date.day,
                                                                                                           e_date.year))
    logging.debug('RWIS(Export) URL : %s' % remote_file)
    try:
        with http.get_url_opener(remote_file) as res:
            html = res.read()
    except url_error.HTTPError as e:
        logging.debug('Could not access html of ScanWeb site (reason={}, http_code={})'.format(str(e.reason), e.code))
        logging.debug('URL : {}'.format(remote_file))
        if e.code == 404:
            rwis_cache.fail(group_id, site_id, date, src_type=SRC_TYPE)
        return None
    except url_error.URLError as e:
        logging.critical('Could not connect to ScanWeb site (reason={})'.format(str(e.reason)))
        logging.debug('URL : {}'.format(remote_file))
        return None
    except ConnectionResetError as e:
        logging.critical('HTTP Connection has been reset. (file={}, reason={})'.format(remote_file, e.errno))
        if n_try <= MAX_TRY_NUM:
            logging.critical('Retrying...')
            time.sleep(1)
            return _read_from_web(page_name, group_id, site_id, sen_id, date, e_date, n_try=n_try+1)
        return None

    try:
        return _parse(html.decode())
    except TypeError as ex:
        logging.critical('Could not parse the exported data from ScanWeb site')
        tb.traceback(ex)

    return None


def _parse(html):
    """ parse and extract csv data from html string

    :param html: html data
    :type html: baestring

    :return: csv data list
    :rtype:list
    """
    ms = re.findall('<div class="SubDataTextLeft">([^<]+)<\/div>', html, re.IGNORECASE)
    csv = []
    for m in ms:
        csv.append([s.replace('&nbsp;', '').strip() for s in m.strip().split(',')])

    return csv


def _convert_to_list(date, csv):
    """ make list of json from csv list

    :param date: target date
    :type date: datetime.datetime

    :param csv: csv data list for a whole day
    :type csv: list

    :return: data list with 1-minute interval
    :rtype: list
    """
    n_csv = len(csv)
    fields = csv[0]
    fields[0] = 'DateTime'
    data = []
    for idx in range(n_csv - 1, 0, -1):
        data.append(_field_data(fields, csv[idx]))

    return fields, data


def _field_data(fields, row):
    """ make dict data from csv row and field names

    :param fields: csv data fields
    :type fields: list

    :param row: csv data row
    :type row: list

    :return: dictionary data integrating field and data
    :rtype: dict
    """
    data = [None] * len(fields)
    for fidx, field in enumerate(fields):
        sval = str(row[fidx])
        if sval == 'None':
            data[fidx] = None
        elif sval.replace('.', '').isdigit():
            if '.' in sval:
                data[fidx] = float(sval)
            else:
                data[fidx] = int(sval)
        else:
            data[fidx] = sval
    return data

# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas.logger import getLogger
from pyticas_noaa.isd.isdtypes import CDS, MDS, ISD_AA, ISD_AU, ISD_OC, ISDRawData, ISDData

cds = CDS()
mds = MDS()
aa = ISD_AA()
au = ISD_AU()
oc = ISD_OC()

def _additional_data_string(s, ads_start):
    if 'ADD' != s[ads_start:ads_start+3]:
        return None
    try:
        end = s.index(' RMK ', ads_start+3)
        return s[ads_start+3:end]
    except:
        return None

def _parse_additional_data(ado, ad_line):
    """
    :type ado: ISDAdditionalData
    :type ad_line: str
    :rtype:
    """
    # logger = getLogger(__name__)
    # logger.debug(' $ ', ado.__class__.__name__)
    ress = ado.parse(ad_line)
    # if any(ress):
    #     for idx, res in enumerate(ress):
    #         logger.debug('   #%d' % idx)
    #         for fn, fl in ado.fields:
    #             logger.debug('    - ', fn, ' : ', res[fn])
    return ress


def parse(filepath):
    """

    :type filepath: str
    :rtype: list[ISDData]
    """
    logger = getLogger(__name__)
    result = []
    with open(filepath, 'r') as f:
        for num, line in enumerate(f):
            res = cds.parse(line, 0)
            date = '%04d-%02d-%02d' % (
                res.geophysical_point_observation_year,
                res.geophysical_point_observation_month,
                res.geophysical_point_observation_day)

            dt = '%s %02d:%02d' % (
                date,
                res.geophysical_point_observation_hour,
                res.geophysical_point_observation_minute,
            )

            #print('## %s' % dt)
            res_cds = cds.parse(line)
            res_mds = mds.parse(line, cds.total_field_length())

            ads_start = cds.total_field_length() + mds.total_field_length()
            ad_line = _additional_data_string(line, ads_start)

            if not ad_line:
                logger.debug('!!! No Additional Data Section : ', dt)
                continue

            ress_aa = _parse_additional_data(aa, ad_line)
            ress_au = _parse_additional_data(au, ad_line)
            ress_oc = _parse_additional_data(oc, ad_line)

            isd_data = ISDData(ISDRawData(res_cds, res_mds, ress_aa, ress_au, ress_oc))
            print(isd_data)
            result.append(isd_data)
    return result



result = parse('726575-94960-2017')

import csv
with open('output-726575-94960-2017.csv', 'w') as f:
    wr = csv.writer(f, lineterminator='\n')
    wr.writerow([
                'time',
                'precip (inch)',
                'precip_type',
                'precip_intensity',
                'RH (%)',
                'visibility (mile)',
                'air_temp (F)',
                'dew_point (F)',
                'wind_dir (degree)',
                'wind_speed (mph)',
                'wind_gust (mph)',
            ])
    sdt = datetime.datetime(2017, 1, 31, 0, 0, 0)
    edt = datetime.datetime(2017, 2, 1, 0, 0, 0)
    for isd_data in result:
        try:
            if isd_data.time() < sdt or isd_data.time() >= edt:
                continue
        except Exception as ex:
            print( type(sdt), type(edt), type(isd_data.time()))
            print( sdt.tzinfo, edt.tzinfo, isd_data.time().tzinfo)
            raise ex
        wr.writerow([
            isd_data.time().strftime('%Y-%m-%d %H:%M'),
            round(isd_data.precipitation(), 3) if isd_data.precipitation() is not None else None,
            isd_data.precipitation_type()[1],
            isd_data.precipitation_intensity()[1],
            round(isd_data.rel_humidity(), 1) if isd_data.rel_humidity() is not None else None,
            round(isd_data.visibility(), 2) if isd_data.visibility() is not None else None,
            round(isd_data.air_temp(), 2) if isd_data.air_temp() is not None else None,
            round(isd_data.dew_point(), 2) if isd_data.dew_point() is not None else None,
            isd_data.wind_direction(),
            round(isd_data.wind_speed(), 2) if isd_data.wind_speed() is not None else None,
            round(isd_data.wind_gust_speed(), 2) if isd_data.wind_gust_speed() is not None else None
        ])
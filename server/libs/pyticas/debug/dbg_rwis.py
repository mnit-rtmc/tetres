# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import logging
import pprint
import unittest

from pyticas.logger import  getDefaultLogger
from pyticas.dr import rwis_scanweb as rwis
from pyticas.test.test_data import weather_data
from pyticas.ttypes import Period
from .base import TestPyTICAS


class TestRWIS(TestPyTICAS):
    def test_weather_info(self):
        logger = getDefaultLogger(__name__)

        rnode = self.infra.get_rnode('S1466')
        site_near_rnode = rwis.find_nearby_sites(rnode.lat, rnode.lon)[0]
        self.assertEqual(site_near_rnode.site_id, 330087)

        for case in weather_data.cases:
            site = rwis.get_site_by_id(case['site_id'])
            if not site:
                logger.warn('No RWIS site of %s' % case['site_id'])
                continue
            wd = rwis.get_weather_by_site(site.group_id, site.site_id, Period(case['start_time'], case['end_time'], 30), nocache=True)
            if not wd:
                logging.critical('SKIP testing : Could not get weather data')
                continue

            # pprint.pprint(wd.data)
            #print(wd.get_data_string())
            #print(wd.get_precip_start_time())
            #print([ dt.strftime('%Y-%m-%d %H:%M:%S') for dt in list(reversed(wd.get_datetimes())) ])

            sf_status = list(reversed(wd.get_surface_statuses()))
            v = (sf_status == case['SfStat'])
            if not v:
                pprint.pprint(list(zip(sf_status, case['SfStat'])))
            self.assertTrue(v)

            sf_temp = list(reversed(wd.get_surface_temperatures()))
            v = (sf_temp == case['SfTemp'])
            if not v:
                pprint.pprint(list(zip(sf_temp, case['SfTemp'])))
            self.assertTrue(v)

            precip_types = list(reversed(wd.get_precip_types()))
            v = (precip_types == case['PrecipType'])
            if not v:
                pprint.pprint(list(zip(precip_types, case['PrecipType'])))
            self.assertTrue(v)

            air_temp = list(reversed(wd.get_air_temperatures()))
            v = (air_temp == case['AirTemp'])
            if not v:
                pprint.pprint(list(zip(air_temp, case['AirTemp'])))
            self.assertTrue(v)

            wind_dirs = list(reversed(wd.get_wind_directions()))
            v = ( wind_dirs == case['WindDirection'] )
            if not v:
                pprint.pprint(list(zip(wind_dirs, case['WindDirection'])))
            self.assertTrue(v)

            dew_points = list(reversed(wd.get_dewpoints()))
            v = ( dew_points == case['Dewpoint'] )
            if not v:
                pprint.pprint(list(zip(dew_points, case['Dewpoint'])))
            self.assertTrue(v)

            rh = list(reversed(wd.get_humidities()))
            v = ( rh == case['RH'] )
            if not v:
                pprint.pprint(list(zip(rh, case['RH'])))
            self.assertTrue(v)




if __name__ == '__main__':
    unittest.main()

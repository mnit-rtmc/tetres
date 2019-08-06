# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import pprint
import unittest

from pyticas.test.test_data import station_data
from pyticas.ttypes import Period
from .base import TestPyTICAS


class TestStationData(TestPyTICAS):
    def test_station_data(self):

        for case in station_data.cases:

            prd = Period(case['start_time'], case['end_time'], case['interval'])
            station = self.infra.get_rnode(case['name'])
            u = self.infra.rdr.get_speed(station, prd)
            res = self._compare_data(u.data, case['u'])
            if not res:
                print('Speed Data ({}, {}, {})'.format(case['name'], prd.get_date_string(), prd.interval))
                for d, du in u.detector_data.items():
                    print(d, du)
                pprint.pprint(list(zip(u.data, case['u'])))
                print('-' * 10)
            self.assertTrue(res, 'Not matched data : speed from {}, {}, {}'.format(case['name'], case['start_time'],
                                                                                   case['interval']))

            k = self.infra.rdr.get_density(station, prd)
            res = self._compare_data(k.data, case['k'])
            if not res:
                print('Density Data ({}, {}, {})'.format(case['name'], prd.get_date_string(), prd.interval))
                pprint.pprint(list(zip(k.data, case['k'])))
                print('-' * 10)
            self.assertTrue(res, 'Not matched data : density from {}, {}, {}'.format(case['name'], case['start_time'],
                                                                                     case['interval']))

            q = self.infra.rdr.get_total_flow(station, prd)
            res = self._compare_data(q.data, case['q'])
            if not res:
                print('Flow Data ({}, {}, {})'.format(case['name'], prd.get_date_string(), prd.interval))
                pprint.pprint(list(zip(q.data, case['q'])))
                print('-' * 10)
            self.assertTrue(res, 'Not matched data : flow from {}, {}, {}'.format(case['name'], case['start_time'],
                                                                                  case['interval']))

            o = self.infra.rdr.get_occupancy(station, prd)
            res = self._compare_data(o.data, case['o'])
            if not res:
                print('Occupancy Data ({}, {}, {})'.format(case['name'], prd.get_date_string(), prd.interval))
                pprint.pprint(zip(o.data, case['o']))
                print('-' * 10)
            self.assertTrue(res, 'Not matched data : occupancy from {}, {}, {}'.format(case['name'], case['start_time'],
                                                                                       case['interval']))

            v = self.infra.rdr.get_volume(station, prd)
            res = self._compare_data(v.data, case['v'])
            if not res:
                print('Volume Data ({}, {}, {})'.format(case['name'], prd.get_date_string(), prd.interval))
                pprint.pprint(list(zip(v.data, case['v'])))
                print('-' * 10)
            self.assertTrue(res, 'Not matched data : volume from {}, {}, {}'.format(case['name'], case['start_time'],
                                                                                    case['interval']))

    def _compare_data(self, d1, d2):
        if len(d1) != len(d2):
            return False

        for idx in range(len(d1)):
            if abs(d1[idx] - d2[idx]) > 0.1:
                return False

        return True


if __name__ == '__main__':
    unittest.main()

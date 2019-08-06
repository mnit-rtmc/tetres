# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import pprint
import unittest

from pyticas.test.test_data import detector_data
from pyticas.ttypes import Period
from .base import TestPyTICAS


class TestDetectorData(TestPyTICAS):
    def test_detector_data(self):

        dr = self.infra.ddr

        for case in detector_data.cases:

            prd = Period(case['start_time'], case['end_time'], case['interval'])

            det = self.infra.get_detector(case['name'])

            u = dr.get_speed(det, prd)
            res = self._compare_data(u, case['u'])
            if not res:
                print('Speed Data ---')
                pprint.pprint(list(zip(u, case['u'])))
                print('-' * 10)
            self.assertTrue(res, 'Not matched data : speed from {}, {}, {}'.format(case['name'], case['start_time'],
                                                                                   case['interval']))

            k = dr.get_density(det, prd)
            res = self._compare_data(k, case['k'])
            if not res:
                print('Density Data ---')
                pprint.pprint(zip(k, case['k']))
                print('-' * 10)
            self.assertTrue(res, 'Not matched data : density from {}, {}, {}'.format(case['name'], case['start_time'],
                                                                                     case['interval']))

            q = dr.get_flow(det, prd)
            res = self._compare_data(q, case['q'])
            if not res:
                print('Flow Data ---')
                pprint.pprint(zip(q, case['q']))
                print('-' * 10)
            self.assertTrue(res, 'Not matched data : flow from {}, {}, {}'.format(case['name'], case['start_time'],
                                                                                  case['interval']))

            o = dr.get_occupancy(det, prd)
            res = self._compare_data(o, case['o'])
            if not res:
                print('Occupancy Data ---')
                pprint.pprint(zip(o, case['o']))
                print('-' * 10)
            self.assertTrue(res, 'Not matched data : occupancy from {}, {}, {}'.format(case['name'], case['start_time'],
                                                                                       case['interval']))

            v = dr.get_volume(det, prd)
            res = self._compare_data(v, case['v'])
            if not res:
                print('Volume Data ---')
                pprint.pprint(zip(v, case['v']))
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

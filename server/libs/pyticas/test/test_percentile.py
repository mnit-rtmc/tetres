# -*- coding: utf-8 -*-
from unittest import TestCase

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.tool import num


class Testpercentile(TestCase):

    def test_percentile(self):
        numbers = [0.159308374, 0.835366703, 0.965087579, 0.77490059, 0.039589591, 0.624168166, 0.781263824,
                   0.090380355, 0.531038332, 0.065043622, 0.523437618, 0.206919518, 0.094903607, 0.102623141,
                   0.085231272, 0.698227113, 0.06548639, 0.21648217]
        expected = {
            0.95: 0.854824834,
            0.90: 0.797494688,
            0.85: 0.777764045,
            0.80: 0.744231199,
        }
        for key, value in expected.items():
            res = num.percentile(numbers, key, interpolation='linear')
            ret = round(res, 9)
            self.assertEqual(value, ret, msg='expected=%f, returned=%f' % (value, ret))

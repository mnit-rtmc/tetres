# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import unittest

from pyticas import ttypes as types
from .base import TestPyTICAS

class TestEnum(TestPyTICAS):

    def test_merge_two_route(self):
        self.assertEqual(types.PrecipType.find_by_text("Other"), types.PrecipType.OTHER)
        self.assertEqual(types.SurfaceCondition.find_by_value(1), types.SurfaceCondition.COM_FAIL)
        self.assertEqual(types.SurfaceCondition.find_by_value(4), types.SurfaceCondition.WET_4)

if __name__ == '__main__':
    unittest.main()

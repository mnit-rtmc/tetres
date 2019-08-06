# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import unittest

from pyticas import ttypes
from .base import TestPyTICAS

class TestEnum(TestPyTICAS):

    def test_merge_two_route(self):
        self.assertEqual(ttypes.PrecipType.find_by_text("Other"), ttypes.PrecipType.OTHER)
        self.assertEqual(ttypes.SurfaceCondition.find_by_value(1), ttypes.SurfaceCondition.COM_FAIL)
        self.assertEqual(ttypes.SurfaceCondition.find_by_value(4), ttypes.SurfaceCondition.WET_4)

if __name__ == '__main__':
    unittest.main()

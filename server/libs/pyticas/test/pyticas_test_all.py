# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import unittest
import os
import sys
import traceback

from pyticas import ticas
from pyticas.infra import Infra
from pyticas.config.mn import mn_cfg
from pyticas.test.base import TestPyTICAS


def test_all():
    TestPyTICAS.data_path = os.path.join(os.path.dirname(__file__), 'test_data_storage')
    metro_file = os.path.join(TestPyTICAS.data_path, 'metro', '2015-09-08.xml')
    try:
        ticas.initialize(TestPyTICAS.data_path, mn_cfg)
        TestPyTICAS.infra = Infra.load_infra_from_config_file(metro_file)
    except Exception as ex:
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)


    testmodules = [
        'pyticas.test.test_enum',
        'pyticas.test.test_percentile',
        'pyticas.test.test_period',
        'pyticas.test.test_json',
        'pyticas.test.test_geo',
        'pyticas.test.test_rnode_info',
        'pyticas.test.test_cam',
        'pyticas.test.test_dms',
        'pyticas.test.test_rwis',
        'pyticas.test.test_distance',
        'pyticas.test.test_detector_data',
        'pyticas.test.test_station_data',
        'pyticas.test.test_tmp_det_loader',
        ]

    suite = unittest.TestSuite()

    for t in testmodules:
        try:
            mod = __import__(t, globals(), locals(), ['suite'])
            suitefn = getattr(mod, 'suite')
            suite.addTest(suitefn())
        except (ImportError, AttributeError):
            suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    test_all()
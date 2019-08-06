# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import logging
import os
import sys
import traceback
import unittest

from pyticas import ticas
from pyticas.config.mn import mn_cfg
from pyticas.infra import Infra

class TestPyTICAS(unittest.TestCase):

    data_path = None
    """:type: str """

    infra = None
    """:type: pyticas.infra.Infra """

    @classmethod
    def setUpClass(cls):
        TestPyTICAS.data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../data'))
        logging.basicConfig(format='[%(asctime)s] (%(levelname)s) %(message)s', level=logging.INFO)
        try:
            ticas.initialize(TestPyTICAS.data_path, mn_cfg)
            TestPyTICAS.infra = Infra.get_infra()
        except Exception as ex:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)

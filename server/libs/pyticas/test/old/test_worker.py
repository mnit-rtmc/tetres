# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import sys
import time
import traceback
import unittest

from pyticas import ticas
from pyticas.config.mn import mn_cfg
from pyticas.infra import Infra
from pyticas.tool import concurrent


class TestRNodeInfo(unittest.TestCase):

    def setUp(self):
        self.metro_file = os.path.join(os.path.dirname(__file__), 'sample_metro_config', 'metro.xml')
        self.data_path = os.path.join(os.path.dirname(__file__), 'test_data_storage')
        try:
            ticas.initialize(self.data_path, mn_cfg)
            self.infra = Infra.load_infra_from_config_file(self.metro_file)
        except Exception as ex:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)

    def _job(self, sleep_time, data):
        time.sleep(sleep_time)
        print('doing job : {} / {}'.format(sleep_time, data))
        return sum(data)

    def _job_done(self, result):
        print('job done : {}'.format(result))

    def test_something(self):
        worker = concurrent.Worker(2)
        for idx in range(2, 10):
            worker.add_task(self._job, 1, [ i for i in range(idx) ])
        ret = worker.run()

        import pprint
        pprint.pprint(ret)


if __name__ == '__main__':
    unittest.main()

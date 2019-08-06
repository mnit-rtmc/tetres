# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import unittest

from pyticas import period as ph
from pyticas import route
from pyticas import ttypes as types
from pyticas.rn.route_config import route_config
from pyticas.tool import json
from .base import TestPyTICAS

class TestJSON(TestPyTICAS):

    def test_layout_json(self):
        r1 = route.create_route('S38', 'S40') # I-35W NB
        lo = route_config.create_route_config(r1.rnodes)
        lo_json = json.dumps(lo, sort_keys=True, indent=4)
        lo_decoded = json.loads(lo_json)

        self.assertIsInstance(lo_decoded, types.RouteConfig)
        for idx, node in enumerate(lo_decoded.node_sets):
            self.assertIsInstance(node, types.RouteConfigNodeSet)
            self.assertIsInstance(node.node1, types.RouteConfigNode)
            self.assertIsInstance(node.node2, types.RouteConfigNode)
            self.assertIsInstance(node.node1.node_config, types.RouteConfigInfo)
            self.assertIsInstance(node.node2.node_config, types.RouteConfigInfo)

        lo_json_again = json.dumps(lo_decoded, sort_keys=True, indent=4)
        self.assertEqual(lo_json, lo_json_again)

    def test_datetime_json(self):
        dt = datetime.datetime.now()
        dt_json = json.dumps(dt, indent=4)
        dt_decoded = json.loads(dt_json)
        self.assertIsInstance(dt_decoded, datetime.datetime)
        self.assertEqual(dt, dt_decoded)

    def test_date(self):
        dt = datetime.datetime.now().date()
        dt_json = json.dumps(dt, indent=4)
        dt_decoded = json.loads(dt_json)
        self.assertIsInstance(dt_decoded, datetime.date)
        self.assertEqual(dt, dt_decoded)

    def test_time(self):
        dt = datetime.datetime.now().time()
        dt_json = json.dumps(dt, indent=4)
        dt_decoded = json.loads(dt_json)
        self.assertIsInstance(dt_decoded, datetime.time)
        self.assertEqual(dt, dt_decoded)

    def test_period_json(self):
        prd = ph.create_period((2015, 9, 1, 6, 0), (2015, 9, 1, 13, 0), 30)
        prd_json = json.dumps(prd, sort_keys=True, indent=4)
        prd_decoded = json.loads(prd_json)
        prd_json_again = json.dumps(prd_decoded, sort_keys=True, indent=4)
        self.assertIsInstance(prd_decoded, types.Period)
        self.assertIsInstance(prd_decoded.start_date, datetime.datetime)
        self.assertIsInstance(prd_decoded.end_date, datetime.datetime)
        self.assertEqual(prd_json, prd_json_again)

    def test_enum(self):
        heavy = types.PrecipIntens.HEAVY
        pi_json = json.dumps(heavy, indent=4)
        pi_decoded = json.loads(pi_json)
        self.assertIsInstance(pi_decoded, types.PrecipIntens)
        self.assertEqual(heavy, types.PrecipIntens.HEAVY)
        self.assertEqual(heavy, pi_decoded)

if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import unittest

from pyticas import route
from pyticas import rc
from .base import TestPyTICAS


class TestRouteConfig(TestPyTICAS):

    def test_opposite(self):
        r = route.create_route('S1585', 'S910') # I-35W NB
        (rns, orns) = self.infra.geo.opposite_rnodes(r.rnodes)

        # self.assertEqual(rns[8].station_id, 'S1589')
        # self.assertEqual(orns[8].station_id, 'S1580')
        # self.assertEqual(rns[9].station_id, 'S1094')
        # self.assertEqual(orns[9].station_id, 'S1579')

        for ridx, rn in enumerate(rns):
            print(ridx, rn, orns[ridx])

    def test_route_i35nb(self):
        r = route.create_route('S1585', 'S910') # I-35W NB
        r.cfg = rc.route_config.create_route_config(r.rnodes)
        filepath = os.path.join(self.infra.get_path('tmp', create=True), 'wz-01.xlsx')
        rc.writer.write(filepath, r)
        #
        # print(nodeset.node1.rnode.station_id, nodeset.node2.rnode.station_id)
        # print(nodeset)

    def _test_layout_write(self):
        r1 = route.create_route('S38', 'S40') # I-35W NB
        r2 = route.create_route('S186', 'S188') # I-494 WB
        r3 = route.create_route('S428', 'S430') # US169 NB
        r4 = route.create_route('S276', 'S279') #  I-394 EB
        r5 = route.create_route('S406', 'S935') #  TH100 NB
        r6 = route.create_route('S147', 'S173') #  I-694 EB
        r7 = route.create_route('S1446', 'S854') #  I-35E SB
        r8 = route.create_route('S1578', 'S1581') #  I-35 SB

        r = route.merge_routes([r1, r2, r3, r4, r5, r6, r7, r8])
        r.cfg = rc.route_config.create_route_config(r.rnodes)
        rc.route_config.print_rc(r.cfg)
        filepath = os.path.join(self.infra.get_path('tmp', create=True), 'wz-01.xlsx')
        rc.writer.write(filepath, r.cfg)

    def test_layout_write2(self):
        r1 = route.create_route('S38', 'S40') # I-35W NB
        route.print_route(r1)
        r1.cfg = rc.route_config.create_route_config(r1.rnodes)
        rc.route_config.print_rc(r1.cfg)
        filepath = os.path.join(self.infra.get_path('tmp', create=True), 'wz-02.xlsx')
        rc.writer.write(filepath, r1)

    def test_layout_load(self):
        filepath = os.path.join(self.infra.get_path('tmp', create=True), 'wz-02.xlsx')
        filepath2 = os.path.join(self.infra.get_path('tmp', create=True), 'wz-02-loaded.xlsx')
        r = rc.loader.load(filepath)
        rc.writer.write(filepath2, r)

    def _test_merge_route(self):
        #r = route_config.create_route('S1588', 'S910')
        #r = route_config.create_route('S40', 'S52')
        r1 = route.create_route('S1588', 'S910')
        r2 = route.create_route('S870', 'S826')
        mr = route.merge_routes([r1, r2])

        route.print_route(mr)


if __name__ == '__main__':
    unittest.main()

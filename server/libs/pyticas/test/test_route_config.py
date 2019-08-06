# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import unittest

from pyticas import rc
from pyticas import route
from .base import TestPyTICAS


class TestRouteConfig(TestPyTICAS):
    def test_opposite(self):
        r = route.create_route('S1585', 'S910')  # I-35W NB
        (rns, orns) = self.infra.geo.opposite_rnodes(r.rnodes)

        """
        <----------S1583----S1582---- SB
        ----S1586--S1587------------> NB
       """
        self.assertEqual(rns[2].station_id, 'S1586')
        self.assertEqual(orns[2].station_id, 'S1583')
        self.assertEqual(rns[3].station_id, 'S1587')
        self.assertEqual(orns[3].station_id, 'S1582')

        """
        <---S1580---S1579------------------ SB
        ----------S1589--S1094------------> NB
       """
        self.assertEqual(rns[7].station_id, 'S1589')
        self.assertEqual(orns[7].station_id, 'S1580')
        self.assertEqual(rns[8].station_id, 'S1094')
        self.assertEqual(orns[8].station_id, 'S1579')
        #
        # for ridx, rn in enumerate(rns):
        #     print(ridx, rn, orns[ridx])

    def test_route_cfg(self):

        cases = [
            {
                'name' : 'I-35 NB (south to split)',
                'route': route.create_route('S1585', 'S910'),
                'tests': [
                    {'rn': 'S1586', 'orn': 'S1583'},
                    {'rn': 'S1587', 'orn': 'S1582'},
                    {'rn': 'S1589', 'orn': 'S1580'},
                    {'rn': 'S1094', 'orn': 'S1579'},
                    {'rn': 'S910', 'orn': 'S916'},
                ]
            },

            {
                'name' : 'I-494 EB (TH212 to TH100)',
                'route': route.create_route('S472', 'S195'),
                'tests': [
                    # {'rn': 'S1586', 'orn': 'S1583'},
                    # {'rn': 'S1587', 'orn': 'S1582'},
                    # {'rn': 'S1589', 'orn': 'S1580'},
                    # {'rn': 'S1094', 'orn': 'S1579'},
                    # {'rn': 'S910', 'orn': 'S916'},
                ]
            }
        ]

        for case in cases:
            r = case['route']
            r.cfg = rc.route_config.create_route_config(r.rnodes)
            for test in case['tests']:
                nodeset = rc.route_config.find_nodeset_by_rnode(r.cfg, self.infra.get_rnode(test['rn']), 1)
                self.assertEqual(nodeset.node1.rnode.name, self.infra.get_rnode(test['rn']).name)
                self.assertEqual(nodeset.node2.rnode.name, self.infra.get_rnode(test['orn']).name)

            filepath = os.path.join(self.infra.get_path('tmp', create=True), 'wz-%s.xlsx' % case['name'])
            rc.writer.write(filepath, r)


    def _test_layout_write(self):
        r1 = route.create_route('S38', 'S40')  # I-35W NB
        r2 = route.create_route('S186', 'S188')  # I-494 WB
        r3 = route.create_route('S428', 'S430')  # US169 NB
        r4 = route.create_route('S276', 'S279')  # I-394 EB
        r5 = route.create_route('S406', 'S935')  # TH100 NB
        r6 = route.create_route('S147', 'S173')  # I-694 EB
        r7 = route.create_route('S1446', 'S854')  # I-35E SB
        r8 = route.create_route('S1578', 'S1581')  # I-35 SB

        r = route.merge_routes([r1, r2, r3, r4, r5, r6, r7, r8])
        r.cfg = rc.route_config.create_route_config(r.rnodes)
        rc.route_config.print_rc(r.cfg)
        filepath = os.path.join(self.infra.get_path('tmp', create=True), 'wz-01.xlsx')
        rc.writer.write(filepath, r)

    def test_layout_write2(self):
        r1 = route.create_route('S38', 'S40')  # I-35W NB
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
        # r = route_config.create_route('S1588', 'S910')
        # r = route_config.create_route('S40', 'S52')
        r1 = route.create_route('S1588', 'S910')
        r2 = route.create_route('S870', 'S826')
        mr = route.merge_routes([r1, r2])

        route.print_route(mr)


if __name__ == '__main__':
    unittest.main()

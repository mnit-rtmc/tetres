# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import unittest

from pyticas import route
from pyticas import rc
from .base import TestPyTICAS

class TestRouteLayout(TestPyTICAS):

    def test_merge_two_route(self):
        r1 = route.create_route('S38', 'S40') # I-35W NB
        r2 = route.create_route('S186', 'S188') # I-494 WB
        r3 = route.create_route('S428', 'S430') # US169 NB
        mr = route.merge_routes([r1, r2, r3])
        route.print_route(r1)
        print('='*20)
        route.print_route(r2)
        print('='*20)
        route.print_route(mr)
        print('='*20)

    def _test_merge_two_route2(self):
        r2 = route.create_route('S186', 'S188') # I-494 WB
        r3 = route.create_route('S428', 'S430') # US169 NB
        mr = route.merge_two_routes(r2, r3)
        route.print_route(r2)
        print('='*20)
        route.print_route(r3)
        print('='*20)
        route.print_route(mr)
        print('='*20)

    def test_merge_routes(self):
        r1 = route.create_route('S38', 'S40') # I-35W NB
        r2 = route.create_route('S186', 'S188') # I-494 WB
        r3 = route.create_route('S428', 'S430') # US169 NB
        mr1 = route.merge_two_routes(r1, r2)
        route.print_route(mr1)
        mr2 = route.merge_two_routes(r2, r3)
        route.print_route(mr2)
        mr3 = route.merge_routes([r1, r2, r3])
        route.print_route(mr3)

    def test_load_route_list(self):
        r1 = route.create_route('S38', 'S40', name='Route I-35W NB') # I-35W NB
        r2 = route.create_route('S186', 'S188', name='Route I-494 WB') # I-494 WB
        r3 = route.create_route('S428', 'S430', name='Route US-169 NB') # US169 NB

        route.save_route(r1, overwrite=True)
        route.save_route(r2, overwrite=True)
        route.save_route(r3, overwrite=True)

        for r in route.load_routes():
            print(r.name)


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import unittest

from pyticas import route
from pyticas.tool import pygmaps
from pyticas.logger import getLogger
from .base import TestPyTICAS

class TestGeo(TestPyTICAS):

    def test_connected(self):
        exts = [ rn for rn in self.infra.rnodes.values() if rn.connected_to ]
        ents = [ rn for rn in self.infra.rnodes.values() if rn.connected_from ]

        init_lat = 44.974878
        init_lon = -93.233414
        mymap = pygmaps.maps(init_lat, init_lon, 10)

        for rn in exts:
            coord = (rn.lat, rn.lon)
            cinfo = []
            for corr_name, ent in rn.connected_to.items():
                cinfo.append('to {} through {}'.format(corr_name, ent.name))
            cstr = '<br/>  - '.join(cinfo)
            mymap.addpoint(coord[0], coord[1], "#FF0000",
                           'Exit: {} ({}) <br/>Label: {}<br/>Connection:<br/>  - {}'.format(rn.name, rn.corridor.name, rn.label, cstr))
        for rn in ents:
            coord = (rn.lat, rn.lon)
            cinfo = []
            for corr_name, ext in rn.connected_from.items():
                cinfo.append('from {} through {}'.format(corr_name, ext.name))
            cstr = '<br/>  - '.join(cinfo)
            mymap.addpoint(coord[0], coord[1], "#0000FF",
                           'Entrance: {} ({})<br/>Label: {}<br/>Connection:<br/>  - {}'.format(rn.name, rn.corridor.name, rn.label, cstr))

        file_path = os.path.join(self.infra.get_path('tmp', create=True), 'corridor_connection_map.html')
        mymap.draw(file_path)

    def _test_find_opposite_rnodes(self):
        geo = self.infra.geo
        rns = geo.find_nearby_opposite_rnodes(self.infra.get_rnode('S40'), n_type='Station', d_limit=0.5)
        print('')
        for (rn, dist) in rns:
            print(rn.corridor.name, rn.station_id, rn.name, dist)

    def _test_opposite_rnodes(self):
        geo = self.infra.geo
        r = route.create_route('S40', 'S42')
        rns = geo.opposite_rnodes(r.rnodes, n_type='Station', d_limit=0.5)
        print('')
        for rn, orn in zip(r.rnodes, rns):
            print((rn.corridor.name, rn.station_id, rn.name, rn.label), ' | ',
                  (orn.corridor.name, orn.station_id, orn.name, orn.label))

    def test_opposite_rnodes_1on12(self):

        geo = self.infra.geo

        r1 = route.create_route('S38', 'S40') # I-35W NB
        r2 = route.create_route('S186', 'S188') # I-494 WB
        r3 = route.create_route('S428', 'S430') # US169 NB
        r = route.merge_routes([r1, r2, r3])

        route.print_route(r)

        for rr in [r1, r2, r3, r]:
            (rns, orns) = geo.opposite_rnodes(rr.rnodes, n_type='RNode')
            print('')
            print('--'*10)
            for ridx, rn in enumerate(rns):
                orn = orns[ridx]
                print((rn.station_id, rn.name, rn.label, rn.n_type) if rn else 'None',
                      ' | ',
                      (orn.station_id, orn.name, orn.label, orn.n_type) if orn else 'None')

    def _res(self, rnodes):
        res = []
        for rn in rnodes:
            if not rn: res.append(None)
            elif rn.is_station(): res.append(rn.station_id)
            else: res.append(rn.name)
        return res


if __name__ == '__main__':
    unittest.main()

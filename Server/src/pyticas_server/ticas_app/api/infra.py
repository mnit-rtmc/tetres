# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas import cfg as ticas_cfg
from pyticas import ttypes as types
from pyticas.infra import Infra
from pyticas.tool.json import dumps as jsonify
from pyticas_server.ticas_app import api_urls


# shared with TICAS client
SHARED_CONFIGS = [
    'CONFIG_XML_URL', 'MAX_OCCUPANCY', 'MAX_SCANS', 'MAX_SPEED',
    'MAX_VOLUME', 'MISSING_DATA', 'RWIS_SITE_INFO', 'SAMPLES_PER_DAY', 'SAMPLES_PER_HOUR',
    'TRAFFIC_DATA_URL',
]

def register_api(app):
    @app.route('/ticas/infra', methods=['GET'])
    def get_infra():
        infra = Infra.get_infra()
        corridors = []
        for corr in sorted(infra.get_corridors(), key=lambda c: c.name):
            corridors.append(corr.__dict__)

        try:
            rnodes = _get_items(infra.rnodes)
            dets = _get_items(infra.detectors)
            dmss = _get_items(infra.dmss)
            cams = _get_items(infra.cameras)
            meters = _get_items(infra.meters)
            configs = {}

            for k in SHARED_CONFIGS:
                configs[k] = getattr(ticas_cfg, k)

            configs['ROUTE_CLASS'] = types.Route.__name__
            configs['ROUTE_MODULE'] = types.Route.__module__

            api_urls_info = {}
            for k, v in api_urls.__dict__.items():
                if k.startswith('_'): continue
                api_urls_info[k] = v

            return jsonify({
                'config': configs,
                'api_urls' : api_urls_info,
                'corridor_list': corridors,
                'rnode_list': rnodes,
                'detector_list': dets,
                'dms_list': dmss,
                'camera_list': cams,
                'meter_list': meters,
            }, indent=4, only_name=True )

        except Exception as ex:
            import sys, traceback
            print('-' * 60)
            traceback.print_exc(file=sys.stdout)
            print('-' * 60)

    @app.route('/ticas/corridors', methods=['GET'])
    def get_corridors():
        infra = Infra.get_infra()
        return jsonify({'corridors': infra.get_corridor_names()})

    def _get_items(cache):
        data = {}
        for n, o in cache.items():
            data[n] = o.__dict__
        return data

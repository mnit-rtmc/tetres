# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import inspect

from pyticas.tool.json import dumps as jsonify
from pyticas_ncrtes import api_urls as APIURLs
from pyticas_ncrtes import itypes

def register_api(app):

    @app.route('/ncrtes/info', methods=['GET'])
    def ncrtes_api_urls():

        api_urls = {}
        for k, v in APIURLs.__dict__.items():
            if k.startswith('_'):
                continue
            api_urls[k] = v

        data_types = {}
        for k, v in itypes.__dict__.items():
            if not hasattr(v, '_info_type_') or not inspect.isclass(v) or k.startswith('_'):
                continue
            data_types[v._info_type_] = {'__module__' : v.__module__, '__class__' : v.__name__}

        return jsonify({'api_urls': api_urls, 'data_types' : data_types}, indent=4)



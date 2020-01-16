# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import inspect

from pyticas.tool.json import dumps as jsonify
from pyticas_tetres import ttypes
from pyticas_tetres import api_urls_admin as ADMIN_APIURLs
from pyticas_tetres import api_urls_user as USER_APIURLs
from pyticas_tetres import api_urls_client as CLIENT_APIURLs


def register_api(app):

    @app.route('/tetres/adm/info', methods=['GET'])
    def tetres_admin_api_urls():

        api_urls = {}
        for k, v in CLIENT_APIURLs.__dict__.items():
            if k.startswith('_'):
                continue
            api_urls[k] = v
        for k, v in ADMIN_APIURLs.__dict__.items():
            if k.startswith('_'):
                continue
            api_urls[k] = v

        data_types = {}
        for k, v in ttypes.__dict__.items():
            if not hasattr(v, '_info_type_') or not inspect.isclass(v) or k.startswith('_'):
                continue
            data_types[v._info_type_] = {'__module__' : v.__module__, '__class__' : v.__name__}

        return jsonify({'api_urls': api_urls, 'data_types' : data_types}, indent=4)


    @app.route('/tetres/user/info', methods=['GET'])
    def tetres_user_api_urls():
        api_urls = {}
        for k, v in CLIENT_APIURLs.__dict__.items():
            if k.startswith('_'):
                continue
            api_urls[k] = v
        for k, v in USER_APIURLs.__dict__.items():
            if k.startswith('_'):
                continue
            api_urls[k] = v

        data_types = {}
        types = [ttypes.TTRouteInfo,
                 ttypes.EstimationRequestInfo,
                 ttypes.ReliabilityEstimationModeInfo,
                 ttypes.OperatingConditionsInfo,
                 ttypes.WeatherConditionInfo,
                 ttypes.IncidentConditionInfo,
                 ttypes.WorkzoneConditionInfo,
                 ttypes.SpecialeventConditionInfo,
                 ttypes.SnowmanagementConditionInfo,
                 ttypes.WeekdayConditionInfo,
                 ttypes.OperatingConditionParamInfo,
                 ]
        for v in types:
            k = v.__name__
            if not hasattr(v, '_info_type_') or not inspect.isclass(v) or k.startswith('_'):
                continue
            data_types[v._info_type_] = {'__module__' : v.__module__, '__class__' : v.__name__}

        return jsonify({'api_urls': api_urls, 'data_types' : data_types}, indent=4)



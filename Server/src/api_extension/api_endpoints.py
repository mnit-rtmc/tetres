import os

from flask import Response
from flask import json

import global_settings
from pyticas_tetres.da.route import TTRouteDataAccess


# app = Flask(__name__)

def register_api(app):
    @app.route('/api-extension', methods=['GET'])
    def api_extension_root():
        data = {
            '/api-extension': 'the root of this api',
            '/api-extension/get-all-routes': 'get all admin configured road routes as json',
            '/api-extension/echo/<your-message-here>': 'echos a message you send in the url back to you',
            '/api-extension/current-database-population': 'the root of this api',
        }
        js = json.dumps(data)
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    @app.route('/api-extension/all-routes', methods=['GET'])
    def api_extension_all_routes():
        da = TTRouteDataAccess()
        return json.dumps(da.list())

    @app.route('/api-extension/echo/<param>', methods=['GET'])
    def api_extension_echo(param):
        return 'Echoing [' + param + '] back to you'

    @app.route('/api-extension/current-database-population', methods=['GET'])
    def api_extension_current_database_population():
        path = global_settings.DATA_PATH + "/cache/det"
        det_dirs = os.listdir(path)
        first_year = "unknown"
        last_year = "unknown"
        for year in det_dirs:
            year_dirs = os.listdir(path + f"/{year}")
            if len(year_dirs) > 0:
                first_year = year_dirs[0]
                break
        for year in reversed(det_dirs):
            year_dirs = os.listdir(path + f"/{year}")
            if len(year_dirs) > 0:
                last_year = year_dirs[-1]
                break

        return json.dumps({
            "traffic-data": {
                "first-date": first_year,
                "last-date": last_year
            },
            "cad-incident": {
            },
            "iris-incident": {
            },
            "noaa-weather": {
            }
        })

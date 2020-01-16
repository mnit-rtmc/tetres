from flask import Response
from flask import json

from pyticas_tetres.da.route import TTRouteDataAccess


# app = Flask(__name__)

def register_api(app):
    @app.route('/ff', methods=['GET'])
    def ff_api_root():
        data = {
            '/ff': 'The root of this api',
            '/ff/api/get-all-routes': 'Get all admin configured road routes as json',
            '/ff/api/create-new-routes': 'unfinished',
            '/ff/api/echo/<your-message-here>': 'Echos a message you send in the url back to you'
        }
        js = json.dumps(data)
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    @app.route('/ff/api/get-all-routes', methods=['GET'])
    def ff_api_get_all_routes():
        da = TTRouteDataAccess()
        return json.dumps(da.list())

    @app.route('/ff/api/create-new-route', methods=['GET'])
    def ff_api_create_new_route():
        da = TTRouteDataAccess()
        da.get_tablename()
        return da.get_tablename()

    @app.route('/ff/api/echo/<param>', methods=['GET'])
    def ff_api_echo(param):
        return 'Echoing [' + param + '] back to you'

# -*- coding: utf-8 -*-

from pyticas.tool.json import dumps as jsonify

def register_api(app):
    """ add api to Flask app

    :type app: flask.Flask
    """

    @app.route('/helloworld_json', methods = ['GET'])
    def print_helloworld_json():
        return jsonify( {'greeting' : 'Hello World!' } )

    @app.route('/helloworld', methods = ['GET'])
    def print_helloworld():
        return 'Hello World'


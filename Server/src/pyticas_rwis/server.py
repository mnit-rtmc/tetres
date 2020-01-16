# # -*- coding: utf-8 -*-
# __author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'
#
# import os
# import socket
# import ssl
#
# from flask import Flask
# from flask.ext.autodoc import Autodoc
# from werkzeug.serving import make_ssl_devcert
#
# from pyticas_rwis.logger import getLogger
# from pyticas_rwis.www import doc
# from pyticas_rwis.app import RWISApiApp
#
# def start_server(port, verbose):
#     rwisServer = RWISServer()
#
#     # add apps
#     rwisServer.add_app(RWISApiApp("RWIS Server"))
#
#     # start server
#     rwisServer.start(port=port, debug=verbose, use_reloader=False)
#
#
# class RWISServer(object):
#
#     def __init__(self):
#         self.server = Flask(__name__, static_url_path = "")
#         self.apps = []
#         doc.autodoc = Autodoc(self.server)
#
#     def add_app(self, ticas_app):
#         self.apps.append(ticas_app)
#
#     def start(self,  port=None, debug = True, use_reloader=False, ssl_path=''):
#
#         logger = getLogger(__name__)
#         logger.info('initializing RWIS Server')
#         # create key and crt for HTTPS
#         logger.info('creating SSL context...')
#         if ssl_path:
#             make_ssl_devcert(os.path.join(ssl_path, 'ssl'), host='localhost')
#             context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
#             context.load_cert_chain(os.path.join(ssl_path, 'ssl.crt'), os.path.join(ssl_path, 'ssl.key'))
#         else:
#             context = None
#
#         # call init modules
#         logger.info('loading init modules...')
#         for app in self.apps:
#             app.init(self.server)
#
#         logger.info('registering service modules...')
#         for app in self.apps:
#             app.register_service(self.server)
#
#         # run api web service
#         if not port:
#             sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             sock.bind(('localhost', 0))
#             port = sock.getsockname()[1]
#             sock.close()
#
#         self.server.run(debug =debug, port=port, ssl_context=context, use_reloader=use_reloader)
#
#         logger.info('program terminated')

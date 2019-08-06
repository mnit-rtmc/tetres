# -*- coding: utf-8 -*-

import sys, os, socket, getopt

# set data_path to "CURRENT_DIR/data"
cur_path = os.path.dirname(__file__)
data_path = os.path.join(cur_path, 'data')

# parse command line options
try:
    opts, args = getopt.getopt(sys.argv[1:], "p:v", ["port"])
except getopt.GetoptError as err:
    print(str(err))
    sys.exit(2)

port = None
verbose = False

for o, a in opts:
    if o == "-v":
        verbose = True
    elif o in ("-p", "--port"):
        port = int(a)
    else:
        assert False, "unhandled option"

# get random port if port is not given
if not port:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    sock.close()

# import required modules
from pyticas_server.server import TICASServer

# automatically generated app package
from myapp.app import MyApp

# create server instance
ticasServer = TICASServer(data_path)

# add apps
ticasServer.add_app(MyApp('My HelloWorld App'))

# start server
ticasServer.start(port=port, debug=verbose, use_reloader=False)

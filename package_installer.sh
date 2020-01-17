#!/bin/bash

# Sets up the virtual environment for the server in ./ve
pip3 install --user virtualenv
virtualenv -p python3 ve
source ve/bin/activate
pip3 install -r requirements.txt
deactivate

chmod +x server.sh

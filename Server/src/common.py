# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import sys

CUR_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(os.path.dirname(CUR_PATH), 'data')
LIB_PATH = os.path.join(os.path.dirname(CUR_PATH), 'libs')
CONFIG_FILE_PATH = os.path.join(os.path.dirname(CUR_PATH), 'tetres.conf')

# add path
sys.path.append(LIB_PATH)



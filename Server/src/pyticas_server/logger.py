# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.logger import getLogger as pyticas_logger
from pyticas_server import cfg

def getLogger(name):
    return pyticas_logger(name, filename=cfg.LOG_FILE_NAME, loglevel=cfg.LOG_LEVEL, to_console=cfg.LOG_TO_CONSOLE)
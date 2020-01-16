# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import logging
import logging.handlers
import os
import tempfile

from pyticas import cfg

LOGGERS = {}
LOG_ROOT_PATH = os.path.join(tempfile.gettempdir(), 'log-pyticas')
if not os.path.exists(LOG_ROOT_PATH):
    os.makedirs(LOG_ROOT_PATH)


def getLogger(name, **kwargs):
    loglevel = kwargs.get('loglevel', 'INFO')
    filename = kwargs.get('filename', '')
    to_console = kwargs.get('to_console', False)
    logger = logging.getLogger(name)
    _updateLogger(name, loglevel, filename, to_console)
    LOGGERS[name] = (loglevel, filename, to_console)
    return logger


def getDefaultLogger(name):
    return getLogger(name,
                     loglevel=cfg.ROOT_LOGGER_LEVEL,
                     filename=cfg.ROOT_LOGGER_FILENAME,
                     to_console=cfg.ROOT_LOGGER_TO_CONSOLE)


def updateLoggerPaths(dir_path):
    global LOG_ROOT_PATH
    LOG_ROOT_PATH = dir_path
    for name, (log_level, filename, to_console) in LOGGERS.items():
        _updateLogger(name, log_level, filename, to_console)


def _updateLogger(name, log_level, filename, to_console):
    log = logging.getLogger(name)
    log.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    log.handlers = []
    log.addHandler(_create_handler(name, filename, to_console))
    log.propagate = False
    return log


def _create_handler(name, filename, to_console):
    formatter = logging.Formatter(cfg.LOG_FORMAT, cfg.LOG_DATE_FORMAT)
    max_bytes = cfg.LOG_MAX_FILE_SIZE
    backup_count = cfg.LOG_BACKUP_COUNT

    if to_console or (not to_console and not filename):
        handler = logging.StreamHandler()
    else:
        filename = filename or cfg.ROOT_LOGGER_FILENAME
        logfile = os.path.join(LOG_ROOT_PATH, 'log-{}.txt'.format(filename))
        handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=max_bytes, backupCount=backup_count)

    handler.setFormatter(formatter)
    return handler

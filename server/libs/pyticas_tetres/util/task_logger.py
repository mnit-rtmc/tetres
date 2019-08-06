# -*- coding: utf-8 -*-
import os

import datetime

from pyticas.tool import json
from pyticas_tetres import tetres

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

LOGGERS = {}

class TaskLogger(object):
    def __init__(self, log_file_path, **kwargs):
        self.capacity = kwargs.get('capacity', 1000)
        self.filepath = log_file_path
        self.registry = {}
        self.logs = []
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, 'r') as f:
            saved = json.loads(f.read())
            self.registry = saved['registry']
            self.logs = saved['logs']

    def save(self):
        with open(self.filepath, 'w') as f:
            self.logs = self.logs[-1*self.capacity:]
            f.write(json.dumps({'registry' : self.registry, 'logs' : self.logs}))

    def now(self):
        """
        :rtype: str
        """
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def add_log(self, value):
        self.logs.append(value)

    def get_logs(self):
        """
        :rtype: list
        """
        return self.logs

    def set_registry(self, key, value):
        self.registry[key] = value

    def get_registry(self, key):
        return self.registry.get(key, None)

    def __getitem__(self, key):
        return self.registry.get(key, None)

    def __setitem__(self, key, value):
        self.registry[key] = value


def get_task_logger(name, **kwargs):
    """
    :type name: str
    :rtype: TaskLogger
    """
    global LOGGERS
    if name in LOGGERS:
        return LOGGERS[name]
    logger = TaskLogger(_logger_path(name), **kwargs)
    LOGGERS[name] = logger
    return logger

def _logger_path(name):
    """
    :type name: str
    :rtype: str
    """
    infra = tetres.get_infra()
    log_root_dir = infra.get_path('tetres/task_log', create=True)
    log_file_path = os.path.join(log_root_dir, '%s.json' % name)
    return log_file_path
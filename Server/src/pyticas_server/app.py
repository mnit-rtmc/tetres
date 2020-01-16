# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
from importlib import import_module

class TICASApp(object):

    def __init__(self, name):
        """
        :type name: str
        """
        self.name = name

    def init(self, app):
        """
        :type app: Flask
        """
        pass

    def register_service(self, app):
        """
        :type app: Flask
        :return:
        """
        pass

    def finalize(self):
        pass

    # def load_api_modules(self, file, name, api_dir):
    #     loaded = []
    #     pkgname = '.'.join(str(name).split(".")[:-1]) + '.' + api_dir
    #     for modfile in os.listdir(os.path.join(os.path.dirname(file), api_dir)):
    #         fileinfo = os.path.splitext(modfile)
    #         modname = fileinfo[0]
    #         ext = fileinfo[1]
    #         if modname.startswith('_') or modname in loaded or ext not in ['.py', '.pyc']: continue
    #         yield import_module(pkgname+'.'+modname)


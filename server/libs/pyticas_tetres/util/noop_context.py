# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

class NonOPContextManager(object):
    def __init__(self, resource=None):
        self.resource = resource
    def __enter__(self):
        return self.resource
    def __exit__(self, *args):
        pass

def nonop_with():
    return NonOPContextManager()

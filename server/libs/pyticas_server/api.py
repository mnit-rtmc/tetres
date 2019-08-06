# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

API_VERSION = 'v1'

def api_url(url):
    return '/{}{}'.format(API_VERSION, url)
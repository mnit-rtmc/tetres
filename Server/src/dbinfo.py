# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from global_settings import *
from pyticas import tetresconf

SERVER_ADDR = tetresconf.get_property('ticas.db_host')
DB_USER = tetresconf.get_property('ticas.db_user')
DB_PASSWD = tetresconf.get_property('ticas.db_pass')

# Set Database Information Here
TETRES_DB_ADDR = SERVER_ADDR
TETRES_DB_PORT = 5432
TETRES_DB_USER = DB_USER
TETRES_DB_PASSWD = DB_PASSWD
TETRES_DB_NAME = tetresconf.get_property('ticas.tetres_db_name')

IRIS_DB_ADDR = SERVER_ADDR
IRIS_DB_PORT = 5432
IRIS_DB_USER = DB_USER
IRIS_DB_PASSWD = DB_PASSWD
IRIS_DB_NAME = tetresconf.get_property('ticas.iris_db_name')

CAD_DB_ADDR = SERVER_ADDR
CAD_DB_PORT = 5432
CAD_DB_USER = DB_USER
CAD_DB_PASSWD = DB_PASSWD
CAD_DB_NAME = tetresconf.get_property('ticas.cad_db_name')

RWIS_DB_ADDR = SERVER_ADDR
RWIS_DB_PORT = 5432
RWIS_DB_USER = DB_USER
RWIS_DB_PASSWD = DB_PASSWD
RWIS_DB_NAME = tetresconf.get_property('ticas.rwis_db_name')


def ncrtes_db_info(data_path):
    return {
        'engine': 'sqlite',
        'filename': os.path.join(data_path, 'db', 'ncrtes.db'),
    }


def tetres_db_info():
    return {
        'engine': 'postgresql',
        'host': TETRES_DB_ADDR,
        'port': TETRES_DB_PORT,
        'db_name': TETRES_DB_NAME,
        'user': TETRES_DB_USER,
        'passwd': TETRES_DB_PASSWD
    }


def iris_incident_db_info():
    return {
        'engine': 'postgresql',
        'host': IRIS_DB_ADDR,
        'port': IRIS_DB_PORT,
        'db_name': IRIS_DB_NAME,
        'user': IRIS_DB_USER,
        'passwd': IRIS_DB_PASSWD
    }


def cad_db_info():
    return {
        'engine': 'postgresql',
        'host': CAD_DB_ADDR,
        'port': CAD_DB_PORT,
        'db_name': CAD_DB_NAME,
        'user': CAD_DB_USER,
        'passwd': CAD_DB_PASSWD
    }


def rwis_db_info():
    return {
        'engine': 'postgresql',
        'host': RWIS_DB_ADDR,
        'port': RWIS_DB_PORT,
        'db_name': RWIS_DB_NAME,
        'user': RWIS_DB_USER,
        'passwd': RWIS_DB_PASSWD
    }

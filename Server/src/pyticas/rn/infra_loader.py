# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import gzip
import io
import os
import urllib.request
from xml.etree import ElementTree as et

from pyticas import cfg
from pyticas.logger import getDefaultLogger
from pyticas.rn.orgs import cam_org as camOrg
from pyticas.rn.orgs import corr_org as corrOrg
from pyticas.rn.orgs import det_org as detOrg
from pyticas.rn.orgs import dms_org as dmsOrg
from pyticas.rn.orgs import meter_org as metOrg
from pyticas.rn.orgs import rnode_org as rnodeOrg
from pyticas.ticas import get_path
from pyticas.tool import util

import inspect

logger = getDefaultLogger(__name__)


def load_metro(cfg_date='', **kwargs):
    """ load_data metro infrastructure

    :param cfg_date: configuration date of xml
    :return: True if succeed else False
    :rtype: (bool, Exception)
    """
    logger.debug("loading roadway network information...")
    # for caller in inspect.stack():
    #     print(caller.filename, caller.function, caller.lineno)
    if kwargs.get('download', False) and not cfg_date:
        metroFile = download_metro_file()
    elif not cfg_date:
        metroFile = recent_metro_file()
    else:
        metroFile = find_metro_file(cfg_date)
    if metroFile == None or not os.path.exists(metroFile):
        if not kwargs.get('load_anyway', True):
            logger.debug('cannot set metro file path')
            raise Exception('cannot load_data metro file : %s' % metroFile)
        metroFile = download_metro_file()

    return _construct_infra(metroFile)


def load_metro_from_file(file_path):
    return _construct_infra(file_path)


def find_metro_file(cfg_date):
    if not cfg_date:
        raise ValueError('configuration date is required')
    for f in list_metro_files():
        if cfg_date in os.path.basename(f):
            return f
    return ''


def recent_metro_file():
    """
    :return: most recent metro file
    """
    files = list_metro_files()
    if files:
        return files.pop()
    else:
        return None


def list_metro_files():
    """

    :return: metro file list
    """
    return util.file_list(get_path('metro'))


def download_metro_file():
    """ load_data metro xml file from IRIS

    :return: metro file path
    """
    logger.debug("loading metro.xml information from : " + cfg.CONFIG_XML_URL)

    logger.debug("loading file from IRIS server")
    try:
        res = urllib.request.urlopen(cfg.CONFIG_XML_URL)
    except urllib.error.HTTPError as e:
        logger.debug('cannot get the remote file (reason={}, http_code={})'.format(str(e.reason), e.code))
        logger.debug('file : {}'.format(cfg.CONFIG_XML_URL))
        raise Exception('cannot load_data metro network information')
    except urllib.error.URLError as e:
        logger.critical('cannot connect to the server (reason={})'.format(str(e.reason)))
        raise Exception('cannot load_data metro network information')

    logger.debug("unzipping the downloaded xml file")

    mem_file = io.BytesIO(res.read())
    tmp_zip = gzip.GzipFile(fileobj=mem_file)
    metro_file = '{0}{1}{2}.xml'.format(get_path('metro'), os.sep, datetime.date.today())
    with open(metro_file, 'w') as mfile:
        mfile.write(tmp_zip.read().decode('utf-8'))

    return metro_file


def _construct_infra(metro_file_path):
    """ construct infra such as corridor, rnode(station, entrance, exit..), detector, DMS..

    :param metro_file_path: metro file path to use
    """
    logger.debug("analyzing xml data and creating road informations")

    if not os.path.exists(metro_file_path):
        raise Exception('metro config file does not exists')

    xml_data = ''
    with open(metro_file_path, "r") as f:
        xml_data = f.read()

    root = et.fromstring(xml_data)
    assert isinstance(root, et.Element)

    CORRIDOR_CACHE = {}
    RNODE_CACHE = {}
    STATION_RNODE_MAP = {}
    DETECTOR_CACHE = {}
    METER_CACHE = {}
    DMS_CACHE = {}
    CORRIDOR_DMS_MAP = {}
    CAMERA_CACHE = {}
    CORRIDOR_CAMERA_MAP = {}

    cfg = [c for c in root.iter('tms_config')]
    cfg_date = _get_date_from_ts(cfg[0].get('time_stamp'))

    for corr in root.iter('corridor'):
        corrObject = corrOrg.create_corridor(corr, CORRIDOR_CACHE)
        corrObject.infra_cfg_date = cfg_date
        for rn in corr.findall('r_node'):
            rnodeObject = rnodeOrg.create_rnode(corrObject, rn, RNODE_CACHE, STATION_RNODE_MAP)
            rnodeObject.infra_cfg_date = cfg_date
            corrOrg.add_rnode(corrObject, rnodeObject)
            for dt in rn.findall('detector'):
                detObject = detOrg.create_detector(rnodeObject, rnodeObject.station_id, dt, DETECTOR_CACHE)
                detObject.infra_cfg_date = cfg_date
                rnodeOrg.add_detector(rnodeObject, detObject)
            rnodeOrg.fix_rnode_lanes(rnodeObject)
            for mt in rn.findall('meter'):
                meterObject = metOrg.create_meter(rnodeObject, mt, METER_CACHE)
                meterObject.infra_cfg_date = cfg_date
                rnodeOrg.add_meter(rnodeObject, meterObject)

        corrOrg.link_rnodes(corrObject)

    for cam in root.findall('camera'):
        camObject, corr_name = camOrg.create_camera(cam, CAMERA_CACHE, CORRIDOR_CAMERA_MAP)
        if camObject:
            camObject.infra_cfg_date = cfg_date
            corrOrg.add_camera(camObject, corr_name, CORRIDOR_CACHE, RNODE_CACHE)

    for dms in root.findall('dms'):
        dmsObject, corr_name = dmsOrg.create_dms(dms, DMS_CACHE, CORRIDOR_DMS_MAP)
        dmsObject.infra_cfg_date = cfg_date
        corrOrg.add_dms(dmsObject, corr_name, CORRIDOR_CACHE)

    logger.debug("synchronization with IRIS server has been done.")

    return {
        'cfg_date': cfg_date,
        'corridors': CORRIDOR_CACHE,
        'rnodes': RNODE_CACHE,
        'station_rnode_map': STATION_RNODE_MAP,
        'detectors': DETECTOR_CACHE,
        'meters': METER_CACHE,
        'cameras': CAMERA_CACHE,
        'corridor_camera_map': CORRIDOR_CAMERA_MAP,
        'dmss': DMS_CACHE,
        'corridor_dms_map': CORRIDOR_DMS_MAP,
    }


def _get_date_from_ts(ts):
    tss = ts.split(' ')
    ds = '{} {}'.format(' '.join(tss[:-2]), tss[-1])
    return str(datetime.datetime.strptime(ds, '%a %b %d %H:%M:%S %Y').date())

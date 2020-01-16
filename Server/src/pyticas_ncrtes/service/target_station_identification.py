# -*- coding: utf-8 -*-
"""
pyticas_ncrtes.service.target_station_identification
=====================================================

- module to identify target detector station
- this module is called by API request handler `pyticas_ncrtes.target_station_identification`
- `run` function can be called as a separated process

"""
import time

from pyticas.infra import Infra
from pyticas.tool import tb
from pyticas.tool import timeutil
from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core import nsrf
from pyticas_ncrtes.da.normal_func import NormalFunctionDataAccess
from pyticas_ncrtes.da.target_station import TargetStationDataAccess
from pyticas_ncrtes.da.winter_season import WinterSeasonDataAccess
from pyticas_ncrtes.db import conn
from pyticas_ncrtes.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

prefix = ''


def run(pid, stations, months, data_path, db_info):
    """ target station identification main process

    Parameters
    ===========
        - pid : process identification for multi-processing
        - stations : station list
        - months : month list
        - data_path : TICAS data path

    :type pid: int
    :type stations: list[str]
    :type months: list[(int, int)]
    :type data_path : str
    :type db_info: dict
    :return:
    """
    if db_info:
        Infra.initialize(data_path)
        infra = Infra.get_infra()

        if conn.Session == None:
            conn.connect(db_info)
    else:
        infra = ncrtes.get_infra()

    logger = getLogger(__name__)
    logger.info('starting target station identification')

    wsDA = WinterSeasonDataAccess()
    nfDA = NormalFunctionDataAccess()
    tsDA = TargetStationDataAccess()

    # process start time
    stime = time.time()
    n_stations = len(stations)
    cnt = 0
    for sidx, st in enumerate(stations):
        station = infra.get_rnode(st)
        logger.info('# PID=%d, SIDX=%d/%d, STATION=%s' % (pid, sidx, n_stations, st))
        try:
            nf = nsrf.get_normal_function(station, months, wsDA=wsDA, nfDA=nfDA, tsDA=tsDA, autocommit=True)
            if nf and nf.is_valid():
                logger.info('  - %s is valid' % station.station_id)
            else:
                logger.debug('  - %s is not valid (nf=%s)' % (station.station_id, nf))

            # cnt += 1
            #
            # if cnt and cnt % 20 == 0:
            #     logger.warning('  - commmit!!')
            #     wsDA.commit()
            #     nfDA.commit()
            #     tsDA.commit()

        except Exception as ex:
            logger.warning(tb.traceback(ex, False))

    # wsDA.commit()
    # nfDA.commit()
    # tsDA.commit()
    # logger.warning('  - commmit!! (final)')

    wsDA.close()
    nfDA.close()
    tsDA.close()

    etime = time.time()

    logger.info('end of target station identification (elapsed time=%s)' % timeutil.human_time(seconds=(etime - stime)))

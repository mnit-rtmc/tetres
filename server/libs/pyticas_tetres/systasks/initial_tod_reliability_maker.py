# -*- coding: utf-8 -*-
"""
Initial TOD Reliability Calculation module
"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
from multiprocessing import Process, Manager, Lock

from pyticas import ticas
from pyticas_tetres.da.route import TTRouteDataAccess
from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine import traveltime_info

DEFAULT_NUMBER_OF_PROCESSES = 5


def run(target_date, db_info):
    """

    :type target_date: datetime.date
    :type db_info: dict
    """
    logger = getLogger(__name__)
    logger.debug('>> Calculating TOD Reliabilities for all routes')
    _run_multi_process(_worker_process_to_calculate_tod_reliabilities, target_date, db_info)
    logger.debug('<< End of calculating TOD Reliabilities for all routes')


def _run_multi_process(target_function, target_date, db_info):
    """
    :type target_function: callable
    :type target_date: datetime.date
    :type db_info: dict
    """
    logger = getLogger(__name__)

    logger.debug('>>> Starting Multi Processing (target-date= %s)' % (target_date))

    m = Manager()
    queue = m.Queue()

    lck = Lock()
    N = DEFAULT_NUMBER_OF_PROCESSES
    data_path = ticas._TICAS_.data_path
    procs = []
    for idx in range(N):
        p = Process(target=target_function,
                    args=(idx, queue, lck, data_path, db_info))
        p.start()
        procs.append(p)

    ttr_route_da = TTRouteDataAccess()
    ttr_ids = [ttri.id for ttri in ttr_route_da.list()]
    ttr_route_da.close_session()

    real_target_date = datetime.datetime.combine(target_date, datetime.time(12, 0, 0, 0))
    total = len(ttr_ids)
    for ridx, ttr_id in enumerate(ttr_ids):
        queue.put((ttr_id, real_target_date, (ridx + 1), total))

    for idx in range(N * 3):
        queue.put((None, None, None, None))

    for p in procs:
        try:
            p.join()
        except:
            pass

    # flush queue
    while not queue.empty():
        queue.get()

    logger.debug('<<< End of Multi Processing (target-date=%s)' % (target_date))


def _worker_process_to_calculate_tod_reliabilities(idx, queue, lck, data_path, db_info):
    import gc
    from pyticas.tool import tb
    from pyticas_tetres.db.tetres import conn
    from pyticas.infra import Infra

    logger = getLogger(__name__)
    # initialize
    logger.debug('[TOD Reliability Worker %d] starting...' % (idx))
    ticas.initialize(data_path)
    Infra.get_infra()
    conn.connect(db_info)

    logger.debug('[TOD Reliability Worker %d] is ready' % (idx))
    while True:
        ttr_id, target_date, num, total = queue.get()
        if target_date is None:
            exit(1)
        try:
            logger.debug('[TOD Reliability Worker %d] (%d/%d) calculating for route=%s at %s' % (
                idx, num, total, ttr_id, target_date.strftime('%Y-%m-%d')))
            traveltime_info.calculate_TOD_reliabilities(ttr_id, target_date, lock=lck)
            gc.collect()
        except Exception as ex:
            tb.traceback(ex)
            continue

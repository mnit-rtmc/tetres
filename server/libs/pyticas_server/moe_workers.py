# -*- coding: utf-8 -*-
from pyticas_server.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import shutil
import threading
import time
import uuid
import zipfile
from multiprocessing import Process, Queue, Lock, Manager

from pyticas import ticas
from pyticas.infra import Infra
from pyticas.tool import tb

DEFAULT_NUMBER_OF_PROCESSES = 2
VACCUM_IS_RUNNING = False
WORKER_IS_RUNNING = False

m = None
queue = None
shared_counters = None


def start(n_workers, db_info, cad_db_info, iris_db_info):
    global m, queue, shared_counters
    m = Manager()
    queue = m.Queue()
    shared_counters = m.dict()

    _start_vaccum_thread()
    _start_worker_processes(n_workers, db_info, cad_db_info, iris_db_info)


def estimate(moe_funcs, moe_names, **kwargs):
    """
    :type moe_funcs: list[callable]
    :type moe_names: list[str]
    :rtype: str
    """
    global shared_counters
    if not moe_funcs or len(moe_funcs) != len(moe_names):
        return None

    uid = _get_uid()
    for idx, moe_func in enumerate(moe_funcs):
        moe_name = moe_names[idx]
        queue.put((moe_func, moe_name, uid, kwargs))
    return uid


def _start_worker_processes(N, db_info, cad_db_info, iris_db_info):
    global queue, shared_counters, WORKER_IS_RUNNING

    if WORKER_IS_RUNNING:
        return

    lock = Lock()
    WORKER_IS_RUNNING = True
    N = N or DEFAULT_NUMBER_OF_PROCESSES
    workers = []
    data_path = ticas._TICAS_.data_path
    for idx in range(N):
        p = Process(target=_estimation_process,
                    args=(idx, queue, shared_counters, lock, data_path, db_info, cad_db_info, iris_db_info))
        p.start()
        workers.append(p)


def _start_vaccum_thread():
    global VACCUM_IS_RUNNING

    if VACCUM_IS_RUNNING:
        return

    VACCUM_IS_RUNNING = True

    def _vaccum():
        allowed_days = 7 * 86400
        output_root_path = _output_path()
        while True:
            now = time.time()
            for f in os.listdir(output_root_path):
                if f.startswith('.'):
                    continue
                filepath = os.path.join(output_root_path, f)
                if os.stat(filepath).st_mtime < now - allowed_days:
                    if os.path.isdir(filepath):
                        shutil.rmtree(filepath, ignore_errors=True)
                    else:
                        os.remove(filepath)
            time.sleep(3 * 3600)  # sleep 3hour

    t = threading.Thread(target=_vaccum)
    t.start()


def _estimation_process(id, queue, counters, lock, data_path, DB_INFO, CAD_DB_INFO, IRIS_DB_INFO):
    """
    :type id: int
    :type queue: Queue
    :type counters: dict
    :type lock: Lock
    :type data_path: str
    :type DB_INFO: dict
    :type CAD_DB_INFO: dict
    :type IRIS_DB_INFO: dict
    """

    from pyticas_tetres.db.iris import conn as iris_conn
    from pyticas_tetres.db.cad import conn as cad_conn
    from pyticas_tetres.db.tetres import conn

    logger = getLogger(__name__)
    # initialize
    logger.debug('[MOE WORKER %d] starting...' % (id))
    ticas.initialize(data_path)
    infra = Infra.get_infra()
    conn.connect(DB_INFO)
    cad_conn.connect(CAD_DB_INFO)
    iris_conn.connect(IRIS_DB_INFO)

    logger.debug('[MOE WORKER %d] is ready' % (id))
    while True:
        (moe_func, moe_name, uid, kwargs) = queue.get()

        try:
            logger.debug('[MOE WORKER %d] >>>>> start estimation (uid=%s, route=%d)' % (id, uid, a_route_id))
            _eparam = eparam.clone()
            _eparam.travel_time_route = ttr_da.get_by_id(a_route_id)
            estimation.estimation(_eparam, uid)
            logger.debug('[MOE WORKER %d] <<<<< end of estimation (uid=%s, route=%d)' % (id, uid, a_route_id))
        except Exception as ex:
            tb.traceback(ex)
            logger.debug('[MOE WORKER %d] <<<<< end of task (exception occured) (uid=%s)' % (id, uid))

        should_pack = False

        with lock:
            counters[uid] = counters[uid] - 1
            if counters[uid] <= 0:
                del counters[uid]
                should_pack = True

        if should_pack:
            logger.debug('[EST WORKER %d] >>> make compressed file (uid=%s)' % (id, uid))
            _pack_result(uid)
            logger.debug('[EST WORKER %d] <<< end of making compressed file (uid=%s)' % (id, uid))


def _pack_result(uid):
    """
    :type uid:
    """
    odir = _output_path(uid)
    ozip = '%s.zip' % odir
    os.chdir(os.path.dirname(odir))
    with zipfile.ZipFile(ozip, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, filenames in os.walk(os.path.basename(odir)):
            for name in filenames:
                name = os.path.join(root, name)
                name = os.path.normpath(name)
                zf.write(name, name)
    # remove output dir
    shutil.rmtree(odir)


def _get_uid(create_dir=True):
    """
    :rtype: str
    """
    while True:
        uid = str(uuid.uuid4())
        odir = _output_path(uid)
        ozip = '%s.zip' % odir
        if not os.path.exists(odir) and not os.path.exists(ozip):
            if create_dir:
                os.mkdir(odir)
            return uid


def _output_path(sub_dir='', create=True):
    infra = Infra.get_infra()
    if sub_dir:
        output_dir = infra.get_path('moe/%s' % sub_dir, create=create)
    else:
        output_dir = infra.get_path('moe', create=create)

    if create and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        return os.path.abspath(output_dir)

    if os.path.exists(output_dir):
        return os.path.abspath(output_dir)
    else:
        return output_dir

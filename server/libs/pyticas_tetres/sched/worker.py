# -*- coding: utf-8 -*-
from pyticas.tool import tb
from pyticas_tetres import cfg
from pyticas_tetres.da.actionlog import ActionLogDataAccess
from pyticas_tetres.da.config import ConfigDataAccess

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import uuid
from multiprocessing import Process, Queue, Lock, Manager

from pyticas import ticas
from pyticas.infra import Infra
from pyticas_tetres.logger import getLogger

DEFAULT_NUMBER_OF_PROCESSES = 1
VACCUM_IS_RUNNING = False
WORKER_IS_RUNNING = False

m = None
queue = None
shared_counters = None



def start(n_workers, db_info, cad_db_info, iris_db_info):
    global m, queue, shared_counters, WORKER_IS_RUNNING

    if WORKER_IS_RUNNING:  # prevent multiple calls
        return

    _initialize_actionlog_status()

    m = Manager()
    queue = m.Queue()
    shared_dict = m.dict()
    lock = Lock()
    WORKER_IS_RUNNING = True
    N = n_workers or DEFAULT_NUMBER_OF_PROCESSES
    data_path = ticas._TICAS_.data_path
    for idx in range(N):
        p = Process(target=_worker_process,
                    args=(idx, queue, shared_dict, lock, data_path, db_info, cad_db_info, iris_db_info))
        p.start()


def add_task(task, *args, **kwargs):
    """
    :type task: callable
    :rtype: str
    """
    global shared_counters
    uid = str(uuid.uuid4())
    now = datetime.datetime.now()
    queue.put((uid, now, task, args, kwargs))


def _worker_process(id, queue, counters, lock, data_path, DB_INFO, CAD_DB_INFO, IRIS_DB_INFO):
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

    from pyticas_tetres.db.tetres import conn
    from pyticas_tetres.db.iris import conn as iris_conn
    from pyticas_tetres.db.cad import conn as cad_conn

    logger = getLogger(__name__)
    # initialize
    logger.debug('[ADMIN WORKER %d] starting...' % (id))
    ticas.initialize(data_path)
    infra = Infra.get_infra()
    conn.connect(DB_INFO)
    cad_conn.connect(CAD_DB_INFO)
    iris_conn.connect(IRIS_DB_INFO)

    logger.debug('[ADMIN WORKER %d] is ready' % (id))
    while True:
        (_uid, _task_added_time, _task, _args, _kwargs) = queue.get()
        try:
            logger.debug('[ADMIN WORKER %d] >>>>> start to run task (uid=%s)' % (id, _uid))
            _task(*_args, **_kwargs)
            logger.debug('[ADMIN WORKER %d] <<<<< end of task (uid=%s)' % (id, _uid))
        except Exception as ex:
            tb.traceback(ex)
            logger.debug('[ADMIN WORKER %d] <<<<< end of task (exception occured) (uid=%s)' % (id, _uid))


def _initialize_actionlog_status():
    """ Delete running action log id from `config` table and delete

    :return:
    :rtype:
    """
    da_config = ConfigDataAccess()
    da_config.insert_or_update(cfg.OPT_NAME_ACTIONLOG_ID_IN_PROCESSING, '')
    da_config.commit()
    da_config.close_session()

    now = datetime.datetime.now()

    da_actionlog = ActionLogDataAccess()
    running_items = da_actionlog.list(status=ActionLogDataAccess.STATUS_RUNNING)
    for item in running_items:
        da_actionlog.update(item.id, {'status' : ActionLogDataAccess.STATUS_STOPPED,
                                      'status_updated_date' : now})
    da_actionlog.commit()
    da_actionlog.close_session()
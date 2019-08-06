# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import time

from functools import wraps
from pyticas.logger import getLogger

PROF_DATA = {}

def profile(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        start_time = time.time()

        ret = fn(*args, **kwargs)

        elapsed_time = time.time() - start_time

        name = fn.__name__
        if args[0] != None and hasattr(args[0], '__class__') and hasattr(args[0], fn.__name__):
            name = '%s.%s.%s' % (fn.__module__, args[0].__class__.__name__, fn.__name__)
        else:
            name = '%s.%s' % (fn.__module__, fn.__name__)

        if name not in PROF_DATA:
            PROF_DATA[name] = [0, []]
        PROF_DATA[name][0] += 1
        PROF_DATA[name][1].append(elapsed_time)

        return ret

    return with_profiling

def print_prof_data():
    logger = getLogger(__name__)
    logger.info('Profile Results ----------------------')
    for fname, data in PROF_DATA.items():
        max_time = max(data[1])
        avg_time = sum(data[1]) / len(data[1])
        logger.info("")
        logger.info("  + function : %s()" % fname)
        logger.info("     - called : %d times" % data[0])
        logger.info("     - execution time : max=%.3fs, avg=%.3fs, total=%.3fs" % (max_time, avg_time, avg_time*data[0]))
    logger.info('-'*40)

def clear_prof_data():
    global PROF_DATA
    PROF_DATA = {}
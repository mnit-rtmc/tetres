# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import time
import unittest
import threading
import random

from pyticas.tool import concurrent


class TestRNodeInfo(unittest.TestCase):

    done_order = 1
    sem = threading.Semaphore(1)

    def _job(self, sleep_time, data, **kwargs):
        st = random.random()*4
        if sleep_time == 19:
            st = 5
        time.sleep(st)
        self.sem.acquire()
        my_order = self.done_order
        self.done_order += 1
        self.sem.release()
        executor = kwargs.get('pe')
        print((data, st, my_order, executor._work_queue.qsize()))
        return (data, st, my_order)

    def _job_done(self, result):
        print('job done : {}'.format(result))

    def test_something(self):
        worker = concurrent.Worker(5)
        for idx in range(20):
            worker.add_task(self._job, idx, idx)
        ret = worker.run()


if __name__ == '__main__':
    unittest.main()

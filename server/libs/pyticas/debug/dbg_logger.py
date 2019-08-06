# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import unittest

from pyticas import logger
from .base import TestPyTICAS

class TestLogger(TestPyTICAS):

    def test_logging(self):

        # write log messages to console from 'INFO' level
        log1 = logger.getLogger('%s-logger1' % __name__)

        # write log messages to file "log-test2.txt" from 'INFO' level
        log2 = logger.getLogger('%s-logger2' % __name__, filename='test2')

        # write log messages to file "log-test3.txt" from 'INFO' level
        log3 = logger.getLogger('%s-logger3' % __name__, filename='test3', loglevel='INFO')

        # write log messages to file "log-test4.txt" from 'DEBUG' level
        log4 = logger.getLogger('%s-logger4' % __name__, filename='test4', loglevel='DEBUG')

        # write log messages to console from 'ERROR' level
        log5 = logger.getLogger('%s-logger5' % __name__, filename='test5', to_console=True, loglevel='ERROR')

        for idx in range(100):


            log1.debug('Test1 Debug Msg - {} : not to console'.format(idx))
            log1.info('Test1 Info Msg - {} : to console'.format(idx))
            log1.warning('Test1 Warning Msg - {} : to console'.format(idx))
            log1.error('Test1 Error Msg - {} : to console'.format(idx))
            log1.critical('Test1 Critical Msg - {} : to console'.format(idx))

            log2.debug('Test2 Debug Msg - {} : not to file and console'.format(idx))
            log2.info('Test2 Info Msg - {} : to file'.format(idx))
            log2.warning('Test2 Warning Msg - {} : to file'.format(idx))
            log2.error('Test2 Error Msg - {} : to file'.format(idx))
            log2.critical('Test2 Critical Msg - {} : to file'.format(idx))

        log3.debug('Test3 Debug Msg : not to console and file')
        log3.info('Test3 Info Msg : to file')
        log3.warn('Test3 Warning Msg : to file')
        log3.error('Test3 Error Msg : to file')
        log3.critical('Test3 Critical Msg : to file')


        log4.debug('Test4 Debug Msg : to file')
        log4.info('Test4 Info Msg : to file')
        log4.warn('Test4 Warning Msg : to file')
        log4.error('Test4 Error Msg : to file')
        log4.critical('Test4 Critical Msg : to file')

        log5.debug('Test5 Debug Msg : not to console')
        log5.info('Test5 Info Msg : not to console')
        log5.warn('Test5 Warn Msg : not to console')
        log5.error('Test5 Error Msg : to console')
        log5.critical('Test5 Critical Msg : to console')

        try:
            raise Exception('Test Error')
        except Exception as ex:
            log5.error('Test5 Error Msg : to console ', exc_info=False)

if __name__ == '__main__':
    unittest.main()
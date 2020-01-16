# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import time
from urllib import request
from urllib import error as url_error

from pyticas import cfg
from pyticas.logger import getLogger

DEFAULT_TIMEOUT = 30
MAX_TRY_NUM = 5

def get_url_opener(remote_file, timeout=None):
    """

    :type remote_file: str
    :type timeout: int
    :rtype:
    """
    if (remote_file.startswith('https:') and cfg.PROXIES.get('https')
        or remote_file.startswith('http:') and cfg.PROXIES.get('http')):
        proxy = request.ProxyHandler(cfg.PROXIES)
        opener = request.build_opener(proxy)
        request.install_opener(opener)

    return request.urlopen(remote_file, timeout=timeout)


def file_download(remote_file, n_try=1, timeout=None):
    """

    :type remote_file: str
    :type n_try: int
    :type timeout: int
    :rtype: (str, Union(url_error.URLError, ConnectionResetError))
    """
    logger = getLogger(__name__)
    timeout = timeout or DEFAULT_TIMEOUT

    try:
        with get_url_opener(remote_file) as res:
            return res.read(), None
    except url_error.HTTPError as e:
        logger.debug('Could not get the remote file : %s (reason=%s, code=%s)'.format(remote_file, str(e.reason), e.code))
        return None, e
    except url_error.URLError as e:
        logger.critical('Could not connect to the remote file : %s (reason=%s)'.format(remote_file, str(e.reason)))
        return None, e
    except ConnectionResetError as e:
        logger.critical('HTTP Connection has been reset : %s (code=%s)'.format(remote_file, e.errno))
        if n_try <= MAX_TRY_NUM:
            logger.critical('Retrying...')
            time.sleep(1)
            return file_download(remote_file, n_try=n_try+1, timeout=timeout)
        return None, e
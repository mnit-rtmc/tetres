# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import shutil
import errno

def write_tpl(tpl_folder_path):
    """

    :type tpl_folder_path: str
    """
    if not os.path.exists(tpl_folder_path):
        os.makedirs(tpl_folder_path)

    ssl_path = os.path.join(tpl_folder_path, 'ssl')
    if not os.path.exists(ssl_path):
        os.makedirs(ssl_path)

    _copy_file('__init__.py', tpl_folder_path)
    _copy_file('server.py', tpl_folder_path)
    _copy_file('myapp', tpl_folder_path)

def _copy_file(src_file_name, tpl_folder_path):
    cur_path = os.path.dirname(__file__)
    src = os.path.join(cur_path, src_file_name)
    dest = os.path.join(tpl_folder_path, src_file_name)
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)
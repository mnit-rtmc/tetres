# -*- coding: utf-8 -*-
from concurrent.futures import process

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import subprocess

def insert_data(DATA_DIR, already=None):
    for f in os.listdir(DATA_DIR):
        if not f.endswith('.txt'):
            continue
        if already and f in already:
            print('!! already inserted file "%s" !!' % f)
            continue
        file = os.path.join(DATA_DIR, f)
        fields = ['site_id', 'sen_id', 'dtime', 'cond', 'temp', 'frz_temp', 'chem', 'chem_pct', 'depth',
                  'ice_pct', 'salinity', 'conductivity', 'blackice_signal', 'error']
        cols = ', '.join(fields)
        params = [r'C:\Program Files\PostgreSQL\9.4\bin\psql.exe',
                  '-U',
                  'postgres',
                  '-d',
                  'rwis',
                  '-c',
                  '\copy surface (%s) from \'%s\' DELIMITER \'|\' CSV HEADER' % (cols, file)]
        print(' '.join(params))
        p = subprocess.Popen(
            params, universal_newlines=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1).communicate()

if __name__ == '__main__':
    SF_DATA_DIR = "Z:\\RWIS DATA\\surface"
    insert_data(SF_DATA_DIR, [])
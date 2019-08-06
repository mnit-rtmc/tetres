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
        fields = ['site_id', 'dtime', 'temp', 'temp_alt', 'temp_max', 'temp_min', 'dew_point', 'rh', 'pc_type', 'pc_intens',
                  'pc_rate', 'pc_accum', 'pc_accum_10min', 'pc_start_dtime', 'pc_end_dtime', 'pc_past_1hour', 'pc_past_3hours',
                  'pc_past_6hours', 'pc_past_12hours', 'pc_past_24hours', 'pc_time_since', 'wet_build_temp', 'vis_distance',
                  'vis_situation', 'barometric', 'wnd_spd_avg', 'wnd_spd_gust', 'wnd_dir_avg', 'wnd_dir_gust']
        cols = ', '.join(fields)
        params = [r'C:\Program Files\PostgreSQL\9.4\bin\psql.exe',
                  '-U',
                  'postgres',
                  '-d',
                  'rwis',
                  '-c',
                  '\copy atmospheric (%s) from \'%s\' DELIMITER \'|\' CSV HEADER' % (cols, file)]
        print(' '.join(params))
        p = subprocess.Popen(
            params, universal_newlines=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1).communicate()

if __name__ == '__main__':
    ATM_DATA_DIR = "Z:\\RWIS DATA"
    insert_data(ATM_DATA_DIR, ['atmospheric_200601_6.txt'])
# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


import os, sys, traceback
import csv
import time
import sqlite3
import codecs

def create_atmospheric_table(c):
    c.execute('''CREATE TABLE "atmospheric" (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`site_id`	INTEGER,
	`dtime`	datetime,
	`temp`	INTEGER,
	`temp_alt`	INTEGER,
	`temp_max`	REAL,
	`temp_min`	TEXT,
	`dew_point`	TEXT,
	`rh`	INTEGER,
	`pc_type`	INTEGER,
	`pc_intens`	INTEGER,
	`pc_rate`	INTEGER,
	`pc_accum`	INTEGER,
	`pc_accum_10min`	INTEGER,
	`pc_start_dtime`	datetime,
	`pc_end_dtime`	datetime,
	`pc_past_1hour`	INTEGER,
	`pc_past_3hours`	INTEGER,
	`pc_past_6hours`	INTEGER,
	`pc_past_12hours`	INTEGER,
	`pc_past_24hours`	INTEGER,
	`pc_time_since`	INTEGER,
	`wet_build_temp`	INTEGER,
	`vis_distance`	INTEGER,
	`vis_situation`	INTEGER,
	`barometric`	INTEGER,
	`wnd_spd_avg`	INTEGER,
	`wnd_spd_gust`	INTEGER,
	`wnd_dir_avg`	INTEGER,
	`wnd_dir_gust`	INTEGER
)''')
    c.execute('''CREATE INDEX AtmoLookUpIndex1 ON atmospheric(site_id, dtime)''')

try:
    create_atmospheric_table()
except:
    pass

def insert_data(DATA_DIR, DB_FILE_FMT):


    n_col = 29
    already = []
    for f in os.listdir(DATA_DIR):
        if not f.endswith('.txt'):
            continue
        if f in already:
            print('!! already inserted file "%s" !!' % f)
            continue

        year = f.split('_')[1][:4]

        DB_FILE = DB_FILE_FMT.replace('<year>', year)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        try:
            create_atmospheric_table(c)
        except:
            pass

        filepath = os.path.join(DATA_DIR, f)

        data_initial = open(filepath, "r")
        creader = csv.reader((line.replace('\0','') for line in data_initial), delimiter="|")

        is_different_type = False
        print('Start for %s' % f)
        for ridx, row in enumerate(creader):
            if not row:
                print('==> ', row)
                print('  - no data : %d line' % ridx)
                continue
            if ridx == 1 and len(row) != n_col:
                is_different_type = True
                break
            to_db = row
            if ridx == 0:
                continue
            try:
                c.execute("INSERT INTO atmospheric (site_id, dtime, temp, temp_alt, temp_max, temp_min, dew_point, rh, pc_type, pc_intens, pc_rate, pc_accum, pc_accum_10min, pc_start_dtime, pc_end_dtime, pc_past_1hour, pc_past_3hours, pc_past_6hours, pc_past_12hours, pc_past_24hours, pc_time_since, wet_build_temp, vis_distance, vis_situation, barometric, wnd_spd_avg, wnd_spd_gust, wnd_dir_avg, wnd_dir_gust) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",to_db)
            except Exception as ex:
                print('  - error on inserting : ', ridx, '>>', row)
                print("Exception in user code:")
                print('-'*60)
                traceback.print_exc(file=sys.stdout)
                print('-'*60)



        if is_different_type:
            print('  - "%s" has different file format' % f)
        else:
            conn.commit()

        print('Done for %s' % f)


def search_test(c):
    sql = "select * from atmospheric where site_id=330096 AND dtime >= '2008-01-01 00:00:00' and dtime <= '2008-01-02 00:00:00' "
    c.execute(sql)
    for row in c.fetchall():
        print('=> ', row)

if __name__ == '__main__':
    start_time = time.time()
    insert_data()
    print("--- inserting data : %s seconds ---" % (time.time() - start_time))

    #
    # start_time = time.time()
    # search_test()
    # print("--- search : %s seconds ---" % (time.time() - start_time))
# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import time
import os
import csv
import sqlite3


def create_surface_table(c):
    c.execute('''CREATE TABLE `surface` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`site_id`	INTEGER NOT NULL,
	`sen_id`	INTEGER NOT NULL,
	`dtime`	Datetime,
	`cond`	INTEGER,
	`temp`	INTEGER,
	`frz_temp`	INTEGER,
	`chem`	INTEGER,
	`chem_pct`	INTEGER,
	`depth`	INTEGER,
	`ice_pct`	INTEGER,
	`salinity`	INTEGER,
	`conductivity`	INTEGER,
	`blackice_signal`	INTEGER,
	`error`	INTEGER
)''')
    c.execute('''CREATE INDEX SurfaceLookUpIndex1 ON surface(site_id, sen_id, dtime)''')

def insert_data(DATA_DIR, DB_FILE_FMT):
    #DATA_DIR = "Z:\\RWIS DATA\\surface"
    already = []
    #already = ['surfacehist_2006.txt']
    for f in os.listdir(DATA_DIR):
        if not f.endswith('.txt'):
            continue
        if f in already:
            print('!! already inserted file "%s" !!' % f)
            continue

        year = f.replace('.txt', '').split('_')[-1]
        DB_FILE = DB_FILE_FMT.replace('<year>', year)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        create_surface_table(c)

        filepath = os.path.join(DATA_DIR, f)
        data_initial = open(filepath, "rU")
        creader = csv.reader((line.replace('\0','') for line in data_initial), delimiter="|")
        is_different_type = False
        print('Start for %s' % f)
        for ridx, row in enumerate(creader):
            if len(row) != 14:
                is_different_type = True
                break
            to_db = row
            if ridx == 0:
                continue
            c.execute("INSERT INTO surface (site_id, sen_id, dtime, cond, temp, frz_temp, chem, chem_pct, depth, ice_pct, salinity, conductivity, blackice_signal, error) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",to_db)
        conn.commit()
        if is_different_type:
            print('  - "%s" has different file format' % f)
        print('Done for %s' % f)


def test_search(c):
    sql = "select * from surface where site_id=330096 AND sen_id=0 AND dtime >= '2008-01-01 00:00:00' and dtime <= '2008-01-02 00:00:00' "
    c.execute(sql)
    for row in c.fetchall():
        print('=> ', row)

if __name__ == '__main__':
    start_time = time.time()
    insert_data()
    print("--- inserting data : %s seconds ---" % (time.time() - start_time))

    # start_time = time.time()
    # test_search()
    # print("--- search : %s seconds ---" % (time.time() - start_time))
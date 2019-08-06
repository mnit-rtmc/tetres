# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import time

from pyticas_rwis.sqlite_frag import atm

from pyticas_rwis.db.old.sqlite_frag import sf

if __name__ == '__main__':
    DATA_DIR = "Z:\\RWIS DATA\\surface"

    start_time = time.time()
    sf.insert_data(DATA_DIR, "D:\\RIWS-<year>.sqlite3")

    print("--- surface inserting data : %s seconds ---" % (time.time() - start_time))

    DATA_DIR = "Z:\\RWIS DATA\\"
    start_time = time.time()
    atm.insert_data(DATA_DIR, "D:\\RIWS-<year>.sqlite3")
    print("--- atm inserting data : %s seconds ---" % (time.time() - start_time))


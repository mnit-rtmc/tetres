# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import csv
import json
import math
import os
import pickle
from stat import S_ISREG, ST_MODE

def file_list(dirpath):
    entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
    entries = ((os.stat(path), path) for path in entries)
    entries = (path for stat, path in entries if S_ISREG(stat[ST_MODE]))
    return sorted(entries)

def get_file_contents(filepath):
    with open(filepath, 'r') as f:
        return f.read()

def save_file_contents(filepath, contents):
    with open(filepath, 'w') as f:
        f.write(contents)

def numbered_filename(filepath):
    fparts = os.path.splitext(filepath)
    path = fparts[0]
    ext = fparts[1]

    def _filepath(num):
        return '%s (%d)%s' % (path, num, ext)

    cur_filepath = filepath
    n = 1
    while True:
        if not os.path.exists(cur_filepath):
            break
        cur_filepath = _filepath(n)
        n += 1

    return cur_filepath

# def step_round(x, base=5):
#     return int(base * round(float(x)/base))

# def save_CSV(filepath, dataList):
#     with open(filepath, 'wb') as csvfile:
#         writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
#         for line in dataList:
#             writer.writerow(line)

# def to_2D_list(dataList, col):
#     _2DList = []
#     rows = int(math.ceil(len(dataList) / col))
#     for r in range(rows):
#         row = []
#         for c in range(col):
#             idx = r * col + c
#             if idx >= len(dataList):
#                 break
#             row.append(dataList[idx])
#         _2DList.append(row)
#     return _2DList

# def isset(field, dic):
#     try:
#         dic[field]
#     except NameError:
#         return False
#
#     return True
        
# def save_object(obj, filepath):
#     with open(filepath, 'wb') as output:
#         pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)
#
# def load_object(filepath):
#     return pickle.load_data(open(filepath, 'rb'))
#
# def save_json_object(obj, filepath):
#     with open(filepath, 'w') as fp:
#         json.dump(obj, fp)
#
# def load_json_object(filepath):
#     with open(filepath) as data_file:
#         return json.load_data(data_file)

# def file_name_list(dirpath):
#     return [ os.path.basename(fpath) for fpath in file_list(dirpath) ]

# def excel_column_name(col):
#     excelCol = str()
#     div = col
#     while div:
#         (div, mod) = divmod(div-1, 26)
#         excelCol = chr(mod + 65) + excelCol
#
#     return excelCol



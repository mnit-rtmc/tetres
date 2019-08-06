# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import copy
from pyticas import cfg

def imputation(data, **kwargs):
    """
    :type data: list[list[float]]
    :return:
    """
    # data structure
    # ---------------
    #
    # data = [
    #               [ d11, d12, d13, d14 ], # of rnode1
    #               [ d21, d22, d23, d24 ], # of rnode2
    #               [ d31, d32, d33, d34 ], # of rnode3
    #               ...
    #           ]
    imp_data = copy.deepcopy(data)
    n_rows = len(imp_data)
    n_cols = len(imp_data[0])

    for r in range(n_rows):
        for c in range(n_cols):
            v = imp_data[r][c]
            if v != cfg.MISSING_VALUE: continue
            (up_data, dn_data) = find_up_dn_data(r, c, imp_data)
            if cfg.MISSING_VALUE not in [up_data, dn_data]:
                imp_data[r][c] = sum([up_data, dn_data])/2
            elif up_data != cfg.MISSING_VALUE:
                imp_data[r][c] = up_data
            elif dn_data != cfg.MISSING_VALUE:
                imp_data[r][c] = dn_data

    return imp_data

def find_up_dn_data(cur_r, cur_c, data):
    # dt_data = [
    #               [ d11, d12, d13, d14 ], # of rnode1
    #               [ d21,  X, d23, d24 ], # of rnode2
    #               [ d31, d32, d33, d34 ], # of rnode3
    #               ...
    #           ]
    # when (2,2) is missing,
    # find (1,2) and (3,2)

    up_data = -1
    for r in range(cur_r-1, -1, -1):
        if data[r][cur_c] != cfg.MISSING_VALUE:
            up_data = data[r][cur_c]
            break

    dn_data = -1
    for r in range(cur_r+1, len(data)):
        if data[r][cur_c] != cfg.MISSING_VALUE:
            dn_data = data[r][cur_c]
            break

    return (up_data, dn_data)
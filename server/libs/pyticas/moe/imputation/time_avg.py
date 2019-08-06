# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import copy
from pyticas import cfg

ALLOWED_TIME_DIFF = 5

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
    allowed_time_diff = kwargs.get('allowed_time_diff', None)
    for r in range(n_rows):
        for c in range(n_cols):
            v = imp_data[r][c]
            if v != cfg.MISSING_VALUE:
                continue
            (prev_data, next_data) = find_prev_next_data(r, c, imp_data, allowed_time_diff=allowed_time_diff)
            if cfg.MISSING_VALUE not in [prev_data, next_data]:
                imp_data[r][c] = sum([prev_data, next_data])/2
            elif prev_data != cfg.MISSING_VALUE:
                imp_data[r][c] = prev_data
            elif next_data != cfg.MISSING_VALUE:
                imp_data[r][c] = next_data

    return imp_data

def find_prev_next_data(cur_r, cur_c, data, allowed_time_diff=ALLOWED_TIME_DIFF):
    # dt_data = [
    #               [ d11, d12, d13, d14 ], # of rnode1
    #               [ d21,  X, d23, d24 ], # of rnode2
    #               [ d31, d32, d33, d34 ], # of rnode3
    #               ...
    #           ]
    # when (2,2) is missing,
    # find (1,2) and (3,2)

    prev_data, prev_idx = -1, 0
    for c in range(cur_c-1, -1, -1):
        if data[cur_r][c] != cfg.MISSING_VALUE:
            prev_data = data[cur_r][c]
            prev_idx = c
            break

    next_data, next_idx = -1, len(data[0])-1
    for c in range(cur_c+1, len(data[0])):
        if data[cur_r][c] != cfg.MISSING_VALUE:
            next_data = data[cur_r][c]
            next_idx = c
            break

    if next_idx - prev_idx > allowed_time_diff:
        return (-1, -1)

    return (prev_data, next_data)
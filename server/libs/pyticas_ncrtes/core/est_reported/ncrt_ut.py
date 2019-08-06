# -*- coding: utf-8 -*-

import numpy as np
from pyticas_ncrtes.core import setting

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

def determine(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: int
    """

    _check_if_recovered_before_wnffs(edata)
    # _check_if_wnffs_is_in_recoverying(edata)
    edata.ncrt = edata.wn_ffs_idx


def _check_if_wnffs_is_in_recoverying(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type op1: int
    :type op2: int
    :rtype: (int, int)
    """
    wn_ffs_idx = edata.wn_ffs_idx
    w = setting.INTV30MIN
    pus = edata.sus[wn_ffs_idx-w:wn_ffs_idx]
    nus = edata.sus[wn_ffs_idx:wn_ffs_idx+w]
    pu = np.mean(pus)
    nu = np.mean(nus)
    if nu - pu > 5:
        for idx in range(wn_ffs_idx, edata.n_data):
            if edata.sus[idx] < edata.sus[idx+1]:
                wn_ffs_idx = idx +1
            else:
                break
    edata.wn_ffs_idx = wn_ffs_idx


def _check_if_recovered_before_wnffs(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type op1: int
    :type op2: int
    :rtype: (int, int)
    """
    op2 = edata.wn_ffs_idx
    op1 = edata.search_start_idx

    op1, op2 = _adjust_recovery_interval(edata, op1, op2)

    edata.wn_ffs_idx = op2


def _adjust_recovery_interval(edata, op1, op2):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type op1: int
    :type op2: int
    :rtype: (int, int)
    """
    if not op1 or not op2 or edata.is_recovered_at_lost:
        return op1, op2

    tks, tus = edata.merged_sks[op1:op2], edata.merged_sus[op1:op2]
    wh1 = np.where(tus >= edata.wn_ffs * 0.9)[0]
    if not any(wh1):
        return op1, op2

    t_recovered_idx = wh1[0] + op1
    tks, tus = edata.merged_sks[t_recovered_idx:op2], edata.merged_sus[t_recovered_idx:op2]
    wh2 = np.where( (tus < edata.wn_ffs * 0.8) & (tks > 20))[0]
    if len(wh2) > setting.INTV30MIN:
        _op2 = np.argmax(edata.merged_sus[t_recovered_idx:t_recovered_idx+setting.INTV30MIN]).item() + t_recovered_idx
        if _op2 < op2:
            minu_idx = np.argmin(edata.merged_sus[_op2:op2]).item() + _op2
            _op2k = np.mean(edata.merged_sks[_op2-setting.INTV15MIN:_op2+setting.INTV15MIN])
            minu_k = np.mean(edata.merged_sks[minu_idx-setting.INTV15MIN:minu_idx+setting.INTV15MIN])
            # if minu_k - _op2k > 3:
            if minu_k > 20:
                print('=> update ncrt (1) : ', t_recovered_idx, op2, '->', _op2)
                return op1, _op2

    tks, tus = edata.merged_sks[op1:op2], edata.merged_sus[op1:op2]
    wh1 = np.where(tus >= edata.wn_ffs * 0.95)[0]
    if not any(wh1):
        return op1, op2

    t_recovered_idx = wh1[0] + op1
    tks, tus = edata.merged_sks[t_recovered_idx:op2], edata.merged_sus[t_recovered_idx:op2]
    wh2 = np.where( tus < edata.wn_ffs * 0.8)[0]
    if not any(wh2):
        _op2 = np.argmax(edata.merged_sus[t_recovered_idx:t_recovered_idx+setting.INTV30MIN]).item() + t_recovered_idx
        if _op2 < op2:
            minu_idx = np.argmin(edata.merged_sus[_op2:op2]).item() + _op2
            _op2k = np.mean(edata.merged_sks[_op2-setting.INTV15MIN:_op2+setting.INTV15MIN])
            minu_k = np.mean(edata.merged_sks[minu_idx-setting.INTV15MIN:minu_idx+setting.INTV15MIN])
            # if minu_k - _op2k > 3:
            if minu_k > 20:
                print('=> update ncrt (2) : ', t_recovered_idx, op2, '->', _op2)
                return op1, _op2

    return op1, op2
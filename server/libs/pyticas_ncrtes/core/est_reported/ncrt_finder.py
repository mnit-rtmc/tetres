# -*- coding: utf-8 -*-
from pyticas_ncrtes.core.est.old import ncrt_uk, ncrt_ut

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

def determine(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: int
    """
    if edata.wn_ffs and edata.normal_func and edata.normal_func.is_valid():
        return ncrt_uk.determine(edata)
    else:
        return ncrt_ut.determine(edata)

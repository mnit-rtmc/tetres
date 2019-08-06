# -*- coding: utf-8 -*-
from pyticas_ncrtes.core.est.old import wnffs_qk, wnffs_ut

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def determine(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: (bool, float)
    """
    wn_ffs = None


    is_found, wn_ffs = wnffs_qk.determine(edata)
    if not is_found and not edata.should_wn_uk_without_ffs:
        is_found, wn_ffs = wnffs_ut.determine(edata)

    # make wet-normal U-K function
    if edata.normal_func and edata.normal_func.is_valid() and edata.should_wn_uk_without_ffs:
        edata.make_wet_normal_pattern_without_wnffs()
    elif is_found and edata.normal_func and edata.normal_func.is_valid():
        wnffs_idx, k_at_wnffs = _k_at_wn_ffs(edata, wn_ffs)
        edata.make_wet_normal_pattern(wn_ffs, k_at_wnffs)

    return (is_found, wn_ffs)


def _k_at_wn_ffs(edata, wn_ffs):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type wn_ffs: float
    :rtype: int, float
    """
    if not wn_ffs:
        return None, None

    # find k at wn_ffs
    k_at_wn_ffs, wn_sidx = None, None
    for idx in range(edata.search_start_idx, len(edata.ks)):
        if edata.merged_sus[idx] >= wn_ffs:
            wn_sidx = idx
            k_at_wn_ffs = edata.sks[idx]
            break

    for idx in range(edata.search_start_idx, len(edata.ks)):
        if edata.merged_sus[idx] >= wn_ffs - 5:
            wn_sidx = idx
            k_at_wn_ffs = edata.sks[idx]
            break

    return wn_sidx, k_at_wn_ffs
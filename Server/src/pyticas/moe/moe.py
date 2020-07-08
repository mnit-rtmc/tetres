# -*- coding: utf-8 -*-

"""
Traffic Measurement Module
"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import importlib

from pyticas.moe import moe_helper
from pyticas.moe.imputation import spatial_avg
from pyticas.ttypes import Period, RNodeData

THREAD_LIMIT_PER_CALL = 5
VIRTUAL_RNODE_DISTANCE = moe_helper.VIRTUAL_RNODE_DISTANCE


def speed(route, prd, **kwargs):
    """
    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return _do_moe(route, prd, 'speed', **kwargs)


def speed_md(route, prds, **kwargs):
    """
    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'speed', **kwargs)


def density(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return _do_moe(route, prd, 'density', **kwargs)


def density_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'density', **kwargs)


def volume(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return _do_moe(route, prd, 'volume', **kwargs)


def volume_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'volume', **kwargs)


def average_flow(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return _do_moe(route, prd, 'average_flow', **kwargs)


def average_flow_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'average_flow', **kwargs)


def total_flow(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return _do_moe(route, prd, 'total_flow', **kwargs)


def total_flow_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'total_flow', **kwargs)


def occupancy(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return _do_moe(route, prd, 'occupancy', **kwargs)


def occupancy_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'occupancy', **kwargs)


def scan(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return _do_moe(route, prd, 'scan', **kwargs)


def estimate_scan_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'scan', **kwargs)


def travel_time(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return _do_moe(route, prd, 'tt', **kwargs)


def travel_time_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'tt', **kwargs)


def vmt(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return _do_moe(route, prd, 'vmt', **kwargs)


def vmt_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'vmt', **kwargs)


def vht(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return _do_moe(route, prd, 'vht', **kwargs)


def vht_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'vht', **kwargs)


def dvh(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return _do_moe(route, prd, 'dvh', **kwargs)


def dvh_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'dvh', **kwargs)


def lvmt(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[list[RNodeData]]
    """
    return _do_moe(route, prd, 'lvmt', **kwargs)


def lvmt_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'lvmt', **kwargs)


# faverolles 1/22/2020: Added For TICAS MOE Integration
def uvmt(route, prd, **kwargs):
    """

    :param default_lane_capacity:
    :param default_critical_density:
    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[list[RNodeData]]
    """

    return _do_moe(route, prd, 'uvmt', **kwargs)


# faverolles 1/22/2020: Added For TICAS MOE Integration
def uvmt_md(route, prds, **kwargs):
    """

    :param default_lane_capacity:
    :param default_critical_density:
    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """

    return _do_moe_md(route, prds, 'uvmt', **kwargs)


def cm(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[list[RNodeData]]
    """
    return _do_moe(route, prd, 'cm', **kwargs)


def cm_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'cm', **kwargs)


def cmh(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[list[RNodeData]]
    """
    return _do_moe(route, prd, 'cmh', **kwargs)


def cmh_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'cmh', **kwargs)


def sv(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[list[RNodeData]]
    """
    return _do_moe(route, prd, 'sv', **kwargs)


def sv_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'sv', **kwargs)


def stt(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[list[RNodeData]]
    """
    return _do_moe(route, prd, 'stt', **kwargs)


def stt_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'stt', **kwargs)


def acceleration(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return _do_moe(route, prd, 'accel', **kwargs)


def acceleration_md(route, prds, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'accel', **kwargs)


def mrf(route, prd, **kwargs):
    """ Mainline and Ramp Flow Rates

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :rtype: list[RNodeData]
    """
    return _do_moe(route, prd, 'mrf', **kwargs)


def mrf_md(route, prds, **kwargs):
    """ Mainline and Ramp Flow Rates

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :rtype: list[list[RNodeData]]
    """
    return _do_moe_md(route, prds, 'mrf', **kwargs)


def _do_moe(route, prd, eval_name, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: Period
    :type eval_name: str
    :rtype: list[RNodeData]
    """
    est_module = importlib.import_module('pyticas.moe.mods.{}'.format(eval_name))
    kwargs['detector_checker'] = kwargs.get('detector_checker', route.get_detector_checker())
    return est_module.run(route, prd, **kwargs)


def _do_moe_md(route, prds, eval_name, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prds: list[Period]
    :type eval_name: str
    :rtype: list[list[RNodeData]]
    """
    return [_do_moe(route, each_prd, eval_name, **kwargs) for each_prd in prds]


def add_virtual_rnodes(results, route, **kwargs):
    """
    :type results: list[RNodeData]
    :type route: pyticas.ttypes.Route
    :rtype: list[RNodeData]
    """
    return moe_helper.add_virtual_rnodes(results, route, **kwargs)


def has_virtual_rnodes(results):
    """
    :type results: list[RNodeData]
    :rtype: boolean
    """
    return moe_helper.has_virtual_rnodes(results)


def remove_virtual_rnodes(results):
    """
    :type results: list[RNodeData]
    :rtype: list[RNodeData]
    """
    return moe_helper.remove_virtual_rnodes(results)


def accumulated_distances(results, route, **kwargs):
    """
    :type results: list[RNodeData]
    :type route: pyticas.ttypes.Route
    :rtype: list[float]
    """
    return moe_helper.accumulated_distances(results, route, **kwargs)


def imputation(res, imp_module=None, **kwargs):
    """

    :type res:
    :type imp_module: any
    :rtype: list[RNodeData]
    """
    if not imp_module:
        imp_module = spatial_avg

    _data = [res.data for res in res]
    _data = imp_module.imputation(_data, **kwargs)
    for ridx, r in enumerate(res):
        r.data = _data[ridx]
    return res


def imputation_md(ress, imp_module=None):
    """

    :type ress: list[list[RNodeData]]
    :type imp_module: module
    :rtype: list[list[RNodeData]]
    """
    for idx, res in enumerate(ress):
        ress[idx] = imputation(res, imp_module)
    return ress

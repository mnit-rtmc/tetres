# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres import cfg
from pyticas_tetres.rengine.filter.ftypes import ExtFilter, SLOT_WORKZONE
from pyticas_tetres.ttypes import LOC_TYPE


OVERLAPPED_LOC_TYPES = [LOC_TYPE.UP_OVERLAPPED.value, LOC_TYPE.DOWN_OVERLAPPED.value,
                        LOC_TYPE.INSIDE.value, LOC_TYPE.WRAP.value]
"""
item
~~~~

- type : TTIncident
- attributes :
    - distance : distance from the upstream rnode of a given route
        - negative distance : incident is located upstream of the route
        - positive distance : incident is located in the distance from the upstream rnode of the route
    - off-distance : distance from the upstream or downstream rnode of a given route
        - negative off-distance : incident is located upstream of the route
        - positive off-distance : instance is located in downstream of the route
        - 0 : incident is inside the route
"""

def _distance_checker(**kwargs):
    dn_distance_limit, up_distance_limit = _get_distance_limit(**kwargs)
    def _f(item):
        return (item.off_distance == 0
                or (item.off_distance < 0 and up_distance_limit > abs(item.off_distance))
                or (item.off_distance > 0 and dn_distance_limit > item.off_distance))
    return _f


def no_workzone(**kwargs):
    kwargs['pass_on_nodata'] = True
    kwargs['all_items_should_pass'] = True
    dn_distance_limit, up_distance_limit = _get_distance_limit(**kwargs)
    return ExtFilter(SLOT_WORKZONE, [
        lambda item: ((item.off_distance < 0 and -up_distance_limit > item.off_distance)
                            or (item.off_distance > 0 and dn_distance_limit < item.off_distance))
    ], **kwargs)


def has_workzone(**kwargs):
    return ExtFilter(SLOT_WORKZONE, [
        _distance_checker(**kwargs),
    ], **kwargs)


def loc_upstream(**kwargs):
    return _loc(1, **kwargs)


def loc_upoverlapped(**kwargs):
    return _loc(2, **kwargs)


def loc_inside(**kwargs):
    return _loc(3, **kwargs)


def loc_downstream(**kwargs):
    return _loc(4, **kwargs)


def loc_downoverlapped(**kwargs):
    return _loc(5, **kwargs)


def loc_wrap(**kwargs):
    return _loc(6, **kwargs)


def loc_overlapped(**kwargs):
    return _loc([2, 3, 5, 6], **kwargs)

def has_crossover(**kwargs):
    def _func(item):
        for f in item._workzone._features:
            if f.use_opposing_lane or f.use_opposing_lane :
                return True
        return False

    return ExtFilter(SLOT_WORKZONE, [
        _distance_checker(**kwargs),
        _func,
    ], **kwargs)


def has_closed(**kwargs):
    def _func(item):
        for f in item._workzone._features:
            if f.has_closed:
                return True
        return False
    return ExtFilter(SLOT_WORKZONE, [
        _distance_checker(**kwargs),
        _func,
    ], **kwargs)


def has_shift(**kwargs):
    def _func(item):
        for f in item._workzone._features:
            if f.has_shift:
                return True
        return False
    return ExtFilter(SLOT_WORKZONE, [
        _distance_checker(**kwargs),
        _func,
    ], **kwargs)


def closed_length(min_length, max_length, **kwargs):
    def _func(item):
        for f in item._workzone._features:
            if min_length <= f.closed_length <= max_length:
                return True
        return False

    return ExtFilter(SLOT_WORKZONE, [
        _distance_checker(**kwargs),
        _func,
    ], **kwargs)


def lane_config(origin_lanes, open_lanes, **kwargs):
    def _func(item):
        for f in item._workzone._laneconfigs:
            if f.origin_lanes == origin_lanes and  f.open_lanes == open_lanes:
                return True
        return False
    return ExtFilter(SLOT_WORKZONE, [
        _distance_checker(**kwargs),
        _func,
    ], **kwargs)



# class LOC_TYPE(enum.Enum):
#     UP = 1
#     UP_OVERLAPPED = 2
#     INSIDE = 3
#     DOWN = 4
#     DOWN_OVERLAPPED = 5
#     WRAP = 6
def _loc(loc_type, **kwargs):
    if isinstance(loc_type, list):
        loc_type = [str(wt) for wt in loc_type]
    else:
        loc_type = str(loc_type)

    def _check_loc(item):
        """
        :type item: pyticas_tetres.ttypes.TTWorkzoneInfo
        :return:
        """
        if isinstance(loc_type, list):
            # print('----- check_loc : ', item.loc_type in loc_type, ' : ', item.loc_type, loc_type)
            return str(item.loc_type) in loc_type
        else:
            return str(item.loc_type) == loc_type


    return ExtFilter(SLOT_WORKZONE, [
        _distance_checker(**kwargs),
        _check_loc
    ], **kwargs)


def _get_distance_limit(**kwargs):
    """
    :rtype: float, float
    """
    dn_distance_limit = kwargs.get('downstream_distance_limit', cfg.WZ_DOWNSTREAM_DISTANCE_LIMIT)
    up_distance_limit = kwargs.get('upstream_distance_limit', cfg.WZ_UPSTREAM_DISTANCE_LIMIT)
    return dn_distance_limit, up_distance_limit


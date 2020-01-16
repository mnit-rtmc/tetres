# -*- coding: utf-8 -*-
from pyticas_tetres.ttypes import LOC_TYPE

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.rengine.filter.ftypes import ExtFilter, SLOT_SNOWMANAGEMENT

DEFAULT_DISTANCE_LIMIT = 5
OVERLAPPED_LOC_TYPES = [LOC_TYPE.UP_OVERLAPPED.value, LOC_TYPE.DOWN_OVERLAPPED.value,
                        LOC_TYPE.INSIDE.value, LOC_TYPE.WRAP.value]


def no_snowmanagement(**kwargs):
    kwargs['pass_on_nodata'] = True
    kwargs['all_items_should_pass'] = True
    return ExtFilter(SLOT_SNOWMANAGEMENT, [
        lambda item: item.loc_type not in OVERLAPPED_LOC_TYPES,
    ], **kwargs)


def has_snowmanagement(**kwargs):
    return ExtFilter(SLOT_SNOWMANAGEMENT, [
        lambda item: item.loc_type in OVERLAPPED_LOC_TYPES,
    ], **kwargs)


# def loc_upstream(**kwargs):
#     return _loc(1, **kwargs)
#
#
# def loc_upoverlapped(**kwargs):
#     return _loc(2, **kwargs)
#
#
# def loc_inside(**kwargs):
#     return _loc(3, **kwargs)
#
#
# def loc_downstream(**kwargs):
#     return _loc(4, **kwargs)
#
#
# def loc_downoverlapped(**kwargs):
#     return _loc(5, **kwargs)
#
# def loc_wrap(**kwargs):
#     return _loc(6, **kwargs)
#
# # class LOC_TYPE(enum.Enum):
# #     UP = 1
# #     UP_OVERLAPPED = 2
# #     INSIDE = 3
# #     DOWN = 4
# #     DOWN_OVERLAPPED = 5
# #     WRAP = 6
# def _loc(ltype, **kwargs):
#     return ExtFilter(SLOT_SNOWMANAGEMENT, [
#         lambda item: item.loc_type == ltype,
#     ], **kwargs)

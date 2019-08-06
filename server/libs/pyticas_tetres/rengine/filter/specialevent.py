# -*- coding: utf-8 -*-

from pyticas_tetres.rengine.filter.ftypes import ExtFilter, SLOT_SPECIALEVENT

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

DEFAULT_DISTANCE_LIMIT = 5


def no_specialevent(**kwargs):
    kwargs['pass_on_nodata'] = True
    kwargs['all_items_should_pass'] = True
    distance_limit = _get_distance_limit(**kwargs)
    return ExtFilter(SLOT_SPECIALEVENT, [
        lambda item: item.distance > distance_limit,
    ], **kwargs)


def has_specialevent(**kwargs):
    distance_limit = _get_distance_limit(**kwargs)
    return ExtFilter(SLOT_SPECIALEVENT, [
        lambda item: item.distance <= distance_limit,
    ], **kwargs)


def type_arrival(**kwargs):
    return _type('A', **kwargs)


def type_departure(**kwargs):
    return _type('D', **kwargs)


def type_all(**kwargs):
    return _type(['A', 'D'], **kwargs)


def attendance(min_attendance, max_attendance, **kwargs):
    return ExtFilter(SLOT_SPECIALEVENT, [
        lambda item: min_attendance <= item._specialevent.attendance < max_attendance,
    ], **kwargs)


def distance(min_distance, max_distance, **kwargs):
    return ExtFilter(SLOT_SPECIALEVENT, [
        lambda item: min_distance <= item.distance < max_distance,
    ], **kwargs)


def _get_distance_limit(**kwargs):
    distance_limit = kwargs.get('distance_limit', DEFAULT_DISTANCE_LIMIT)
    return abs(distance_limit) if distance_limit else DEFAULT_DISTANCE_LIMIT


def _type(data, **kwargs):
    distance_limit = _get_distance_limit(**kwargs)

    if isinstance(data, list):
        data = [str(wt) for wt in data]
    else:
        data = str(data)

    def _check_type(item):
        """
        :type item: pyticas_tetres.ttypes.TTSpecialeventInfo
        :return:
        """
        if isinstance(data, list):
            return item.event_type in data
        else:
            return item.event_type == data

    return ExtFilter(SLOT_SPECIALEVENT, [
        lambda item: item.distance < distance_limit,
        _check_type,
    ], **kwargs)

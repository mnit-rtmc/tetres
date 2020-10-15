# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres import cfg
from pyticas_tetres.rengine.filter.ftypes import ExtFilter, SLOT_INCIDENT

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


def no_incident(**kwargs):
    kwargs['pass_on_nodata'] = True
    kwargs['all_items_should_pass'] = True
    dn_distance_limit, up_distance_limit = _get_distance_limit(**kwargs)
    return ExtFilter(SLOT_INCIDENT, [
        lambda item: ((item.off_distance < 0 and -up_distance_limit > item.off_distance)
                      or (item.off_distance > 0 and dn_distance_limit < item.off_distance))
    ], **kwargs)


def has_incident(**kwargs):
    return ExtFilter(SLOT_INCIDENT, [
        _distance_checker(**kwargs),
    ], **kwargs)


def iris_type_crash(**kwargs):
    return _iris_type('crash', **kwargs)


def iris_type_hazard(**kwargs):
    return _iris_type('hazard', **kwargs)


def iris_type_stall(**kwargs):
    return _iris_type('stall', **kwargs)


def iris_type_roadwork(**kwargs):
    return _iris_type('roadwork', **kwargs)


def classification_stall(**kwargs):
    return _classification(['stall'], **kwargs)


def classification_spinout(**kwargs):
    return _classification(['spinout'], **kwargs)


def classification_crash(**kwargs):
    return _classification(['crash'], **kwargs)


def classification_maintenance(**kwargs):
    return _classification([
        'mnpass maintenance',
        'maintenance',
    ], **kwargs)


def classification_debris(**kwargs):
    return _classification(['debris'], **kwargs)


def classification_pedestrian(**kwargs):
    return _classification(['pedestrian'], **kwargs)


def classification_animal(**kwargs):
    return _classification(['animal'], **kwargs)


def classification_wrongway(**kwargs):
    return _classification(['wrong way driver'], **kwargs)


def classification_slumper(**kwargs):
    return _classification(['slumper'], **kwargs)


def classification_fire(**kwargs):
    return _classification(['fire'], **kwargs)


def classification_medical(**kwargs):
    return _classification(['medical'], **kwargs)


def classification_lawenforcement(**kwargs):
    return _classification(['law enforcement'], **kwargs)


def classification_jumper(**kwargs):
    return _classification(['jumper'], **kwargs)


def classification_trafficcontrol(**kwargs):
    return _classification(['traffic control'], **kwargs)


def classification_test(**kwargs):
    return _classification(['test'], **kwargs)


def severity_fatal(**kwargs):
    return _type(['fatal'], **kwargs)


def severity_injury_all(**kwargs):
    f1 = severity_injury_personal(**kwargs)
    f2 = severity_injury_serious(**kwargs)

    def _check(item):
        return f1.check(item) or f2.check(item)

    return ExtFilter(SLOT_INCIDENT, [_check], **kwargs)


def severity_injury_personal(**kwargs):
    return _type(['personal inj'], **kwargs)


def severity_injury_serious(**kwargs):
    return _type(['serious injury'], **kwargs)


def severity_property_damage(**kwargs):
    return _type([
        'property damage',
        'damage to property'
    ], **kwargs)


def severity_other(**kwargs):
    f1 = severity_injury_all(**kwargs)
    f2 = severity_property_damage(**kwargs)
    f3 = severity_fatal(**kwargs)

    def _check(item):
        return not f1.check(item) and not f2.check(item) and not f3.check(item)

    return ExtFilter(SLOT_INCIDENT, [_check], **kwargs)


def impact_blocking(**kwargs):
    return _flag(['blocking'], True)


def impact_not_blocking(**kwargs):
    return _flag(['blocking'], False)


# TODO: for impact
# def impact_road_closed(**kwargs):
#     symbols = kwargs.get('symbols', '!?')
#     distance_limit = _get_distance_limit(**kwargs)
#
#     def _check_impact(item):
#         """
#         :type item: pyticas_tetres.ttrms_types.TTIncidentInfo
#         :rtype:
#         """
#         incident = item.get_incident()
#         impact = incident.impact
#         if not impact:
#             return False
#
#         from pyticas.infra import Infra
#         infra = Infra.get_infra()
#
#         corr = infra.get_corridor(incident.road, incident.direction)
#         up_node, dn_node = infra.geo.find_updown_rnodes(incident.lat, incident.lon, corr.stations)
#         infra.geo.nearby_rnode()
#         len_impact = len(impact)
#
#         if up_node and up_node.lanes == len_impact - 2:
#
#         # count = sum([impact.count(s) for s in symbols])
#         return count == len(impact)
#
#     return ExtFilter(SLOT_INCIDENT, [
#         lambda item: 0 <= item.off_distance <= distance_limit,
#         _check_impact
#     ], **kwargs)


def impact_lane_closed(**kwargs):
    return iris_impact_blocked(1, 'eq', **kwargs)


def impact_two_plus_lane_closed(**kwargs):
    return iris_impact_blocked(2, 'gte', **kwargs)


def off_distance(distance_limit=None, **kwargs):
    # faverolles 12/27/2019: ??? not defined anywhere
    # distance_limit = abs(distance_limit) if distance_limit else DEFAULT_DOWNSTREAM_DISTANCE_LIMIT
    distance_limit = abs(distance_limit) if distance_limit else 0
    return ExtFilter(SLOT_INCIDENT, [
        lambda item: -distance_limit <= item.off_distance <= distance_limit,
    ], **kwargs)


def loc_upstream(**kwargs):
    distance_limit = _get_distance_limit(**kwargs)
    return ExtFilter(SLOT_INCIDENT, [
        lambda item: 0 <= item.off_distance <= distance_limit,
        lambda item: item.distance < 0,
    ], **kwargs)


def loc_inside(**kwargs):
    distance_limit = _get_distance_limit(**kwargs)
    return ExtFilter(SLOT_INCIDENT, [
        lambda item: 0 <= item.off_distance <= distance_limit,
        lambda item: item.off_distance == 0,
    ], **kwargs)


def loc_downstream(**kwargs):
    distance_limit = _get_distance_limit(**kwargs)
    return ExtFilter(SLOT_INCIDENT, [
        lambda item: 0 <= item.off_distance <= distance_limit,
        lambda item: item.off_distance > 0,
    ], **kwargs)


def has_blocking_in_iris_impact(op='gt', **kwargs):
    return iris_impact_blocked(0, op, **kwargs)


def no_blocking_in_iris_impact(**kwargs):
    return iris_impact_blocked(0, 'eq', **kwargs)


def iris_impact_blocked(n, op='eq', **kwargs):
    """ 'n' lanes are blocked ?

    Caution:
        number of blocked lanes includes shoulder

    Args:
        op : can be 'eq', 'gt', 'gte', 'lt', 'lte'

    :param int n: number of blocked lanes
    :param str op: operator
    """
    symbols = kwargs.get('symbols', '!?')

    def _check_impact(item):
        """

        :type item: pyticas_tetres.ttypes.TTIncidentInfo
        :rtype:
        """
        impact = item._incident.impact
        if not impact:
            return False
        count = sum([impact.count(s) for s in symbols])
        if op == 'eq':
            return count == n
        elif op == 'gt':
            return count > n
        elif op == 'gte':
            return count >= n
        elif op == 'lt':
            return count < n
        elif op == 'lte':
            return count <= n
        else:
            raise Exception('Not supported operator')

    return ExtFilter(SLOT_INCIDENT, [
        _distance_checker(**kwargs),
        _check_impact
    ], **kwargs)


def _iris_type(itype, **kwargs):
    distance_limit = _get_distance_limit(**kwargs)
    return ExtFilter(SLOT_INCIDENT, [
        _distance_checker(**kwargs),
        lambda
            item: item._incident._incident_type.iris_class and item._incident._incident_type.iris_class.lower() == itype.lower(),
    ], **kwargs)


def _classification(cls_strings, **kwargs):
    """

    :type cls_strings: list[str]
    :rtype:
    """
    return _has_attr('classification', cls_strings, **kwargs)


def _type(type_strings, **kwargs):
    """

    :type type_strings: list[str]
    :rtype:
    """
    return _has_attr('eventtype', type_strings, **kwargs)


def _flag(flag_names, target_value, **kwargs):
    """

    :type flag_names: list[str]
    :type target_value: bool
    :rtype: callable
    """

    def _check(item):
        """

        :type item: pyticas_tetres.ttypes.TTIncidentInfo
        :rtype:
        """
        for fn in flag_names:
            if getattr(item._incident._incident_type, fn, False) == target_value:
                return True
        return False

    return ExtFilter(SLOT_INCIDENT, [
        _distance_checker(**kwargs),
        _check
    ], **kwargs)


def _has_attr(attr_name, target_strings, **kwargs):
    """

    :type target_strings: list[str]
    :rtype:
    """

    def _check_etype(item):
        """

        :type item: pyticas_tetres.ttypes.TTIncidentInfo
        :rtype:
        """
        etype = getattr(item._incident._incident_type, attr_name, '').lower()
        if not attr_name:
            return False
        for ts in target_strings:
            if ts.lower() in etype:
                return True
        return False

    return ExtFilter(SLOT_INCIDENT, [
        _distance_checker(**kwargs),
        _check_etype
    ], **kwargs)


def _get_distance_limit(**kwargs):
    """
    :rtype: float, float
    """
    dn_distance_limit = kwargs.get('downstream_distance_limit', cfg.INCIDENT_DOWNSTREAM_DISTANCE_LIMIT)
    up_distance_limit = kwargs.get('upstream_distance_limit', cfg.INCIDENT_UPSTREAM_DISTANCE_LIMIT)
    return dn_distance_limit, up_distance_limit

# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.rengine.filter.ftypes import SLOT_WEATHER, ExtFilter, And_, Or_


def normal_explicit(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _type(0, **kwargs)


def normal_implicit(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.IExtFilter
    """
    return And_(_type([0, 9, 99], **kwargs),  # including Unknown, Missing
                ExtFilter(SLOT_WEATHER, [lambda item: item._weather.precip in [0, None, '']], **kwargs))


def has_weather_explicit(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _type([1, 2, 3, 4, 5, 6, 7, 8])


def has_weather_implicit(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.IExtFilter
    """
    return Or_(_type([1, 2, 3, 4, 5, 6, 7, 8], **kwargs),
               ExtFilter(SLOT_WEATHER, [lambda item: item._weather.precip not in [0, None, '']], **kwargs))


# INTENSITY_TYPES = {
#     0 : "Not Reported",
#     1 : "Light",
#     2 : "Moderate or Not Reported",
#     3 : "Heavy",
#     4 : "Vicinity",
#     9 : "Missing",
# }

def intensity_not_reported(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _intensity(0, **kwargs)


def intensity_light(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _intensity(1, **kwargs)


def intensity_moderate(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _intensity(2, **kwargs)


def intensity_heavy(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _intensity(3, **kwargs)


def intensity_vicinity(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _intensity(9, **kwargs)


def intensity_unknown(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _intensity(9, **kwargs)


# see : http://www.theweatherprediction.com/preciptypes/
# PRECIP_TYPES = {
#     0 : 'No Precip',
#     1 : 'Drizzle',
#     2 : 'Rain',
#     3 : 'Snow',
#     4 : 'Snow Grains',
#     5 : 'Ice Crystals',
#     6 : 'Ice Pellets',
#     7 : 'Hail',
#     8 : 'Small Hail and/or Snow Pellets',
#     9 : 'Unknown',
#     99 : 'Missing'
# }

def type_drizzle(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _type([1], **kwargs)


def type_rain(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _type([2], **kwargs)


def type_snow(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _type([3, 4], **kwargs)


def type_ice_crystals_pellets(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _type([5, 6], **kwargs)


def type_hail(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _type([7, 8], **kwargs)


def type_unknown(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _type([9, 99], **kwargs)


def type_clear(**kwargs):
    """
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    return _type([0], **kwargs)


def precip(min_precip, max_precip, **kwargs):
    """

    :type min_precip: float
    :type max_precip: float
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    wtypes = [1, 2, 3, 4, 5, 6, 7, 8]
    return ExtFilter(SLOT_WEATHER, [
        lambda item: (min_precip <= item._weather.precip <= max_precip and
                      item._weather.precip_type in wtypes)
    ], **kwargs)


def _type(wtypes, **kwargs):
    """

    :type wtypes: Union(list, object)
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    # `precip_type` is saved as string into database
    if isinstance(wtypes, list):
        wtypes = [str(wt) for wt in wtypes]
    else:
        wtypes = str(wtypes)

    def _check_type(item):
        """
        :type item: pyticas_tetres.db.model.TTWeather
        :return:
        """
        if isinstance(wtypes, list):
            return item._weather.precip_type in wtypes
        else:
            return item._weather.precip_type == wtypes

    return ExtFilter(SLOT_WEATHER, [_check_type], **kwargs)


def _intensity(intensities, **kwargs):
    """

    :type intensities: Union(list, object)
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    # `intensity` is saved as string into database
    if isinstance(intensities, list):
        intensities = [str(intensity) for intensity in intensities]
    else:
        intensities = str(intensities)

    return ExtFilter(SLOT_WEATHER, [
        lambda item: (item._weather.precip_intensity in intensities) if isinstance(intensities, list)
        else (item._weather.precip_intensity == intensities)
    ], **kwargs)

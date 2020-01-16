# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.ttypes import DMSObject


def create_dms(dms, DMS_CACHE, CORRIDOR_DMS_MAP):
    name = dms.get('name')
    tmp = name.split('_')
    dms_name = tmp[0]

    description = dms.get('description', '')
    corridor_name, label = _get_corridor(description)

    if corridor_name:
        if corridor_name not in CORRIDOR_DMS_MAP.keys():
            CORRIDOR_DMS_MAP[corridor_name] = []
        CORRIDOR_DMS_MAP[corridor_name].append(name)

    dmsObject = DMS_CACHE.get(dms_name, None)
    if not dmsObject:
        dmsObject = DMSObject(dict(label=label,
                                   name=dms_name,
                                   description=description,
                                   lon=float(dms.get('lon', 0.0)),
                                   lat=float(dms.get('lat', 0.0)),
                                   dms_list=[],
                                   width_pixels=int(dms.get('shift', 0))))
        DMS_CACHE[dms_name] = dmsObject

    dmsObject.dms_list.append(name)
    if dmsObject.lat == 0.0 and dms.get('lat', None):
        dmsObject.lat = float(dms.get('lat'))
        dmsObject.lon = float(dms.get('lon'))

    return dmsObject, corridor_name

def _get_corridor(description):
    splitted = description.split(' ')
    corr_route = splitted[0]
    corr_dir = splitted[1] if len(splitted) >= 2 else 'All'
    corridor_name = '{0} ({1})'.format(corr_route, corr_dir)
    label = description
    return corridor_name, label

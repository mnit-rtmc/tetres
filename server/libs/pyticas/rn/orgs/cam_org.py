# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.ttypes import CameraObject


def create_camera(camera, CAMERA_CACHE, CORRIDOR_CAMERA_MAP):
    name = camera.get('name')
    description = camera.get('description')
    corridor_name, label = _get_corridor_name(description)

    if not corridor_name:
        return False, False

    if corridor_name not in CORRIDOR_CAMERA_MAP.keys():
        CORRIDOR_CAMERA_MAP[corridor_name] = []
    CORRIDOR_CAMERA_MAP[corridor_name].append(name)

    cameraObject = CAMERA_CACHE.get(name, None)
    if not cameraObject:
        cameraObject = CameraObject({
            'name' : name,
            'label' : label,
            'description' : description,
            'lon' : float(camera.get('lon', 0.0)),
            'lat' : float(camera.get('lat', 0.0))
        })
        CAMERA_CACHE[name] = cameraObject

    return cameraObject, corridor_name


def _get_corridor_name(description):
    splitted = description.split(' ')
    corr_route = splitted[0]
    corr_dir = splitted[1] if len(splitted) >= 2 else 'All'
    corridor_name = '{0} ({1})'.format(corr_route, corr_dir)
    label = description
    return corridor_name, label


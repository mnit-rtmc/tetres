# -*- coding: utf-8 -*-
from pyticas.tool import tb

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import json
import enum

from importlib import import_module
from pyticas.logger import getLogger

TYPE_MODULES = []

try:
    import numpy
except ImportError:
    class numpy(object):
        ndarray = type('ndarray', (), {})

        def array(self, data):
            return data
        def asscalar(self, v):
            return v

numpy_types = ['numpy.float32', 'numpy.float64', 'numpy.int32', 'numpy.int64', 'numpy.datetime64', 'numpy.timedelta64']

def _json_encoder(obj, **kwargs):
    """ Return serializable object for json

    Note:
        - serialize_infraobject() : see `pyticas.ttypes.InfraObject`
        - serialize() : see `pyticas.ttypes.Serializable`

    :type obj: object
    :rtype: dict
    """

    if hasattr(obj, 'get_json_data'):
        return obj.get_json_data()
    elif hasattr(obj, '_obj_type_'):
        encode_method = kwargs.pop('encode_method', 'serialize')
        return getattr(obj, encode_method)()
    elif hasattr(obj, 'serialize'):
        return obj.serialize()
    elif isinstance(obj, enum.Enum):
            return {"__enum__": str(obj)}
    elif isinstance(obj, datetime.datetime):
        return {
            '__type__' : 'datetime',
            'datetime' : obj.strftime('%Y-%m-%d %H:%M:%S'),
        }
    elif isinstance(obj, datetime.date):
        return {
            '__type__' : 'date',
            'date' : obj.strftime('%Y-%m-%d'),
        }
    elif isinstance(obj, datetime.time):
        return {
            '__type__' : 'time',
            'time' : obj.strftime('%H:%M:%S'),
        }
    elif isinstance(obj, numpy.ndarray):
        return {
            '__type__' : 'numpy.ndarray',
            'list' : obj.tolist(),
        }
    elif 'numpy' in str(type(obj)):
        obj_type = str(type(obj))
        _type = None
        for t in numpy_types:
            if t in obj_type:
                _type = t
                break
        return {
            '__type__' : _type,
            'item' : numpy.asscalar(obj)
        }
    else:
        try:
            return obj.__dict__
        except Exception as ex:
            print(obj, type(obj))
            raise ex

def _json_encoder_with_name(obj, **kwargs):
    kwargs['encode_method'] = 'serialize_name'
    return _json_encoder(obj, **kwargs)

def _json_decoder(args):
    """ Return object that is unserialized

    :type args: dict
    :rtype: object
    """

    # for `datetime.datetime`

    if '__type__' in args and args['__type__'] == 'datetime':
        inst = datetime.datetime.strptime(args['datetime'], '%Y-%m-%d %H:%M:%S')
    elif '__type__' in args and args['__type__'] == 'date':
        inst = datetime.datetime.strptime(args['date'], '%Y-%m-%d').date()
    elif '__type__' in args and args['__type__'] == 'time':
        inst = datetime.datetime.strptime(args['time'], '%H:%M:%S').time()
    elif '__type__' in args and args['__type__'] == 'numpy.ndarray':
        inst = numpy.array(args['list'])
    elif '__type__' in args and args['__type__'] in numpy_types:
        inst = eval(args['__type__'])(args['item'])
    elif '__enum__' in args:
        if '.' in args["__enum__"]:
            name, member = args["__enum__"].split(".")
        else:
            member = args["__enum__"]
            name = 'ValidState'
        enumObj = _find_serializable_class(name)
        return getattr(enumObj, member)

    # for `InfraObject` class
    elif '_obj_type_' in args and 'name' in args:
        _obj_type_ = args.pop('_obj_type_')
        getter = 'get_%s' % _obj_type_.lower()
        from pyticas.infra import Infra
        inst = getattr(Infra.get_infra(args.get('infra_cfg_date', '')), getter)(args['name'])

    # for `Serializable` class
    elif '__class__' in args:
        class_name = args.pop('__class__')
        module_name = args.pop('__module__', None)
        try:
            module = import_module(module_name)
            cls = getattr(module, class_name)
        # if module is not found by changing module name or path
        except Exception as ex:
            tb.traceback(ex)
            getLogger(__name__).error('fail to unserialize for %s.%s' % (module_name, class_name))
            cls = _find_serializable_class(class_name)

        if cls and hasattr(cls, 'unserialize'):
            args = dict((key, value) for key, value in args.items())
            inst = cls.unserialize(args)
        else:
            inst = args

    else:
        inst = args

    if hasattr(inst, '__unserialized__'):
        inst.__unserialized__()

    return inst

# def _convert_type(ttype, args):
#     type = args.pop('__type__')
#     try:
#         inst = ttype(**args)
#     except:
#         args['__type__'] = type
#         inst = args
#     return inst

def _find_serializable_class(cls_name):
    """ Return class from pyticas.ttypes

    Note:
        - all `Serializable` classes are defined to `pyticas.ttypes` module
        - this function can be used just in case that
          the `__module__` in json string is not found in the current version

    :type cls_name: str
    :rtype: type
    """
    from pyticas import ttypes
    if hasattr(ttypes, cls_name):
        return getattr(ttypes, cls_name)
    else:
        for md in TYPE_MODULES:
            if hasattr(md, cls_name):
                return getattr(md, cls_name)
        return None


def dumps(obj, **kwargs):
    if kwargs.pop('only_name', False):
        return json.dumps(obj, default=_json_encoder_with_name, **kwargs)
    else:
        return json.dumps(obj, default=_json_encoder, **kwargs)


def loads(json_string, target_type=None):
    if not target_type:
        return json.loads(json_string, object_hook=_json_decoder)
    else:
        obj = target_type()
        dict_data = json.loads(json_string, object_hook=_json_decoder)
        for k, v in obj.__dict__.items():
            if hasattr(dict_data, k):
                setattr(obj, k, getattr(dict_data, k, None))
        return obj



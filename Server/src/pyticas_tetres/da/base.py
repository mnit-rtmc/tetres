# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from sqlalchemy import or_, and_
from sqlalchemy.orm.exc import NoResultFound

from pyticas.tool import json
from pyticas.tool import profile, tb
from pyticas.ttypes import Route
from pyticas_server.util import json2route
from pyticas_tetres.db.tetres import conn

DEFAULT_PRINT_EXCEPTION = True


class DataAccessBase(object):
    def __init__(self, dbModel, dataInfoType, **kwargs):
        """
        :param dbModel: DB model defined in `pyticas_tetres.db.model`
        :param dataInfoType:  corresponding class to DB model defined in `pyticas_tetres.ttrms_types`
        """
        self.primary_key = kwargs.get('primary_key', 'id')
        self.dbModel = dbModel
        self.dataInfoType = dataInfoType
        self.dt_attrs = dataInfoType._dt_attrs_ if hasattr(dataInfoType, '_dt_attrs_') else []
        self.route_attrs = dataInfoType._route_attrs_ if hasattr(dataInfoType, '_route_attrs_') else []
        self.rel_attrs = dataInfoType._rel_attrs_ if hasattr(dataInfoType, '_rel_attrs_') else {}
        self.enum_attrs = dataInfoType._enum_attrs_ if hasattr(dataInfoType, '_enum_attrs_') else {}
        self.json_attrs = dataInfoType._json_attrs_ if hasattr(dataInfoType, '_json_attrs_') else {}
        self.session = kwargs.get('session', conn.get_session())
        """:type: sqlalchemy.orm.Session """

    def query_generator(self, qry, window_size=1000):
        start = 0
        while True:
            stop = start + window_size
            items = qry.slice(start, stop).all()
            if not items:
                break
            for thing in items:
                yield (thing)
            start += window_size

    def get_model_by_name(self, name, **kwargs):
        """ return DB model data by name (use only if applicable)

        :type name: str
        :rtype: dbModel
        """
        print_exception = kwargs.get('print_exception', DEFAULT_PRINT_EXCEPTION)
        try:
            return self.session.query(self.dbModel).filter(self.dbModel.name == name).first()
        except Exception as ex:
            if print_exception:
                tb.traceback(print_exception)
            return None

    def get_model_by_id(self, id, **kwargs):
        """ return DB model data by id
        :type id: int
        :rtype: dbModel
        """
        print_exception = kwargs.get('print_exception', DEFAULT_PRINT_EXCEPTION)
        try:
            return self.session.query(self.dbModel).filter(getattr(self.dbModel, self.primary_key) == id).first()
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return None

    def get_data_by_name(self, name, **kwargs):
        """ return data by name (use only if applicable)

        :type name: str
        :return: dataInfoType
        """
        model_data = self.get_model_by_name(name, **kwargs)
        if not model_data:
            return None
        return self.to_info(model_data)

    def get_data_by_id(self, id):
        """ return data by id

        :type id: int
        :return: dataInfoType
        """
        model_data = self.get_model_by_id(id)
        if not model_data:
            return None
        return self.to_info(model_data)

    def get_next_pk(self):
        last_item = self.session.query(self.dbModel).order_by(self.dbModel.id.desc()).first()
        return last_item.id + 1 if last_item else 1

    def insert(self, data, **kwargs):
        """ insert data

        :param data: dataInfoType
        :return: dbModel data
        """
        print_exception = kwargs.get('print_exception', DEFAULT_PRINT_EXCEPTION)

        model_data = self.to_model(data)
        try:
            self.session.add(model_data)
            data.id = model_data.id
            return model_data
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def list_as_generator(self, **kwargs):
        """ return data list

        :return: list[dataInfoType]
        """
        as_model = kwargs.get('as_model', False)
        limit = kwargs.get('limit', None)
        group_by = kwargs.get('group_by', None)
        order_by = kwargs.get('order_by', None)
        window_size = kwargs.get('window_size', 1000)

        qry = self.session.query(self.dbModel)

        # apply 'order by'
        if order_by and isinstance(order_by, tuple):
            # e.g. order_by = ('id', 'desc')
            # e.g. order_by = ('name', 'asc')
            qry = qry.order_by(getattr(getattr(self.dbModel, order_by[0]), order_by[1])())
        # apply 'order by'
        if order_by and isinstance(order_by, list):
            # e.g. order_by = ('id', 'desc')
            # e.g. order_by = ('name', 'asc')
            order_by_args = list()
            for each_order_by in order_by:
                order_by_args.append(getattr(getattr(self.dbModel, each_order_by[0]), each_order_by[1])())
            qry = qry.order_by(*order_by_args)

        if group_by:
            if isinstance(group_by, str):
                qry = qry.group_by(getattr(self.dbModel, group_by))
            else:
                qry = qry.group_by(group_by)

        # apply 'limit'
        if limit:
            qry = qry.limit(limit)

        for m in self.query_generator(qry, window_size):
            if as_model:
                yield m
            else:
                yield self.to_info(m)

    def list(self, **kwargs):
        """ return data list

        :return: list[dataInfoType]
        """
        return [m for m in self.list_as_generator(**kwargs)]

    def delete(self, pkey, **kwargs):
        """ delete object

        :type pkey: int
        """
        print_exception = kwargs.get('print_exception', DEFAULT_PRINT_EXCEPTION)

        try:
            (self.session.query(self.dbModel)
             .filter(getattr(self.dbModel, self.primary_key) == pkey)
             .delete(synchronize_session=False))
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def delete_items(self, pkeys, **kwargs):
        """ delete object

        :type pkeys: list[int]
        """
        print_exception = kwargs.get('print_exception', DEFAULT_PRINT_EXCEPTION)
        if not pkeys:
            return True
        try:
            qry = (self.session.query(self.dbModel)
                   .filter(getattr(self.dbModel, self.primary_key).in_(pkeys)))

            # from sqlalchemy.dialects import postgresql
            # print(str(qry.statement.compile(dialect=postgresql.dialect())))
            qry = qry.delete(synchronize_session=False)
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def update(self, id, field_data, **kwargs):
        """ update data

        :param id: index
        :param field_data: dictionary data (key must be same to field name of the model)
        :return: boolean
        """
        print_exception = kwargs.get('print_exception', DEFAULT_PRINT_EXCEPTION)

        if not id:
            raise ValueError('`id` must be provided')
        converted = {}
        for key, value in field_data.items():
            if key in self.dt_attrs and not isinstance(value, datetime.datetime):
                converted[key] = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            elif key in self.route_attrs and isinstance(value, Route):
                converted[key] = json.dumps(value)
            elif key in self.enum_attrs:
                if isinstance(value.value, tuple):
                    converted[key] = value.value[0]
                else:
                    converted[key] = value.value
            else:
                converted[key] = value

        try:
            self.session.query(self.dbModel).filter_by(id=id).update(converted)
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def search(self, searches, op='and', cond='match', **kwargs):
        """ search data

        **Example**
            - find item that `sevent_id` is 1
                >>> search([('sevent_id', 1)]

            - find item that `name` == 'test and start_time == 2016-01-01 00:00 and end_time == 2016-01-01 07:00
                >>> search([('name', 'test'), ('start_time', datetime(2016, 1, 1, 0, 0)), ('end_time', 2016, 1, 1, 7, 0)], op='and', cond='match')

            - find items that `years` contains one of 2014, 2015 and 2016
                >>> search([('years', y) for y in [2014, 2015, 2016]], op='or', cond='like')

        :param searches: search condition list (see the above example)
        :param op: operand ('and', 'or')
        :param cond: condition ('match', 'like')
        :param kwargs: if `as_model` is True, returns data as `dbModel` type
        :return: data list
        """
        as_model = kwargs.get('as_model', False)
        limit = kwargs.get('limit', None)
        order_by = kwargs.get('order_by', None)

        operator = and_ if op == 'and' else or_
        clauses = operator()
        for (key, value) in searches:
            if cond == 'like':
                clauses = operator(clauses, getattr(self.dbModel, key).like('%{}%'.format(value)))
            else:
                clauses = operator(clauses, getattr(self.dbModel, key) == value)

        qry = self.session.query(self.dbModel).filter(clauses)

        # apply 'order by'
        if order_by and isinstance(order_by, tuple):
            # e.g. order_by = ('id', 'desc')
            # e.g. order_by = ('name', 'asc')
            qry = qry.order_by(getattr(getattr(self.dbModel, order_by[0]), order_by[1])())

        # apply 'limit'
        if limit:
            qry = qry.limit(limit)

        qry = qry.all()

        data_list = []
        for model_data in qry:
            if as_model:
                data_list.append(model_data)
            else:
                data_list.append(self.to_info(model_data))
        return data_list

    def search_date_range(self, sinfo, einfo):
        """ search data overlapped with the given data range

        :param sinfo: start datetime info, e.g. sinfo = ('sdate', datetime('2013-12-01 00:00:00'))
        :type sinfo: (str, datetime.datetime)
        :param einfo: end datetime info e.g. einfo = ('edate', datetime('2013-12-01 23:55:00'))
        :type einfo: (str, datetime.datetime)
        :return:
        """
        sfield, sdt = sinfo
        efield, edt = einfo
        qry = (self.session.query(self.dbModel)
               .filter(getattr(self.dbModel, sfield) <= edt)
               .filter(getattr(self.dbModel, efield) >= sdt))

        data_list = []
        for model_data in qry:
            data_list.append(self.to_info(model_data))
        return data_list

    @profile.profile
    def to_info(self, model_data, data_info_type=None, **kwargs):
        """ change DB model type to info type

        :param model_data: retrieved data from DB
        :param data_info_type: info class defined in `pyticas_tetres.ttrms_types`
        :return: corresponding class instance to DB model
        """
        route_attrs = data_info_type._route_attrs_ if data_info_type else self.route_attrs
        dt_attrs = data_info_type._dt_attrs_ if data_info_type else self.dt_attrs
        rel_attrs = data_info_type._rel_attrs_ if data_info_type else self.rel_attrs
        enum_attrs = data_info_type._enum_attrs_ if data_info_type else self.enum_attrs
        json_attrs = data_info_type._json_attrs_ if data_info_type else self.json_attrs
        info = data_info_type() if data_info_type else self.dataInfoType()
        none_route = kwargs.get('none_route', False)

        if not model_data:
            return None

        for key, value in model_data.__dict__.items():
            if key.startswith('_'):
                continue
            if key in dt_attrs:  # isinstance(value, datetime.datetime):
                valueToSet = value.strftime('%Y-%m-%d %H:%M:%S') if value else None
            elif key in route_attrs:
                if not none_route:
                    valueToSet = json2route(value)
                    if not isinstance(valueToSet, Route):
                        valueToSet = value
                else:
                    valueToSet = None
            elif key in enum_attrs:
                enum_type = enum_attrs.get(key)
                valueToSet = enum_type.find_by_value(value)
            elif key in json_attrs:
                valueToSet = json.loads(value)
            else:
                valueToSet = value
            setattr(info, key, valueToSet)

        for attr_name, rel_info in rel_attrs.items():
            if model_data and not attr_name.startswith('_'):
                valueToSet = self.to_info(getattr(model_data, attr_name), data_info_type=rel_info['info_cls'], **kwargs)
            else:
                valueToSet = None
            setattr(info, attr_name, valueToSet)

        return info

    def to_model(self, info_data, data_info_type=None):
        """ change info type to DB model type

        :param info_data: corresponding class instance to DB model
        :return: converted DB model data
        """
        route_attrs = data_info_type._route_attrs_ if data_info_type else self.route_attrs
        dt_attrs = data_info_type._dt_attrs_ if data_info_type else self.dt_attrs
        rel_attrs = data_info_type._rel_attrs_ if data_info_type else self.rel_attrs
        enum_attrs = data_info_type._enum_attrs_ if data_info_type else self.enum_attrs
        json_attrs = data_info_type._json_attrs_ if data_info_type else self.json_attrs

        model_data = self.dbModel()
        for key, value in info_data.__dict__.items():
            valueToSet = value
            if key in dt_attrs:
                if value:
                    valueToSet = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            elif key in route_attrs:
                valueToSet = json.dumps(value, only_name=True)
            elif key in enum_attrs:
                if not value:
                    valueToSet = value
                elif isinstance(value.value, tuple):
                    valueToSet = value.value[0]
                else:
                    valueToSet = value.value
            elif key in json_attrs:
                valueToSet = json.dumps(value)
            setattr(model_data, key, valueToSet)

        for attr_name, rel_info in rel_attrs.items():
            value = getattr(info_data, attr_name, None)
            valueToSet = value
            if value:
                continue
            rel_key = rel_info['key']
            rel_model_cls = rel_info['model_cls']
            try:
                rel_id = getattr(info_data, rel_key)
                if rel_id:
                    with self.session.no_autoflush:
                        valueToSet = self.session.query(rel_model_cls).filter(rel_model_cls.id == rel_id).first()
            except NoResultFound as ex:
                pass

            setattr(model_data, attr_name, valueToSet)

        return model_data

    def flush(self):
        return self.session.flush()

    def commit(self, **kwargs):
        try:
            self.session.commit()
            return True
        except Exception as ex:
            if kwargs.get('print_exception', DEFAULT_PRINT_EXCEPTION):
                tb.traceback(ex)
            return False

    def execute(self, *args, **kwargs):
        return self.session.execute(*args, **kwargs)

    def bulk_insert(self, dict_list, **kwargs):
        """

        :type dict_list: list[dict]
        :rtype: Union(list[int], False)
        """
        print_exception = kwargs.get('print_exception', DEFAULT_PRINT_EXCEPTION)

        ids = []
        pk = self.get_next_pk()
        for idx, data in enumerate(dict_list):
            data['id'] = pk + idx
            ids.append(pk + idx)
        try:
            self.execute(self.dbModel.__table__.insert(), dict_list)
            return ids
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            return False

    def transaction_start(self):
        if self.session.transaction is None:
            self.session.begin_nested()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()

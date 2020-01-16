# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


class DataAccess(object):
    def __init__(self, **kwargs):
        self.da_base = None

    def get_model_by_id(self, id):
        return self.da_base.get_model_by_id(id)

    def get_data_by_id(self, id):
        return self.da_base.get_data_by_id(id)

    def get_next_pk(self):
        """
        :rtype: int
        """
        return self.da_base.get_next_pk()

    def get_tablename(self):
        """ returns the db table name

        :rtype: str
        """
        return str(self.da_base.dbModel.__table__.name)

    def delete(self, id, **kwargs):
        """
        :type id: int
        """
        return self.da_base.delete(id, **kwargs)

    def delete_items(self, ids, **kwargs):
        """
        :type ids: list[int]
        """
        return self.da_base.delete_items(ids, **kwargs)

    def update(self, id, field_data, **kwargs):
        """
        :type id: int
        :type field_data: dict
        :rtype: bool
        """
        return self.da_base.update(id, field_data, **kwargs)

    def execute(self, *args, **kwargs):
        return self.da_base.execute(*args, **kwargs)

    def bulk_insert(self, dict_list, **kwargs):
        """

        :type dict_list: list[dict]
        :rtype: Union(list[int], False)
        """
        return self.da_base.bulk_insert(dict_list, **kwargs)

    def transaction_start(self):
        return self.da_base.transaction_start()

    def rollback(self):
        return self.da_base.rollback()

    def commit(self, **kwargs):
        committed = self.da_base.commit(**kwargs)
        if committed:
            return True
        else:
            if kwargs.get('rollback', True):
                self.da_base.rollback()
            return False

    def close_session(self):
        return self.da_base.session.close()

    def get_session(self):
        """
        :rtype: slqlalchemy.orm.Session
        """
        return self.da_base.session

    def get_model(self):
        return self.da_base.dbModel

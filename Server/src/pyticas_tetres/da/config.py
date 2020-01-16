# -*- coding: utf-8 -*-
from pyticas.tool import tb

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.da.base import DataAccessBase
from pyticas_tetres.da.data_access import DataAccess
from pyticas_tetres.db.tetres import model
from pyticas_tetres.ttypes import ConfigInfo

DEFAULT_PRINT_EXCEPTION = True

class ConfigDataAccess(DataAccess):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.da_base = DataAccessBase(model.Config, ConfigInfo, **kwargs)

    def list(self, **kwargs):
        """
        :rtype: list[pyticas_tetres.ttypes.ConfigInfo]
        """
        return self.da_base.list(**kwargs)


    def get_by_id(self, pkey):
        """
        :type pkey: int
        :rtype: ConfigInfo
        """
        return self.da_base.get_data_by_id(pkey)

    def get_by_name(self, name, **kwargs):
        """
        :type name: str
        :rtype: pyticas_tetres.ttypes.ConfigInfo
        """
        if kwargs.get('as_model', False):
            return self.da_base.get_model_by_name(name, **kwargs)
        else:
            return self.da_base.get_data_by_name(name, **kwargs)

    def insert(self, name, content, **kwargs):
        """
        :type name: str
        :type content: str
        :rtype: model.Config
        """
        c = ConfigInfo()
        c.name = name
        c.content = content
        return self.da_base.insert(c, **kwargs)

    def insert_or_update(self, name, content):
        """

        :type name: str
        :type content: str
        :rtype: Union(model.Config, bool)
        """
        item = self.get_by_name(name, as_model=True)
        if not item:
            return self.insert(name, content)
        else:
            if self.update(item.id, {'content' : content}):
                item.content = content
                return item
            return False

    def delete_by_name(self, name, **kwargs):
        """
        :type name: str
        :rtype: bool
        """
        print_exception = kwargs.get('print_exception', DEFAULT_PRINT_EXCEPTION)
        sess = self.get_session()
        try:
            sess.query(model.Config).filter(model.Config.name == name).delete()
            sess.commit()
            return True
        except Exception as ex:
            if print_exception:
                tb.traceback(ex)
            sess.rollback()
            return False


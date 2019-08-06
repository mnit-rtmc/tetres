# -*- coding: utf-8 -*-

from pyticas_server.app import TICASApp

class MyApp(TICASApp):

    def init(self, app):
        """ add some bootstrap codes for system such as
            database connection and starting job scheduler

        :type app: flask.Flask
        """
        pass

    # def register_service(self, app):
    #     """ it calls 'register_api' function of all modules in 'api' directory
    #         see 'api/helloworld.py'
    #
    #     :type app: flask.Flask
    #     """
    #     for mod in self.load_api_modules(__file__, __name__, 'api'):
    #         mod.register_api(app)

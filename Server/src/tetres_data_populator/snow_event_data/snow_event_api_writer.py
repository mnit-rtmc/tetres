from tetres_data_populator.mixins.api_writer_mixin import APIWriterMixin


class SnowEventAPIWriter(APIWriterMixin):
    def __init__(self, infra):
        self.infra = infra

    def excel_row_to_snow_management_data_dict(self, excel_data):
        snow_management_data = {'lane_lost_time': excel_data['lane_lost_time'],
                                'lane_regain_time': excel_data['lane_regain_time'],
                                'sroute_id': excel_data['sroute_id'],
                                'sevent_id': excel_data['sevent_id'],
                                'duration': excel_data['duration'],
                                '__module__': 'pyticas_tetres.ttypes',
                                '__class__': 'SnowManagementInfo'}
        return snow_management_data

    def excel_row_to_snow_event_data_dict(self, excel_data):
        snow_event_data = {
            "start_time": excel_data["start_time"],
            "end_time": excel_data["end_time"],
            "__module__": "pyticas_tetres.ttypes",
            "__class__": "SnowEventInfo"
        }
        return snow_event_data

    def excel_row_to_snow_route_data_dict(self, excel_data):
        """
        {
           "name":"Test",
           "description":"Test Description",
           "prj_id":"TestTest",
           "route1":{
              "__module__":"pyticas.ttypes",
              "__class__":"Route",
              "name":"Test",
              "desc":"Test Description",
              "rnodes":[
                 "rnd_7199",
                 "rnd_7278"
              ]
           },
           "__module__":"pyticas_tetres.ttypes",
           "__class__":"SnowRouteInfo"
        }
        """
        name = excel_data.get('name')
        description = excel_data.get('description')
        prj_id = excel_data.get('prj_id')
        starting_station = excel_data.get('starting_station')
        ending_station = excel_data.get('ending_station')
        route1 = self.__class__.generate_route(self.infra, starting_station=starting_station,
                                               ending_station=ending_station, name=name,
                                               description=description)
        snow_route_data = {
            "name": name,
            "description": description,
            "prj_id": prj_id,
            "route1": route1,
            "__module__": "pyticas_tetres.ttypes",
            "__class__": "SnowRouteInfo"
        }

        return snow_route_data

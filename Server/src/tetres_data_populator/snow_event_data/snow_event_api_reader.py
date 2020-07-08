from tetres_data_populator.mixins.api_reader_mixin import APIReaderMixin


class SnowEventAPIReader(APIReaderMixin):
    def get_snow_route_data_dict(self, list_url, *args, **kwargs):
        dict_data = dict()
        snow_route_list_data = self.get_list_data(list_url)
        for data in snow_route_list_data:
            data_tuple = (
                data['name'], data['prj_id']
            )
            dict_data[data_tuple] = data
        return dict_data

    def get_prj_id_vs_snow_route_id_map(self):
        dict_data = dict()
        base_url = "http://localhost:5000"
        snow_route_list_route = "/tetres/adm/snowroute/list"
        list_url = base_url + snow_route_list_route
        snow_route_list_data = self.get_list_data(list_url)
        for data in snow_route_list_data:
            dict_data[data['prj_id']] = data["id"]
        return dict_data

    def get_start_end_time_vs_snow_event_id_map(self):
        dict_data = dict()
        base_url = "http://localhost:5000"
        snow_event_list_route = "/tetres/adm/snowevent/list"
        list_url = base_url + snow_event_list_route
        snow_event_list_data = self.get_list_data(list_url)
        for data in snow_event_list_data:
            data_tuple = (
                data['start_time'], data['end_time']
            )
            dict_data[data_tuple] = data["id"]
        return dict_data

    def get_snow_event_data_dict(self, list_url, *args, **kwargs):
        dict_data = dict()
        snow_event_list_data = self.get_list_data(list_url)
        for data in snow_event_list_data:
            data_tuple = (
                data['start_time'], data['end_time']
            )
            dict_data[data_tuple] = data
        return dict_data

    def get_snow_management_data_dict(self, list_url, *args, **kwargs):
        dict_data = dict()
        snow_management_list_data = self.get_list_data(list_url)
        for data in snow_management_list_data:
            data_tuple = (
                data['sroute_id'], data['sevent_id']
            )
            dict_data[data_tuple] = data
        return dict_data

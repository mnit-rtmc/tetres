from pyticas_tetres import api_urls_admin

from tetres_data_populator.mixins.api_reader_mixin import APIReaderMixin


class WorkZoneAPIReader(APIReaderMixin):
    def get_work_zone_group_data_dict(self, list_url, *args, **kwargs):
        dict_data = dict()
        work_zone_group_list_data = self.get_list_data(list_url)
        for data in work_zone_group_list_data:
            data_tuple = (
                data['name'],
            )
            dict_data[data_tuple] = data
        return dict_data

    def get_work_zone_group_name_vs_work_zone_group_id_map(self):
        dict_data = dict()
        base_url = "http://localhost:5000"
        work_zone_group_list_route = api_urls_admin.WZ_GROUP_LIST

        list_url = base_url + work_zone_group_list_route
        work_zone_group_list_data = self.get_list_data(list_url)
        for data in work_zone_group_list_data:
            dict_data[data['name']] = data["id"]
        return dict_data

    def get_work_zone_data_dict(self, list_url, *args, **kwargs):
        dict_data = dict()
        work_zone_list_data = self.get_list_data(list_url)
        for data in work_zone_list_data:
            rnodes_string_representation = ",".join(data['route1']['rnodes'])
            data_tuple = (
                data['wz_group_id'], data['start_time'], data['end_time'], rnodes_string_representation
            )
            dict_data[data_tuple] = data
        return dict_data

import json

import requests
from pyticas_tetres import api_urls_admin

from tetres_data_populator.mixins.api_writer_mixin import APIWriterMixin
from tetres_data_populator.utils.date_utils import get_years


class WorkZoneAPIWriter(APIWriterMixin):
    def __init__(self, infra):
        self.infra = infra

    def excel_row_to_work_zone_group_data_dict(self, excel_data):
        work_zone_group_data = {'name': excel_data['name'],
                                'description': excel_data['description'],
                                'impact': excel_data['impact'],
                                '__module__': 'pyticas_tetres.ttypes',
                                '__class__': 'WorkZoneGroupInfo'}
        return work_zone_group_data

    def excel_row_to_work_zone_data_dict(self, excel_data):
        work_zone_group_data = {'wz_group_id': excel_data['wz_group_id'],
                                'memo': excel_data['memo'],
                                'start_time': excel_data['start_time'],
                                'end_time': excel_data['end_time'],
                                'route1': excel_data['route1'],
                                '__module__': 'pyticas_tetres.ttypes',
                                '__class__': 'WorkZoneInfo'}
        return work_zone_group_data

    def post_data(self, excel_reader, post_url, list_url, data_type, api_reader_class):
        creatable_dict = self.get_creatable_dict(excel_reader=excel_reader, list_url=list_url,
                                                 data_type=data_type, api_reader_class=api_reader_class)
        for data in creatable_dict.values():
            if data_type == "work_zone":
                self.post_one_data_for_work_zone(data, post_url)
            else:
                super().post_one_data(data, post_url)

    @staticmethod
    def post_one_data_for_work_zone(data, post_url):

        route = data["route1"]
        del data["route1"]
        json_data = json.dumps(data)
        json_route_data = json.dumps(route)
        formatted_data = {
            "data": json_data,
            "route": json_route_data
        }
        try:
            response = requests.post(post_url, data=formatted_data)
            if response.status_code != 200:
                raise Exception("Unsuccessful Request. Response Code: {}".format(response.status_code))
        except Exception as e:
            print("Error: ", formatted_data, e)

    def populate_work_zone_years(self, api_reader):
        base_url = "http://localhost:5000"
        work_zone_group_list_url = base_url + api_urls_admin.WZ_GROUP_LIST
        work_zone_list_url = base_url + api_urls_admin.WZ_LIST_ALL
        work_zone_group_raw_list_data = api_reader.get_list_data(list_url=work_zone_group_list_url)
        work_zone_raw_list_data = api_reader.get_list_data(list_url=work_zone_list_url)
        work_zone_group_data_dict = dict()
        for work_zone_group in work_zone_group_raw_list_data:
            work_zone_group["year_list"] = set()
            work_zone_group_data_dict[work_zone_group["id"]] = work_zone_group
        for work_zone in work_zone_raw_list_data:
            wz_group_id = work_zone["wz_group_id"]
            work_zone_group = work_zone_group_data_dict[wz_group_id]
            year_list = get_years(work_zone["start_time"], work_zone["end_time"])
            for year in year_list:
                work_zone_group["year_list"].add(year)
        updatable_data_count = 0
        for work_zone_group in work_zone_group_raw_list_data:
            work_zone_group["year_list"] = sorted(list(work_zone_group["year_list"]))
            years = ",".join(work_zone_group["year_list"])
            if years and years != work_zone_group["years"]:
                del work_zone_group["year_list"]
                work_zone_group["years"] = years
                json_data = json.dumps(work_zone_group)
                formatted_data = {
                    "id": work_zone_group["id"],
                    "data": json_data
                }
                try:
                    requests.post(base_url + api_urls_admin.WZ_GROUP_UPDATE, data=formatted_data)
                except Exception as e:
                    print("Error: ", formatted_data, e)

                updatable_data_count += 1
        print("Total Work Zone Group Data: {}".format(len(work_zone_group_raw_list_data)))
        print("Total Updatable Work Zone Group Data: {}".format(updatable_data_count))

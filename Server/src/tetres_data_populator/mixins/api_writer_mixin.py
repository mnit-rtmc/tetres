import json
from collections import OrderedDict

import requests


class APIWriterMixin:
    @staticmethod
    def post_one_data(data, post_url):
        json_data = json.dumps(data)
        formatted_data = {
            "data": json_data
        }
        try:
            response = requests.post(post_url, data=formatted_data)
            if response.status_code != 200:
                raise Exception("Unsuccessful Request. Response Code: {}".format(response.status_code))

        except Exception as e:
            print("Error: ", formatted_data, e)

    @classmethod
    def generate_route(cls, infra, starting_station, ending_station, name, description):
        route_dict = {
            "__module__": "pyticas.ttypes",
            "__class__": "Route",
            "name": name,
            "desc": description,
            "rnodes": []
        }

        starting_rnode_name = infra.station_rnode_map[starting_station]
        starting_rnode = infra.get_rnode(starting_rnode_name)
        ending_rnode_name = infra.station_rnode_map[ending_station]
        ending_rnode = infra.get_rnode(ending_rnode_name)
        if starting_rnode_name == ending_rnode_name:
            route_dict["rnodes"] = [starting_rnode_name]
            return route_dict
        between_nodes = infra.geo.between_rnodes(starting_rnode, ending_rnode)
        rnodes = [starting_rnode_name]
        for each_rnode in between_nodes:
            rnodes.append(each_rnode.name)
        rnodes.append(ending_rnode_name)
        route_dict["rnodes"] = rnodes
        return route_dict

    def get_creatable_dict(self, excel_reader, list_url, data_type, api_reader_class):
        creatable_dict = OrderedDict()
        api_reader = api_reader_class()
        method_name = "get_{}_data_dict".format(data_type)
        existing_data_dict = getattr(api_reader, method_name)(list_url=list_url, infra=self.infra)
        candidate_data_dict = getattr(excel_reader, method_name)(api_reader=api_reader, infra=self.infra)

        data_in_excel_count = 0
        for data_tuple, data in candidate_data_dict.items():
            data_in_excel_count += 1
            if data_tuple in creatable_dict or data_tuple in existing_data_dict:
                continue
            try:
                conversion_method_name = "excel_row_to_{}_data_dict".format(data_type)
                data = getattr(self, conversion_method_name)(excel_data=data)
                creatable_dict[data_tuple] = data
            except Exception as e:
                print("Failed to convert excel data to creatable data. Error: {}. Data: {}".format(data, e))
        print("{} rows of data in excel.".format(data_in_excel_count))
        print("{} rows of data is creatable.".format(len(creatable_dict)))
        return creatable_dict

    def post_data(self, excel_reader, post_url, list_url, data_type, api_reader_class):
        creatable_dict = self.get_creatable_dict(excel_reader=excel_reader, list_url=list_url,
                                                 data_type=data_type, api_reader_class=api_reader_class)
        for data in creatable_dict.values():
            self.post_one_data(data, post_url)

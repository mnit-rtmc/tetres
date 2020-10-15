import requests


class SpecialEventAPIReader:
    def __init__(self, base_url="http://localhost:5000", list_url="/tetres/adm/sevent/list"):
        self.base_url = base_url
        self.list_url = list_url
        self.url = self.base_url + self.list_url
        self.list_data = self.get_list_data()
        self.dict_data = self.get_dict_data()

    def get_list_data(self):
        response = requests.get(self.url)
        json_data = response.json()['obj']['list']
        return json_data

    def get_dict_data(self):
        dict_data = dict()
        for data in self.list_data:
            data_tuple = (
                data['name'], data['description'], data['start_time'], data['end_time'], data['lat'], data['lon'],
                data['attendance'])
            dict_data[data_tuple] = data
        return dict_data

import requests


class APIReaderMixin:
    @staticmethod
    def get_list_data(list_url):
        response = requests.get(list_url)
        json_data = response.json()['obj']['list']
        return json_data

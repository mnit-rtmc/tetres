import sys
sys.path.append("Server/src")
from tetres_data_populator.special_event_data.special_event_excel_reader import SpecialEventExcelReader
from tetres_data_populator.special_event_data.special_event_api_writer import SpecialEventAPIWriter

base_url = "http://localhost:5000"
special_event_add_route = "/tetres/adm/sevent/add"
special_event_list_route = "/tetres/adm/sevent/list"
only_file_name = input("Enter filename: ")
special_event_filename = "Server/src/tetres_data_populator/excel_data/special_event_data/{}".format(only_file_name)

# special_event_data = {
#     "name": "Cricket Match",
#     "description": "Biggest Cricket match in history",
#     "start_time": "2018-04-01 00:00:00",
#     "end_time": "2020-04-30 00:00:00",
#     "lat": 44.98422783516651,
#     "lon": -93.25538635253906,
#     "attendance": 5000,
#     "__module__": "pyticas_tetres.ttypes",
#     "__class__": "SpecialEventInfo"
# }


if __name__ == "__main__":
    special_event_excel_reader = SpecialEventExcelReader(filename=special_event_filename)
    special_event_api_writer = SpecialEventAPIWriter(base_url=base_url, add_url=special_event_add_route,
                                                     list_url=special_event_list_route)
    special_event_api_writer.post_special_event_data(special_event_excel_reader)

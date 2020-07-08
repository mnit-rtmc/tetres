import sys
sys.path.append("Server/src")
import global_settings
from pyticas import ticas
from pyticas.infra import Infra
from pyticas_tetres import api_urls_admin

from tetres_data_populator.snow_event_data.snow_event_api_reader import SnowEventAPIReader
from tetres_data_populator.snow_event_data.snow_event_api_writer import SnowEventAPIWriter
from tetres_data_populator.snow_event_data.snow_event_excel_reader import SnowEventExcelReader

if __name__ == "__main__":
    ticas.initialize(global_settings.DATA_PATH)
    print(global_settings.DATA_PATH)
    infra = Infra.get_infra()

    base_url = "http://localhost:5000"

    only_file_name = input("Enter the name of the snow event excel file: ")
    snow_event_filename = "Server/src/tetres_data_populator/excel_data/snow_event_data/{}".format(only_file_name)
    snow_event_excel_reader = SnowEventExcelReader(filename=snow_event_filename)

    # adding snow route data
    snow_event_api_writer = SnowEventAPIWriter(infra)
    snow_event_api_writer.post_data(excel_reader=snow_event_excel_reader,
                                    post_url=base_url + api_urls_admin.SNR_INSERT,
                                    list_url=base_url + api_urls_admin.SNR_LIST,
                                    data_type="snow_route",
                                    api_reader_class=SnowEventAPIReader)

    # adding snow event data
    snow_event_api_writer.post_data(excel_reader=snow_event_excel_reader,
                                    post_url=base_url + api_urls_admin.SNE_INSERT,
                                    list_url=base_url + api_urls_admin.SNE_LIST,
                                    data_type="snow_event",
                                    api_reader_class=SnowEventAPIReader)

    # adding snow management data
    snow_event_api_writer.post_data(excel_reader=snow_event_excel_reader,
                                    post_url=base_url + api_urls_admin.SNM_INSERT,
                                    list_url=base_url + api_urls_admin.SNM_LIST_ALL,
                                    data_type="snow_management",
                                    api_reader_class=SnowEventAPIReader)

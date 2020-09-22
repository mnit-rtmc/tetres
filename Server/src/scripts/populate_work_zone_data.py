import sys

sys.path.append("Server/src")
import global_settings
from pyticas import ticas
from pyticas.infra import Infra
from pyticas_tetres import api_urls_admin

from tetres_data_populator.work_zone_data.work_zone_api_reader import WorkZoneAPIReader
from tetres_data_populator.work_zone_data.work_zone_api_writer import WorkZoneAPIWriter
from tetres_data_populator.work_zone_data.work_zone_excel_reader import WorkZoneExcelReader

if __name__ == "__main__":
    ticas.initialize(global_settings.DATA_PATH)
    infra = Infra.get_infra()

    base_url = "http://localhost:5000"
    only_file_name = input("Enter the name of the snow event excel file: ")
    work_zone_filename = "Server/src/tetres_data_populator/excel_data/work_zone_data/{}".format(only_file_name)
    work_zone_excel_reader = WorkZoneExcelReader(filename=work_zone_filename)

    # adding work zone group data
    work_zone_api_writer = WorkZoneAPIWriter(infra=infra)
    work_zone_api_writer.post_data(excel_reader=work_zone_excel_reader,
                                   post_url=base_url + api_urls_admin.WZ_GROUP_INSERT,
                                   list_url=base_url + api_urls_admin.WZ_GROUP_LIST,
                                   data_type="work_zone_group",
                                   api_reader_class=WorkZoneAPIReader)

    work_zone_api_writer.post_data(excel_reader=work_zone_excel_reader,
                                   post_url=base_url + api_urls_admin.WZ_INSERT,
                                   list_url=base_url + api_urls_admin.WZ_LIST_ALL,
                                   data_type="work_zone",
                                   api_reader_class=WorkZoneAPIReader)

    work_zone_api_writer.populate_work_zone_years(api_reader=WorkZoneAPIReader())

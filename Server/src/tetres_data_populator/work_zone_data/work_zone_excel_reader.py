from collections import OrderedDict

from tetres_data_populator.mixins.api_writer_mixin import APIWriterMixin
from tetres_data_populator.mixins.excel_reader_mixin import ExcelReaderMixin


class WorkZoneExcelReader(ExcelReaderMixin):
    def __init__(self, filename):
        super(WorkZoneExcelReader, self).__init__(filename=filename)
        self.work_zone_group_discriminatory_properties = ["name",]
        self.work_zone_discriminatory_properties = ["wz_group_id", "start_time", "end_time", "rnodes"]

    def get_work_zone_group_data_dict(self, api_reader=None, *args, **kwargs):
        try:
            work_zone_group_sheet_name = "'Add Work Zone'"
            work_zone_group_raw_data = self.get_all_rows(sheet_name=work_zone_group_sheet_name)
        except:
            work_zone_group_sheet_name = "Add Work Zone"
            work_zone_group_raw_data = self.get_all_rows(sheet_name=work_zone_group_sheet_name)

        work_zone_group_data_dict = OrderedDict()
        for index, each_row in enumerate(work_zone_group_raw_data):
            if index == 0:
                continue
            name = str(each_row[0].value).strip()
            description = str(each_row[1].value).strip()
            # TODO: might need modification
            impact_raw = str(each_row[2].value).strip()
            impact_map = {
                "low": "Low",
                "med": "Medium",
                "hi": "High"
            }
            current_dict = {
                "name": name,
                "description": description,
                "impact": impact_map.get(impact_raw.lower(), "")

            }
            discriminatory_key = self.get_discriminatory_key(self.work_zone_group_discriminatory_properties,
                                                             current_dict)
            work_zone_group_data_dict[discriminatory_key] = current_dict
        return work_zone_group_data_dict

    def get_work_zone_data_dict(self, api_reader=None, *args, **kwargs):
        work_zone_sheet_name = "'Add Work Zone Config.'"
        work_zone_raw_data = self.get_all_rows(sheet_name=work_zone_sheet_name)
        work_zone_data_dict = OrderedDict()
        wz_name_vs_id_map = api_reader.get_work_zone_group_name_vs_work_zone_group_id_map()
        infra = kwargs.get("infra")
        for index, each_row in enumerate(work_zone_raw_data):
            if index == 0:
                continue
            work_zone_group_name = str(each_row[0].value).strip() or work_zone_group_name
            wz_group_id = wz_name_vs_id_map[work_zone_group_name]
            memo = str(each_row[1].value).strip() or memo
            start_time = self.get_date_time(cell=each_row[2], default_date_time=None) or start_time
            end_time = self.get_date_time(cell=each_row[3], default_date_time=None,
                                          add_date_end_time_offset=True) or end_time
            begin_station = str(each_row[4].value).strip()
            end_station = str(each_row[5].value).strip()
            route1 = APIWriterMixin.generate_route(infra, begin_station, end_station, "", "")
            rnodes_string_representation = ",".join(route1['rnodes'])
            current_dict = {
                "wz_group_id": wz_group_id,
                "memo": memo,
                "start_time": start_time,
                "end_time": end_time,
                "route1": route1,
                "rnodes": rnodes_string_representation

            }
            discriminatory_key = self.get_discriminatory_key(self.work_zone_discriminatory_properties,
                                                             current_dict)
            work_zone_data_dict[discriminatory_key] = current_dict
        return work_zone_data_dict
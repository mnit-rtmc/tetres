from collections import OrderedDict

from tetres_data_populator.mixins.excel_reader_mixin import ExcelReaderMixin
from tetres_data_populator.utils.date_utils import get_duration


class SnowEventExcelReader(ExcelReaderMixin):
    def __init__(self, filename):
        super(SnowEventExcelReader, self).__init__(filename=filename)
        self.snow_route_discriminatory_properties = ["name", "prj_id"]
        self.snow_event_discriminatory_properties = ["start_time", "end_time"]
        self.snow_management_discriminatory_properties = ["sroute_id", "sevent_id"]

    def get_snow_route_data_dict(self, api_reader=None, *args, **kwargs):
        try:
            plow_route_sheet_name = "PlowRoutes"
            plow_route_raw_data = self.get_all_rows(sheet_name=plow_route_sheet_name)
        except:
            plow_route_sheet_name = "Plow Routes"
            plow_route_raw_data = self.get_all_rows(sheet_name=plow_route_sheet_name)
        plow_route_data_dict = OrderedDict()
        prev_name = None
        for index, each_row in enumerate(plow_route_raw_data):
            if index == 0:
                continue
            name = str(each_row[0].value).strip()
            prj_id = str(each_row[1].value).strip()
            starting_station = str(each_row[2].value).strip()
            ending_station = str(each_row[3].value).strip()

            if name:
                prev_name = name
            else:
                name = prev_name
            formatted_name = "{} - {}".format(name, prj_id)
            current_dict = {
                "name": formatted_name,
                "description": "",
                "prj_id": prj_id,
                "starting_station": starting_station,
                "ending_station": ending_station

            }
            discriminatory_key = self.get_discriminatory_key(self.snow_route_discriminatory_properties, current_dict)
            plow_route_data_dict[discriminatory_key] = current_dict
        return plow_route_data_dict

    def get_snow_event_data_dict(self, api_reader=None, *args, **kwargs):
        snow_event_sheet_name = "Snow Events & Lane LossRegain"
        snow_event_raw_data = self.get_all_rows(sheet_name=snow_event_sheet_name)
        snow_event_data_dict = OrderedDict()
        start_time = None
        end_time = None
        for index, each_row in enumerate(snow_event_raw_data):
            if index == 0:
                continue
            start_time = self.get_date_time(each_row[0], start_time)
            end_time = self.get_date_time(each_row[1], end_time)
            current_dict = {
                "start_time": start_time,
                "end_time": end_time,

            }
            discriminatory_key = self.get_discriminatory_key(self.snow_event_discriminatory_properties, current_dict)
            snow_event_data_dict[discriminatory_key] = current_dict
        return snow_event_data_dict

    def get_snow_management_data_dict(self, api_reader=None, *args, **kwargs):
        snow_management_sheet_name = "Snow Events & Lane LossRegain"
        snow_management_raw_data = self.get_all_rows(sheet_name=snow_management_sheet_name)
        snow_management_data_dict = OrderedDict()
        start_time = None
        end_time = None
        prj_id_vs_snow_route_data_map = api_reader.get_prj_id_vs_snow_route_id_map()
        start_end_time_vs_snow_event_id_map = api_reader.get_start_end_time_vs_snow_event_id_map()
        for index, each_row in enumerate(snow_management_raw_data):
            if index == 0:
                continue
            lane_lost_time = self.get_date_time(each_row[3], None)
            lane_regain_time = self.get_date_time(each_row[4], None)
            if not lane_lost_time or not lane_regain_time:
                continue
            try:
                start_time = self.get_date_time(each_row[0], start_time)
                end_time = self.get_date_time(each_row[1], end_time)
                prj_id = str(each_row[2].value).strip()
                sroute_id = prj_id_vs_snow_route_data_map[prj_id]
                sevent_id = start_end_time_vs_snow_event_id_map[(start_time, end_time)]
                duration = get_duration(lane_lost_time, lane_regain_time)
                current_dict = {
                    "sroute_id": sroute_id,
                    "sevent_id": sevent_id,
                    "lane_lost_time": lane_lost_time,
                    "lane_regain_time": lane_regain_time,
                    "duration": duration

                }
                discriminatory_key = self.get_discriminatory_key(self.snow_management_discriminatory_properties,
                                                                 current_dict)
                snow_management_data_dict[discriminatory_key] = current_dict
            except Exception as e:
                print("Can't convert excel data to snow management data. Error: {}. Data: {}".format(e, each_row))
        return snow_management_data_dict

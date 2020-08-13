import sys

import json
import requests
from xlrd.sheet import ctype_text

sys.path.append("Server/src")

from tetres_data_populator.special_event_data.special_event_api_reader import SpecialEventAPIReader


class SpecialEventAPIWriter:
    def __init__(self, base_url="http://localhost:5000",
                 add_url="/tetres/adm/sevent/add", list_url="/tetres/adm/sevent/list"):
        self.base_url = base_url
        self.add_url = add_url
        self.list_url = list_url
        self.post_url = self.base_url + self.add_url

    def get_formatted_date_from_string(self, date):
        date = date.strip()
        month, day, year = date.split("/")
        month = month.strip().zfill(2)
        day = day.strip().zfill(2)
        year = year.strip()
        formatted_date = "-".join([year, month, day])
        return formatted_date

    def get_hour_minute_second_from_string(self, time, am_pm="AM"):
        time, _ = time.split(am_pm)
        time = time.strip()
        hour, minute = time.split(":")
        hour = hour.strip().zfill(2)
        minute = minute.strip().zfill(2)
        if am_pm == "PM" and hour != "12":
            hour = str(int(hour) + 12).strip().zfill(2)
        second = "00"
        return hour, minute, second

    def get_formatted_time_from_string(self, time):
        time = time.strip()
        if time.endswith("PM"):
            hour, minute, second = self.get_hour_minute_second_from_string(time, am_pm="PM")
        else:
            hour, minute, second = self.get_hour_minute_second_from_string(time, am_pm="AM")
        return ":".join([hour, minute, second])

    def get_formatted_date_time(self, formatted_date, formatted_time):
        formatted_date_time = " ".join([formatted_date, formatted_time])
        return formatted_date_time

    def excel_row_to_data_dict(self, row, location_narrative, special_event_excel_reader):
        if ctype_text.get(row[0].ctype) == "xldate":
            date = special_event_excel_reader.get_formatted_date_from_xl_date(row[0].value)
        else:
            date = str(row[0].value).strip()
            # For version 1 excel file
            # date = self.get_formatted_date_from_string(date)

        if ctype_text.get(row[1].ctype) == "xldate":
            start_time = special_event_excel_reader.get_formatted_time_from_xl_date(row[1].value)
        else:
            start_time = str(row[1].value).strip()
            # For version 1 excel file
            # start_time = self.get_formatted_time_from_string(start_time)

        if ctype_text.get(row[2].ctype) == "xldate":
            end_time = special_event_excel_reader.get_formatted_time_from_xl_date(row[2].value)
        else:
            end_time = str(row[2].value).strip()
            # For version 1 excel file
            # end_time = self.get_formatted_time_from_string(end_time)

        title = str(row[3].value)

        event_type = str(row[4].value)

        number_of_attendees = str(row[5].value)

        lat = float(str(row[6].value).strip())
        lon = float(str(row[7].value).strip())
        start_date_time = self.get_formatted_date_time(date, start_time)
        end_date_time = self.get_formatted_date_time(date, end_time)
        end_date_time = self.adjust_end_date_time(start_date_time, end_date_time)
        special_event_data = {
            "name": title,
            "description": event_type,
            "start_time": start_date_time,
            "end_time": end_date_time,
            "lat": lat,
            "lon": lon,
            "attendance": int(float(number_of_attendees.replace(",", ""))),
            "__module__": "pyticas_tetres.ttypes",
            "__class__": "SpecialEventInfo"
        }

        return special_event_data

    def adjust_end_date_time(self, start_date_time, end_date_time):
        import datetime
        start_date_time_object = datetime.datetime.strptime(start_date_time, '%Y-%m-%d %H:%M:%S')
        end_date_time_object = datetime.datetime.strptime(end_date_time, '%Y-%m-%d %H:%M:%S')
        if start_date_time_object > end_date_time_object:
            end_date_time_object = end_date_time_object + datetime.timedelta(days=1)
        return end_date_time_object.strftime('%Y-%m-%d %H:%M:%S')

    def get_creatable_special_event_dict(self, special_event_excel_reader):
        creatable_dict = dict()
        special_event_api_reader = SpecialEventAPIReader(base_url=self.base_url, list_url=self.list_url)
        data_in_excel_count = 0
        for sheet_name, sheet_object in special_event_excel_reader.sheet_dict.items():
            rows = sheet_object.get_rows()
            for index, each_row in enumerate(rows):
                if index == 0:
                    continue
                special_event_data = self.excel_row_to_data_dict(row=each_row, location_narrative=sheet_name,
                                                                 special_event_excel_reader=special_event_excel_reader)
                data_tuple = (
                    special_event_data['name'], special_event_data['description'], special_event_data['start_time'],
                    special_event_data['end_time'], special_event_data['lat'], special_event_data['lon'],
                    special_event_data['attendance'])
                if data_tuple not in special_event_api_reader.dict_data and data_tuple not in creatable_dict:
                    creatable_dict[data_tuple] = special_event_data
                data_in_excel_count += 1
        print("{} rows of data in excel.".format(data_in_excel_count))
        print("{} rows of data is creatable.".format(len(creatable_dict)))
        return creatable_dict

    def post_special_event_data(self, special_event_excel_reader):
        creatable_dict = self.get_creatable_special_event_dict(special_event_excel_reader=special_event_excel_reader)
        for special_event_data in creatable_dict.values():
            json_data = json.dumps(special_event_data)
            data = {
                "data": json_data
            }
            try:
                requests.post(self.post_url, data=data)
            except Exception as e:
                print("Error: ", data, e)

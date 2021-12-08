import os
import string
import sys

import xlsxwriter
from tetres_data_populator.mixins.excel_reader_mixin import ExcelReaderMixin

moe_index_dict = {"vmt": 3, "vht": 4, "dvh": 5, "lvmt": 6, "uvmt": 7, "cm": 8, "cmh": 9}


def tt_aggregate(data):
    return sum([each_row[1].value for each_row in data])


def vmt_aggregate(data):
    index = moe_index_dict["vmt"]
    return sum([float(each_row[index].value) for each_row in data if each_row[index].value])


def vht_aggregate(data):
    index = moe_index_dict["vht"]
    return sum([float(each_row[index].value) for each_row in data if each_row[index].value])


def dvh_aggregate(data):
    index = moe_index_dict["dvh"]
    return sum([float(each_row[index].value) for each_row in data if each_row[index].value])


def lvmt_aggregate(data):
    index = moe_index_dict["lvmt"]
    return sum([float(each_row[index].value) for each_row in data if each_row[index].value])


def uvmt_aggregate(data):
    index = moe_index_dict["uvmt"]
    return sum([float(each_row[index].value) for each_row in data if each_row[index].value])


def cm_aggregate(data):
    index = moe_index_dict["cm"]
    return sum([float(each_row[index].value) for each_row in data if each_row[index].value])


def cmh_aggregate(data):
    index = moe_index_dict["cmh"]
    return sum([float(each_row[index].value) for each_row in data if each_row[index].value])


def populate_data_in_memory(each_row, daily_data_dict, monthly_data_dict, yearly_data_dict):
    date_time = each_row[0].value
    daily_time = date_time.split()[0]
    monthly_time = daily_time[:7]
    yearly_time = monthly_time[:4]
    if daily_time not in daily_data_dict:
        daily_data_dict[daily_time] = list()
    daily_data_dict[daily_time].append(each_row)
    if monthly_time not in monthly_data_dict:
        monthly_data_dict[monthly_time] = list()
    monthly_data_dict[monthly_time].append(each_row)
    if yearly_time not in yearly_data_dict:
        yearly_data_dict[yearly_time] = list()
    yearly_data_dict[yearly_time].append(each_row)


def prepare_aggregated_data(yearly_data_dict, monthly_data_dict, daily_data_dict):
    yearly_aggregated_data_dict = dict()
    monthly_aggregated_data_dict = dict()
    daily_aggregated_data_dict = dict()

    for each_moe in moe_index_dict.keys():
        for yearly_time, yearly_data in yearly_data_dict.items():
            if yearly_time not in yearly_aggregated_data_dict:
                yearly_aggregated_data_dict[yearly_time] = dict()
            yearly_aggregated_data_dict[yearly_time][each_moe] = getattr(sys.modules[__name__],
                                                                         "{}_aggregate".format(each_moe))(yearly_data)
        for monthly_time, monthly_data in monthly_data_dict.items():
            if monthly_time not in monthly_aggregated_data_dict:
                monthly_aggregated_data_dict[monthly_time] = dict()
            monthly_aggregated_data_dict[monthly_time][each_moe] = getattr(sys.modules[__name__],
                                                                           "{}_aggregate".format(each_moe))(
                monthly_data)
        for daily_time, daily_data in daily_data_dict.items():
            if daily_time not in daily_aggregated_data_dict:
                daily_aggregated_data_dict[daily_time] = dict()
            daily_aggregated_data_dict[daily_time][each_moe] = getattr(sys.modules[__name__],
                                                                       "{}_aggregate".format(each_moe))(daily_data)
    return yearly_aggregated_data_dict, monthly_aggregated_data_dict, daily_aggregated_data_dict


def create_excel_file(filename):
    base_path, only_filename = os.path.split(filename)
    new_filename = "{}_aggregated.xlsx".format(only_filename.split(".xlsx")[0])
    new_filename = os.path.join(base_path, new_filename)
    workbook = xlsxwriter.Workbook(new_filename)
    return workbook


def write_into_excel_file(workbook, sheet_name, yearly_aggregated_data_dict, monthly_aggregated_data_dict,
                          daily_aggregated_data_dict):
    data_dict = {
        "yearly_aggregated_data_dict": yearly_aggregated_data_dict,
        "monthly_aggregated_data_dict": monthly_aggregated_data_dict,
        "daily_aggregated_data_dict": daily_aggregated_data_dict
    }
    for time_range in ["yearly", "monthly", "daily"]:
        current_sheet_name = "{} {}".format(sheet_name, time_range.capitalize())
        current_sheet = workbook.add_worksheet(name=current_sheet_name)
        for i, column_value in enumerate(["time"] + list(moe_index_dict.keys())):
            column_number = string.ascii_uppercase[i] + "1"
            current_sheet.write(column_number, column_value)
        current_data_dict = data_dict["{}_aggregated_data_dict".format(time_range)]
        for i, actual_time_range in enumerate(list(current_data_dict.keys())):
            row_number = i + 2
            value_dict = current_data_dict[actual_time_range]
            for j, value in enumerate([actual_time_range] + list(value_dict.values())):
                column_number = string.ascii_uppercase[j] + str(row_number)
                current_sheet.write(column_number, value)


if __name__ == "__main__":
    filename = input("Please type the full path of the excel file: \n")
    workbook = create_excel_file(filename)
    excel_reader = ExcelReaderMixin(filename=filename)

    sheets = excel_reader.xl_workbook.sheets()

    for index, sheet in enumerate(sheets):
        if index:
            yearly_data_dict = dict()
            monthly_data_dict = dict()
            daily_data_dict = dict()
            all_rows = excel_reader.get_all_rows(sheet.name)
            for i, each_row in enumerate(all_rows):
                # skipping rows 0, 1, 2
                if i < 3:
                    continue
                populate_data_in_memory(each_row, daily_data_dict, monthly_data_dict, yearly_data_dict)
            yearly_aggregated_data_dict, monthly_aggregated_data_dict, daily_aggregated_data_dict = prepare_aggregated_data(
                yearly_data_dict, monthly_data_dict, daily_data_dict)
            write_into_excel_file(workbook, sheet.name, yearly_aggregated_data_dict, monthly_aggregated_data_dict,
                                  daily_aggregated_data_dict)
    workbook.close()

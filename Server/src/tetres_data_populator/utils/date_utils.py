from datetime import datetime

import xlrd


def get_formatted_date_from_xl_date(xldate, xl_workbook):
    date_tuple = xlrd.xldate_as_tuple(xldate, xl_workbook.datemode)
    year = str(date_tuple[0])
    month = str(date_tuple[1]).zfill(2)
    day = str(date_tuple[2]).zfill(2)
    formatted_date = "-".join([year, month, day])
    return formatted_date


def get_formatted_time_from_xl_date(xldate, xl_workbook):
    date_tuple = xlrd.xldate_as_tuple(xldate, xl_workbook.datemode)
    hour = str(date_tuple[3]).zfill(2)
    minute = str(date_tuple[4]).zfill(2)
    second = str(date_tuple[5]).zfill(2)
    formatted_time = ":".join([hour, minute, second])
    return formatted_time


def get_formatted_date_time(xldate, xl_workbook, add_date_end_time_offset=False):
    formatted_date = get_formatted_date_from_xl_date(xldate=xldate, xl_workbook=xl_workbook)
    if add_date_end_time_offset:
        formatted_time = "23:55:00"
    else:
        formatted_time = get_formatted_time_from_xl_date(xldate=xldate, xl_workbook=xl_workbook)
    formatted_date_time = " ".join([formatted_date, formatted_time])
    return formatted_date_time


def get_duration(start_time, end_time):
    """
    :param start_time: datetime string in format '%Y-%m-%d %H:%M:%S'
    :param end_time: datetime string in format '%Y-%m-%d %H:%M:%S'
    :return: duration between start_time and end_time in hours
    """
    _format = '%Y-%m-%d %H:%M:%S'
    start_date_time_obj = datetime.strptime(start_time, _format)
    end_date_time_obj = datetime.strptime(end_time, _format)
    delta = end_date_time_obj - start_date_time_obj
    return round(delta.total_seconds() / 3600, 2)


def get_years(start_date_string, end_date_string):
    start_year = int(start_date_string.split("-")[0])
    end_year = int(end_date_string.split("-")[0])
    year_list = list(range(start_year, end_year + 1))
    year_list = [str(i) for i in year_list]
    return year_list

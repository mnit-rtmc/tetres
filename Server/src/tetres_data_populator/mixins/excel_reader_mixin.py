import xlrd
from xlrd.sheet import ctype_text

from tetres_data_populator.utils.date_utils import get_formatted_date_time


class ExcelReaderMixin:
    def __init__(self, filename):
        self.filename = filename
        self.xl_workbook = xlrd.open_workbook(self.filename)
        self.sheet_dict = self.get_sheet_dict()

    @staticmethod
    def get_discriminatory_key(discriminatory_properties, data_dict):
        list_key = []
        for key in discriminatory_properties:
            list_key.append(data_dict[key])
        return tuple(list_key)

    def get_all_rows(self, sheet_name):
        sheet = self.sheet_dict[sheet_name]
        return sheet.get_rows()

    def get_sheet_dict(self):
        sheet_dict = dict()
        sheets = self.xl_workbook.sheets()
        for sheet in sheets:
            sheet_dict[sheet.name] = sheet
        return sheet_dict

    def get_date_time(self, cell, default_date_time, add_date_end_time_offset=False):
        date_time = None
        if ctype_text.get(cell.ctype) == "xldate":
            date_time = get_formatted_date_time(xldate=cell.value, xl_workbook=self.xl_workbook,
                                                add_date_end_time_offset=add_date_end_time_offset)
        elif ctype_text.get(cell.ctype) == "empty":
            date_time = default_date_time if default_date_time else ""
        else:
            print(
                "Invalid date. Type: {}. Value: {}.".format(ctype_text.get(cell.ctype),
                                                            cell.value))
        return date_time

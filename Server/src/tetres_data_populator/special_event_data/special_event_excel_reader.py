import xlrd


class SpecialEventExcelReader:
    def __init__(self, filename):
        self.filename = filename
        self.xl_workbook = xlrd.open_workbook(self.filename)
        self.sheet_dict = self.get_sheet_dict()

    def get_sheet_dict(self):
        sheet_dict = dict()
        sheets = self.xl_workbook.sheets()
        for sheet in sheets:
            if sheet.name == 'Cover':
                continue
            sheet_dict[sheet.name] = sheet
        return sheet_dict

    def get_all_rows(self, sheet_name):
        sheet = self.sheet_dict[sheet_name]
        return sheet.get_rows()

    def get_formatted_date_from_xl_date(self, xldate):
        date_tuple = xlrd.xldate_as_tuple(xldate, self.xl_workbook.datemode)
        year = str(date_tuple[0])
        month = str(date_tuple[1]).zfill(2)
        day = str(date_tuple[2]).zfill(2)
        formatted_date = "-".join([year, month, day])
        return formatted_date

    def get_formatted_time_from_xl_date(self, xldate):
        date_tuple = xlrd.xldate_as_tuple(xldate, self.xl_workbook.datemode)
        hour = str(date_tuple[3]).zfill(2)
        minute = str(date_tuple[4]).zfill(2)
        second = str(date_tuple[5]).zfill(2)
        formatted_time = ":".join([hour, minute, second])
        return formatted_time

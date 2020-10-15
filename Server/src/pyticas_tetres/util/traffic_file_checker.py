import os
from global_settings import DATA_PATH
import datetime


def has_traffic_files(start_date_str, end_date_str):
    try:
        detector_path = os.path.join(DATA_PATH, 'cache', 'det')
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        except:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
        if start_date > end_date:
            return False
        while start_date <= end_date:
            day_path = os.path.join(detector_path, "{}".format(start_date.year),
                                    "{}{}{}".format(start_date.year, str(start_date.month).zfill(2),
                                                    str(start_date.day).zfill(2)))
            if not os.listdir(day_path):
                return False
            start_date += datetime.timedelta(days=1)
    except Exception:
        return False
    return True

from datetime import datetime, timedelta
import sys

sys.path.append("Server/src")

from pyticas.dr.det_reader_raw import _save_file_to_cache
from pyticas.tool import http


def gen_days(start_date_string, end_date_string=None):
    year, month, day = [int(i) for i in start_date_string.split('-')]
    start_date = datetime(year, month, day)
    if end_date_string:
        year, month, day = [int(i) for i in start_date_string.split('-')]
        end_date = datetime(year, month, day)
    else:
        end_date = datetime.today() - timedelta(days=1)
    d = start_date
    dates = [start_date]
    while d < end_date:
        d += timedelta(days=1)
        dates.append(d)
    return dates


class TrafficType:
    def __init__(self, extension):
        self.extension = extension


if __name__ == "__main__":
    import global_settings
    from pyticas import ticas, cfg
    from pyticas.infra import Infra


    class TrafficType:
        def __init__(self, extension):
            self.extension = extension


    ticas.initialize(global_settings.DATA_PATH)
    infra = Infra.get_infra()
    sdt_str = input('# Enter start date to load data (e.g. 2015-01-01) : ')
    edt_str = input('# Enter end date to load data (e.g. 2017-12-31) : ')
    days = gen_days(start_date_string=sdt_str, end_date_string=edt_str)
    formats = ("v30", "c30")
    success_count = 0
    fail_count = 0
    for day in days:
        dirname = str(day.year) + str(day.month).zfill(2) + str(day.day).zfill(2)
        print("Downloading traffic data for {}".format(dirname))
        for detector in infra.detectors:
            for format in formats:
                remote_file = cfg.TRAFFIC_DATA_URL + '/' + str(day.year) + '/' + dirname + '/' + detector + "." + format
                try:
                    with http.get_url_opener(remote_file, timeout=30) as res:
                        binData = res.read()
                        if binData:
                            _save_file_to_cache(detector, day, binData, TrafficType("." + format))
                            success_count += 1
                except Exception as e:
                    fail_count += 1
    print("Success: {}".format(success_count))
    print("Fail: {}".format(fail_count))

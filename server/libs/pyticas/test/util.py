# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import glob
import datetime
import csv

def rm_dir(dir_path):
    """ delete sub directory of test directory safely

    :param dir_path: directory path to delete
    :type dir_path: str
    :return: True or False
    """

    cur_path = os.path.dirname(__file__)
    if cur_path not in dir_path or cur_path == dir_path:
        return False
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

    os.rmdir(dir_path)
    return True

def read_traffic_data(target_dir):
    """ read traffic data file

    :type target_dir: str
    :rtype: dict[str, mixed]
    """
    traffic_data_source = os.path.join(os.path.dirname(__file__), target_dir)
    cases = []
    for f in glob.glob1(traffic_data_source, '*.csv'):
        station_name, t_start_time, t_end_time, t_interval = f.replace('.csv', '').split('-')
        start_datetime = datetime.datetime.strptime(t_start_time, '%Y%m%d%H%M')
        end_datetime = datetime.datetime.strptime(t_end_time, '%Y%m%d%H%M')
        interval = int(t_interval)
        data = {}
        ffile = os.path.join(traffic_data_source, f)
        with open(ffile, 'r') as csvfile:
            for row in csv.reader(csvfile):
                data[row[0]] = [ float(d) for d in row[1:]]
        case = {'name' : station_name,
                      'start_datetime' : start_datetime,
                      'end_datetime' : end_datetime,
                      'interval' : interval,
                      'file_name' : f,
                      'file_path' : ffile}

        for k, r in data.items():
            case[k] = r

        cases.append(case)

    return cases

def read_weather_data(target_dir):
    """ read weather data file

    :type target_dir: str
    :rtype: dict[str, mixed]
    """
    weather_data_source = os.path.join(os.path.dirname(__file__), target_dir)
    cases = []
    for f in glob.glob1(weather_data_source, '*.csv'):
        site_id, t_start_time, t_end_time = f.replace('.csv', '').split('-')
        start_datetime = datetime.datetime.strptime(t_start_time, '%Y%m%d%H%M')
        end_datetime = datetime.datetime.strptime(t_end_time, '%Y%m%d%H%M')
        data = {}
        ffile = os.path.join(weather_data_source, f)
        with open(ffile, 'r') as csvfile:
            for idx, row in enumerate(csv.reader(csvfile)):
                if str(row[1]).replace('.', '').isdigit():
                    data[row[0]] = [ float(d) for d in row[1:]]
                else:
                    data[row[0]] = [ d.strip() if d.strip() != 'None' else None for d in row[1:]]


        case = {'site_id' : int(site_id),
                'start_datetime' : start_datetime,
                'end_datetime' : end_datetime,
                'file_name' : f,
                'file_path' : ffile}

        for k, r in data.items():
            case[k] = r

        cases.append(case)

    return cases


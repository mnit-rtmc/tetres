import os
import shutil
from zipfile import ZipFile
import sys
sys.path.append("Server/src")
import global_settings

DATA_DIRECTORY = global_settings.DATA_PATH
CACHE_DIRECTORY = os.path.join(DATA_DIRECTORY, "cache")
DET_DIRECTORY = os.path.join(CACHE_DIRECTORY, "det")


def create_traffic_data_container():
    print("Creating traffic data container...")
    print("Creating: {} ...".format(os.path.abspath(DATA_DIRECTORY)))
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)
    print("Creating: {} ...".format(os.path.abspath(CACHE_DIRECTORY)))

    if not os.path.exists(CACHE_DIRECTORY):
        os.makedirs(CACHE_DIRECTORY)
    print("Creating: {} ...".format(os.path.abspath(DET_DIRECTORY)))
    if not os.path.exists(DET_DIRECTORY):
        os.makedirs(DET_DIRECTORY)
    print("Done!")


def extract_yearly_traffic_data(yearly_traffic_data_directory):
    if not os.path.exists(yearly_traffic_data_directory):
        print("Failed. Cannot find a directory named: {} in the system".format(yearly_traffic_data_directory))
        return
    print("Starting traffic data extraction...")
    year_wise_directory = None
    for traffic_file in os.listdir(yearly_traffic_data_directory):
        if not traffic_file.endswith(".traffic"):
            continue
        if year_wise_directory is None:
            try:
                year = traffic_file[:4]
                year_wise_directory = os.path.join(DET_DIRECTORY, year)
                if not os.path.exists(year_wise_directory):
                    os.makedirs(year_wise_directory)
                print("Created traffic data directory for the year: {}. Directory: {}".format(year, os.path.abspath(
                    year_wise_directory)))
            except Exception as e:
                print("Failed to create year-wise directory. Error: {}".format(e))
                return
        try:
            day = traffic_file.split(".traffic")[0]
        except Exception as e:
            print("Failed to extract day information from .traffic file. Error: {}".format(e))
            continue
        try:
            day_wise_directory = os.path.join(year_wise_directory, day)
            if os.path.exists(day_wise_directory):
                shutil.rmtree(day_wise_directory)
                print("Removing existing traffic data for the day: {}".format(day))
            os.makedirs(day_wise_directory)
            print("Created traffic data directory for the day: {}. Directory: {}".format(day, os.path.abspath(
                day_wise_directory)))
            traffic_file_directory = os.path.join(yearly_traffic_data_directory, traffic_file)
            print("Extracting traffic data for the day {} ...".format(day))
            with ZipFile(traffic_file_directory, 'r') as zip_obj:
                zip_obj.extractall(day_wise_directory)
            print("Done Extracting traffic data for the day {} ...".format(day))
            print()
            print()
        except Exception as e:
            print("Failed to extract traffic data for the date: {}. Error: {}".format(day, e))

    if year_wise_directory is None:
        print("Couldn't find any .traffic files to extract in the specified directory: {}".format(yearly_traffic_data_directory))


if __name__ == "__main__":
    create_traffic_data_container()
    traffic_data_directories = list()
    print(
        "Please type the full path of the folder for a specific year's traffic data and then press enter. For example:")
    print("D:\Traffic Data\\2011")
    while True:
        print("Please type the full path in the space below:")
        directory_name = input()
        traffic_data_directories.append(directory_name)
        choice = input("Do you want to add another directory[y/n]: ")
        if choice.lower() == "n":
            break
    for traffic_data_directory in traffic_data_directories:
        try:
            extract_yearly_traffic_data(traffic_data_directory)
        except Exception as e:
            print(e)

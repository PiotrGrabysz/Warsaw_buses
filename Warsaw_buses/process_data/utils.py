from pathlib import Path
import json
import sys
import numpy as np


def dist(lat1, lon1, lat2, lon2):
    """ Returns a distance between two locations using formula described here:
    https://andrew.hedges.name/experiments/haversine/ """

    # Convert coordinates in degrees into radians
    lat1_r = np.radians(lat1)
    lat2_r = np.radians(lat2)
    lon1_r = np.radians(lon1)
    lon2_r = np.radians(lon2)

    # Radius of the Earth
    R = 6373.

    # haversine formula:
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_r) * np.cos(lat2_r) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    d = R * c

    return d


def bus_data_iterator(dir_to_busestrams: str) -> list:
    """For a given directory with busestrams data it returns a list containing all the files with busestrams data
    in this directory. Such list is used in many places in the module, so I moved it into the separate function.

    If there are no files satisfying proper conditions an error is thrown and the whole program quits.

    :param dir_to_busestrams: The directory where the busestrams data are stored in.
    :return: List.
    """

    # Check if the directory exists:
    try:
        if not Path(dir_to_busestrams).exists():
            raise FileNotFoundError(f"Error! This directory does not exist: {dir_to_busestrams}")
    except FileNotFoundError as er:
        print(er)
        sys.exit("Due to the non existing directory I have to shut down the program.")
        
    # dir_to_busestrams has the following structure: dir_to_busestrams / "line/brigade/vehicle.txt"

    paths_in_dir = Path(dir_to_busestrams).glob('*/*/*')
    # files_list is a list of all the files in the directory dir_to_busestrams
    bus_files_list = [x for x in paths_in_dir if x.is_file()]

    return bus_files_list


def timetables_iterator(dir_to_timetables: str, line: str) -> list:

    # check if the directory exists:
    try:
        if not Path(dir_to_timetables).exists():
            raise FileNotFoundError(f"Error! This directory does not exist: '{dir_to_timetables}'")
    except FileNotFoundError as er:
        print(er)
        sys.exit("Due to the non existing directory I have to shut down the program.")

    # the files I am looking for have the path structure: dir_timetables / line / busstopId_busstopNr.json
    p = Path(dir_to_timetables).glob(f"{line}/*")
    # files_list is a list of all the timetables for the given line at the given stop
    files_list = [x for x in p if x.is_file()]
    return files_list


def divided_map_area(round_to: int) -> [float, float]:

    lat1 = 52.0
    lon1 = 21.0
    lat2 = 52.0 + 0.1**round_to
    lon2 = 21.0 + 0.1**round_to

    height = dist(lat1, lon1, lat2, lon1)
    width = dist(lat1, lon1, lat1, lon2)

    return height, width


def how_many_stop(dir_to_stops_coord: str) -> None:
    """How many records are int stops coord"""
    try:
        with open(dir_to_stops_coord, "r") as f:
            stops_coord = json.load(f)
    except FileNotFoundError as err:
        print(err)
        sys.exit()

    for counter, _ in enumerate(stops_coord):
        pass
    print(f"There are {counter+1} stops.")

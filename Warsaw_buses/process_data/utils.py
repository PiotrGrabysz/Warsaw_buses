from pathlib import Path
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

    # dir_to_busestrams has the following structure: dir_to_busestrams / "line/brigade/vehicle.txt"

    paths_in_dir = Path(dir_to_busestrams).glob('*/*/*')
    # files_list is a list of all the files in the directory dir_to_busestrams
    bus_files_list = [x for x in paths_in_dir if x.is_file()]
    return bus_files_list

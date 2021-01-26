""" This is velocity analysis"""

from pathlib import Path
import os
import numpy as np
import pandas as pd
import datetime

def dist(lat1, lon1, lat2, lon2):
    """ Using formula described here: https://andrew.hedges.name/experiments/haversine/"""

    # Convert coordinates in degrees into radians
    lat1_r = np.radians(lat1)
    lat2_r = np.radians(lat2)
    lon1_r = np.radians(lon1)
    lon2_r = np.radians(lon2)

    # Radius of the Earth
    R = 6373.

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = np.sin(dlat/2)**2 + np.cos(lat1_r)*np.cos(lat2_r) * np.sin(dlon/2)**2
    c = 2*np.arctan2(np.sqrt(a), np.sqrt(1-a))
    d = R * c

    return d


def calc_velocity(dir_to_busestrams: str):

    # for path in Path(dir_to_busestrams).iterdir():
    #     if path.is_dir():
    #         pass
    # for file_name in os.listdir(folder_name):
    #     if file_name.endswith(".json"):
    #         file_path = os.path.join(folder_name, file_name)
    #         with open(file_path) as file:
    #             data = json.load(file)

    p = Path(dir_to_busestrams).glob('*/*')
    # files_list is a list of all files in the directory dir_to_busestrams
    files_list = [x for x in p if x.is_file()]
    for bus_file in files_list:

        bus_data = pd.read_csv(bus_file, names=["Lat", "Lon", "Time"])

        # Calculating time differences:
        time_column = pd.to_datetime(bus_data["Time"]).dt.strftime('%H:%M:%S')
        time_column = pd.to_timedelta(time_column).dt.total_seconds()
        # I convert it into numpy.array to make arithmetic operations without the loop
        time_column = time_column.to_numpy()
        time_diffs = (time_column[1:] - time_column[:-1])

        # Calculating distance in space:
        lat1 = bus_data["Lat"].to_numpy()[1:]
        lon1 = bus_data["Lon"].to_numpy()[1:]
        lat2 = bus_data["Lat"].to_numpy()[:-1]
        lon2 = bus_data["Lon"].to_numpy()[:-1]

        tmp = np.sum(time_diffs == 0)
        if tmp > 0 :
            print(bus_file)
            
        velocity = dist(lat1, lon1, lat2, lon2) / time_diffs

        # For now, velocity is in km/s. Convert it into km/h:
        velocity = velocity * 3600.

        # Creating new pd.DataFrame
        new_bus_data = bus_data.iloc[1:].assign(velocity=velocity)

        # Saving new data frame to a file.
        # I want to save this file in another directory than bus_data to be sure that it didn't mess around anything in
        # the original data. But I want this new directory to have similar structure.
        file_path_split = bus_file.parts
        # The new directory has the same beginning, but name of folder with all buses is suffixed with "_with_velocity"
        new_file_path = Path("/".join(file_path_split[:-3])) / (file_path_split[-3] + "_with_velocity")
        # file_path_split[-2] is the line number of the bus
        new_file_path = new_file_path / file_path_split[-2]
        # Create new directory in case it doesn't exist yet
        Path(new_file_path).mkdir(parents=True, exist_ok=True)
        # Append file_name (brigade number) to the new_path
        new_file_path = new_file_path / file_path_split[-1]
        # Save pd.DataFrame() to the file
        new_bus_data.to_csv(new_file_path)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", "-d", type=str)
    args = parser.parse_args()

    calc_velocity(dir_to_busestrams=args.dir)

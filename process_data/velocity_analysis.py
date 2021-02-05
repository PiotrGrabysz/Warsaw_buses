""" This is speed analysis"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle

def dist(lat1, lon1, lat2, lon2):
    """ Returns a distance between to locations using formula described here:
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


def calc_speed(dir_to_busestrams: str):
    """ For a given directory with busestrams data it creates NEW directory where a column describing speed is added to
    each data file."""

    # dir_to_busestrams has structure: dir_to_busestrams / "line/brigade/vehicle.txt"
    p = Path(dir_to_busestrams).glob('*/*/*')
    # files_list is a list of all the files in the directory dir_to_busestrams
    files_list = [x for x in p if x.is_file()]
    for bus_file in files_list:
        bus_data = pd.read_csv(bus_file, names=["Lat", "Lon", "Time"])

        # Calculating time differences:
        time_column = pd.to_datetime(bus_data["Time"]).dt.strftime('%H:%M:%S')
        time_column = pd.to_timedelta(time_column).dt.total_seconds()
        # I convert it into numpy.array to make arithmetic operations without the loop
        time_column = time_column.to_numpy()
        time_diffs = (time_column[1:] - time_column[:-1])

        # Calculating distance:
        lat1 = bus_data["Lat"].to_numpy()[1:]
        lon1 = bus_data["Lon"].to_numpy()[1:]
        lat2 = bus_data["Lat"].to_numpy()[:-1]
        lon2 = bus_data["Lon"].to_numpy()[:-1]

        # Calculating speed
        speed = dist(lat1, lon1, lat2, lon2) / time_diffs

        # For now, speed is in km/s. Convert it into km/h:
        speed = speed * 3600.

        # Creating new pd.DataFrame
        new_bus_data = bus_data.iloc[1:].assign(Speed=speed)

        # Saving the new data frame to a file.
        # I want to save this file in different directory than the dir_to_busestrams to be sure that it didn't mess
        # around anything in the original data. But I want this new directory to have similar structure.
        # I keep the path almost the same, but I suffix the name of folder where all the buses are stored
        # with "_with_speed". So the path
        # " * /busestrams_folder/line_number/brigade_number/vehicle_number.txt"
        # becomes
        # " * /busestrams_folder_with_speed/line_number/brigade_number/vehicle_number.txt"

        file_path_split = bus_file.parts
        # The new directory has the same beginning, but the name of a folder with all the buses is suffixed with
        # "_with_speed"
        new_file_path = Path("/".join(file_path_split[:-4])) / (file_path_split[-4] + "_with_speed")
        # file_path_split[-2] is the line number of the bus
        new_file_path = new_file_path / file_path_split[-3] / file_path_split[-2]
        # Create new directory in case it doesn't exist yet
        Path(new_file_path).mkdir(parents=True, exist_ok=True)
        # Append file_name (brigade number) to the new_path
        new_file_path = new_file_path / file_path_split[-1]
        # Save pd.DataFrame() to the file
        new_bus_data.to_csv(new_file_path)


def speed_statistics(dir_to_data: str, speed: float = 50., outlier_speed: float = None):
    """
    Print percent of times when the given speed is exceeded and maximal and minimal speed. It also plots the
    histogram of all the measured speeds.

    :param dir_to_data: directory to the folder containing busestrams data. By default it should be a folder with the
    name ending with "with_speed".
    :param speed: percent of times when exceeding speed is printed
    :param outlier_speed: if specified, speeds greater than outlier_speed are not taken into consideration.
    :return: None
    """

    # number of all measurements
    total_number_of_records = 0
    # number of measurements when a bus exceeded given speed
    exceeding_speed = 0
    # impossible_speed = 120.  # THIS IS FOR TRACKING WEIRD OUTLIERS!

    # Very long list with all the measured speed. Used for plotting a histogram
    # TODO change in to a dict with specified intervals:
    speed_list = []

    # dir_to_data has structure: dir_to_data / "line/brigade/vehicle.txt"
    p = Path(dir_to_data).glob('*/*/*')
    # files_list is a list of all files in the directory dir_to_busestrams
    files_list = [x for x in p if x.is_file()]
    for bus_file in files_list:
        bus_data = pd.read_csv(bus_file, usecols=["Speed"])

        if outlier_speed is not None:
            # Inform the user if speed greater than the outlier_speed is found
            if sum(bus_data["Speed"] > outlier_speed) > 0:
                print(f"Warning! I found a bus with speed faster than {outlier_speed} in the file {bus_file}")
            # Filter out all rows containing speed greater than the outlier_speed
            bus_data = bus_data[bus_data["Speed"] < outlier_speed]

        total_number_of_records += len(bus_data)
        exceeding_speed += sum(bus_data["Speed"] > speed)

        speed_list += bus_data["Speed"].tolist()

    # Print some statistics:
    print(f"Maximal measured speed: {max(speed_list)}\nMinimal measured speed: {min(speed_list)}")
    print(f"Percent of times when any bus exceeds {speed} km/h vs all measurements is "
          f"{100 * exceeding_speed / total_number_of_records :.2f}%.")

    # Show the histogram:
    # TODO labels
    speed_numpy = np.array(speed_list)
    plt.hist(speed_numpy, bins=30, density=True)
    plt.show()


def exceeding_the_speed_location(dir_to_data: str, speed: float, outlier_speed: float = None):

    exceeding_location_list = []
    p = Path(dir_to_data).glob('*/*/*')
    # files_list is a list of all files in the directory dir_to_busestrams
    files_list = [x for x in p if x.is_file()]
    for bus_file in files_list:
        bus_data = pd.read_csv(bus_file)
        exceeding_location = bus_data.query(f"speed > {speed} & speed < {outlier_speed}")

        if sum(bus_data["Speed"] > 50.) > 1:
            line_number = bus_file.parts[-3]
            # for _, row in bus_data.loc[(bus_data["Speed"]) > 50. & (bus_data["Speed"] < filter_outliers)].iterrows():
            for _, row in exceeding_location.iterrows():
                exceeding_location_list.append({"Line": line_number,
                                           "Lat": row["Lat"],
                                           "Lon": row["Lon"]})

    # results_path = Path("../data/speed_exceeded.txt")
    results_path = Path("../data/speed_exceeded_pickle2")
    with results_path.open("wb") as f:
        # for line in exceeding_location:
        #     f.write(f"{line}\n")
        pickle.dump(exceeding_location_list, f)


def exceeding_the_speed_location2(dir_to_data: str, speed: float, round_to: int = 2,
                                  outlier_speed: float = None) -> dict:
    """

    :param dir_to_data:
    :param speed:
    :param round_to:
    :param outlier_speed:
    :return:
    """
    exceeding_locations_dict = dict()
    p = Path(dir_to_data).glob('*/*/*')
    # files_list is a list of all files in the directory dir_to_busestrams
    files_list = [x for x in p if x.is_file()]
    for bus_file in files_list:
        bus_data = pd.read_csv(bus_file)

        if outlier_speed is not None:
            # Filter out all rows containing speed greater than the outlier_speed
            bus_data = bus_data[bus_data["Speed"] < outlier_speed]

        for _, row in bus_data[bus_data["Speed"]>speed].iterrows(): # TODO what happens when this is emtpy?
            location = (round(row["Lat"], round_to), round(row["Lon"], round_to))
            if location in exceeding_locations_dict:
                exceeding_locations_dict[location] += 1
            else:
                exceeding_locations_dict[location] = 1

    return exceeding_locations_dict


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", "-d", type=str)
    parser.add_argument("--calc_speed", action="store_true")
    parser.add_argument("--statistics", action="store_true")
    parser.add_argument("--locations", action="store_true")
    parser.add_argument("--speed", "-s", type=float, default=50.)
    args = parser.parse_args()

    if args.calc_speed:
        print("Starts calculating speed...")
        calc_speed(dir_to_busestrams=args.dir)
        print("calc_speed run successfully.")

    new_path = args.dir + "_with_speed"
    if args.statistics:
        print("Starts calculating statistics...")
        speed_statistics(dir_to_data=new_path, speed=args.speed, outlier_speed=120.)

    if args.locations:
        print(f"Looking for locations were {args.speed} is exceeded...")
        exceeding_locations_dict = exceeding_the_speed_location2(dir_to_data=new_path,
                                                                 speed=args.speed,
                                                                 round_to=1,
                                                                 outlier_speed=120.)
        # I want to find locations were the speed is exceeded significant amount of times
        all_locations = sum(exceeding_locations_dict.values())
        cum_sum = 0
        for val in sorted(exceeding_locations_dict.values(), reverse=True):
            cum_sum += val
            print(f"{val} which is {100*(val/all_locations):.2f}%")
            if cum_sum/all_locations > 0.9:
                break

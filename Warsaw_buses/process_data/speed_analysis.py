""" This is speed analysis"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle


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


def calc_speed(dir_to_busestrams: str, dir_to_output_data: str = None) -> None:
    """For the given directory with busestrams data it creates NEW directory where in each file a column describing the
    speed is added. By default dir_to_output_data is dir_to_busestrams suffixed with "_with_speed". As a result, the
    following file:
    'dir_to_busestrams/line_number/brigade_number/vehicle_number.txt'
    is used to create a new file with speed column added in the directory:
    dir_to_busestrams_with_speed/line_number/brigade_number/vehicle_number.txt'
    It is recommended in most cases. Specifying dir_to_output_data is useful in tests.

    :param dir_to_busestrams: The directory where the busestrams data are stored in.
    :param dir_to_output_data: The directory where the created files with speed are saved in. If None, then it is
    dir_to_output_data is dir_to_busestrams suffixed with "_with_speed".
    :return: None.
    """

    # I want to save this file in different directory than the dir_to_busestrams to be sure that it didn't mess
    # around anything in the original data. But I want this new directory to have similar structure.
    if dir_to_output_data is None:
        # By default dir_to_output_data is dir_to_busestrams suffixed with "_with_speed"
        dir_to_output_data = Path(dir_to_busestrams + "_with_speed")

    for bus_file in bus_data_iterator(dir_to_busestrams=dir_to_busestrams):
        # Read the bus data
        bus_data = pd.read_csv(bus_file, names=["Lat", "Lon", "Time"])

        # Calculating time differences:
        time_column = pd.to_datetime(bus_data["Time"]).dt.strftime('%H:%M:%S')
        time_column = pd.to_timedelta(time_column).dt.total_seconds()
        # I convert it into numpy.array to make arithmetic operations without the loop
        time_column = time_column.to_numpy()
        time_diffs = (time_column[1:] - time_column[:-1])

        # Calculating the distance:
        lat1 = bus_data["Lat"].to_numpy()[1:]
        lon1 = bus_data["Lon"].to_numpy()[1:]
        lat2 = bus_data["Lat"].to_numpy()[:-1]
        lon2 = bus_data["Lon"].to_numpy()[:-1]

        # Calculating speed
        speed = dist(lat1, lon1, lat2, lon2) / time_diffs

        # For now, the speed is in km/s. Convert it into km/h:
        speed = speed * 3600.

        # Create a new pd.DataFrame with Speed column added
        new_bus_data = bus_data.iloc[1:].assign(Speed=speed)

        # Save the new data frame to a file. To recreate the original files structure I need to extract line number,
        # brigade number and vehicle number from the bus_file path
        file_path_split = bus_file.parts
        line = file_path_split[-3]
        brigade = file_path_split[-2]
        new_file_path = dir_to_output_data / line / brigade
        # Create the new directory in case it doesn't exist yet
        new_file_path.mkdir(parents=True, exist_ok=True)
        # Append file_name (vehicle number) to the new_path
        new_file_path = new_file_path / file_path_split[-1]
        # Save pd.DataFrame() to the file
        new_bus_data.to_csv(new_file_path)


def speed_statistics(dir_to_data: str, speed: float = 50., outlier_speed: float = None) -> None:
    """
    Print percent of times when the given speed is exceeded and maximal and minimal speed. It also plots the
    histogram of all the measured speeds.

    :param dir_to_data: The directory to the folder containing busestrams with speed data (so the data created by the
    calc_speed() function). By default it should be a folder with the name ending with "with_speed".
    :param speed: Percent of times when exceeding the specified speed is printed.
    :param outlier_speed: If specified, speeds greater than outlier_speed are not taken into consideration.
    :return: None.
    """

    # number of all measurements
    total_number_of_records = 0
    # number of measurements when a bus exceeded given speed
    exceeding_speed = 0

    # Very long list with all the measured speeds. Used for plotting a histogram
    # TODO change it to a dict with specified intervals:
    speed_list = []

    for bus_file in bus_data_iterator(dir_to_busestrams=dir_to_data):

        # Read only the speed column from the bus data
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

    print("\nSpeed statistics:")
    print("-" * 20)
    print(f"Maximal measured speed: {max(speed_list)}\nMinimal measured speed: {min(speed_list)}")
    print(f"Percent of times when any bus exceeds {speed} km/h vs all measurements is "
          f"{100 * exceeding_speed / total_number_of_records :.2f}%.")
    print("-" * 20)
    # Show the histogram:
    speed_numpy = np.array(speed_list)
    plt.hist(speed_numpy, bins=30, density=True)
    plt.xlabel("Speed in km/h")
    plt.ylabel("Percent %")
    plt.show()


def exceeding_the_speed_locations(dir_to_data: str, speed: float, round_to: int = 2,
                                  outlier_speed: float = None) -> dict:
    """
    Return the dictionary with position (latitude and longitude) as the key. Latitude and longitude are rounded
    according to the round_to parameter, to help to group the data. The values of the dictionary are two-element lists.
    The first element is number of times when the speed was exceeded at the given location. The second element describes
    number of all measurements taken at the given location.

    :param dir_to_data: The directory to busestrams data.
    :param speed: The program looks for the times for the speed specified here is exceeded.
    :param round_to: The notion of exceeding location is rounded up to round_to decimal places.
    :param outlier_speed: If specified, speeds greater than outlier_speed are not taken into the consideration.
    :return: Dictionary.
    """

    # exceeding_locations_dict keeps how many times the speed is speed is exceed at the given location and how many
    # measurements are taken at the given location.
    exceeding_locations_dict = dict()

    for bus_file in bus_data_iterator(dir_to_busestrams=dir_to_data):

        bus_data = pd.read_csv(bus_file)

        if outlier_speed is not None:
            # Filter out all the rows containing speed greater than the outlier_speed
            bus_data = bus_data[bus_data["Speed"] < outlier_speed]

        # for _, row in bus_data[bus_data["Speed"] > speed].iterrows():
        #     location = (round(row["Lat"], round_to), round(row["Lon"], round_to))
        #     if location in exceeding_locations_dict:
        #         exceeding_locations_dict[location] += 1
        #     else:
        #         exceeding_locations_dict[location] = 1

        for _, row in bus_data.iterrows():
            # Round the location
            location = (round(row["Lat"], round_to), round(row["Lon"], round_to))

            # Update all_locations_dict
            if location in exceeding_locations_dict:
                exceeding_locations_dict[location][0] += 1
                if row["Speed"] > speed:
                    exceeding_locations_dict[location][1] += 1
            else:
                if row["Speed"] > speed:
                    exceeding_locations_dict[location] = [1, 1]
                else:
                    exceeding_locations_dict[location] = [1, 0]

    return exceeding_locations_dict


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir_to_busestrams", "-d", type=str,
                        help="The directory with the busestrams data."
                        )
    parser.add_argument("--calc_speed", action="store_true",
                        help="calc_speed() is run if this flag is active."
                        )
    parser.add_argument("--statistics", action="store_true",
                        help="speed_statistics() is run if this flag is active."
                        )
    parser.add_argument("--locations", action="store_true",
                        help="exceeding_the_speed_location() is run if this flag is active."
                        )
    parser.add_argument("--speed", "-s", type=float, default=50.,
                        help="The program looks for the times for the speed specified here is exceeded. It is used in "
                             "speed_statistics() and exceeding_the_speed_location()."
                        )

    args = parser.parse_args()

    if args.calc_speed:
        print("Starts calculating speed...")
        calc_speed(dir_to_busestrams=args.dir_to_busestrams)
        print("calc_speed run successfully.")

    new_path = args.dir_to_busestrams + "_with_speed"
    if args.statistics:
        print("Starts calculating statistics...")
        speed_statistics(dir_to_data=new_path, speed=args.speed, outlier_speed=120.)

    if args.locations:
        print(f"Looking for locations were {args.speed} km/h is exceeded...")
        exceeding_locations_dict = exceeding_the_speed_locations(dir_to_data=new_path,
                                                                 speed=args.speed,
                                                                 round_to=2,
                                                                 outlier_speed=120.)

        # Save exceeding_locations_dict to a file for the sake of future usage (like on the map)
        results_path = Path("./speed_exceeded_pickle")
        with results_path.open("wb") as f:
            pickle.dump(exceeding_locations_dict, f)

        # I want to find locations were the speed is exceeded significant amount of times
        thres = 0.9
        for loc, counts in exceeding_locations_dict.items():
            exceeding_percent = counts[1] / counts[0]
            if exceeding_percent > thres:
                print(f"The speed was exceeded {100*exceeding_percent:.0f}% of times around {loc}.")

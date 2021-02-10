from pathlib import Path
import json
import pandas as pd

import math
import matplotlib.pyplot as plt
import statistics


def load_timetable(f_path: str):

    with open(f_path) as file:
        data = json.load(file)

    # I create empty data frame which I append rows to
    df = pd.DataFrame()
    for row in data:
        vals = []
        keys = []
        for d in row["values"]:
            vals.append(d["value"])
            keys.append(d["key"])
        row_series = pd.Series(vals, keys)
        df = df.append(row_series, ignore_index=True)
    return df

def timetable(line, bus_stop_id: str, bus_stop_nr: str, dir_to_timetables: str):
    
    f_path = Path.cwd() / dir_to_timetables / str(line) / f"{bus_stop_id}_{bus_stop_nr}.json"
    timetable_data_frame = load_timetable(f_path)
    return timetable_data_frame

def bus_stop_name_to_id(stop_name: str, stops_coord_path: str):
    """ For a given bus stop name, it returns busstopId. Names are more meaningful to humans, but busstopId is used
    to request the website"""

    with open(stops_coord_path) as file:
        stops_coord = json.load(file)
    busstopId = ""
    busstopNr = []

    for row in stops_coord:
        if row["values"][2]["value"] == stop_name:
            busstopId = row["values"][0]["value"]
            busstopNr.append(row["values"][1]["value"])

    if busstopId == "":
        # TODO raise an exception
        print(f"I couldn't find such a bus stop: {stop_name}")
    else:
        print(f"{stop_name} bus stop id is {busstopId}. Possible bus stop nr are {busstopNr}")

def bus_stop_id_to_name(stop_id: str, stops_coord_path: str):

    with open(stops_coord_path) as file:
        stops_coord = json.load(file)

    stop_name = ""

    for row in stops_coord:
        if row["values"][0]["value"] == stop_id:
            stop_name = row["values"][2]["value"]

    if stop_name == "":
        # TODO raise an exception
        print(f"I couldn't find such a bus stop: {stop_name}")
    else:
        print(f"{stop_id} bus stop name is {stop_name}.")


def timestamps_diffs_statistics(dir_to_busestrams: str) -> None:

    timestamps_diffs_list = []
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

        if time_diffs[time_diffs > 600.].sum() > 0:
            print(f"I've found time difference greater than one minute in the file {bus_file}.")

        timestamps_diffs_list += time_diffs.tolist()

    print(f"Mean difference between timestamps is {statistics.mean(timestamps_diffs_list):.2f} seconds.")
    print(f"Standard deviation of differences between timestamps is {statistics.stdev(timestamps_diffs_list):.2f} "
          f"seconds.")
    print(f"Median of differences between timestamps is {statistics.median(timestamps_diffs_list):.2f} seconds.")
    print(f"Maximum difference is {max(timestamps_diffs_list):.2f} seconds.")
    # plt.hist(timestamps_diffs_list, bins=50)
    # plt.show()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--f_path", "-f", type=str, help="")
    args = parser.parse_args()
    # df = load_timetable(args.f_path)
    # print(df.head())
    # print(df.tail())

    # stops_coord_path = r"..\data\timetables\stops_coord.json"
    # bus_stop_id_to_name("R-13", stops_coord_path)
    
    # df = timetable(line=2, bus_stop_id=1122, bus_stop_nr="03", dir_to_timetables="..\\data\\timetables")
    # print(df)

    timestamps_diffs_statistics(args.f_path)

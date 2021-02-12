"""This is punctuality analysis"""

from pathlib import Path
import json
import datetime
import pandas as pd
import numpy as np

from .speed_analysis import dist


def get_bus_schedule(line: str, brigade: str, dir_timetables: str, dir_stops_coord: str,
                     min_time, max_time) -> pd.DataFrame:
    """Create pd.DataFrame describing the schedule for the given line and given brigade.
    :param line: Bus line number
    :param brigade: Bus brigade number
    :param dir_timetables: The directory where the files with timetables are stored
    :param dir_stops_coord: The name of the file with bus stops coordinates
    :param min_time: times of stop earlier than min_time are not considered. There is no point loading whole bus 
    schedule if one has bus data for only e.g. one hour.
    :param max_time: the same os min_time, but times of stop later than max_time are not considered
    :return: pd.DataFrame. It has following columns:
                            "direction": the name of the last stop at this route
                            "arrives_at": the time when the bus should arrive at the stop
                            "busstopId": id of the stop
                            "busstopNr": nr of the stop
                            "name": the name the stop
                            "busstop_latitude": the latitude of the stop
                            "busstop_longitude": the longitude of the stop
                            "next_stop": the name of the next stop in the schedule
    """

    # load stops coordinates
    with open(dir_stops_coord, "r") as f:
        stops_coord = json.load(f)

    # the files I am looking for have the path structure: dir_timetables / line / busstopId_busstopNr.json
    p = Path(dir_timetables).glob(f"{line}/*")
    # files_list is a list of all the timetables for the given line at the given stop
    files_list = [x for x in p if x.is_file()]

    # create an empty pd.DataFrame(), to which rows are added in the following loop
    bus_schedule = pd.DataFrame()

    for timetable_file in files_list:
        # timetable_file is the name of the file describing the given bus schedule for the given stop. I want to
        # extract schedule for the given brigade at the time when I have bus data
        with open(timetable_file) as file:
            timetable_at_stop = json.load(file)
        # go through every item in the json file timetable_at_stop
        for record in timetable_at_stop:
            # check if this item in the schedule relate to the given brigade
            if record["values"][2]["value"] == brigade:
                # Warning: in the original files there happens times as 25:05:00. I need to convert them into the
                # correct datetime format TODO: make this correction while downloading in future

                day = min_time.date()
                hour = int(record["values"][5]["value"][:2])
                minutes = int(record["values"][5]["value"][3:5])
                sec = int(record["values"][5]["value"][6:])

                if hour < 24:
                    stop_time = datetime.datetime.combine(day, datetime.time(hour, minutes, sec))
                else:
                    day += datetime.timedelta(days=1)
                    stop_time = datetime.datetime.combine(day, datetime.time(hour - 24, minutes, sec))

                # consider only those times which are between min_time and max_time
                if (stop_time >= min_time) and (stop_time <= max_time):
                    # While saving the timetables files I give them the name: ####_##.json where first 4 characters
                    # describe stop id and the fifth and sixth character describe stop number
                    stop_id = timetable_file.name[:4]
                    stop_nr = timetable_file.name[5:7]

                    # Extract info about the stop from stops_coord. Data I'm looking for are name, latitude, longitude
                    # of the stop and the direction
                    for stop in stops_coord:
                        if (stop["values"][0]["value"]) == stop_id and (stop["values"][1]["value"] == stop_nr):
                            stop_name = stop["values"][2]["value"]
                            stop_lat = stop["values"][4]["value"]
                            stop_lon = stop["values"][5]["value"]
                            direction = stop["values"][6]["value"]

                    vals = [record["values"][3]["value"],
                            stop_time,
                            stop_id,
                            stop_nr,
                            stop_name,
                            float(stop_lat),
                            float(stop_lon),
                            direction
                            ]
                    keys = ["direction",
                            "arrives_at",  # the time when the bus should arrive at this stop
                            "busstopId",
                            "busstopNr",
                            "name",  # the name of the stop
                            "busstop_latitude",
                            "busstop_longitude",
                            "next_stop"
                            ]

                    row_series = pd.Series(vals, keys)
                    bus_schedule = bus_schedule.append(row_series, ignore_index=True)
    return bus_schedule


def dist_bus_from_stop(bus_file_name: str, dir_timetables: str, dir_stops_coord: str,
                       max_speed_around_the_stop: float, time_weight: float) -> pd.DataFrame:
    """Use get_bus_schedule() to find the bus schedule and calculates the positions of the bus closest to each stop. See
    delays_statics() description for details.

    :param bus_file_name: The name of the file with bus data. It should be something like
    dir_busestrams/line/brigade/vehicle.txt
    :param dir_timetables: The directory where the files with timetables are stored
    :param dir_stops_coord: The name of the file with bus stops coordinates
    :param max_speed_around_the_stop: It might happen (in fact - it happens almost every time) that the bus updates its
    position near the stop but not exactly at the stop. To estimate the time needed to drive exactly to the stop I
    assume the bus drives with the speed max_speed_around_the_stop
    :param time_weight: How much the time difference is import in calculating spacetime distance.
    :return: pd.DataFrame. Its columns are the same as returned by the get_bus_schedule() plus it has two additional
    columns: bus_time, which is the timestamps of the point when the bus is closest (in spacetime) to the stop
             delay, which is estimated delay of the bus at the stop
    """
    bus_data = pd.read_csv(bus_file_name,
                           names=["Lat", "Lon", "Time"],
                           dtype={"Lat": float, "Lon": float, "Time": str})
    # Convert columns "Time" into datetime format. It make some operations on the timestamps easier
    bus_data["Time"] = pd.to_datetime(bus_data["Time"])

    # min_time and max_time are parameters passed to get_bus_schedule()
    min_time = bus_data["Time"].min()
    max_time = bus_data["Time"].max()

    # Extract info about bus line and brigade from the bus file name
    file_path_split = bus_file_name.parts
    line = file_path_split[-3]
    brigade = file_path_split[-2]
    bus_schedule = get_bus_schedule(line=line, brigade=brigade, dir_timetables=dir_timetables,
                                    dir_stops_coord=dir_stops_coord, min_time=min_time, max_time=max_time)

    # List of timestamps when the bus is closest the each stop
    time_of_min_dist_list = []
    # List of delays at each stop
    delay_list = []

    # Every row in bus_schedule describes different bus stop
    for _, row in bus_schedule.iterrows():
        # Time of the expected arrival
        arrives_at = pd.to_datetime(row["arrives_at"])
        # Differences between arrival_time and every bus timestamp
        time_diffs = (bus_data["Time"] - arrives_at).dt.total_seconds()

        # Distances between the stop and every bus position
        distances_in_space = dist(float(row["busstop_latitude"]),
                                  float(row["busstop_longitude"]),
                                  bus_data["Lat"].to_numpy(),
                                  bus_data["Lon"].to_numpy()
                                  )

        # Add time 'penalty' to distances in space two create distance in spacetime
        distances_in_spacetime = distances_in_space + time_weight*abs(time_diffs)

        # Find index minimizing distance in spacetime
        arg_min = np.argmin(distances_in_spacetime)

        # Calculate delay as the difference between bus timestamps and expected time of the arrival at the stop
        # plus estimated time needed to drive to the stop
        delay = time_diffs[arg_min] + distances_in_space[arg_min]/max_speed_around_the_stop

        # round delay to seconds
        delay = round(delay, 0)
        # If calculated delay is less than 0, assume it is perfect timing (meaning delay == 0)
        if delay < 0:
            delay_list.append(0.0)
        else:
            delay_list.append(delay)

        time_of_min_dist_list.append(bus_data["Time"][arg_min])
        # min_dist_list.append(distances_in_space[arg_min])

    # bus_schedule["bus_dist"] = min_dist_list
    bus_schedule["bus_time"] = time_of_min_dist_list
    bus_schedule["delay"] = delay_list

    return bus_schedule


def calc_delays(dir_busestrams: str, dir_timetables: str, dir_stops_coord: str,
                max_speed_around_the_stop: float = 40., time_weight: float = 0.001) -> dict:
    """Calculate delays for every bus in the dir_busestrams directory. See delays_statics() description for details.

    :param dir_busestrams: The directory where the files with bus data are stored
    :param dir_timetables: The directory where the files with timetables are stored
    :param dir_stops_coord: The name of the file with bus stops coordinates
    :param max_speed_around_the_stop: It might happen (in fact - it happens almost every time) that the bus updates its
    position near the stop but not exactly at the stop. To estimate the time needed to drive exactly to the stop I
    assume the bus drives with the speed max_speed_around_the_stop
    :param time_weight: How much the time difference is import in calculating spacetime distance.
    :return: Dictionary. Its keys are delays (in seconds) and the values are number of times when the given delay
    occurred.
    """

    # To filled in the loop and returned
    delays_dict = dict()

    # dir_to_busestrams has structure: dir_to_busestrams / "line/brigade/vehicle.txt"
    p = Path(dir_busestrams).glob('*/*/*')
    # files_list is a list of all the files in the directory dir_to_busestrams
    files_list = [x for x in p if x.is_file()]
    for bus_file in files_list:
        # Now bus schedule contains info about closest positions also
        bus_schedule = dist_bus_from_stop(bus_file_name=bus_file,
                                          dir_timetables=dir_timetables,
                                          dir_stops_coord=dir_stops_coord,
                                          max_speed_around_the_stop=max_speed_around_the_stop,
                                          time_weight=time_weight)

        delay_list = bus_schedule["delay"].tolist()
        for delay in delay_list:
            delay = int(delay)
            if delay in delays_dict:
                delays_dict[delay] += 1
            else:
                delays_dict[delay] = 1

    return delays_dict


def delays_statistics(dir_busestrams: str, dir_timetables: str, dir_stops_coord: str,
                      max_speed_around_the_stop: float = 40., time_weight: float = 0.001) -> None:
    """Print some statistics of the bus delays calculated with calc_delays(). To calculate delays I need to calculate
    distance between each stop and the closest position of the bus. But by close I mean close in space AND time. Why?
    Suppose that a bus gets to the final station, waits and then goes in the other direction. Then it might pass a bus
    stop twice, but clearly I am interested only in one such passing. Put it differently, while analysing punctuality I
    want to know when the bus is near the stop but only if this bus is going in the right direction. So I take the
    distance between the stop and the bus and add some 'penalty' which is the difference between bus timestamp and the
    time of arrival in the schedule.

    :param dir_busestrams: The directory where the files with bus data are stored.
    :param dir_timetables: The directory where the files with timetables are stored.
    :param dir_stops_coord: The name of the file with bus stops coordinates.
    :param max_speed_around_the_stop: It might happen (in fact - it happens almost every time) that the bus updates its
    position near the stop but not exactly at the stop. To estimate the time needed to drive exactly to the stop I
    assume the bus drives with the speed max_speed_around_the_stop.
    :param time_weight: How much the time difference is import in calculating spacetime distance.
    :return: None.
    """

    delays_dict = calc_delays(dir_busestrams=dir_busestrams,
                              dir_timetables=dir_timetables,
                              dir_stops_coord=dir_stops_coord,
                              max_speed_around_the_stop=max_speed_around_the_stop,
                              time_weight=time_weight)

    # Number of all observations
    total_sum = 0
    mean = 0

    # Number of times when the delay is lesser than one or equal to one minute
    less_or_eq_than_one = 0
    # Number of times when the delay is greater than one minute
    more_than_one = 0
    # Number of times when the delay is greater than five minutes
    more_than_five = 0

    for delay, counter in delays_dict.items():
        total_sum += counter
        mean += delay*counter

        if delay < 1.0:
            less_or_eq_than_one += counter
        if delay > 1.0:
            more_than_one += counter
        if delay > 5.0:
            more_than_five += counter

    mean = mean/total_sum
    print("\nDelays statistics:")
    print("-" * 20)
    print(f"Mean delay is: {mean:.0f} seconds.")
    print(f"Percent of times when the bus is on time or its delay is at most one minute: "
          f"{100*less_or_eq_than_one/total_sum:.0f}%")
    print(f"Percent of delays longer than one minute: {100*more_than_one/total_sum:.0f}%.")
    print(f"Percent of delays longer than five minute: {100*more_than_five/total_sum:.0f}%.")
    print(f"The longest found delay is: {max(list(delays_dict.keys()))} seconds.")
    print("-" * 20)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir_to_busestrams", "-db", type=str,
                        help="The directory where the files with bus data are stored.")
    parser.add_argument("--dir_to_timetables", "-dt", type=str,
                        help="The directory where the files with timetables are stored.")
    parser.add_argument("--dir_to_stops_coord", "-ds", type=str,
                        help="The name of the file with bus stops coordinates.")
    args = parser.parse_args()

    delays_statistics(dir_busestrams=args.dir_to_busestrams, dir_timetables=args.dir_to_timetables,
                      dir_stops_coord=args.dir_to_stops_coord)

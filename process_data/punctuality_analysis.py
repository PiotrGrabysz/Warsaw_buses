"""This is punctuality analysis"""
from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import numpy as np

from process_data.velocity_analysis import dist


# from velocity_analysis import dist


def get_bus_route(line: str, brigade: str, dir_timetables: str, dir_stops_coord: str,
                  min_time, max_time) -> pd.DataFrame:
    with open(dir_stops_coord, "r") as f:
        stops_coord = json.load(f)

    # the files I am looking for have path structure: dir_timetables / line / busstopId_busstopNr.json
    p = Path(dir_timetables).glob(f"{line}/*")
    # files_list is a list of all timetables for the given line at the given stop
    files_list = [x for x in p if x.is_file()]
    df = pd.DataFrame()
    for timetable_file in files_list:
        with open(timetable_file) as file:
            timetable_at_stop = json.load(file)
        for record in timetable_at_stop:
            if record["values"][2]["value"] == brigade:
                stop_time = datetime.strptime("2021-02-03 " + record["values"][5]["value"], "%Y-%m-%d %H:%M:%S")
                if (stop_time >= min_time) and (stop_time <= max_time):

                    stop_id = timetable_file.name[:4]
                    stop_nr = timetable_file.name[5:7]
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
                    df = df.append(row_series, ignore_index=True)
    return df


def dist_bus_from_stop(bus_file_name: str, dir_timetables: str, dir_stops_coord: str,
                       max_speed_around_the_stop: float, time_weight: float) -> pd.DataFrame:

    bus_data = pd.read_csv(bus_file_name,
                           names=["Lat", "Lon", "Time"],
                           dtype={"Lat": float, "Lon": float, "Time": str})

    bus_data["Time"] = pd.to_datetime(bus_data["Time"])

    min_time = bus_data["Time"].min()
    max_time = bus_data["Time"].max()

    file_path_split = bus_file_name.parts
    line = file_path_split[-3]
    brigade = file_path_split[-2]
    bus_route = get_bus_route(line=line, brigade=brigade,
                              dir_timetables=dir_timetables, dir_stops_coord=dir_stops_coord, min_time=min_time,
                              max_time=max_time)

    # min_dist_list = []
    time_of_min_dist_list = []
    delay_list = []
    for _, row in bus_route.iterrows():
        arrives_at = pd.to_datetime(row["arrives_at"])
        time_diffs = (bus_data["Time"] - arrives_at).dt.total_seconds()

        distances_in_space = dist(float(row["busstop_latitude"]),
                                  float(row["busstop_longitude"]),
                                  bus_data["Lat"].to_numpy(),
                                  bus_data["Lon"].to_numpy()
                                  )

        distances_in_spacetime = distances_in_space + time_weight*abs(time_diffs)

        arg_min = np.argmin(distances_in_spacetime)

        delay = time_diffs[arg_min] + distances_in_space[arg_min]/max_speed_around_the_stop
        if delay < 0:
            delay_list.append(0.0)
        else:
            delay_list.append(delay)

        time_of_min_dist_list.append(bus_data["Time"][arg_min])

        # min_dist_list.append(distances_in_space[arg_min])

    # bus_route["bus_dist"] = min_dist_list
    bus_route["bus_time"] = time_of_min_dist_list

    bus_route["delay"] = delay_list
    return bus_route


def calc_delays(dir_busestrams: str, dir_timetables: str, dir_stops_coord: str,
                max_speed_around_the_stop: float = 40., time_weight: float = 0.001) -> list:

    delay_list = []
    # dir_to_busestrams has structure: dir_to_busestrams / "line/brigade/vehicle.txt"
    p = Path(dir_busestrams).glob('*/*/*')
    # files_list is a list of all the files in the directory dir_to_busestrams
    files_list = [x for x in p if x.is_file()]
    for bus_file in files_list:
        bus_route = dist_bus_from_stop(bus_file_name=bus_file, 
                                       dir_timetables=dir_timetables,
                                       dir_stops_coord=dir_stops_coord, 
                                       max_speed_around_the_stop=max_speed_around_the_stop,
                                       time_weight=time_weight)

        delay_list += bus_route["delay"].tolist()
    return delay_list

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir_to_busestrams", "-db", type=str)
    parser.add_argument("--dir_to_timetables", "-dt", type=str)
    parser.add_argument("--dir_to_stops_coord", "-ds", type=str)
    parser.add_argument("--line", type=str)
    parser.add_argument("--brigade", type=str)
    args = parser.parse_args()

    # dist_bus_from_stop(line=args.line, brigade=args.brigade, dir_busestrams=args.dir_to_busestrams,
    #                    dir_stops_coord=args.dir_to_stops_coord,
    #                    dir_timetables=args.dir_to_timetables)

    lst = calc_delays(dir_busestrams=args.dir_to_busestrams, dir_timetables=args.dir_to_timetables,
                dir_stops_coord=args.dir_to_stops_coord)

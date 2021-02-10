"""This is punctuality analysis"""
from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import numpy as np

from process_data.velocity_analysis import dist
# from velocity_analysis import dist


def get_bus_route(line: str, brigade: str, dir_timetables: str):

    timetable_list = []

    # the files I am looking for has path structure: dir_timetables / line / busstopId_busstopNr.json
    p = Path(dir_timetables).glob(f"{line}/*")
    # files_list is a list of all timetables for the given line at the given stop
    files_list = [x for x in p if x.is_file()]
    for timetable_file in files_list:

        with open(timetable_file) as file:
            timetable_at_stop = json.load(file)
        for record in timetable_at_stop:
            if record["values"][2]["value"] == brigade:
                timetable_list.append(record["values"])
        print(timetable_list)
        break


def get_bus_route2(line: str, brigade: str, dir_timetables: str, dir_stops_coord: str) -> pd.DataFrame():

    #TODO cannot be hardcoded!
    min_time = datetime.strptime("2021-02-03 12:21:50", "%Y-%m-%d %H:%M:%S")
    max_time = datetime.strptime("2021-02-03 13:21:26", "%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame()
    with open(dir_stops_coord, "r") as f:
        stops_coord = json.load(f)

    # the files I am looking for have path structure: dir_timetables / line / busstopId_busstopNr.json
    p = Path(dir_timetables).glob(f"{line}/*")
    # files_list is a list of all timetables for the given line at the given stop
    files_list = [x for x in p if x.is_file()]
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
                    keys = ["kierunek",
                            "czas",
                            "busstopId",
                            "busstopNr",
                            "nazwa",
                            "szerokosc",
                            "dlugosc",
                            "nastepna stacja"
                            ]

                    row_series = pd.Series(vals, keys)
                    df = df.append(row_series, ignore_index=True)
    return df


def dist_bus_from_stop(line: str, brigade: str, dir_busestrams: str, dir_timetables: str, dir_stops_coord: str):

    # Buses are stored in the path dir_to_busestrams/line/brigade/vehicle_number.txt
    # but I don't know the vehicle_number, so I use glob()
    bus_path = Path(dir_busestrams) / line / brigade
    for bus_file in bus_path.glob("*.txt"):
        bus_data = pd.read_csv(bus_file,
                               names=["Lat", "Lon", "Time"],
                               dtype={"Lat": float, "Lon": float, "Time": str})
    bus_data["Time"] = pd.to_datetime(bus_data["Time"])

    bus_route = get_bus_route2(line=line, brigade=brigade,
                               dir_timetables=dir_timetables, dir_stops_coord=dir_stops_coord)

    min_dist_list = []
    time_of_min_dist_list = []
    min_time_list = []
    for _, row in bus_route.iterrows():
        dt = pd.to_datetime(row["czas"])
        ddt = abs(bus_data["Time"] - dt).dt.total_seconds()
        min_time_list.append(ddt.min())
        array_of_dist = dist(float(row["szerokosc"]),
                             float(row["dlugosc"]),
                             bus_data["Lat"].to_numpy(),
                             bus_data["Lon"].to_numpy()
                             ) + ddt

        min_arg = np.argmin(array_of_dist)
        min_dist_list.append(array_of_dist[min_arg])
        time_of_min_dist_list.append(bus_data["Time"][min_arg])
    bus_route["bus_dist"] = min_dist_list
    bus_route["bus_time"] = time_of_min_dist_list
    bus_route["min_time"] = min_time_list

    return bus_route


def dist_bus_from_stop2(line: str, brigade: str, dir_busestrams: str, dir_timetables: str, dir_stops_coord: str):

    # Buses are stored in the path dir_to_busestrams/line/brigade/vehicle_number.txt
    # but I don't know the vehicle_number, so I use glob()
    bus_path = Path(dir_busestrams) / line / brigade
    for bus_file in bus_path.glob("*.txt"):
        bus_data = pd.read_csv(bus_file,
                               names=["Lat", "Lon", "Time"],
                               dtype={"Lat": float, "Lon": float})
    bus_data["Time"] = pd.to_datetime(bus_data["Time"])
    bus_data.set_index(keys="Time", inplace=True)

    bus_route = get_bus_route2(line=line, brigade=brigade,
                               dir_timetables=dir_timetables, dir_stops_coord=dir_stops_coord)

    min_dist_list = []
    time_of_min_dist_list = []
    closest_time_list = []
    dist_from_stop_list = []
    bus_lat_list = []
    bus_lon_list = []
    for _, row in bus_route.iterrows():
        dt = pd.to_datetime(row["czas"])
        nearest_bus_time_stamp = bus_data.index.get_loc(dt, method='nearest')
        closest_time_list.append(bus_data.index[nearest_bus_time_stamp])
        dist_from_stop_list.append(dist(row["szerokosc"],
                                        row["dlugosc"],
                                        bus_data["Lat"][nearest_bus_time_stamp],
                                        bus_data["Lon"][nearest_bus_time_stamp]))
        # bus_data["Time"] - row["czas"]

    #
    #     min_arg = np.argmin(array_of_dist)
    #     min_dist_list.append(array_of_dist[min_arg])
    #     time_of_min_dist_list.append(bus_data["Time"][min_arg])
    # bus_route["bus_dist"] = min_dist_list
    bus_route["bus_closest_time"] = closest_time_list
    bus_route["dist_from_stop"] = dist_from_stop_list

    return bus_route


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir_to_busestrams", "-db", type=str)
    parser.add_argument("--dir_to_timetables", "-dt", type=str)
    parser.add_argument("--dir_to_stops_coord", "-ds", type=str)
    parser.add_argument("--line", type=str)
    parser.add_argument("--brigade", type=str)
    args = parser.parse_args()

    # tmp = get_bus_route2(dir_timetables=args.dir_timetables,
    #                      line=args.line,
    #                      brigade=args.brigade,
    #                      dir_stops_coord=args.dir_to_stops_coord
    #                      )
    # print(tmp)

    dist_bus_from_stop2(line=args.line, brigade=args.brigade, dir_busestrams= args.dir_to_busestrams,
                       dir_stops_coord=args.dir_to_stops_coord,
                       dir_timetables=args.dir_to_timetables)
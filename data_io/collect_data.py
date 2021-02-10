import requests
import json
from pathlib import Path
from typing import Union

APIKEY = "96bc1c08-5f6e-411e-a69a-bdbff719bc7e"


def timetables_request(action: str, busstopId: str = None, busstopNr: str = None, line: int = None,
                       timeout: float = 1.0):
    if action == "stops_coord":
        # Gets coordinates of all the buses and trams stops
        url = "https://api.um.warszawa.pl/api/action/dbstore_get"
        params = dict(id="ab75c33d-3a26-4342-b36a-6e5fef0a3ac3",
                      apikey=APIKEY
                      )

    elif action == "lines_wrt_stop":
        # Gets all the bus lines connected with the given stop
        url = "https://api.um.warszawa.pl/api/action/dbtimetable_get"
        params = dict(id="88cd555f-6f31-43ca-9de4-66c479ad5942",
                      busstopId=busstopId, busstopNr=busstopNr,
                      apikey=APIKEY
                      )

    elif action == "timetable":
        url = "https://api.um.warszawa.pl/api/action/dbtimetable_get"
        params = dict(id="e923fa0e-d96c-43f9-ae6e-60518c9f3238",
                      busstopId=busstopId, busstopNr=busstopNr,
                      line=line, apikey=APIKEY
                      )

    r = requests.get(url, params=params, timeout=timeout).json()
    return r["result"]


def timetables_collect_all(dir_to_save: str, verbose: bool = False,
                           resume_from_row: int = 0, repeat_rows_file: Union[None, str] = None):
    """ stops() -> lines_wrt_stop -> timetable_wrt_line_and_stop
    Jako repeat_rows_file podaj errors_log.txt
    """

    if repeat_rows_file is not None or resume_from_row > 0:
        f_path = Path.cwd().joinpath(dir_to_save, "stops_coord.json")
        with f_path.open("r") as f:
            stops_coord = json.load(f)
        print("Stops coordinates loaded.")

    else:
        stops_coord = timetables_request(action="stops_coord")
        print("Downloaded bus stops coordinates.")

        # Saving to a file
        Path(dir_to_save).mkdir(parents=True, exist_ok=True)
        f_path = Path.cwd().joinpath(dir_to_save, "stops_coord.json")
        with f_path.open("w") as f:
            json.dump(stops_coord, f)
        print("Bus stops coordinates saved to a file.")

    # For now I assume that rows are loaded from errors_log
    repeat_rows = []
    if repeat_rows_file is not None:
        with open(repeat_rows_file, "r") as f:
            for line in f:
                repeat_rows.append(int(line.split(" ")[0]))

    errors_log_file_name = Path.cwd().joinpath(dir_to_save, "errors_log.txt")
    errors_count = 0

    for row_count, row in enumerate(stops_coord):
        if (row_count >= resume_from_row) and ((repeat_rows_file is None) or (row_count in repeat_rows)):
            row = row["values"]
            busstopId = row[0]["value"]
            busstopNr = row[1]["value"]

            if verbose:
                print(f"Processing {row_count}th row.")
                print(f"Requesting lines from a stop {row[2]['value']} nr {busstopNr}.")

            try:
                lines = timetables_request(action="lines_wrt_stop", busstopId=busstopId, busstopNr=busstopNr)
            except requests.exceptions.RequestException as e:
                print(f"{e} occurred! I skip the row {row_count} {busstopId} {busstopNr}")
                with errors_log_file_name.open("a") as errors_file:
                    errors_file.write(f"{row_count} {e}\n")
                errors_count += 1

            for line in lines:
                line = line["values"][0]["value"]

                if verbose:
                    print(f"Requesting line {line} at stop {row[2]['value']} nr {busstopNr} timetable.")

                try:
                    timetable = timetables_request(action="timetable", busstopId=busstopId,
                                                   busstopNr=busstopNr, line=line)

                    # Save timetable to a file
                    f_path = Path.cwd().joinpath(dir_to_save, f"{line}")
                    Path(f_path).mkdir(parents=True, exist_ok=True)
                    f_name = Path.cwd().joinpath(f_path, f"{busstopId}_{busstopNr}.json")
                    with f_name.open("w") as f:
                        json.dump(timetable, f)

                    if verbose:
                        print(f"{f_name} is saved.")

                except requests.exceptions.RequestException as e:
                    # Error during requesting the timetable
                    print(f"{e} occurred. I skip the row {row_count} {busstopId} {busstopNr} {line}")
                    with errors_log_file_name.open("a") as errors_file:
                        errors_file.write(f"{row_count} {e}\n")
                    errors_count += 1

            # If verbose is False, inform the user about the progress each 500 processed rows
            if not verbose and ((row_count + 1) % 500) == 0:
                print(f"Processed {row_count + 1} rows.")

    if errors_count > 0:
        print(f"{errors_count} connection errors occurred. See {errors_log_file_name} for details")


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir_to_save", "-d", type=str, help="")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--repeat_rows_file", "-r", type=str, default=None)
    parser.add_argument("--resume_from_row", "-r_row", type=int, default=0)

    parser.add_argument("--action", "-a", type=str, default = None, help="")
    parser.add_argument("--busstopId", "-Id", type=int)
    parser.add_argument("--busstopNr", "-Nr", type=str)
    parser.add_argument("--line", type=int)
    args = parser.parse_args()

    # Check if the given path exists and if it doesn't, a new directory is created.
    # If the path already exists, the user is asked if he wants to use this directory or close the program
    try:
        Path(args.dir_to_save).mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("This directory already exist. Do you want to proceed (you risk overwriting some files)?")
        user_ans = input("y : n")
        if user_ans == "y":
            Path(args.dir_to_save).mkdir(parents=True, exist_ok=True)
        else:
            sys.exit("Closing the program")

    if args.action is not None:
        tmp = timetables_request(action=args.action, busstopId=args.busstopId,
                                 busstopNr=args.busstopNr, line=args.line)
        print(tmp)

    # IDEA: when velocity is bigger than 50 km/h check the closest bus stop from timetables
    else:
        timetables_collect_all(dir_to_save=args.dir_to_save, verbose=args.verbose, repeat_rows_file=args.repeat_rows_file,
                               resume_from_row=args.resume_from_row)

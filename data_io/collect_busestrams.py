import requests
import json
from pathlib import Path
from datetime import datetime
import time
from typing import Union

import timeit


APIKEY = "96bc1c08-5f6e-411e-a69a-bdbff719bc7e"

def busestrams_get(dir_to_save: str, type: int=1, timeout: float=1.0):

    url = 'https://api.um.warszawa.pl/api/action/busestrams_get'
    params = dict(resource_id = 'f2e5503e-927d-4ad3-9500-4ab9e55deb59',
                  apikey=APIKEY,
                  type=type)

    errors_log_file_name = Path.cwd().joinpath(dir_to_save, "errors_log.txt")

    try:
        r = requests.get(url, params=params, timeout=timeout).json()
    except requests.exceptions.RequestException as e:
        with errors_log_file_name.open("a") as errors_file:
            errors_file.write(f"Error catch at {datetime.now()}: {e}\n")
    else:
        # Data were correctly requested

        # r["result"] is a list of dictionaries
        for record in r["result"]:
            try:
                # There is a change that record would be something like "Nieprawidłowa metoda" instead of correct data
                line = record["Lines"]
                brigade = record["Brigade"]
            except (KeyError, TypeError) as e:
                with errors_log_file_name.open("a") as errors_file:
                    errors_file.write(f"Error {e} catch at {datetime.now()} in row: {record}\n")
            else:
                f_path = Path.cwd() / dir_to_save / str(line)
                Path(f_path).mkdir(parents=True, exist_ok=True)
                f_name = f_path.joinpath(f"{brigade}.txt")
                row = ",".join([str(record["Lat"]), str(record["Lon"]), record["Time"]])
                try:
                    with f_name.open("r+") as f:
                        # If I request the url faster than buses update their position, there would be some duplicates.
                        # So I go to the last line of data file to see if it is different from the current row. I save the
                        # row only if they are different.
                        data_lines = f.read().splitlines()
                        last_line = data_lines[-1]

                        if last_line != row:
                            f.write(f"{row}\n")

                except  FileNotFoundError:
                    with f_name.open("w") as f:
                        f.write(f"{row}\n")



def collect_busestrams(dir_to_save: str, type: int=1, time_step: float=5.0, how_long: float=60.0):
    start_collecting_time = time.time()
    start_requesting_time = time.time()
    while time.time() < (start_collecting_time + how_long):
        time_diff = time.time() - start_requesting_time
        if time_diff > time_step:
            print(f"Warning! Saving data to files takes {time_diff} which is longer than the chosen time step!")
        if time.time() > (start_requesting_time + time_step):
            start_requesting_time = time.time()
            busestrams_get(dir_to_save=dir_to_save, type=type)


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir_to_save", "-d", type=str, help="")
    parser.add_argument("--time_step", type=float, default=5.0)
    parser.add_argument("--how_long", type=float, default=60.0)
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

    collect_busestrams(dir_to_save=args.dir_to_save, time_step=args.time_step, how_long=args.how_long)


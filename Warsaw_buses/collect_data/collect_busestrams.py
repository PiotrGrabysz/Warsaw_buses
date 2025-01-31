import requests
from pathlib import Path
from datetime import datetime
import time

APIKEY = "96bc1c08-5f6e-411e-a69a-bdbff719bc7e"


def busestrams_get(dir_to_save: str, type: int = 1, timeout: float = 1.0) -> None:
    """ Send a request to the api https://api.um.warszawa.pl/api to get busestrams data. This data consist of bus
    line number, brigade number, vehicle number, time stamp and its position (latitude and longitude). If any error
    happens during the requesting it is saved to the file: "dir_to_save/errors_log.txt"

    :param dir_to_save: A directory where the files with all the buses (or/and trams) will be stored in
    :param type: 1 means buses, 2 means trams
    :param timeout: this parameter is passes to the request.get() function. From request docs: 'timeout is not a time
    limit on the entire response download; rather, an exception is raised if the server has not issued a response for
    timeout seconds'. Specifying this parameter is crucial to prevent the program from asking the api forever is some
    error happens.
    :return: None
    """

    url = 'https://api.um.warszawa.pl/api/action/busestrams_get'
    params = dict(resource_id='f2e5503e-927d-4ad3-9500-4ab9e55deb59',
                  apikey=APIKEY,
                  type=type)

    # If any error happens, it is written into this file:
    errors_log_file_name = Path.cwd().joinpath(dir_to_save, "errors_log.txt")

    # Requesting the data from the url:
    try:
        r = requests.get(url, params=params, timeout=timeout).json()
    except requests.exceptions.RequestException as e:
        # Save the error message and the time of its occurrence into the errors_log file
        with errors_log_file_name.open("a") as errors_file:
            errors_file.write(f"Error catch at {datetime.now()}: {e}\n")
    else:
        # else block is run if the data were correctly requested

        # r["result"] is a list of dictionaries
        for record in r["result"]:
            try:
                # There is a chance that the record would be something like "Nieprawidłowa metoda" instead of
                # a list of dictionaries. In that case, attempt to access record["Lines"] or record ["Brigade"] will
                # raise the TypeError
                line = record["Lines"]
                brigade = record["Brigade"]
                # Sometimes a weird bug happens and Brigade number is " ".
                if brigade == " ":
                    brigade = "not_given"
                vehicle = record["VehicleNumber"]
            except (KeyError, TypeError) as e:
                with errors_log_file_name.open("a") as errors_file:
                    errors_file.write(f"Error {e} catch at {datetime.now()} in row: {record}\n")
            else:
                # No error happened - save the busestrams data to the file

                # Prepare data file path
                f_path = Path.cwd() / dir_to_save / str(line) / str(brigade)
                Path(f_path).mkdir(parents=True, exist_ok=True)
                f_name = f_path.joinpath(f"{vehicle}.txt")

                # Row of data is latitude, longitude and time
                row = ",".join([str(record["Lat"]), str(record["Lon"]), record["Time"]])

                # Saving new row to the file
                try:
                    # Try to open the file. It throws FileNotFoundError if the file doesn't exist yet
                    with f_name.open("r+") as f:
                        # If the website is requested faster than buses update their position, there would be some
                        # duplicates. I go to the last line of the data file to see if this last line is different from
                        # the row I want to append. I append the row only if it is different.
                        data_lines = f.read().splitlines()
                        last_line = data_lines[-1]
                        if last_line != row:
                            f.write(f"{row}\n")

                except FileNotFoundError:
                    # This fil doesn't exit yet - create the new one
                    with f_name.open("w") as f:
                        f.write(f"{row}\n")


def collect_busestrams(dir_to_save: str, type: int = 1, time_step: float = 1.0, how_long: float = 60.0):
    """
    Collect busestrams data for a given period of time and save it to the files.  If any error happens during the
    requesting it is saved to the file: "dir_to_save/errors_log.txt"

    :param dir_to_save: A directory where the files with all the buses (or/and trams) will be stored in
    :param type: 1 means buses, 2 means trams
    :param time_step: The website will be requested every time_step (in seconds) or longer, if processing and saving
    the data takes more time than time_step
    :param how_long: for how long the request will be send to the website (in seconds)
    :return: None
    """

    start_collecting_time = time.time()
    # start_requesting_time is updated before every request
    start_requesting_time = time.time()
    while time.time() < (start_collecting_time + how_long):
        if time.time() > (start_requesting_time + time_step):
            start_requesting_time = time.time()
            busestrams_get(dir_to_save=dir_to_save, type=type)

            time_diff = time.time() - start_requesting_time
            if time_diff > time_step:
                print(f"Warning! Saving data to files takes {time_diff} which is longer than the chosen time step!")


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir_to_save", "-d", type=str,
                        help="A directory where the files with all the buses (or/and trams) will be stored")
    parser.add_argument("--time_step", type=float, default=6.0,
                        help="The website will be requested every time_step (in seconds) or longer, if processing and /"
                             "saving the data takes more time than time_step")
    parser.add_argument("--how_long", type=float, default=60.0,
                        help="for how long the request will be send to the website (in seconds)")
    args = parser.parse_args()

    # Check if the given path exists and if it doesn't, a new directory is created.
    # If the path already exists, the user is asked if he wants to use this directory or close the program
    try:
        Path(args.dir_to_save).mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("This directory already exist. Do you want to proceed (you risk overwriting some files)?")
        user_ans = input("y : n ")
        if user_ans == "y":
            Path(args.dir_to_save).mkdir(parents=True, exist_ok=True)
        else:
            sys.exit("Closing the program")

    collect_busestrams(dir_to_save=args.dir_to_save, time_step=args.time_step, how_long=args.how_long)

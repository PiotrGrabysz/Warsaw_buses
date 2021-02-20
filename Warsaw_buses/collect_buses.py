import argparse
from pathlib import Path
import sys

from Warsaw_buses.collect_data.collect_busestrams import collect_busestrams


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir_to_save", "-d", type=str,
                        help="A directory where the files with all the buses  will be stored.")
    parser.add_argument("--time_step", type=float, default=6.0,
                        help="The website will be requested every time_step (in seconds) or longer, if processing and /"
                             "saving the data takes more time than time_step. Default to 6.0.")
    parser.add_argument("--how_long", type=float, default=60.0,
                        help="For how long the request will be sent to the website (in seconds). Default to 60.0.")
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

    print("Collecting the buses data...")
    collect_busestrams(dir_to_save=args.dir_to_save, time_step=args.time_step, how_long=args.how_long)
    print(f"Done! The buses data are saved in the directory: '{Path(args.dir_to_save).absolute()}'")


if __name__ == "__main__":
    main()
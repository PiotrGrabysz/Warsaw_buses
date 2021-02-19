from pathlib import Path
import numpy as np
import pandas as pd


def is_time_monotonically_increasing(dir_to_data: str):
    p = Path(dir_to_data).glob("*/*/*")
    # files_list is a list of all files in the directory dir_to_data
    files_list = [x for x in p if x.is_file()]

    errors_log_file = Path("./is_time_monotonically_increasing_errors_log.txt")
    errors_counter = 0
    all_files_counter = 0
    for bus_file in files_list:
        bus_data = pd.read_csv(bus_file, names=["Lat", "Lon", "Time"])
        all_files_counter += 1
        # Calculating time differences:
        time_column = pd.to_datetime(bus_data["Time"]).dt.strftime('%H:%M:%S')
        time_column = pd.to_timedelta(time_column).dt.total_seconds()
        # I convert it into numpy.array to make arithmetic operations without the loop
        time_column = time_column.to_numpy()
        time_diffs = np.diff(time_column)

        if not np.all(time_diffs > 0):
            errors_counter += 1
            with errors_log_file.open("a") as errors_f:
                errors_f.write(
                    f"{bus_file}: {np.sum(time_diffs <= 0)} non-increasing rows in lines {np.where(time_diffs <= 0)}\n")

    if errors_counter == 0:
        print(f"Everything is fine! Subsequent measurements are not time monotonous.")
    else:
        print(f"Subsequent measurements are not time monotonous!. I've found {errors_counter} incorrect files which "
              f"is {100 * errors_counter / all_files_counter :.0f}% of the total number of files. See "
              f"{errors_log_file.absolute()} for details.")


def filter_data_from_non_monotonically_increasing_time(dir_to_data: str):
    p = Path(dir_to_data).glob("*/*/*")
    # files_list is a list of all files in the directory dir_to_data
    files_list = [x for x in p if x.is_file()]

    for bus_file in files_list:
        bus_data = pd.read_csv(bus_file, names=["Lat", "Lon", "Time"])
        # Calculating time differences:
        time_column = pd.to_datetime(bus_data["Time"]).dt.strftime('%H:%M:%S')
        time_column = pd.to_timedelta(time_column).dt.total_seconds()
        # I convert it into numpy.array to make arithmetic operations without the loop
        time_column = time_column.to_numpy()
        time_diffs = np.diff(time_column)

        if np.all(time_diffs > 0):
            file_path_split = bus_file.parts
            new_file = Path("/".join(file_path_split[:-4]))
            new_file = new_file / (file_path_split[-4] + "_filtered")
            new_file = new_file / file_path_split[-3] / file_path_split[-2]
            Path(new_file).mkdir(parents=True, exist_ok=True)
            new_file = new_file / file_path_split[-1]

            bus_data.to_csv(new_file, header=False, index=False)


# def one_brigade_one_vehicle_number(dir_to_data: str):
#     p = Path(dir_to_data).glob("*/*/*")
#     # files_list is a list of all files in the directory dir_to_data
#     files_list = [x for x in p if x.is_file()]
#
#     # errors_log_file = Path("./is_time_monotonically_increasing_errors_log.txt")
#     # errors_counter = 0
#     # all_files_counter = 0
#     for bus_file in files_list:
#         print(bus_file)
#         break


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dir_to_data", "-d", type=str,
                        help="")

    args = parser.parse_args()

    # TODO let user chose what to do with argparse
    is_time_monotonically_increasing(dir_to_data=args.dir_to_data)
    ans = input("Do you want to filter out the files where data is not monotonous? y : n ")
    if ans == "y":
        print("Starts filtering the data...")
        filter_data_from_non_monotonically_increasing_time(dir_to_data=args.dir_to_data)
        print(f"Finished! The filtered data are saved in {args.dir_to_data}_filtered")

    # one_brigade_one_vehicle_number(dir_to_data=args.dir_to_data)

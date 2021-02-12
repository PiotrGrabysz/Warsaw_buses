import argparse
from pathlib import Path

from Warsaw_buses.process_data import speed_analysis, punctuality_analysis


def main():

    parser = argparse.ArgumentParser()

    # Choose what should be analysed:
    parser.add_argument("--punctuality", action="store_true",
                        help=" ")
    parser.add_argument("--calc_speed", action="store_true",
                        help="calc_speed() is run if this flag is active."
                        )
    parser.add_argument("--speed_statistics", action="store_true",
                        help="speed_statistics() is run if this flag is active."
                        )
    parser.add_argument("--speed_locations", action="store_true",
                        help="exceeding_the_speed_location() is run if this flag is active."
                        )

    # Directory with busestrams data
    parser.add_argument("--dir_to_busestrams", "-db", type=str, default="./data/busestrams",
                        help="The directory with the busestrams data."
                        )

    # Params for punctuality analysis:
    parser.add_argument("--dir_to_timetables", "-dt", type=str, default="./data/timetables",
                        help="The directory where the files with timetables are stored.")
    parser.add_argument("--dir_to_stops_coord", "-ds", type=str, default="./data/timetables/stops_coord.json",
                        help="The name of the file with bus stops coordinates."
                        )

    # Params for speed analysis:
    parser.add_argument("--exceeded_speed", "-s", type=float, default=50.,
                        help="The program looks for the times for the speed specified here is exceeded. It is used in "
                             "speed_statistics() and exceeding_the_speed_location()."
                        )

    args = parser.parse_args()

    print(f"Using buses data from the directory {Path(args.dir_to_busestrams).absolute()}")
    print(f"Using timetables data from the directory {Path(args.dir_to_timetables).absolute()}")
    print(f"Using coordinates of the stops data from the directory {Path(args.dir_to_stops_coord).absolute()}")

    if args.punctuality:
        print("\nStarts calculating delays...")
        print(f"It might take a while...")

        punctuality_analysis.delays_statistics(dir_busestrams=args.dir_to_busestrams,
                                               dir_timetables=args.dir_to_timetables,
                                               dir_stops_coord=args.dir_to_stops_coord)

    if args.calc_speed:
        print("\nStarts calculating speed...")
        speed_analysis.calc_speed(dir_to_busestrams=args.dir_to_busestrams)
        print("Speed calculated and saved successfully.")

    dir_to_busestrams_with_speed = args.dir_to_busestrams + "_with_speed"
    if args.speed_statistics:
        print("\nStarts calculating statistics...")
        speed_analysis.speed_statistics(dir_to_data=dir_to_busestrams_with_speed,
                                        speed=args.exceeded_speed,
                                        outlier_speed=120.)

    if args.speed_locations:
        print(f"Looking for locations were {args.exceeded_speed} km/h is exceeded...")
        # exceeding_locations_dict = speed_analysis.exceeding_the_speed_locations(dir_to_data=dir_to_busestrams_with_speed,
        #                                                                         speed=args.speed,
        #                                                                         round_to=2,
        #                                                                         outlier_speed=120.)

        # Save exceeding_locations_dict to a file for the sake of future usage (like on the map)
        # results_path = Path("./speed_exceeded_pickle")
        # with results_path.open("wb") as f:
        #     pickle.dump(exceeding_locations_dict, f)
        #
        # # I want to find locations were the speed is exceeded significant amount of times
        # thres = 0.9
        # for loc, counts in exceeding_locations_dict.items():
        #     exceeding_percent = counts[1] / counts[0]
        #     if exceeding_percent > thres:
        #         print(f"The speed was exceeded {100 * exceeding_percent:.0f}% of times around {loc}.")



if __name__ == "__main__":
    main()

import argparse
from pathlib import Path
import pickle
from collections import OrderedDict

from Warsaw_buses.process_data import speed_analysis, punctuality_analysis, utils, filter_data


def main():

    parser = argparse.ArgumentParser()

    # Choose what should be analysed:
    parser.add_argument("--punctuality", action="store_true",
                        help="Run punctuality_analysis()")
    parser.add_argument("--filter", action="store_true",
                       help="Filters out bus records that are not time monotonous."
                       )
    parser.add_argument("--calc_speed", action="store_true",
                        help="Run calc_speed(). For the given directory with busestrams data it creates NEW directory "
                             "where in each file a column describing the speed is added. This new directory's name is "
                             "dir_to_busestrams suffixed with '_with_speed'."
                        )
    parser.add_argument("--speed_statistics", action="store_true",
                        help="Run speed_statistics(). Print percent of times when the given speed is exceeded and "
                             "maximal and minimal speed."
                        )
    parser.add_argument("--speed_locations", action="store_true",
                        help="Run exceeding_the_speed_location()."
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
                        help="The program looks for the times when the speed specified here is exceeded.  It is set to "
                             "50 km/h by default.It is used in speed_statistics() and exceeding_the_speed_location()."
                        )
    parser.add_argument("--outlier_speed", type=float, default=120.,
                        help="If specified, speeds greater than outlier_speed are not taken into consideration. "
                             "It is set to 120 km/h by default."
                        )
    parser.add_argument("--round_to", type=int, default=2,
                        help="The notion of an exceeding location is rounded up to round_to decimal places. It is set"
                             " to 2 by default."
                        )
    parser.add_argument("--radius", type=float, default=None,
                        help="Locations further than the radius from the Warsaw centre are not considered. Defualt "
                             "to None"
                        )

    args = parser.parse_args()

    print(f"Using buses data from the directory {Path(args.dir_to_busestrams).absolute()}")
    if args.punctuality:
        print(f"Using timetables data from the directory {Path(args.dir_to_timetables).absolute()}")
        print(f"Using coordinates of the stops data from the directory {Path(args.dir_to_stops_coord).absolute()}")

    if args.filter:
        filter_data.filter_data_from_non_monotonically_increasing_time(dir_to_data=args.dir_to_busestrams)
    
    if args.calc_speed:
        print("\nStarts calculating speed...")
        speed_analysis.calc_speed(dir_to_busestrams=args.dir_to_busestrams)
        print("Speed calculated and saved successfully.")

    dir_to_busestrams_with_speed = args.dir_to_busestrams + "_with_speed"
    if args.speed_statistics:
        print("\nStarts calculating statistics...")
        speed_analysis.speed_statistics(dir_to_data=dir_to_busestrams_with_speed,
                                        speed=args.exceeded_speed,
                                        outlier_speed=args.outlier_speed)

    if args.speed_locations:
        print(f"\nLooking for locations were {args.exceeded_speed} km/h is exceeded...")
        print(f"You chose round_to as {args.round_to} so the map is divided into rectangles of the size "
              f"{utils.divided_map_area(args.round_to)[0]:.3f} km height and "
              f"{utils.divided_map_area(args.round_to)[1]:.3f} km width.")
        exceeding_locations_dict = speed_analysis.exceeding_the_speed_locations(dir_to_data=dir_to_busestrams_with_speed,
                                                                                speed=args.exceeded_speed,
                                                                                round_to=args.round_to,
                                                                                outlier_speed=args.outlier_speed)

        n_of_all_measurements = 0
        for loc, counts in exceeding_locations_dict.items():
            counts.append(counts[1]/counts[0])
            n_of_all_measurements += counts[0]

        exceeding_locations_dict_sorted = OrderedDict(sorted(exceeding_locations_dict.items(),
                                                             key=lambda t: t[1][2],
                                                             reverse=True))

        Warsaw_centre = [52.23213243754829, 21.0060709762026]
        n = 0
        print("\nFive locations with the biggest percent of buses exceeding the speed:")
        print("lat    lon      exceeding %")
        for (loc, counts) in exceeding_locations_dict_sorted.items():
            if args.radius is not None:
                if utils.dist(Warsaw_centre[0], Warsaw_centre[1], loc[0], loc[1]) < args.radius:
                    print(f"{loc[0]}, {loc[1]}    {100 * counts[2]:.0f}% ")
                    n += 1
            else:
                print(f"{loc[0]}, {loc[1]}    {100 * counts[2]:.0f}% ")
                n += 1

            if n >= 5:
                break

        # # Save exceeding_locations_dict to a file for the sake of future usage (like on the map)
        results_path = Path("./speed_exceeded_pickle")
        with results_path.open("wb") as f:
            pickle.dump(exceeding_locations_dict, f)

    if args.punctuality:
        print("\nStarts calculating delays...")
        print(f"It might take a while...")

        delays_dict = punctuality_analysis.calc_delays(dir_busestrams=args.dir_to_busestrams,
                                                       dir_timetables=args.dir_to_timetables,
                                                       dir_stops_coord=args.dir_to_stops_coord)
        punctuality_analysis.delays_statistics(delays_dict=delays_dict)


if __name__ == "__main__":
    main()

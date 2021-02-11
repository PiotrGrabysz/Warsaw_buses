import pytest
import numpy as np
from pathlib import Path
import pandas as pd

from process_data.punctuality_analysis import dist_bus_from_stop


DIR_TIMETABLES = Path("./test_punctuality_analysis_data/timetables")
DIR_STOPS_COORD = Path("./test_punctuality_analysis_data/stops_coord.json")


@pytest.mark.parametrize("bus_file_name,dir_correct_results",
                         [("./test_punctuality_analysis_data/busestrams_perfect_punctuality/128/1/5972.txt",
                           "./test_punctuality_analysis_data/busestrams_perfect_punctuality/results.txt"),
                          ("./test_punctuality_analysis_data/busestrams_delay_1/128/1/5972.txt",
                           "./test_punctuality_analysis_data/busestrams_delay_1/results.txt"),
                          ("./test_punctuality_analysis_data/busestrams_delay_2/128/1/5972.txt",
                           "./test_punctuality_analysis_data/busestrams_delay_2/results.txt")
                          ])
def test_punctuality(bus_file_name, dir_correct_results, dir_timetables=DIR_TIMETABLES,
                     dir_stops_coord=DIR_STOPS_COORD):

    bus_file_name = Path(bus_file_name)

    df = dist_bus_from_stop(bus_file_name=bus_file_name,
                            dir_timetables=dir_timetables,
                            dir_stops_coord=dir_stops_coord,
                            time_weight=0.001,
                            max_speed_around_the_stop=40.)

    correct_results = pd.read_csv(dir_correct_results)

    pd.testing.assert_series_equal(df["delay"], correct_results["delay"])


if __name__ == "__main__":
    pass
    # dir_busestrams = "./test_punctuality_analysis_data/busestrams_delay_2"
    # dir_timetables = DIR_TIMETABLES
    # dir_stops_coord = DIR_STOPS_COORD
    # line = "128"
    # brigade = "1"
    #
    # df = dist_bus_from_stop(dir_busestrams=dir_busestrams,
    #                         dir_timetables=dir_timetables,
    #                         dir_stops_coord=dir_stops_coord,
    #                         time_weight=0.001)
    #
    # df["delay"].to_csv("./test_punctuality_analysis_data/results.txt", index=False)

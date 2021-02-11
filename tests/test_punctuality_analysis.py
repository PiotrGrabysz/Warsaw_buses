import pytest
import numpy as np
from pathlib import Path
import pandas as pd

from process_data.punctuality_analysis import calc_delays
# import ..\process_data\punctuality_analysis\dist_bus_from_stopfrom process_data.punctuality_analysis import dist_bus_from_stop


DIR_TIMETABLES = Path("./test_punctuality_analysis_data/timetables")
DIR_STOPS_COORD = Path("./test_punctuality_analysis_data/stops_coord.json")


@pytest.mark.parametrize("dir_busestrams,dir_correct_results",
                         [("./test_punctuality_analysis_data/busestrams_perfect_punctuality",
                           "./test_punctuality_analysis_data/busestrams_perfect_punctuality/results.txt"),
                          ("./test_punctuality_analysis_data/busestrams_delay_1",
                           "./test_punctuality_analysis_data/busestrams_delay_1/results.txt"),
                          ("./test_punctuality_analysis_data/busestrams_delay_2",
                           "./test_punctuality_analysis_data/busestrams_delay_2/results.txt")
                          ])
def test_punctuality(dir_busestrams, dir_correct_results, dir_timetables=DIR_TIMETABLES,
                     dir_stops_coord=DIR_STOPS_COORD):

    line = "128"
    brigade = "1"

    delays = calc_delays(dir_busestrams=dir_busestrams,
                         dir_timetables=dir_timetables,
                         dir_stops_coord=dir_stops_coord,
                         time_weight=0.001)

    correct_results = np.loadtxt(dir_correct_results)
    assert np.allclose(np.array(delays), correct_results)


if __name__ == "__main__":

    dir_busestrams = "./test_punctuality_analysis_data/busestrams_delay_2"
    dir_timetables = DIR_TIMETABLES
    dir_stops_coord = DIR_STOPS_COORD
    line = "128"
    brigade = "1"

    df = dist_bus_from_stop(line=line,
                            brigade=brigade,
                            dir_busestrams=dir_busestrams,
                            dir_timetables=dir_timetables,
                            dir_stops_coord=dir_stops_coord,
                            time_weight=0.001)

    df["delay"].to_csv("./test_punctuality_analysis_data/results.txt", index=False)
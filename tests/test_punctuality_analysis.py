import pytest
from pathlib import Path
import pickle
import pandas as pd

from Warsaw_buses.process_data import punctuality_analysis


DIR_STOPS_COORD = Path("./test_punctuality_analysis_data/stops_coord.json")


@pytest.mark.parametrize("bus_file_name,dir_correct_results",
                         [("./test_punctuality_analysis_data/dist_bus_from_stop/busestrams_perfect_punctuality/128/1/5972.txt",
                           "./test_punctuality_analysis_data/dist_bus_from_stop/busestrams_perfect_punctuality/results.txt"),
                          ("./test_punctuality_analysis_data/dist_bus_from_stop/busestrams_delay_1/128/1/5972.txt",
                           "./test_punctuality_analysis_data/dist_bus_from_stop/busestrams_delay_1/results.txt"),
                          ("./test_punctuality_analysis_data/dist_bus_from_stop/busestrams_delay_2/128/1/5972.txt",
                           "./test_punctuality_analysis_data/dist_bus_from_stop/busestrams_delay_2/results.txt")
                          ])
def test_dist_bus_from_stop(bus_file_name, dir_correct_results):

    dir_timetables = Path("./test_punctuality_analysis_data/dist_bus_from_stop/timetables")
    dir_stops_coord = Path("./test_punctuality_analysis_data/stops_coord.json")

    bus_file_name = Path(bus_file_name)

    df = punctuality_analysis.dist_bus_from_stop(bus_file_name=bus_file_name,
                                                 dir_timetables=dir_timetables,
                                                 dir_stops_coord=dir_stops_coord,
                                                 time_weight=0.001,
                                                 max_speed_around_the_stop=40.)

    correct_results = pd.read_csv(dir_correct_results)

    pd.testing.assert_series_equal(df["delay"], correct_results["delay"])


def test_calc_delays():

    dir_to_busestrams = "./test_punctuality_analysis_data/calc_delays/busestrams"
    dir_to_timetables = "./test_punctuality_analysis_data/calc_delays/timetables"
    dir_to_stops_coord = "./test_punctuality_analysis_data/stops_coord.json"

    locations_dict = punctuality_analysis.calc_delays(dir_busestrams=dir_to_busestrams,
                                                      dir_timetables=dir_to_timetables,
                                                      dir_stops_coord=dir_to_stops_coord)

    correct_locations_path = Path("./test_punctuality_analysis_data/calc_delays/delays")
    with correct_locations_path.open("rb") as f:
        correct_locations = pickle.load(f)

    assert locations_dict == correct_locations


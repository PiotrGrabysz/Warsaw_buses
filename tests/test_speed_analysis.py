import pytest
from pathlib import Path
import pickle
import numpy as np
import pandas as pd

from Warsaw_buses.process_data import speed_analysis, utils


@pytest.mark.parametrize("f_path", ["./test_speed_analysis_data/dist/1.txt"])
def test_dist(f_path: str):
    """ Test dist() from process_data.velocity_analysis. The reference data were calculated using
    geopy.distance.distance() which use different algorithm than haversine.
    """
    data = np.loadtxt(f_path, delimiter=",")
    lat1 = data[:, 0]
    lon1 = data[:, 1]
    lat2 = data[:, 2]
    lon2 = data[:, 3]
    result = data[:, 4]

    dist_return = speed_analysis.dist(lat1, lon1, lat2, lon2)
    # atol=0.001 means tolerance up to 0.5 meter
    assert np.allclose(dist_return, result, atol=0.0005)


@pytest.mark.parametrize("dir_to_busestrams, dir_correct_results",
                         [("./test_speed_analysis_data/calc_speed/busestrams",
                          "./test_speed_analysis_data/calc_speed/busestrams_with_speed_correct")])
def test_calc_speed(dir_to_busestrams: str, dir_correct_results: str, tmp_path):
    """Test if files created by calc_speed are correct"""

    dir_to_output_data = Path(tmp_path) / "buses_with_speed"
    speed_analysis.calc_speed(dir_to_busestrams=dir_to_busestrams, dir_to_output_data=dir_to_output_data)

    for bus_file in utils.bus_data_iterator(dir_to_busestrams=dir_to_output_data):

        # Find the path the the correct file used for comparison
        bus_file_parts = bus_file.parts
        line = bus_file_parts[-3]
        brigade = bus_file_parts[-2]
        f_name = bus_file_parts[-1]
        bus_data_correct_file = Path(dir_correct_results) / line / brigade / f_name

        # The data calculated by calc_speed()
        bus_speed = pd.read_csv(bus_file, usecols=["Speed"])
        # The correct data
        bus_speed_correct = pd.read_csv(bus_data_correct_file, usecols=["Speed"])

        # Assert if the two pd.DataFrames are equal
        pd.testing.assert_frame_equal(bus_speed, bus_speed_correct)


def test_statistics_output(capsys):
    """Tests if info printed by speed_statistics() is correct"""

    dir_to_buses = Path("./test_speed_analysis_data/calc_speed/busestrams_with_speed_correct")
    statistics_correct_output_path = Path("./test_speed_analysis_data/speed_statistics/statistics_output.txt")

    statistics_correct_output = []
    with statistics_correct_output_path.open("r") as f:
        for line in f:
            statistics_correct_output.append(line.rstrip())

    speed_analysis.speed_statistics(dir_to_data=dir_to_buses, outlier_speed=120)
    out, err = capsys.readouterr()
    out_lines = out.split("\n")

    assert statistics_correct_output == out_lines


def test_exceeding_the_speed_locations():
    """Tests the exceeding_the_speed_locations()."""

    dir_to_data = Path("./test_speed_analysis_data/calc_speed/busestrams_with_speed_correct")
    correct_results_path = Path("./test_speed_analysis_data/exceeding_locations/exceeding_locations_dict")

    locations_dict = speed_analysis.exceeding_the_speed_locations(dir_to_data=dir_to_data, speed=50, round_to=2,
                                                                  outlier_speed=120)

    with correct_results_path.open("rb") as f:
        correct_results = pickle.load(f)

    assert correct_results == locations_dict





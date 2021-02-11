import pytest
from pathlib import Path
import numpy as np
import pandas as pd
from process_data.speed_analysis import dist, bus_data_iterator
from process_data.speed_analysis import calc_speed

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

    dist_return = dist(lat1, lon1, lat2, lon2)
    # atol=0.001 means tolerance up to 0.5 meter
    assert np.allclose(dist_return, result, atol=0.0005)


@pytest.mark.parametrize("dir_to_busestrams, dir_correct_results",
                         [("./test_speed_analysis_data/calc_speed/busestrams",
                          "./test_speed_analysis_data/calc_speed/busestrams_with_speed_correct")])
def test_calc_speed(dir_to_busestrams: str, dir_correct_results: str, tmp_path):
    """Test if files created by calc_speed are correct"""

    dir_to_output_data = Path(tmp_path) / "buses_with_speed"
    calc_speed(dir_to_busestrams=dir_to_busestrams, dir_to_output_data=dir_to_output_data)

    for bus_file in bus_data_iterator(dir_to_busestrams=dir_to_output_data):

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


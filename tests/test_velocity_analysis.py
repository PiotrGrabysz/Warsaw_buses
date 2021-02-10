import pytest
import numpy as np
from process_data.velocity_analysis import dist

@pytest.mark.parametrize("f_path", ["./test_velocity_analysis_data/dist/1.txt"])
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


test_dist("./test_velocity_analysis_data/dist/1.txt")

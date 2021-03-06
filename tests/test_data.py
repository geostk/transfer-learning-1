import os
import numpy as np

import imageio

def load_jpg(filename):
    return np.array(imageio.imread(filename))

def test_load_data():
    SCRIPTLOC = os.path.dirname(__file__)
    data = load_jpg('{}/data/j8za09050_drz_small.jpg'.format(SCRIPTLOC))
    cmp = np.array([[255, 252, 246, 255], [255, 241, 255, 241], [255, 255, 246, 13], [248, 255, 255, 0]])
    assert np.allclose(data[10:14, 10:14], cmp, atol=1)

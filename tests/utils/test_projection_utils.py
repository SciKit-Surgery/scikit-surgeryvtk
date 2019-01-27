# -*- coding: utf-8 -*-

import pytest
import numpy as np

import sksurgeryvtk.utils.projection_utils as pu


def test_project_points_invalid_as_input_null():

    with pytest.raises(ValueError):
        pu.project_points(None, None, None, None)

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 2]), None, None, None)

    with pytest.raises(ValueError):
        pu.project_points(np.zeros([4, 2]), np.zeros([4, 4]), None, None)

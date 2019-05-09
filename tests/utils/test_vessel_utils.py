# -*- coding: utf-8 -*-

import pytest
import vtk
import numpy as np
from vtk.util import colors
from sksurgeryvtk.models.vtk_surface_model import VTKSurfaceModel
import sys
import os

import sksurgeryvtk.utils.vessel_utils as vu


def test_load_vessel_centrelines_from_file_valid():
    input_file = 'tests/data/vessel_centrelines/vessel_centrelines.dat'
    vu.load_vessel_centrelines(input_file)

#  -*- coding: utf-8 -*-

import pytest
import vtk
from vtk.util import colors
from sksurgeryoverlay.vtk.vtk_surface_model import VTKSurfaceModel


@pytest.fixture(scope="function")
def valid_vtk_model():
    input_file = 'inputs/tests/Prostate.vtk'
    model = VTKSurfaceModel(input_file, colors.red)
    return model


def test_valid_vtk_results_in_vtkpolydatareader(valid_vtk_model):
    assert isinstance(valid_vtk_model.reader, vtk.vtkPolyDataReader)


def test_valid_stl_results_in_vtkstlreader():
    input_file = 'inputs/tests/Fiducial.stl'
    model = VTKSurfaceModel(input_file, colors.red)
    assert isinstance(model.reader, vtk.vtkSTLReader)


def test_valid_ply_results_in_vtkplyreader():
    input_file = 'inputs/tests/Tumor.ply'
    model = VTKSurfaceModel(input_file, colors.red)
    assert isinstance(model.reader, vtk.vtkPLYReader)


def test_invalid_model_file_format():
    input_file = 'tox.ini'
    with pytest.raises(ValueError):
        VTKSurfaceModel(input_file, colors.red)


def test_its_valid_for_null_filename():
    model = VTKSurfaceModel(None, colors.red)
    assert model.source is not None


def test_invalid_color_red_not_float():
    with pytest.raises(TypeError):
        VTKSurfaceModel('inputs/tests/Prostate.vtk', (1, 0.0, 0.0))


def test_invalid_color_green_not_float():
    with pytest.raises(TypeError):
        VTKSurfaceModel('inputs/tests/Prostate.vtk', (0.0, 1, 0.0))


def test_invalid_color_blue_not_float():
    with pytest.raises(TypeError):
        VTKSurfaceModel('inputs/tests/Prostate.vtk', (0.0, 0.0, 1))


def test_invalid_color_red_too_low():
    with pytest.raises(ValueError):
        VTKSurfaceModel('inputs/tests/Prostate.vtk', (-1.0, 0.0, 0.0))


def test_invalid_color_green_too_low():
    with pytest.raises(ValueError):
        VTKSurfaceModel('inputs/tests/Prostate.vtk', (0.0, -1.0, 0.0))


def test_invalid_color_blue_too_low():
    with pytest.raises(ValueError):
        VTKSurfaceModel('inputs/tests/Prostate.vtk', (0.0, 0.0, -1.0))


def test_invalid_color_red_too_high():
    with pytest.raises(ValueError):
        VTKSurfaceModel('inputs/tests/Prostate.vtk', (1.1, 0.0, 0.0))


def test_invalid_color_green_too_high():
    with pytest.raises(ValueError):
        VTKSurfaceModel('inputs/tests/Prostate.vtk', (1.0, 1.1, 0.0))


def test_invalid_color_blue_too_high():
    with pytest.raises(ValueError):
        VTKSurfaceModel('inputs/tests/Prostate.vtk', (1.0, 0.0, 1.1))


def test_invalid_opacity_not_float():
    with pytest.raises(TypeError):
        VTKSurfaceModel('inputs/tests/Prostate.vtk', (1.0, 0.0, 1.0), opacity=1)


def test_invalid_opacity_too_low():
    with pytest.raises(ValueError):
        VTKSurfaceModel('inputs/tests/Prostate.vtk', (1.0, 0.0, 1.0), opacity=-1.0)


def test_invalid_opacity_too_high():
    with pytest.raises(ValueError):
        VTKSurfaceModel('inputs/tests/Prostate.vtk', (1.0, 0.0, 1.0), opacity=1.1)


def test_invalid_visibility_not_bool():
    with pytest.raises(TypeError):
        VTKSurfaceModel('inputs/tests/Prostate.vtk', (1.0, 0.0, 1.0), visibility=1.0)

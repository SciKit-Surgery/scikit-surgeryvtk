# -*- coding: utf-8 -*-

import pytest
import vtk
import numpy as np
from vtk.util import colors
from sksurgeryvtk.models.vtk_surface_model import VTKSurfaceModel


@pytest.fixture(scope="function")
def valid_vtk_model():
    input_file = 'tests/data/models/Prostate.vtk'
    model = VTKSurfaceModel(input_file, colors.red)
    return model


def test_valid_vtk_results_in_vtkpolydatareader(valid_vtk_model):
    assert isinstance(valid_vtk_model.reader, vtk.vtkPolyDataReader)


def test_valid_stl_results_in_vtkstlreader():
    input_file = 'tests/data/models/Fiducial.stl'
    model = VTKSurfaceModel(input_file, colors.red)
    assert isinstance(model.reader, vtk.vtkSTLReader)


def test_valid_ply_results_in_vtkplyreader():
    input_file = 'tests/data/models/Tumor.ply'
    model = VTKSurfaceModel(input_file, colors.red)
    assert isinstance(model.reader, vtk.vtkPLYReader)


def test_invalid_because_model_file_format():
    input_file = 'tox.ini'
    with pytest.raises(ValueError):
        VTKSurfaceModel(input_file, colors.red)


def test_its_valid_for_null_filename():
    model = VTKSurfaceModel(None, colors.red)
    assert model.source is not None


def test_invalid_because_filename_invalid():
    with pytest.raises(TypeError):
        VTKSurfaceModel(9, colors.red)


def test_invalid_because_color_red_not_float():
    with pytest.raises(TypeError):
        VTKSurfaceModel('tests/data/models/Prostate.vtk', (1, 0.0, 0.0))


def test_invalid_because_color_green_not_float():
    with pytest.raises(TypeError):
        VTKSurfaceModel('tests/data/models/Prostate.vtk', (0.0, 1, 0.0))


def test_invalid_because_color_blue_not_float():
    with pytest.raises(TypeError):
        VTKSurfaceModel('tests/data/models/Prostate.vtk', (0.0, 0.0, 1))


def test_invalid_because_color_red_too_low():
    with pytest.raises(ValueError):
        VTKSurfaceModel('tests/data/models/Prostate.vtk', (-1.0, 0.0, 0.0))


def test_invalid_because_color_green_too_low():
    with pytest.raises(ValueError):
        VTKSurfaceModel('tests/data/models/Prostate.vtk', (0.0, -1.0, 0.0))


def test_invalid_because_color_blue_too_low():
    with pytest.raises(ValueError):
        VTKSurfaceModel('tests/data/models/Prostate.vtk', (0.0, 0.0, -1.0))


def test_invalid_because_color_red_too_high():
    with pytest.raises(ValueError):
        VTKSurfaceModel('tests/data/models/Prostate.vtk', (1.1, 0.0, 0.0))


def test_invalid_because_color_green_too_high():
    with pytest.raises(ValueError):
        VTKSurfaceModel('tests/data/models/Prostate.vtk', (1.0, 1.1, 0.0))


def test_invalid_because_color_blue_too_high():
    with pytest.raises(ValueError):
        VTKSurfaceModel('tests/data/models/Prostate.vtk', (1.0, 0.0, 1.1))


def test_invalid_because_opacity_not_float():
    with pytest.raises(TypeError):
        VTKSurfaceModel('tests/data/models/Prostate.vtk', (1.0, 0.0, 1.0), opacity=1)


def test_invalid_because_opacity_too_low():
    with pytest.raises(ValueError):
        VTKSurfaceModel('tests/data/models/Prostate.vtk', (1.0, 0.0, 1.0), opacity=-1.0)


def test_invalid_because_opacity_too_high():
    with pytest.raises(ValueError):
        VTKSurfaceModel('tests/data/models/Prostate.vtk', (1.0, 0.0, 1.0), opacity=1.1)


def test_invalid_because_visibility_not_bool():
    with pytest.raises(TypeError):
        VTKSurfaceModel('tests/data/models/Prostate.vtk', (1.0, 0.0, 1.0), visibility=1.0)


def test_invalid_because_name_is_none():
    with pytest.raises(TypeError):
        model = VTKSurfaceModel(None, (1.0, 0.0, 1.0))
        model.set_name(None)


def test_invalid_because_name_is_empty():
    with pytest.raises(ValueError):
        model = VTKSurfaceModel(None, (1.0, 0.0, 1.0))
        model.set_name("")


def test_ensure_setter_and_getter_set_something():
    model = VTKSurfaceModel(None, (1.0, 0.0, 1.0))
    assert model.get_name() == ""
    model.set_name("banana")
    assert model.get_name() == "banana"


def test_set_get_user_transform_do_set_something():
    model = VTKSurfaceModel(None, (1.0, 0.0, 1.0))
    vtk_matrix = vtk.vtkMatrix4x4()
    vtk_matrix.Identity()
    vtk_matrix.SetElement(0, 0, 2)  # i.e. not identity
    model.set_user_matrix(vtk_matrix)
    result = model.get_user_matrix()
    assert result is not None
    assert result == vtk_matrix


def test_set_model_transform_is_used():
    model = VTKSurfaceModel(None, (1.0, 0.0, 1.0))
    vtk_matrix = vtk.vtkMatrix4x4()
    vtk_matrix.Identity()
    vtk_matrix.SetElement(0, 0, 2)  # i.e. not identity
    model.set_model_transform(vtk_matrix)
    result = model.get_model_transform()
    assert result is not None
    assert result.GetElement(0, 0) == vtk_matrix.GetElement(0, 0)


def test_extract_points_and_normals_as_numpy_array():
    input_file = 'tests/data/models/Prostate.vtk'
    model = VTKSurfaceModel(input_file, colors.red)
    number_of_points = model.get_number_of_points()
    points = model.get_points_as_numpy()
    assert isinstance(points, np.ndarray)
    assert points.shape[0] == number_of_points
    assert points.shape[1] == 3
    normals = model.get_normals_as_numpy()
    assert isinstance(normals, np.ndarray)
    assert normals.shape[0] == number_of_points
    assert normals.shape[1] == 3




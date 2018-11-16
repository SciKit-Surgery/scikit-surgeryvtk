import pytest
import vtk

from sksurgeryoverlay.vtk.vtk_model import VTKModel
from vtk.util import colors

@pytest.fixture(scope="function")
def valid_vtk_model():
    input_file = 'inputs/tests/Prostate.vtk'
    model = VTKModel(input_file, colors.red)
    return model

def test_valid_vtk(valid_vtk_model):
    assert isinstance(valid_vtk_model.reader, vtk.vtkPolyDataReader)

def test_valid_stl():
    input_file = 'inputs/tests/Fiducial.stl'
    model = VTKModel(input_file, colors.red)
    assert isinstance(model.reader,vtk.vtkSTLReader)

def test_valid_ply():
    input_file = 'inputs/tests/Tumor.ply'
    model = VTKModel(input_file, colors.red)
    assert isinstance(model.reader,vtk.vtkPLYReader)

def test_valid_stl_failing():
    input_file = 'inputs/tests/Fiducial.stl'
    model = VTKModel(input_file, colors.red)
    assert not isinstance(model.reader,vtk.vtkPolyDataReader)

def test_invalid_model_file():
    input_file = 'tox.ini'
    with pytest.raises(ValueError):
        model = VTKModel(input_file, colors.red)

def test_toggle_visiblity(valid_vtk_model):

    valid_vtk_model.toggle_visible()
    assert not valid_vtk_model.visible

    valid_vtk_model.toggle_visible()
    assert valid_vtk_model.visible



import pytest
import vtk

from sksurgeryoverlay.vtk.vtk_model import VTKModel
from vtk.util import colors

def test_valid_vtk():
    input_file = 'inputs/tests/Prostate.vtk'
    model = VTKModel(input_file, colors.red)
    assert isinstance(model.reader, vtk.vtkPolyDataReader)

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

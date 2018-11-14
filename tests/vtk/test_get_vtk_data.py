# coding=utf-8

"""ardavin tests"""

import pytest
from sksurgeryoverlay.vtk.vtk_model import LoadVTKModelsFromDirectory


def test_load_models():
    vtk_dir = 'inputs/Liver'
    model_loader = LoadVTKModelsFromDirectory()
    models = model_loader.get_models(vtk_dir)

    num_models = len(models)
    expected_num_models = 9

    assert num_models == expected_num_models

def test_load_invalid_model_dir():
    vtk_dir = ''
    model_loader = LoadVTKModelsFromDirectory()
    models = model_loader.get_models(vtk_dir)

    assert models == []

def test_load_dir_with_no_VTKs():
    vtk_dir = 'tests/'
    model_loader = LoadVTKModelsFromDirectory()
    models = model_loader.get_models(vtk_dir)

    assert models == []
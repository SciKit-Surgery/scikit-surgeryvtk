# -*- coding: utf-8 -*-

import os
import platform
import six
import pytest

from sksurgeryvtk.models.vtk_surface_model_directory_loader import VTKSurfaceModelDirectoryLoader


@pytest.fixture(scope="function")
def valid_vtk_model():
    input_file = 'tests/data/models/tests/Prostate.vtk'
    model = VTKModel(input_file, colors.red)
    return model


def test_invalid_because_null_directory_name():
    with pytest.raises(ValueError):
        VTKSurfaceModelDirectoryLoader(None)


def test_invalid_because_empty_directory_name():
    with pytest.raises(ValueError):
        VTKSurfaceModelDirectoryLoader("")

def print_dir_permissions(dir_name):
        print("R: {} W: {} X: {}".format(os.access(dir_name, os.R_OK),
                                     os.access(dir_name, os.W_OK),
                                     os.access(dir_name, os.X_OK)))
    

def test_invalid_because_directory_not_readable():

    if platform.system() == 'Windows' or not platform.system():
        six.print_('Not running test as Windows doesnt do permissions.')
        return
    
    output_name = 'tests/output/'
    if not os.path.exists(output_name):
        os.mkdir(output_name)
    dir_name = 'tests/output/unreadable'
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    print_dir_permissions(dir_name)

    os.chmod(dir_name, 0o000)
    print_dir_permissions(dir_name)
    with pytest.raises(ValueError):
        VTKSurfaceModelDirectoryLoader(dir_name)
    os.chmod(dir_name, 0o100)
    print_dir_permissions(dir_name)
    with pytest.raises(ValueError):
        VTKSurfaceModelDirectoryLoader(dir_name)
    os.chmod(dir_name, 0o400)
    print_dir_permissions(dir_name)
    with pytest.raises(ValueError):
        VTKSurfaceModelDirectoryLoader(dir_name)
    os.chmod(dir_name, 0o500)
    print_dir_permissions(dir_name)
    VTKSurfaceModelDirectoryLoader(dir_name)  # should instantiate, but no data.
    os.rmdir(dir_name)

def test_valid_dir_with_default_colours():
    dir_name = 'tests/data/models/Kidney'
    loader = VTKSurfaceModelDirectoryLoader(dir_name)
    assert len(loader.models) == 2
    assert loader.models[0].get_colour() == loader.colours[str(0)]
    assert loader.models[1].get_colour() == loader.colours[str(1)]


def test_valid_dir_with_colours_from_file_from_issue_4():
    dir_name = 'tests/data/models/Liver'
    loader = VTKSurfaceModelDirectoryLoader(dir_name)
    assert len(loader.models) == 9

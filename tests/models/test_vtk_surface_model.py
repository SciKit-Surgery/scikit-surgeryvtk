# -*- coding: utf-8 -*-


import os
import sys

import cv2
import numpy as np
import pytest
import vtk
from sksurgeryimage.utilities.utilities import are_similar
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


def test_invalid_because_pickable_not_bool():
    with pytest.raises(TypeError):
        VTKSurfaceModel('tests/data/models/Prostate.vtk', (1.0, 0.0, 1.0),
                        pickable=1.0)


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


def test_flat_shaded_on_coloured_background(setup_vtk_overlay_window):
    # input_file = 'tests/data/models/liver.ply' # Don't use this one. It renders Grey, regardless of what colour you create it at.
    input_file = 'tests/data/liver/liver_sub.ply'
    model = VTKSurfaceModel(input_file, colors.white)
    widget, _, app = setup_vtk_overlay_window
    widget.add_vtk_actor(model.actor)
    model.set_no_shading(True)
    widget.get_background_renderer().SetBackground(0, 0, 1)
    widget.show()
    model.set_no_shading(False)
    widget.get_background_renderer().SetBackground(0, 1, 0)
    widget.show()
    # app.exec()


def test_valid_set_texture_with_png_format(vtk_overlay_with_gradient_image):
    input_file = 'tests/data/models/liver.ply'
    model = VTKSurfaceModel(input_file, colors.red)
    texture_file = 'tests/data/images/image0232.png'
    model.set_texture(texture_file)
    image, widget, _, app = vtk_overlay_with_gradient_image
    widget.add_vtk_actor(model.actor)
    widget.show()
    # return model

    with pytest.raises(ValueError):
        model.set_texture('')

    # Save the scene to a file for parity check.
    # See test_set_texture_regression() below.
    # This line should be run again if the code is (purposefully) changed.
    # screenshot_filename = 'tests/data/images/set_texture_test.png'
    # widget.save_scene_to_file(screenshot_filename)
    # app.exec()


def test_valid_set_texture_with_jpeg_format(vtk_overlay_with_gradient_image):
    input_file = 'tests/data/models/liver.ply'
    model = VTKSurfaceModel(input_file, colors.red)
    model.set_texture('tests/data/images/image0232.jpeg')
    image, widget, _, app = vtk_overlay_with_gradient_image
    widget.add_vtk_actor(model.actor)
    widget.show()

    # # return model
    with pytest.raises(ValueError):
        model.set_texture('')

    # app.exec()


def test_valid_set_texture_with_jpg_format(vtk_overlay_with_gradient_image):
    input_file = 'tests/data/models/liver.ply'
    model = VTKSurfaceModel(input_file, colors.red)
    model.set_texture('tests/data/images/image0232.jpg')
    image, widget, _, app = vtk_overlay_with_gradient_image
    widget.add_vtk_actor(model.actor)
    widget.show()
    # return model
    with pytest.raises(ValueError):
        model.set_texture('')

    # app.exec()


def test_invalid_set_texture_because_texture_file_format():
    input_file = 'tests/data/models/liver.ply'
    model = VTKSurfaceModel(input_file, colors.red)
    texture_file = 'tox.ini'
    with pytest.raises(ValueError):
        model.set_texture(texture_file)


def test_invalid_set_texture_because_texture_filename_empty():
    input_file = 'tests/data/models/liver.ply'
    model = VTKSurfaceModel(input_file, colors.red)
    with pytest.raises(ValueError):
        model.set_texture('')


def test_valid_unset_texture_when_called_with_none(vtk_overlay_with_gradient_image):
    input_file = 'tests/data/models/liver.ply'
    model = VTKSurfaceModel(input_file, colors.red)
    model.set_texture('tests/data/images/image0232.jpg')
    image, widget, _, app = vtk_overlay_with_gradient_image
    widget.add_vtk_actor(model.actor)
    widget.show()
    model.set_texture(None)

    # return model
    with pytest.raises(ValueError):
        model.set_texture('')

    # app.exec()


def test_set_texture_regression(vtk_overlay_with_gradient_image):
    """
    Test texture regression
    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """
    in_github_ci = os.environ.get('CI')
    print("Github CI: " + str(in_github_ci))

    input_file = 'tests/data/models/liver.ply'
    model = VTKSurfaceModel(input_file, colors.red)
    model.set_texture('tests/data/images/image0232.png')

    image, widget, _vtk_std_err, _pyside_qt_app = vtk_overlay_with_gradient_image

    widget.add_vtk_actor(model.actor)
    widget.resize(400, 400)
    widget.AddObserver("ExitEvent", lambda o, e, a=_pyside_qt_app: a.quit())

    widget.show()
    widget.Initialize()
    widget.Start()

    # Read the saved scene and compare it with the current scene.
    screenshot_filename = 'tests/data/images/set_texture_test.png'
    screenshot = cv2.imread(screenshot_filename)
    # OpenCV uses BGR while VTK uses RGB.
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

    current_scene = widget.convert_scene_to_numpy_array()

    tmp_dir = 'tests/output'
    if not os.path.isdir(tmp_dir):
        os.makedirs(tmp_dir)
    cv2.imwrite(os.path.join(tmp_dir, 'screenshot.png'), screenshot)
    cv2.imwrite(os.path.join(tmp_dir, 'current_scene.png'), current_scene)

    assert are_similar(screenshot, current_scene, threshold=0.995,
                       metric=cv2.TM_CCOEFF_NORMED, mean_threshold=0.005)

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    widget.close()


def test_get_set_visibility():
    input_file = 'tests/data/models/liver.ply'
    model = VTKSurfaceModel(input_file, colors.red)
    assert (isinstance(model.get_visibility(), bool))
    assert (model.get_visibility())
    model.set_visibility(False)
    assert (not model.get_visibility())
    model.set_visibility(True)
    assert (model.get_visibility())


def test_get_set_outline():
    """Setting and getting the outline rendering status"""
    input_file = 'tests/data/models/liver.ply'
    model = VTKSurfaceModel(input_file, colors.red, visibility=True,
                            opacity=1.0, pickable=True,
                            outline=True)
    assert (isinstance(model.get_outline(), bool))
    assert (model.get_outline())
    model.set_outline(False)
    assert (not model.get_outline())
    model.set_outline(True)
    assert (model.get_outline())


def test_get_outline_actor():
    """Calling get_outline rendering without a camera"""
    input_file = 'tests/data/models/liver.ply'
    model = VTKSurfaceModel(input_file, colors.red, visibility=True,
                            opacity=1.0, pickable=True,
                            outline=True)
    model.get_outline_actor(active_camera=None)

    model.set_outline(False)
    assert model.get_outline_actor(active_camera=None) is None

import pytest
import vtk
import six
import numpy as np

import sksurgeryvtk.camera.vtk_camera_model as cam

def test_create_vtk_matrix_4x4_from_numpy_fail_on_invalid_shape():

    array = np .ones([2,3])

    with pytest.raises(ValueError):
        cam.create_vtk_matrix_4x4_from_numpy(array)


def test_create_vtk_matrix_4x4_from_numpy():

    array = np.random.rand(4,4)

    vtk_matrix = cam.create_vtk_matrix_4x4_from_numpy(array)

    for i in range(4):
        for j in range(4):
            assert vtk_matrix.GetElement(i,j) == array[i,j]


def test_set_projection_matrix_fail_on_invalid_camera():

    not_a_camera = np.ones([5,5])
    vtk_matrix = vtk.vtkMatrix4x4()

    with pytest.raises(TypeError):
        cam.set_projection_matrix(not_a_camera,  vtk_matrix)


def test_set_projection_matrix_fail_on_invalid_camera():

    camera = vtk.vtkCamera()
    not_a_vtk_matrix = np.ones([5,5])

    with pytest.raises(TypeError):
        cam.set_projection_matrix(camera,  not_a_vtk_matrix)


def test_set_projection_matrix():

    camera = vtk.vtkCamera()
    vtk_matrix = vtk.vtkMatrix4x4()
    cam.set_projection_matrix(camera, vtk_matrix)
    
    assert camera.GetExplicitProjectionTransformMatrix() == vtk_matrix


def test_get_projection_matrix_from_intrinsics():
        camera = vtk.vtkCamera()
        array = cam.get_projection_matrix_from_intrinsics(camera, 400, 400, 1, 0)

        assert isinstance(array, np.ndarray)





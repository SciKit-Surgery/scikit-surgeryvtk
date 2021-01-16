import pytest
import numpy as np
import vtk
import sksurgeryvtk.utils.matrix_utils as mu


def test_get_l2r_matrix_smartliver_format():
    
    l2r = np.array([[1, 2, 3, 1],
                    [4, 5, 6, 2],
                    [7, 8, 9, 3],
                    [0, 0, 0, 1]])

    l2r_smartliver = \
        mu.get_l2r_smartliver_format(l2r)

    expected = np.array([[1, 2, 3],
                         [4, 5, 6],
                         [7, 8, 9],
                         [1, 2, 3]])

    assert(np.array_equal(l2r_smartliver, expected))


def test_numpy_to_vtk():

    numpy_array = np.random.random((4, 4))
    vtk_matrix = mu.create_vtk_matrix_from_numpy(numpy_array)
    converted_back = mu.create_numpy_matrix_from_vtk(vtk_matrix)
    assert np.allclose(numpy_array, converted_back)
    assert id(numpy_array) != id(converted_back)


def test_invalid_because_not_vtk_matrix():

    with pytest.raises(TypeError):
        _ = mu.create_numpy_matrix_from_vtk("banana")


def test_invalid_because_not_numpy_matrix():

    with pytest.raises(TypeError):
        _ = mu.create_vtk_matrix_from_numpy("banana")


def test_invalid_because_not_4x4():

    with pytest.raises(ValueError):
        _ = mu.create_vtk_matrix_from_numpy(np.random.random((3, 4)))

    with pytest.raises(ValueError):
        _ = mu.create_vtk_matrix_from_numpy(np.random.random((4, 3)))


def test_numpy_rotation_matches_vtk():

    # The C++ code says VTK does Z, X, Y
    rx = 10
    ry = 45
    rz = 20
    transform = vtk.vtkTransform()
    transform.Identity()
    transform.PreMultiply()
    transform.RotateZ(rz)
    transform.RotateX(rx)
    transform.RotateY(ry)
    vtk_matrix = transform.GetMatrix()
    assert vtk_matrix

    # Im calling this string based function, just to get some coverage.
    # This function goes on to call a list based function.
    numpy = mu.create_matrix_from_string(str(rx) + ","
                                         + str(ry) + ","
                                         + str(rz) + ",0,0,0",
                                         is_in_radians=False)
    vtk_matrix = mu.create_numpy_matrix_from_vtk(vtk_matrix)
    assert np.allclose(numpy, vtk_matrix)


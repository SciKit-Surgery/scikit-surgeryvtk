# -*- coding: utf-8 -*-

import pytest
import vtk
import six
import cv2
import numpy as np
import sksurgeryvtk.camera.vtk_camera_model as cam
import sksurgeryvtk.utils.projection_utils as pu
import sksurgeryvtk.utils.matrix_utils as mu
import sksurgeryvtk.models.vtk_surface_model as sm


def test_create_vtk_matrix_4x4_from_numpy_fail_on_invalid_type():

    with pytest.raises(TypeError):
        mu.create_vtk_matrix_from_numpy("hello")


def test_create_vtk_matrix_4x4_from_numpy_fail_on_invalid_shape():

    array = np.ones([2, 3])

    with pytest.raises(ValueError):
        mu.create_vtk_matrix_from_numpy(array)


def test_create_vtk_matrix_4x4_from_numpy():

    array = np.random.rand(4, 4)

    vtk_matrix = mu.create_vtk_matrix_from_numpy(array)

    for i in range(4):
        for j in range(4):
            assert vtk_matrix.GetElement(i, j) == array[i, j]


def test_set_pose_identity_should_give_origin():

    np_matrix = np.eye(4)
    vtk_matrix = mu.create_vtk_matrix_from_numpy(np_matrix)

    vtk_camera = vtk.vtkCamera()
    cam.set_camera_pose(vtk_camera, vtk_matrix)

    position = vtk_camera.GetPosition()
    focal_point = vtk_camera.GetFocalPoint()
    view_up = vtk_camera.GetViewUp()

    # Identity matrix should give:
    # Position at origin
    # Facing along positive z axis
    # If x points right in the image, y axis points down.
    assert position == (0, 0, 0)
    assert focal_point[2] > 0
    assert view_up == (0, -1, 0)


def test_camera_projection(setup_vtk_overlay_window):

    vtk_overlay, factory, vtk_std_err, app = setup_vtk_overlay_window

    # See data:
    # chessboard_14_10_3_no_ID.txt - 3D chessboard coordinates
    # left-1095.png - image taken of chessboard
    # left-1095.png.points.txt - detected 2D image points
    # calib.intrinsic.txt - top 3x3 matrix are intrinsic parameters
    # left-1095.extrinsic.txt - model to camera matrix, a.k.a camera extrinsics, a.k.a pose

    # Load 3D points
    model_points_file = 'tests/data/calibration/chessboard_14_10_3_no_ID.txt'
    model_points = np.loadtxt(model_points_file)
    number_model_points = model_points.shape[0]
    model_polydata = [sm.VTKSurfaceModel('tests/data/calibration/chessboard_14_10_3.vtk', (1.0, 1.0, 0.0))]

    # Load images
    left_image = cv2.imread('tests/data/calibration/left-1095-undistorted.png')
    left_mask = cv2.imread('tests/data/calibration/left-1095-undistorted-mask.png')
    left_mask = cv2.cvtColor(left_mask, cv2.COLOR_RGB2GRAY)

    # Load 2D points
    image_points_file ='tests/data/calibration/left-1095-undistorted.png.points.txt'
    image_points = np.loadtxt(image_points_file)
    number_image_points = image_points.shape[0]

    # Load intrinsics for projection matrix.
    intrinsics_file = 'tests/data/calibration/calib.left.intrinsic.txt'
    intrinsics = np.loadtxt(intrinsics_file)

    # Load extrinsics for camera pose (position, orientation).
    extrinsics_file = 'tests/data/calibration/left-1095.extrinsic.txt'
    extrinsics = np.loadtxt(extrinsics_file)

    # OpenCV maps from chessboard to camera.
    # Assume chessboard == world, so the input matrix is world_to_camera.
    # We need camera_to_world to position the camera in world coordinates.
    # So, invert it.
    camera_to_world = np.linalg.inv(extrinsics)

    assert number_model_points == 140
    assert number_image_points == 140
    assert len(image_points) == 140
    assert len(model_points) == 140

    screen = app.primaryScreen()
    width = left_image.shape[1]
    height = left_image.shape[0]
    while width >= screen.geometry().width() or height >= screen.geometry().height():
        width //= 2
        height //= 2

    vtk_overlay.add_vtk_models(model_polydata)
    vtk_overlay.set_video_image(left_image)
    vtk_overlay.set_camera_pose(camera_to_world)
    vtk_overlay.resize(width, height)
    vtk_overlay.show()

    vtk_renderer = vtk_overlay.get_foreground_renderer()
    vtk_camera = vtk_overlay.get_foreground_camera()
    vtk_renderwindow_size = vtk_overlay.GetRenderWindow().GetSize()

    # Wierdly, vtkRenderWindow, sometimes seems to use the wrong resolution,
    # like its trying to render at high resolution, maybe for anti-aliasing or averaging?
    scale_x = left_image.shape[1] / vtk_renderwindow_size[0]
    scale_y = left_image.shape[0] / vtk_renderwindow_size[1]

    # Print out some debug. On some displays, the widget size and the size of the vtkRenderWindow don't match.
    six.print_('Left image = (' + str(left_image.shape[1]) + ', ' + str(left_image.shape[0]) + ')')
    six.print_('Chosen size = (' + str(width) + ', ' + str(height) + ')')
    six.print_('Render window = ' + str(vtk_overlay.GetRenderWindow().GetSize()))
    six.print_('Widget = (' + str(vtk_overlay.width()) + ', ' + str(vtk_overlay.height()) + ')')
    six.print_('Viewport = ' + str(vtk_renderer.GetViewport()))
    six.print_('Scale = ' + str(scale_x) + ', ' + str(scale_y))

    # Set intrisic parameters, which internally sets vtkCamera vars.
    vtk_overlay.set_camera_matrix(intrinsics)

    # Compute the rms error, using a vtkCoordinate loop, which is slow.
    rms = pu.compute_rms_error(model_points,
                               image_points,
                               vtk_renderer,
                               scale_x,
                               scale_y,
                               left_image.shape[0]
                               )
    six.print_('rms using VTK =' + str(rms))

    # Now check the rms error, using an OpenCV projection, which should be faster.
    projected_points = pu.project_points(model_points,
                                         camera_to_world,
                                         intrinsics
                                         )

    counter = 0
    rms_opencv = 0
    for counter in range(0, number_model_points):
        i_c = image_points[counter]
        dx = projected_points[counter][0][0] - float(i_c[0])
        dy = projected_points[counter][0][1] - float(i_c[1])
        rms_opencv += (dx * dx + dy * dy)
        counter += 1
    rms_opencv /= float(counter)
    rms_opencv = np.sqrt(rms_opencv)

    six.print_('rms using OpenCV =' + str(rms_opencv))

    assert rms < 1.2
    assert rms_opencv < 0.7

    model_polydata_points = model_polydata[0].get_points_as_numpy()
    model_polydata_normals = model_polydata[0].get_normals_as_numpy()

    six.print_('model_points=' + str(model_polydata_points))

    projected_facing_points = pu.project_facing_points(model_polydata_points,
                                                       model_polydata_normals,
                                                       camera_to_world,
                                                       intrinsics
                                                       )

    assert projected_facing_points.shape[0] == 4
    assert projected_facing_points.shape[2] == 2

    # Can't think how to do this more efficiently yet.
    masked = []
    for point_index in range(projected_facing_points.shape[0]):
        x = projected_facing_points[point_index][0][0]
        y = projected_facing_points[point_index][0][1]
        val = left_mask[int(y), int(x)]
        six.print_('p=' + str(x) + ', ' + str(y))
        if int(x) >= 0 \
            and int(x) < left_mask.shape[1] \
            and int(y) >= 0 \
            and int(y) < left_mask.shape[0] \
            and val > 0:
            masked.append((x, y))

    assert len(masked) == 2

    #app.exec_()






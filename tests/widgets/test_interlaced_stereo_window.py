# -*- coding: utf-8 -*-

import os
import platform

import cv2
import numpy as np
import pytest

import sksurgeryvtk.camera.vtk_camera_model as cam
import sksurgeryvtk.utils.projection_utils as pu
from sksurgeryvtk.models import vtk_point_model

## Skipif maker for all OSs
skip_pytest_in_oss = pytest.mark.skipif(
    platform.system() == 'Linux' or platform.system() == 'Windows' or platform.system() == 'Darwin',
    reason=f'for [{platform.system()} OSs with CI=[{os.environ.get("CI")}] with RUNNER_OS=[{os.environ.get("RUNNER_OS")}] '
           f'{os.environ.get("SESSION_MANAGER")[0:20] if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'with {os.environ.get("XDG_CURRENT_DESKTOP") if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'due to issues with VTK pipelines and pyside workflows with Class Inheritance'
)


@skip_pytest_in_oss
def test_stereo_overlay_window(vtk_interlaced_stereo_window):
    widget, _vtk_std_err, _pyside_qt_app = vtk_interlaced_stereo_window

    model_points_file = 'tests/data/calibration/chessboard_14_10_3_no_ID.txt'
    model_points = np.loadtxt(model_points_file)
    number_model_points = model_points.shape[0]
    assert number_model_points == 140

    # Load images
    left_image = cv2.imread('tests/data/calibration/left-1095-undistorted.png')
    right_image = cv2.imread('tests/data/calibration/right-1095-undistorted.png')

    # Load left intrinsics for projection matrix.
    left_intrinsics_file = 'tests/data/calibration/calib.left.intrinsic.txt'
    left_intrinsics = np.loadtxt(left_intrinsics_file)

    # Load right intrinsics for projection matrix.
    right_intrinsics_file = 'tests/data/calibration/calib.right.intrinsic.txt'
    right_intrinsics = np.loadtxt(right_intrinsics_file)

    # Load 2D points
    image_points_file = 'tests/data/calibration/right-1095-undistorted.png.points.txt'
    image_points = np.loadtxt(image_points_file)
    number_image_points = image_points.shape[0]
    assert number_model_points == number_image_points

    # Load extrinsics for camera pose (position, orientation).
    extrinsics_file = 'tests/data/calibration/left-1095.extrinsic.txt'
    extrinsics = np.loadtxt(extrinsics_file)
    left_camera_to_world = np.linalg.inv(extrinsics)

    # Load extrinsics for stereo.
    stereo_extrinsics_file = 'tests/data/calibration/calib.l2r.4x4'
    stereo_extrinsics = np.loadtxt(stereo_extrinsics_file)

    width = left_image.shape[1]
    height = left_image.shape[0]
    screen = _pyside_qt_app.primaryScreen()
    while width >= screen.geometry().width() or height >= screen.geometry().height():
        width /= 2
        height /= 2

    # Create a vtk point model.
    vtk_points = vtk_point_model.VTKPointModel(model_points.astype(float),
                                               model_points.astype(np.uint8))
    widget.add_vtk_actor(vtk_points.actor)

    widget.set_video_images(left_image, right_image)
    widget.set_camera_matrices(left_intrinsics, right_intrinsics)
    widget.set_left_to_right(stereo_extrinsics)
    widget.set_camera_poses(left_camera_to_world)

    widget.resize(width, height)
    widget.show()
    widget.set_current_viewer_index(0)
    widget.set_current_viewer_index(1)
    widget.set_current_viewer_index(2)
    widget.render()

    print(f'Chosen size = ( {width}x{height} )')
    print(f'Left image = : {left_image.shape}')
    print(f'Right image = : {right_image.shape}')
    print(f'Widget = : {widget.width()}, {widget.height()}')

    # Project points using OpenCV.
    right_camera_to_world = cam.compute_right_camera_pose(left_camera_to_world, stereo_extrinsics)

    right_points = pu.project_points(model_points,
                                     right_camera_to_world,
                                     right_intrinsics
                                     )

    rms_opencv = 0
    for counter in range(0, number_model_points):
        i_c = image_points[counter]
        dx = right_points[counter][0][0] - i_c[0]
        dy = right_points[counter][0][1] - i_c[1]
        rms_opencv += (dx * dx + dy * dy)

    rms_opencv /= number_model_points
    rms_opencv = np.sqrt(rms_opencv)
    print(f' rms_opencv= {rms_opencv}. is rms_opencv < 1 {rms_opencv < 1}')
    assert rms_opencv < 1

    widget.save_scene_to_file('tests/output/test_interlaced_stereo_window_E.png')

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    widget.close()

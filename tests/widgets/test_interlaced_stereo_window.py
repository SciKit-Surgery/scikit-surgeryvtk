# -*- coding: utf-8 -*-

import numpy as np
import cv2
import six
from sksurgeryvtk.models import vtk_point_model
import sksurgeryvtk.camera.vtk_camera_model as cam
import sksurgeryvtk.utils.projection_utils as pu


def test_stereo_overlay_window(vtk_interlaced_stereo_window):

    widget, _, _, app = vtk_interlaced_stereo_window

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
    image_points_file ='tests/data/calibration/right-1095-undistorted.png.points.txt'
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

    screen = app.primaryScreen()
    width = left_image.shape[1]
    height = left_image.shape[0]
    while width >= screen.geometry().width() or height >= screen.geometry().height():
        width /= 2
        height /= 2

    # Create a vtk point model.
    vtk_points = vtk_point_model.VTKPointModel(model_points.astype(np.float),
                                               model_points.astype(np.byte))
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

    six.print_('Chosen size = (' + str(width) + 'x' + str(height) + ')')
    six.print_('Left image = :' + str(left_image.shape))
    six.print_('Right image = :' + str(right_image.shape))
    six.print_('Widget = (' + str(widget.width()) + ', ' + str(widget.height()) + ')')

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
    assert rms_opencv < 1

    widget.save_scene_to_file('tests/output/test_interlaced_stereo_window.png')
    #app.exec_()
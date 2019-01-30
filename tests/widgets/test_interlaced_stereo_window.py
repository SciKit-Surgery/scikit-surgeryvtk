# -*- coding: utf-8 -*-

import numpy as np
import cv2
import sksurgeryvtk.camera.vtk_camera_model as cam


def test_stereo_overlay_window(vtk_interlaced_stereo_window):

    widget, _, _, app = vtk_interlaced_stereo_window

    screen = app.primaryScreen()
    width = screen.geometry().width()//2
    height = screen.geometry().height()//2
    print(screen.geometry())

    widget.resize(width, height)
    widget.show()

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

    # Load extrinsics for camera pose (position, orientation).
    extrinsics_file = 'tests/data/calibration/left-1095.extrinsic.txt'
    extrinsics = np.loadtxt(extrinsics_file)
    model_to_camera = cam.create_vtk_matrix_from_numpy(extrinsics)

    # Load extrinsics for stereo.
    stereo_extrinsics_file = 'tests/data/calibration/calib.l2r.txt'
    stereo_extrinsics = np.loadtxt(stereo_extrinsics_file)

    widget.set_video_images(left_image, right_image)
    widget.set_current_viewer_index(1)
    app.exec_()

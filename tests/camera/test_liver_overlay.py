# -*- coding: utf-8 -*-

import copy
import pytest
import vtk
import cv2
import numpy as np
import sksurgeryvtk.models.vtk_surface_model as sm
import os

def reproject_and_save(image,
                       model_to_camera,
                       point_cloud,
                       camera_matrix,
                       output_file):
    """
    For testing purposes, projects points onto image, and writes to file.

    :param image: BGR image, undistorted.
    :param model_to_camera: [4x4] ndarray of model-to-camera transform
    :param point_cloud: [Nx3] ndarray of cloud of points to project
    :param camera_matrix: [3x3] OpenCV camera_matrix (intrinsics)
    :param output_file: file name
    """
    output_image = copy.deepcopy(image)

    rmat = model_to_camera[:3, :3]
    rvec = cv2.Rodrigues(rmat)[0]
    tvec = model_to_camera[:3, 3]

    projected, _ = cv2.projectPoints(point_cloud,
                                     rvec,
                                     tvec,
                                     camera_matrix,
                                     None)

    for i in range(projected.shape[0]):

        x_c, y_c = projected[i][0]
        x_c = int(x_c)
        y_c = int(y_c)

        # Skip points that aren't in the bounds of image
        if x_c <= 0 or x_c >= output_image.shape[1]:
            continue
        if y_c <= 0 or y_c >= output_image.shape[0]:
            continue

        output_image[y_c, x_c, :] = [255, 0, 0]

    cv2.imwrite(output_file, output_image)


def test_overlay_liver_points(setup_vtk_overlay_window):

    output_name = 'tests/output/'
    if not os.path.exists(output_name):
        os.mkdir(output_name)

    # We aren't using 'proper' hardware rendering on GitHub CI, so skip
    in_github_ci = os.environ.get('CI')
    if in_github_ci:
        pytest.skip("Don't run rendering test on GitHub CI")

    intrinsics_file = 'tests/data/liver/calib.left.intrinsics.txt'
    intrinsics = np.loadtxt(intrinsics_file)

    model_to_camera_file = 'tests/data/liver/model_to_camera.txt'
    model_to_camera = np.loadtxt(model_to_camera_file)

    image_file = 'tests/data/liver/fig06_case1b.png'
    image = cv2.imread(image_file)

    model = sm.VTKSurfaceModel('tests/data/liver/liver_sub.ply', (1.0, 1.0, 1.0))
    point_cloud = model.get_points_as_numpy()

    print("Loaded model with " + str(point_cloud.shape) + " points.")

    # Ensure that OpenCV projection works with this image.
    reproject_and_save(image,
                       model_to_camera,
                       point_cloud,
                       intrinsics,
                       'tests/output/liver_sub_projected.png')

    # Now try overlay widget.
    vtk_overlay, factory, vtk_std_err, app = setup_vtk_overlay_window

    screen = app.primaryScreen()
    width = image.shape[1]
    height = image.shape[0]
    while width >= screen.geometry().width() or height >= screen.geometry().height():
        width //= 2
        height //= 2

    vtk_overlay.add_vtk_models([model])
    vtk_overlay.set_video_image(image)
    vtk_overlay.set_camera_pose(np.linalg.inv(model_to_camera))
    opengl_mat, vtk_mat = vtk_overlay.set_camera_matrix(intrinsics)
    vtk_overlay.resize(width, height)
    vtk_overlay.show()

    print("OpenGL matrix=" + str(opengl_mat))
    print("VTK matrix=" + str(vtk_mat))

    for r in range(0, 4):
        for c in range(0, 4):
            assert np.isclose(opengl_mat.GetElement(r, c),
                              vtk_mat.GetElement(r, c))

    # Extract image from overlay widget.
    vtk_overlay.save_scene_to_file('tests/output/fig06_case1b_overlay.png')

    # Compare with expected result.
    reference_image = cv2.imread('tests/data/liver/fig06_case1b_overlay.png')
    rendered_image = cv2.imread('tests/output/fig06_case1b_overlay.png')

    assert np.allclose(reference_image, rendered_image, atol=1)

    # Just for interactive testing.
    # app.exec_()

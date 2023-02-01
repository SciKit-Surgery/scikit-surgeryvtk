# -*- coding: utf-8 -*-

import copy
import os
import platform

import cv2
import numpy as np
from sksurgeryimage.utilities.utilities import are_similar

import sksurgeryvtk.models.vtk_surface_model as sm


def _reproject_and_save(image,
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

    ref_image_path = 'tests/data/liver/fig06_case1b_overlay.png'
    # We aren't using 'proper' hardware rendering on GitHub CI, so skip
    in_github_ci = os.environ.get('CI')
    if in_github_ci:
        ref_image_path = 'tests/data/liver/fig06_case1b_overlay_for_ci.png'
        if 'Linux' in platform.system():
            ref_image_path = 'tests/data/liver/fig06_case1b_overlay_for_linux_ci.png'

    print("\nenviron = ", in_github_ci)
    print("platform.system = ", platform.system())
    print("platform.machine = ", platform.machine())
    print("platform.architecture = ", platform.architecture())
    print("\nusing ref_image_path: ", ref_image_path)
    reference_image = cv2.imread(ref_image_path)
    # pytest.skip("Don't run rendering test on GitHub CI")

    input_image_file = 'tests/data/liver/fig06_case1b.png'
    image = cv2.imread(input_image_file)
    print("image.shape of ", str(input_image_file), image.shape)
    width = image.shape[1]
    height = image.shape[0]

    model_to_camera_file = 'tests/data/liver/model_to_camera.txt'
    model_to_camera = np.loadtxt(model_to_camera_file)

    model = sm.VTKSurfaceModel('tests/data/liver/liver_sub.ply', (1.0, 1.0, 1.0))
    point_cloud = model.get_points_as_numpy()
    print("Loaded model with " + str(point_cloud.shape) + " points.")

    intrinsics_file = 'tests/data/liver/calib.left.intrinsics.txt'
    intrinsics = np.loadtxt(intrinsics_file)
    output_image_file = 'tests/output/liver_sub_projected.png'

    # Ensure that OpenCV projection works with this image.
    _reproject_and_save(image,
                        model_to_camera,
                        point_cloud,
                        intrinsics,
                        output_image_file)

    # Now try overlay widget.
    widget_vtk_overlay, _vtk_std_err, pyside_qt_app = setup_vtk_overlay_window

    screen = pyside_qt_app.primaryScreen()

    while width >= screen.geometry().width() or height >= screen.geometry().height():
        width //= 2
        height //= 2

    widget_vtk_overlay.add_vtk_models([model])
    widget_vtk_overlay.set_video_image(image)
    widget_vtk_overlay.set_camera_pose(np.linalg.inv(model_to_camera))
    opengl_mat, vtk_mat = widget_vtk_overlay.set_camera_matrix(intrinsics)
    widget_vtk_overlay.resize(width, height)
    widget_vtk_overlay.show()

    print("OpenGL matrix=" + str(opengl_mat))
    print("VTK matrix=" + str(vtk_mat))

    for r in range(0, 4):
        for c in range(0, 4):
            assert np.isclose(opengl_mat.GetElement(r, c),
                              vtk_mat.GetElement(r, c))

    # Extract image from overlay widget.
    ref_output_image_path = 'tests/output/fig06_case1b_overlay.png'
    widget_vtk_overlay.save_scene_to_file(ref_output_image_path)

    # Compare with expected result.
    rendered_image = cv2.imread(ref_output_image_path)
    print("reference_image.shape ", reference_image.shape)
    print("rendered_image.shape ", rendered_image.shape)

    assert are_similar(reference_image, rendered_image, threshold=0.995,
                       metric=cv2.TM_CCOEFF_NORMED, mean_threshold=0.005)

    # Just for interactive testing.
    # pyside_qt_app.exec()
    # widget_vtk_overlay.close()

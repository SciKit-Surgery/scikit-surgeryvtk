# -*- coding: utf-8 -*-

import os
import platform

import cv2
import numpy as np
import pytest
from sksurgeryimage.utilities.utilities import are_similar
import sksurgeryvtk.widgets.vtk_rendering_generator as rg

# Shared skipif maker for all modules
skip_pytest_in_linux = pytest.mark.skipif(
    platform.system() == "Linux",
    reason=f'for [{platform.system()} OSs with CI=[{os.environ.get("CI")}] with RUNNER_OS=[{os.environ.get("RUNNER_OS")}] '
           f'{os.environ.get("SESSION_MANAGER")[0:20] if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'with {os.environ.get("XDG_CURRENT_DESKTOP") if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'due to issues with VTK pipelines and pyside workflows with Class Inheritance'
)


@skip_pytest_in_linux
def test_basic_rendering_generator(setup_vtk_err):
    """
    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """
    _vtk_std_err, _pyside_qt_app = setup_vtk_err

    if 'Linux' in platform.system():
        init_widget = False
    else:
        init_widget = True

    ## Tutorial-section1: [Rotation x,y,z Translation x,y,z]
    model_to_world = [45, 45, 45, 0, 0, 0]
    camera_to_world = [0, 0, 0, 47.5, 65, -300]
    left_to_right = [0, 0, 0, 0, 0, 0]

    model_file = "tests/data/rendering/models-calibration-pattern.json"
    background_image = "tests/data/rendering/background-1920-x-1080.png"
    cam_intrinsics = "tests/data/rendering/calib.left.intrinsic.txt"

    ## Tutorial-section2
    generator = rg.VTKRenderingGenerator(model_file,
                                         background_image,
                                         cam_intrinsics,
                                         camera_to_world,
                                         left_to_right,
                                         zbuffer=False,
                                         init_widget=init_widget  # Set to false if you're on Linux.
                                         )
    generator.set_all_model_to_world(model_to_world)
    generator.set_clipping_range(200, 400)
    generator.set_smoothing(2, 11)
    generator.show()

    ## Tutorial-section3
    img = generator.get_image()
    bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imwrite("tests/output/rendering-m2w-1.png", bgr)

    ## Tutorial-section4
    # Now check we get same image, if we use the other set_model_to_worlds.
    generator.set_all_model_to_world([0, 0, 0, 0, 0, 0])  # to reset it.
    dict_of_trans = {'calibration pattern': model_to_world}
    generator.set_model_to_worlds(dict_of_trans)
    generator.show()

    img = generator.get_image()
    bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imwrite("tests/output/rendering-m2w-2.png", bgr)

    img_a = cv2.imread("tests/output/rendering-m2w-1.png")
    img_b = cv2.imread("tests/output/rendering-m2w-2.png")
    assert are_similar(img_a, img_b, threshold=0.995,
                       metric=cv2.TM_CCOEFF_NORMED, mean_threshold=0.005)

    # Now check we get ValueError if name is invalid.
    dict_of_trans = {'banana': model_to_world}
    with pytest.raises(ValueError):
        generator.set_model_to_worlds(dict_of_trans)

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    generator.close()


@skip_pytest_in_linux
def test_basic_rendering_generator_zbuffer(setup_vtk_err):
    """
    To test rendering z-buffer type images.
    Not really a unit test as it does not assert anything.
    But at least it might throw an error if something else changes.

    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """
    _vtk_std_err, _pyside_qt_app = setup_vtk_err

    if 'Linux' in platform.system():
        init_widget = False
    else:
        init_widget = True

    ## Tutorial-section1: [Rotation x,y,z Translation x,y,z]
    model_to_world = [45, 45, 45, 0, 0, 0]
    camera_to_world = [0, 0, 0, 47.5, 65, -300]
    left_to_right = [0, 0, 0, 0, 0, 0]

    model_file = "tests/data/rendering/models-calibration-pattern.json"
    background_image = "tests/data/rendering/background-1920-x-1080.png"
    cam_intrinsics = "tests/data/rendering/calib.left.intrinsic.txt"

    generator2 = rg.VTKRenderingGenerator(model_file,
                                          background_image,
                                          cam_intrinsics,
                                          camera_to_world,
                                          left_to_right,
                                          zbuffer=True,
                                          init_widget=init_widget  # Set to false if you're on Linux.
                                          )
    generator2.set_all_model_to_world(model_to_world)
    generator2.set_clipping_range(200, 400)
    generator2.set_smoothing(0, 11)
    generator2.show()

    img = generator2.get_image()
    cv2.imwrite("tests/output/rendering-zbuffer.png", img)

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    generator2.close()


@skip_pytest_in_linux
def test_mask_generator(setup_vtk_err):
    """

    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """
    _vtk_std_err, _pyside_qt_app = setup_vtk_err

    if 'Linux' in platform.system():
        init_widget = False
    else:
        init_widget = True

    model_to_world = [0, 0, 0, 0, 0, 0]
    camera_to_world = [0, 0, 0, 0, 0, 0]
    left_to_right = [0, 0, 0, 0, 0, 0]

    model_file = "tests/data/config/surface_model_two_livers_no_shading.json"
    background_file = "tests/data/rendering/background-960-x-540.png"
    intrinsics_file = "tests/data/liver/calib.left.intrinsics.halved.txt"

    generator = rg.VTKRenderingGenerator(model_file,
                                         background_file,
                                         intrinsics_file,
                                         camera_to_world,
                                         left_to_right,
                                         zbuffer=False,
                                         init_widget=init_widget  # Set to false if you're on Linux.
                                         )

    generator.set_all_model_to_world(model_to_world)
    generator.setFixedSize(960, 540)
    generator.show()

    # As input data could have origin anywhere, work out mean of point cloud.
    points = generator.model_loader.get_surface_model('liver50').get_points_as_numpy()
    mean = np.mean(points, axis=0)

    # Then put model in line with camera, some distance away along z-axis.
    model_to_world = [0, 0, 0, -mean[0], -mean[1], -mean[2] + 200]
    generator.set_all_model_to_world(model_to_world)

    # Then, as we have 2 livers the same, offset them, so we see two livers.
    dict_of_transforms = {'liver50': [0, 0, 0, -mean[0] - 50, -mean[1] - 10, -mean[2] + 210],
                          'liver127': [0, 0, 0, -mean[0] + 50, -mean[1] + 10, -mean[2] + 200]}
    generator.set_model_to_worlds(dict_of_transforms)

    # Render result for debugging
    img = generator.get_image()
    bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imwrite("tests/output/rendering-liver-both.png", bgr)

    # Save all masks for debugging, and do regression test against ref img.
    masks = generator.get_masks()
    for name in masks.keys():
        mask = masks[name]
        file_name = 'rendering-liver-mask-' + name + '.png'
        cv2.imwrite(os.path.join('tests/output/', file_name), mask)

        ref_img_name = os.path.join('tests/data/rendering', file_name)
        ref_img = cv2.cvtColor(cv2.imread(ref_img_name), cv2.COLOR_BGR2GRAY)
        print(f'\nmask: {name} with shape {mask.shape}')
        print(f'ref_img_name: {ref_img_name} with shape {ref_img.shape}')

        diff = mask - ref_img
        sqdiff = diff * diff
        ssd = np.sum(sqdiff)
        print(f' is ssd= {ssd} less than 240000: {ssd < 240000}')
        assert ssd < 240000

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    generator.close()


@skip_pytest_in_linux
def test_mask_generator_w_all_shading(setup_vtk_err):
    """

    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """
    _vtk_std_err, _pyside_qt_app = setup_vtk_err

    if 'Linux' in platform.system():
        init_widget = False
    else:
        init_widget = True

    model_to_world = [0, 0, 0, 0, 0, 0]
    camera_to_world = [0, 0, 0, 0, 0, 0]
    left_to_right = [0, 0, 0, 0, 0, 0]

    model_file = "tests/data/config/surface_model_two_livers_no_shading.json"
    background_file = "tests/data/rendering/background-960-x-540.png"
    intrinsics_file = "tests/data/liver/calib.left.intrinsics.halved.txt"

    generator = rg.VTKRenderingGenerator(model_file,
                                         background_file,
                                         intrinsics_file,
                                         camera_to_world,
                                         left_to_right,
                                         zbuffer=False,
                                         init_widget=init_widget  # Set to false if you're on Linux.
                                         )

    generator.set_all_model_to_world(model_to_world)
    generator.setFixedSize(960, 540)
    generator.show()

    # Change shading to test same mask rendered
    models = generator.model_loader.get_surface_models()
    for model in models:
        model.set_no_shading(False)

    # As input data could have origin anywhere, work out mean of point cloud.
    points = generator.model_loader.get_surface_model('liver50').get_points_as_numpy()
    mean = np.mean(points, axis=0)

    # Then put model in line with camera, some distance away along z-axis.
    model_to_world = [0, 0, 0, -mean[0], -mean[1], -mean[2] + 200]
    generator.set_all_model_to_world(model_to_world)

    # Then, as we have 2 livers the same, offset them, so we see two livers.
    dict_of_transforms = {'liver50': [0, 0, 0, -mean[0] - 50, -mean[1] - 10, -mean[2] + 210],
                          'liver127': [0, 0, 0, -mean[0] + 50, -mean[1] + 10, -mean[2] + 200]}
    generator.set_model_to_worlds(dict_of_transforms)

    # Get image to check the rendering after masks generated
    image_before = generator.get_image()

    # Do regression test against no shading model test data.
    masks = generator.get_masks()
    for name in masks.keys():
        mask = masks[name]
        file_name = 'rendering-liver-mask-shaded-' + name + '.png'
        file_name_regress = 'rendering-liver-mask-' + name + '.png'

        ref_img_name = os.path.join('tests/data/rendering', file_name_regress)
        ref_img = cv2.cvtColor(cv2.imread(ref_img_name), cv2.COLOR_BGR2GRAY)

        print(f'\nmask: {name} with shape {masks[name].shape}')
        print(f'ref_img_name: {ref_img_name} with shape {ref_img.shape}')

        diff = mask - ref_img
        sqdiff = diff * diff
        ssd = np.sum(sqdiff)
        print(f' is ssd= {ssd} less than 240000: {ssd < 240000}')
        assert ssd < 240000

    # Check image before and after the mask rendering is the same.
    image_after = generator.get_image()
    print(f'\nimage_before.shape {image_before.shape}')
    print(f'image_after.shape {image_after.shape}')

    # Check difference
    diff = image_before - image_after
    sqdiff = diff * diff
    ssd = np.sum(sqdiff)
    print(f' is ssd {ssd} is equal to 0: {ssd == 0}')
    assert ssd == 0

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    generator.close()


@skip_pytest_in_linux
def test_mask_generator_w_some_shading(setup_vtk_err):
    """

    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """
    _vtk_std_err, _pyside_qt_app = setup_vtk_err

    if 'Linux' in platform.system():
        init_widget = False
    else:
        init_widget = True

    model_to_world = [0, 0, 0, 0, 0, 0]
    camera_to_world = [0, 0, 0, 0, 0, 0]
    left_to_right = [0, 0, 0, 0, 0, 0]

    model_file = "tests/data/config/surface_model_two_livers_no_shading.json"
    background_file = "tests/data/rendering/background-960-x-540.png"
    intrinsics_file = "tests/data/liver/calib.left.intrinsics.halved.txt"

    generator = rg.VTKRenderingGenerator(model_file,
                                         background_file,
                                         intrinsics_file,
                                         camera_to_world,
                                         left_to_right,
                                         zbuffer=False,
                                         init_widget=init_widget  # Set to false if you're on Linux.
                                         )

    generator.set_all_model_to_world(model_to_world)
    generator.setFixedSize(960, 540)
    generator.show()

    # Change shading of one element to test same mask rendered
    models = generator.model_loader.get_surface_models()
    for i, model in enumerate(models):
        if i == 0:
            model.set_no_shading(False)

    # As input data could have origin anywhere, work out mean of point cloud.
    points = generator.model_loader.get_surface_model('liver50').get_points_as_numpy()
    mean = np.mean(points, axis=0)

    # Then put model in line with camera, some distance away along z-axis.
    model_to_world = [0, 0, 0, -mean[0], -mean[1], -mean[2] + 200]
    generator.set_all_model_to_world(model_to_world)

    # Then, as we have 2 livers the same, offset them, so we see two livers.
    dict_of_transforms = {'liver50': [0, 0, 0, -mean[0] - 50, -mean[1] - 10, -mean[2] + 210],
                          'liver127': [0, 0, 0, -mean[0] + 50, -mean[1] + 10, -mean[2] + 200]}
    generator.set_model_to_worlds(dict_of_transforms)

    # Get image to check the rendering after masks generated
    image_before = generator.get_image()

    # Do regression test against no shading model test data.
    masks = generator.get_masks()
    for name in masks.keys():
        mask = masks[name]
        file_name = 'rendering-liver-mask-shaded-' + name + '.png'
        file_name_regress = 'rendering-liver-mask-' + name + '.png'

        ref_img_name = os.path.join('tests/data/rendering', file_name_regress)
        ref_img = cv2.cvtColor(cv2.imread(ref_img_name), cv2.COLOR_BGR2GRAY)
        print(f'\nmask: {name} with shape {masks[name].shape}')
        print(f'ref_img_name: {ref_img_name} with shape {ref_img.shape}')

        diff = mask - ref_img
        sqdiff = diff * diff
        ssd = np.sum(sqdiff)
        print(f' is ssd= {ssd} less than 240000: {ssd < 240000}')
        assert ssd < 240000

    # Check image before and after the mask rendering is the same.
    image_after = generator.get_image()
    print(f'\nimage_before.shape {image_before.shape}')
    print(f'image_after.shape {image_after.shape}')

    # Check difference
    diff = image_before - image_after
    sqdiff = diff * diff
    ssd = np.sum(sqdiff)
    print(f' is ssd {ssd} is equal to 0: {ssd == 0}')
    assert ssd == 0

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    generator.close()

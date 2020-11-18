# -*- coding: utf-8 -*-

import vtk
import os
import pytest
import numpy as np
import cv2
import sksurgeryvtk.widgets.vtk_rendering_generator as rg


def test_basic_rendering_generator(setup_vtk_offscreen):

    _, _, _ = setup_vtk_offscreen

    #Tutorial-section1
    # [Rotation x,y,z Translation x,y,z]
    model_to_world = [45, 45, 45, 0, 0, 0]
    camera_to_world = [0, 0, 0, 47.5, 65, -300]
    left_to_right = [0, 0, 0, 0, 0, 0]

    model_file = "tests/data/rendering/models-calibration-pattern.json"
    background_image = "tests/data/rendering/background-1920-x-1080.png"
    cam_intrinsics = "tests/data/rendering/calib.left.intrinsic.txt"

    #Tutorial-section2
    generator = rg.VTKRenderingGenerator(model_file,
                                         background_image,
                                         cam_intrinsics,
                                         camera_to_world,
                                         left_to_right,
                                         zbuffer=False
                                         )

    generator.set_all_model_to_world(model_to_world)
    generator.set_clipping_range(200, 400)
    generator.set_smoothing(2, 11)
    generator.show()

    #Tutorial-section3
    img = generator.get_image()
    bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imwrite("tests/output/rendering-m2w-1.png", bgr)
    #Tutorial-section4
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
    assert np.allclose(img_a, img_b)

    # Now check we get ValueError if name is invalid.
    dict_of_trans = {'banana': model_to_world}
    with pytest.raises(ValueError):
        generator.set_model_to_worlds(dict_of_trans)

    # Now testing we can render z-buffer type images.
    generator2 = rg.VTKRenderingGenerator("tests/data/rendering/models-calibration-pattern.json",
                                          "tests/data/rendering/background-1920-x-1080.png",
                                          "tests/data/rendering/calib.left.intrinsic.txt",
                                          camera_to_world,
                                          left_to_right,
                                          zbuffer=True
                                          )
    generator2.set_all_model_to_world(model_to_world)
    generator2.set_clipping_range(200, 400)
    generator2.set_smoothing(0, 11)
    generator2.show()

    img = generator2.get_image()
    cv2.imwrite("tests/output/rendering-zbuffer.png", img)

def test_mask_generator(setup_vtk_offscreen):

    _, _, app = setup_vtk_offscreen

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
                                         zbuffer=False
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
        diff = mask - ref_img
        sqdiff = diff * diff
        ssd = np.sum(sqdiff)
        assert ssd < 240000


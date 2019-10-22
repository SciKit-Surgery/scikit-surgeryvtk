# -*- coding: utf-8 -*-

import vtk
import pytest
import numpy as np
import cv2
import sksurgeryvtk.widgets.vtk_rendering_generator as rg


def test_basic_rendering_generator(setup_vtk_offscreen):

    _, _, _ = setup_vtk_offscreen

    model_to_world = [45, 45, 45, 0, 0, 0]
    camera_to_world = [0, 0, 0, 47.5, 65, -300]
    left_to_right = [0, 0, 0, 0, 0, 0]

    generator = rg.VTKRenderingGenerator("tests/data/rendering/models-calibration-pattern.json",
                                         "tests/data/rendering/background-1920-x-1080.png",
                                         "tests/data/rendering/calib.left.intrinsic.txt",
                                         model_to_world,
                                         camera_to_world,
                                         left_to_right,
                                         zbuffer=False
                                         )
    generator.set_clipping_range(200, 400)
    generator.set_smoothing(2, 11)
    generator.show()

    img = generator.get_image()
    bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imwrite("tests/output/rendering.png", bgr)

    generator2 = rg.VTKRenderingGenerator("tests/data/rendering/models-calibration-pattern.json",
                                          "tests/data/rendering/background-1920-x-1080.png",
                                          "tests/data/rendering/calib.left.intrinsic.txt",
                                          model_to_world,
                                          camera_to_world,
                                          left_to_right,
                                          zbuffer=True
                                          )
    generator2.set_clipping_range(200, 400)
    generator2.set_smoothing(0, 11)
    generator2.show()

    img = generator2.get_image()
    cv2.imwrite("tests/output/rendering-zbuffer.png", img)

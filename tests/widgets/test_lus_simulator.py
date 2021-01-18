# -*- coding: utf-8 -*-

import vtk
import os
import pytest
import numpy as np
import cv2
import sksurgeryvtk.widgets.vtk_lus_simulator as lus


def test_basic_rendering_generator(setup_vtk_err):

    _, app = setup_vtk_err

    model_file = "tests/data/lus/surface_model_liver_probe.json"
    background_file = "tests/data/rendering/background-960-x-540-black.png"
    intrinsics_file = "tests/data/liver/calib.left.intrinsics.halved.txt"
    reference_l2c_file = "tests/data/lus/spp_liver2camera.txt"
    reference_p2c_file = "tests/data/lus/spp_probe2camera.txt"

    generator = lus.VTKLUSSimulator(model_file,
                                    background_file,
                                    intrinsics_file,
                                    reference_l2c_file,
                                    reference_p2c_file)

    # First generate image at reference pose exactly.
    final_l2c, final_p2c, angle, position = generator.set_pose([0, 0, 0, 0, 0, 0], # anatomy rx, ry, rz, tx, ty, tz
                                                               [0, 0, 0, 0, 0, 0], # probe rx, ry, rz, tx, ty, tz
                                                               0,
                                                               None
                                                               )
    generator.show()
    generator.setFixedSize(960, 540)

    image = generator.get_image()
    cv2.imwrite('tests/output/lus_refererence_posn_image.png', image)
    masks = generator.get_masks()
    for mask in masks.keys():
        cv2.imwrite('tests/output/lus_refererence_posn_mask_' + mask + '.png',
                    masks[mask]
                    )


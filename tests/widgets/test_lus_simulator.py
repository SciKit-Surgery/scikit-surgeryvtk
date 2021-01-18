# -*- coding: utf-8 -*-

import pytest
import cv2
import sksurgeryvtk.widgets.vtk_lus_simulator as lus


def test_basic_rendering_generator(setup_vtk_err):

    _, app = setup_vtk_err

    pytest.skip("Skipped, for now, as we can't publish test data.")

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
    l2c, p2c, angle, position = generator.set_pose([0, 0, 0, 0, 0, 0], # anatomy rx, ry, rz, tx, ty, tz
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

    print("test_basic_rendering_generator: ref l2c=" + str(l2c))
    print("test_basic_rendering_generator: ref p2c=" + str(p2c))
    print("test_basic_rendering_generator: ref angle=" + str(angle))
    print("test_basic_rendering_generator: ref position=" + str(position))

    # Now try another pose.
    l2c, p2c, angle, position = generator.set_pose([20, 30, 40, 5, 10, 15], # anatomy rx, ry, rz, tx, ty, tz
                                                   [2, 3, 4, 5, 6, 7], # probe rx, ry, rz, tx, ty, tz
                                                   -20,
                                                   [10.97657775878900566, -80.58924865722650566, -27.99212646484369316]
                                                   )

    print("test_basic_rendering_generator: alt l2c=" + str(l2c))
    print("test_basic_rendering_generator: alt p2c=" + str(p2c))
    print("test_basic_rendering_generator: alt angle=" + str(angle))
    print("test_basic_rendering_generator: alt position=" + str(position))

    image = generator.get_image()
    cv2.imwrite('tests/output/lus_alternative_posn_image.png', image)
    masks = generator.get_masks()
    for mask in masks.keys():
        cv2.imwrite('tests/output/lus_alternative_posn_mask_' + mask + '.png',
                    masks[mask]
                    )



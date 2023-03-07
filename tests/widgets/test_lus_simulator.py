# -*- coding: utf-8 -*-

import os
import platform

import cv2
import numpy as np
import pytest

import sksurgeryvtk.widgets.vtk_lus_simulator as lus

## Shared skipif maker for all modules
skip_pytest_in_linux_and_none_ci = pytest.mark.skipif(
    platform.system() == 'Linux' and os.environ.get('CI') == None,
    reason=f'for [{platform.system()} OSs with CI=[{os.environ.get("CI")}] with RUNNER_OS=[{os.environ.get("RUNNER_OS")}] '
           f'{os.environ.get("SESSION_MANAGER")[0:20] if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'with {os.environ.get("XDG_CURRENT_DESKTOP") if (platform.system() == "Linux" and os.environ.get("GITHUB_ACTIONS") == None) else ""} '
           f'because of issues with VTK pipelines and pyside workflows with Class Inheritance'
)




@skip_pytest_in_linux_and_none_ci
def test_basic_rendering_generator(setup_vtk_err):
    """
    Not really a unit test as it does not assert anything.
    But at least it might throw an error if something else changes.

    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """
    _vtk_std_err, _pyside_qt_app = setup_vtk_err


    model_file = "tests/data/lus/test_data.json"
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
    l2c, p2c, angle, position = generator.set_pose([0, 0, 0, 0, 0, 0],  # anatomy rx, ry, rz, tx, ty, tz
                                                   [0, 0, 0, 0, 0, 0],  # probe rx, ry, rz, tx, ty, tz
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

    print(f'test_basic_rendering_generator: ref l2c= {l2c}')
    print(f'test_basic_rendering_generator: ref p2c= {p2c}')
    print(f'test_basic_rendering_generator: ref angle= {angle}')
    print(f'test_basic_rendering_generator: ref position= {position}')

    # Now try another pose.
    l2c, p2c, angle, position = generator.set_pose([20, 30, 40, 5, 10, 15],  # anatomy rx, ry, rz, tx, ty, tz
                                                   [2, 3, 4, 5, 6, 7],  # probe rx, ry, rz, tx, ty, tz
                                                   -20,
                                                   [10.97657775878900566, -80.58924865722650566, -27.99212646484369316]
                                                   )

    print(f'test_basic_rendering_generator: alt l2c= {l2c}')
    print(f'test_basic_rendering_generator: alt p2c= {p2c}')
    print(f'test_basic_rendering_generator: alt angle= {angle}')
    print(f'test_basic_rendering_generator: alt position= {position}')

    image = generator.get_image()
    cv2.imwrite('tests/output/lus_alternative_posn_image.png', image)
    masks = generator.get_masks()
    for mask in masks.keys():
        cv2.imwrite('tests/output/lus_alternative_posn_mask_' + mask + '.png',
                    masks[mask]
                    )

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    generator.close()


@skip_pytest_in_linux_and_none_ci
def test_matrices_rendering_generator(setup_vtk_err):
    """
    Testing rendering generator returns the same images if matrix used or params used.

    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """

    _vtk_std_err, _pyside_qt_app = setup_vtk_err

    model_file = "tests/data/lus/test_data.json"
    background_file = "tests/data/rendering/background-960-x-540-black.png"
    intrinsics_file = "tests/data/liver/calib.left.intrinsics.halved.txt"
    reference_l2c_file = "tests/data/lus/spp_liver2camera.txt"
    reference_p2c_file = "tests/data/lus/spp_liver2camera.txt"

    generator = lus.VTKLUSSimulator(model_file,
                                    background_file,
                                    intrinsics_file,
                                    reference_l2c_file,
                                    reference_p2c_file)

    # First generate image at reference pose exactly.
    l2c, p2c, angle, position = generator.set_pose([0, 0, 0, 0, 0, 0],  # anatomy rx, ry, rz, tx, ty, tz
                                                   [0, 0, 0, 0, 0, 0],  # probe rx, ry, rz, tx, ty, tz
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

    # Check that the resulting masks with set_pose_with_matrices method are the same
    generator.set_pose_with_matrices(p2c, l2c, angle)
    generator.show()
    generator.setFixedSize(960, 540)

    image_w_matrix = generator.get_image()
    cv2.imwrite('tests/output/lus_refererence_posn_image_w_matrices.png', image)
    masks_w_matrix = generator.get_masks()
    for mask in masks_w_matrix.keys():
        cv2.imwrite('tests/output/lus_refererence_posn_mask_' + mask + '_w_matrices.png',
                    masks_w_matrix[mask]
                    )
        assert np.allclose(masks_w_matrix[mask], masks[mask])

    assert np.allclose(image, image_w_matrix)

    # Now try another pose.
    l2c, p2c, angle, position = generator.set_pose([20, 30, 40, 5, 10, 15],  # anatomy rx, ry, rz, tx, ty, tz
                                                   [2, 3, 4, 5, 6, 7],  # probe rx, ry, rz, tx, ty, tz
                                                   -20,
                                                   [10.97657775878900566, -80.58924865722650566, -27.99212646484369316]
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

    # Check that the resulting masks with set_pose_with_matrices method are the same
    generator.set_pose_with_matrices(p2c, l2c, angle)
    generator.show()
    generator.setFixedSize(960, 540)

    image_w_matrix = generator.get_image()
    cv2.imwrite('tests/output/lus_refererence_posn_image_w_matrices.png', image)
    masks_w_matrix = generator.get_masks()
    for mask in masks_w_matrix.keys():
        cv2.imwrite('tests/output/lus_refererence_posn_mask_' + mask + '_w_matrices.png',
                    masks_w_matrix[mask]
                    )
        assert np.allclose(masks_w_matrix[mask], masks[mask])

    assert np.allclose(image, image_w_matrix)

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    generator.close()

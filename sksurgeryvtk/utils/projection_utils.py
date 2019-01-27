# -*- coding: utf-8 -*-

"""
Any useful little utilities to do with projecting 3D to 2D.
"""

import cv2
import numpy as np

# pylint: disable=no-member


def project_points(points,
                   extrinsics,
                   intrinsics,
                   distortion=None
                   ):
    """
    Projects all 3D points to 2D.

    :param points: nx3 ndarray representing 3D points, typically in millimetres
    :param intrinsics: 3x3 ndarray representing OpenCV camera intrinsics
    :param distortion: 1x4,5 etc. OpenCV distortion parameters
    :param extrinsics: 4x4 ndarray representing camera position and orientation
    :return: nx2 ndarray representing 2D points, typically in pixels
    """
    if points is None:
        raise ValueError('points is NULL')

    if extrinsics is None:
        raise ValueError('extrinsics is NULL')

    if intrinsics is None:
        raise ValueError('intrinsics is NULL')

    if not isinstance(points, np.ndarray):
        raise ValueError('points is not an np.ndarray')

    if not isinstance(extrinsics, np.ndarray):
        raise ValueError('extrinsics is not an np.ndarray')

    if not isinstance(intrinsics, np.ndarray):
        raise ValueError('intrinsics is not an np.ndarray')

    if distortion is not None and not isinstance(distortion, np.ndarray):
        raise ValueError('distortion is not an np.ndarray')

    t_vec = np.zeros((3, 1))
    t_vec[0:3, :] = extrinsics[0:3, 3:4]
    r_vec, _ = cv2.Rodrigues(extrinsics[0:3, 0:3])

    projected = cv2.projectPoints(points,
                                  r_vec,
                                  t_vec,
                                  intrinsics,
                                  distortion
                                  )
    return projected

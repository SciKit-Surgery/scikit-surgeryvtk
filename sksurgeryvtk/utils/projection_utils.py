# -*- coding: utf-8 -*-

"""
Any useful little utilities to do with projecting 3D to 2D.
"""

import cv2
import vtk
import numpy as np
import sksurgerycore.utilities.validate_matrix as vm


def _validate_input_for_projection(points,
                                   camera_to_world,
                                   camera_matrix,
                                   distortion=None):
    """
    Validation of input, for both project_points and
    project_facing_points.

    :param points: nx3 ndarray representing 3D points, typically in millimetres
    :param camera_to_world: 4x4 ndarray representing camera_to_world transform
    :param camera_matrix: 3x3 ndarray representing OpenCV camera intrinsics
    :param distortion: 1x4,5 etc. OpenCV distortion parameters
    :raises ValueError, TypeError:
    :return: nx2 ndarray representing 2D points, typically in pixels
    """
    if points is None:
        raise ValueError('points is NULL')
    if not isinstance(points, np.ndarray):
        raise TypeError('points is not an np.ndarray')
    if len(points.shape) != 2:
        raise ValueError("points should have 2 dimensions.")
    if points.shape[1] != 3:
        raise ValueError("points should have 3 columns.")

    if camera_to_world is None:
        raise ValueError('camera_to_world is NULL')

    vm.validate_rigid_matrix(camera_to_world)

    if camera_matrix is None:
        raise ValueError('camera_matrix is NULL')

    vm.validate_camera_matrix(camera_matrix)

    if distortion is not None:
        vm.validate_distortion_coefficients(distortion)


def project_points(points,
                   camera_to_world,
                   camera_matrix,
                   distortion=None
                  ):
    """
    Projects all 3D points to 2D, using OpenCV cv2.projectPoints().

    :param points: nx3 ndarray representing 3D points, typically in millimetres
    :param camera_to_world: 4x4 ndarray representing camera to world transform
    :param camera_matrix: 3x3 ndarray representing OpenCV camera intrinsics
    :param distortion: 1x4,5 etc. OpenCV distortion parameters
    :raises: ValueError, TypeError:
    :return: nx2 ndarray representing 2D points, typically in pixels
    """

    _validate_input_for_projection(points,
                                   camera_to_world,
                                   camera_matrix,
                                   distortion)

    world_to_camera = np.linalg.inv(camera_to_world)

    t_vec = np.zeros((3, 1))
    t_vec[0:3, :] = world_to_camera[0:3, 3:4]
    r_vec, _ = cv2.Rodrigues(world_to_camera[0:3, 0:3])

    projected, _ = cv2.projectPoints(points,
                                     r_vec,
                                     t_vec,
                                     camera_matrix,
                                     distortion
                                    )

    return projected


def project_facing_points(points,
                          normals,
                          camera_to_world,
                          camera_matrix,
                          distortion=None,
                          upper_cos_theta=0
                         ):
    """
    Projects 3D points that face the camera to 2D pixels.

    This assumes:
    Camera direction is a unit vector from the camera, towards focal point.
    Surface Normal is a unit vector pointing out from the surface.
    Vectors are not checked for unit length.

    :param points: nx3 ndarray representing 3D points, typically in millimetres
    :param normals: nx3 ndarray representing unit normals for the same points
    :param camera_to_world: 4x4 ndarray representing camera to world transform
    :param camera_matrix: 3x3 ndarray representing OpenCV camera intrinsics
    :param distortion: 1x4,5 etc. OpenCV distortion parameters
    :param upper_cos_theta: upper limit for cos theta, angle between normal and
        viewing direction, where cos theta is normally -1 to 0.

    :raises: ValueError, TypeError:
    :return: projected_facing_points_2d
    """
    _validate_input_for_projection(points,
                                   camera_to_world,
                                   camera_matrix,
                                   distortion)

    if normals is None:
        raise ValueError("normals is NULL")
    if not isinstance(normals, np.ndarray):
        raise TypeError('normals is not an np.ndarray')
    if normals.shape != points.shape:
        raise ValueError("normals and points should have the same shape")

    camera_pose = np.array([[0, 0], [0, 0], [0, 1]])  # Origin and focal point
    transformed = np.matmul(camera_to_world[0:3, 0:3], camera_pose)
    camera_direction = np.array([[transformed[0][1] - transformed[0][0]],
                                 [transformed[1][1] - transformed[1][0]],
                                 [transformed[2][1] - transformed[2][0]]
                                ]
                               )
    camera_direction_t = camera_direction.transpose()

    facing_points = points[np.einsum('ij,ij->i', normals, camera_direction_t)
                           < upper_cos_theta]

    projected_points = np.zeros((0, 1, 2))

    if facing_points.shape[0] > 0:
        projected_points = project_points(facing_points,
                                          camera_to_world,
                                          camera_matrix,
                                          distortion=distortion
                                         )
    return projected_points


def compute_rms_error(model_points,
                      image_points,
                      renderer,
                      scale_x,
                      scale_y,
                      image_height
                     ):
    """
    Mainly for unit testing. Computes rms error between projected
    model points, and image points.

    :param model_points: nx3 numpy array of 3D points
    :param image_points: nx2 numpy array of 2D expected points
    :param renderer: vtkRenderer
    :param scale_x: scale factor for x
    :param scale_y: scale factor for y
    :param image_height: image height
    """
    coord_3d = vtk.vtkCoordinate()
    coord_3d.SetCoordinateSystemToWorld()
    counter = 0
    rms = 0

    for m_c in model_points:

        coord_3d.SetValue(float(m_c[0]), float(m_c[1]), float(m_c[2]))
        i_c = image_points[counter]

        # This will scale to the vtkRenderWindow, which may
        # well be a different size to the original image.
        p_x, p_y = coord_3d.GetComputedDoubleDisplayValue(renderer)

        # Scale them up to the right image size.
        p_x *= scale_x
        p_y *= scale_y

        # And flip the y-coordinate, as OpenGL numbers Y from bottom up,
        # OpenCV numbers top-down.
        p_y = image_height - 1 - p_y  #

        # Difference between VTK points and reference points.
        d_x = p_x - float(i_c[0])
        d_y = p_y - float(i_c[1])
        rms += (d_x * d_x + d_y * d_y)

        counter += 1

    rms /= float(counter)
    rms = np.sqrt(rms)

    return rms

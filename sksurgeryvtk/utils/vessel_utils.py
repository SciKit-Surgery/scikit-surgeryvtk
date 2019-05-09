# -*- coding: utf-8 -*-

"""
Any useful little utilities to do with vessels,
which currently are the centrelines computed by a VMTK script
(vmtkcenterlines).
"""
import vtk
import numpy as np
import sksurgerycore.utilities.validate_file as f

# pylint: disable=invalid-name


def load_vessel_centrelines(file_name):
    """
    Loads vessel centrelines from a file generated from VMTK
    (vmtkcenterlines) and converts them into vtkPolyData.

    :param file_name: A path to the vessel centrelines file

    :return: vtkPolyData containing the vessel centrelines
    """

    f.validate_is_file(file_name)

    positions = []

    with open(file_name, 'r') as read_file:
        line_index = 1

        for line in read_file:
            # Each line in the vessel centrelines file contains:
            # X Y Z
            # MaximumInscribedSphereRadius
            # EdgeArray0
            # EdgeArray1
            # EdgePCoordArray.
            # Here we only use the 3D position of a point in the line, i.e.,
            # X, Y, Z.

            # First line is a comment.
            if line_index == 1:
                line_index += 1
                continue

            # Each token is separated by a space.
            x, y, z, _, _, _, _ = line.split(' ')
            positions.append([x, y, z])

            line_index += 1

        # Convert the list of positions into a numpy array.
        positions = np.array(positions, dtype=float)

    poly_data = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    points.SetData(vtk.util.numpy_support.numpy_to_vtk(positions))
    poly_data.SetPoints(points)

    return poly_data

# -*- coding: utf-8 -*-

"""
Any useful little utilities to do with vessels,
which currently are the centrelines computed by a VMTK script
(vmtkcenterlines).
"""
import os
import vtk
import numpy as np
import sksurgerycore.utilities.validate_file as f

# pylint: disable=invalid-name


def load_vessel_centrelines(file_name):
    """
    Loads vessel centrelines from a file generated from VMTK
    (vmtkcenterlines) and converts them into vtkPolyData.

    :param file_name: A path to the vessel centrelines file

    :return: poly_data: vtkPolyData containing the vessel centrelines
             poly_data_mapper: vtkPolyDataMapper for the vessel centrelines
    """

    f.validate_is_file(file_name)

    positions = []

    with open(file_name, 'r') as read_file:
        # Check if the file is empty.
        if os.path.getsize(file_name) == 0:
            raise ValueError('The file is empty.')

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

    centre_of_mass_filter = vtk.vtkCenterOfMass()
    centre_of_mass_filter.SetInputData(poly_data)
    centre_of_mass_filter.SetUseScalarsAsWeights(False)
    centre_of_mass_filter.Update()
    centre = centre_of_mass_filter.GetCenter()
    centre = np.array(centre)

    new_points = vtk.vtkPoints()
    number_of_points = poly_data.GetNumberOfPoints()

    # Current scale factor is empirically set.
    # The liver model is not scaled.
    scale = 1

    for i in range(number_of_points):
        point = poly_data.GetPoint(i)
        # point = point - centre
        new_points.InsertNextPoint([point[0] * scale,
                                    point[1] * scale,
                                    point[2] * scale])

    poly_data.SetPoints(new_points)

    lines = vtk.vtkCellArray()
    lines.InsertNextCell(number_of_points)
    for i in range(number_of_points):
        lines.InsertCellPoint(i)

    poly_data.SetLines(lines)

    poly_data_mapper = vtk.vtkPolyDataMapper()
    poly_data_mapper.SetInputData(poly_data)

    return poly_data, poly_data_mapper

def compute_closest_vessel_centreline_point_for_organ_voxel(
        vessel_centrelines,
        organ_voxels):
    """
    Computes the closest point on the vessel centrelines
    for each voxel in the organ model.

    :param vessel_centrelines: vtkPolyData containing vessel centrelines
    :param organ_voxels: vtkImageData containing the organ voxels

    :return:
    """

    # Iterate through the organ voxels and
    # compute the closest vessel centreline point.
    voxel_dimensions = organ_voxels.GetDimensions()

    print('voxel_dimensions', voxel_dimensions)

    for x in range(voxel_dimensions[0]):
        for y in range(voxel_dimensions[1]):
            for z in range(voxel_dimensions[2]):
                pixel_value = \
                    organ_voxels.GetPointData().GetScalars().GetTuple1(
                        x + voxel_dimensions[0] * (y + voxel_dimensions[1] * z))

                # Process only occupied voxels.
                # if pixel_value != 0:
                #     points.InsertNextPoint([x, y, z])

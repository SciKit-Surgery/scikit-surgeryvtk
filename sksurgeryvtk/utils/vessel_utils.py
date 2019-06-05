# -*- coding: utf-8 -*-

"""
Any useful little utilities to do with vessels,
which currently are the centrelines computed by a VMTK script
(vmtkcenterlines).
"""
import os
import random
import vtk
import sksurgerycore.utilities.validate_file as f

# pylint: disable=invalid-name, line-too-long, unused-variable


def load_vessel_centrelines(file_name):
    """
    Loads vessel centrelines from a file generated using
    'Accurate Fast Matching
     (https://uk.mathworks.com/matlabcentral/fileexchange/24531-accurate-fast-marching)'
    and converts them into vtkPolyData.

    :param file_name: A path to the vessel centrelines file (.txt),
                      which contains vessel centrelines and branch infomation.

    :return: poly_data: vtkPolyData containing the vessel centrelines
             poly_data_mapper: vtkPolyDataMapper for the vessel centrelines
    """

    f.validate_is_file(file_name)

    poly_data = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    line_indices = vtk.vtkCellArray()
    colours = vtk.vtkUnsignedCharArray()
    colours.SetNumberOfComponents(3)
    colours.SetName('colours')
    point_index = 0

    with open(file_name, 'r') as file:
        # Check if the file is empty.
        if os.path.getsize(file_name) == 0:
            raise ValueError('The file is empty.')

        # Branches.
        print(file.readline().strip())

        # Number of branches.
        print(file.readline().strip())

        number_of_branches = int(file.readline().strip())
        print(number_of_branches)

        for i in range(number_of_branches):
            # Branch ID.
            print(file.readline().strip())

            # Number of points.
            print(file.readline().strip())
            number_of_points = int(file.readline().strip())
            print(number_of_points)

            # Points.
            print(file.readline().strip())

            # Create a line for each branch.
            line_indices.InsertNextCell(number_of_points)

            for j in range(number_of_points):
                x, y, z = file.readline().strip().split(',')
                points.InsertNextPoint([float(x), float(y), float(z)])
                line_indices.InsertCellPoint(point_index + j)

            point_index += number_of_points

            # Set a random colour for each branch
            r = random.randint(1, 256)
            g = random.randint(1, 256)
            b = random.randint(1, 256)
            colours.InsertNextTuple3(r, g, b)

    poly_data.SetPoints(points)
    poly_data.SetLines(line_indices)
    poly_data.GetCellData().SetScalars(colours)

    poly_data_mapper = vtk.vtkPolyDataMapper()
    poly_data_mapper.SetInputData(poly_data)

    return poly_data, poly_data_mapper


def compute_closest_vessel_centreline_point_for_organ_voxels(
        vessel_centrelines, organ_glyph_3d_mapper):
    """
    Computes the closest point on the vessel centrelines
    for each voxel in the organ model.

    :param vessel_centrelines: vtkPolyData containing vessel centrelines
           and branch information
    :param organ_glyph_3d_mapper: vtkGlyph3DMapper
           for rendering the organ voxels

    :return:
    """

    # Iterate through the organ voxels and
    # compute the closest vessel centreline point.
    voxel_data = organ_glyph_3d_mapper.GetInput()
    number_of_voxels = voxel_data.GetNumberOfPoints()
    number_of_centreline_points = vessel_centrelines.GetNumberOfPoints()
    print('num vessel points', number_of_centreline_points)

    # For adding the closest point index to the voxel.
    indices = vtk.vtkIntArray()
    indices.SetNumberOfComponents(1)
    indices.SetName('Closest centreline point index')

    for cur_voxel in range(number_of_voxels):
        voxel_position = voxel_data.GetPoint(cur_voxel)
        min_distance = 1e6
        closest_point = 0

        for cur_point in range(number_of_centreline_points):
            point_position = vessel_centrelines.GetPoint(cur_point)
            # Compute the square distance for speed.
            distance = \
                (point_position[0] - voxel_position[0]) ** 2 + \
                (point_position[1] - voxel_position[1]) ** 2 + \
                (point_position[2] - voxel_position[2]) ** 2

            if distance < min_distance:
                closest_point = cur_point
                min_distance = distance

        # Add the closest point index to the voxel.
        indices.InsertNextValue(closest_point)

    voxel_data.GetPointData().AddArray(indices)

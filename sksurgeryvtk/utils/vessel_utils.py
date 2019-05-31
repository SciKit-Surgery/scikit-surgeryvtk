# -*- coding: utf-8 -*-

"""
Any useful little utilities to do with vessels,
which currently are the centrelines computed by a VMTK script
(vmtkcenterlines).
"""
import os
import vtk
import random
import numpy as np
import sksurgerycore.utilities.validate_file as f

# pylint: disable=invalid-name


def load_vessel_centrelines(file_name):
    """
    Loads vessel centrelines from a file generated using
    'Accurate Fast Matching (https://uk.mathworks.com/matlabcentral/fileexchange/24531-accurate-fast-marching)'
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

    # points = vtk.vtkPoints()
    # points.SetData(vtk.util.numpy_support.numpy_to_vtk(positions))
    # poly_data.SetPoints(points)
    #
    # centre_of_mass_filter = vtk.vtkCenterOfMass()
    # centre_of_mass_filter.SetInputData(poly_data)
    # centre_of_mass_filter.SetUseScalarsAsWeights(False)
    # centre_of_mass_filter.Update()
    # centre = centre_of_mass_filter.GetCenter()
    # centre = np.array(centre)
    #
    # new_points = vtk.vtkPoints()
    # number_of_points = poly_data.GetNumberOfPoints()
    #
    # # Current scale factor is empirically set.
    # # The liver model is not scaled.
    # scale = 1
    #
    # for i in range(number_of_points):
    #     point = poly_data.GetPoint(i)
    #     # point = point - centre
    #     new_points.InsertNextPoint([point[0] * scale,
    #                                 point[1] * scale,
    #                                 point[2] * scale])
    #
    # poly_data.SetPoints(new_points)
    #
    # lines = vtk.vtkCellArray()
    # lines.InsertNextCell(number_of_points)
    # for i in range(number_of_points):
    #     lines.InsertCellPoint(i)
    #
    # poly_data.SetLines(lines)

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

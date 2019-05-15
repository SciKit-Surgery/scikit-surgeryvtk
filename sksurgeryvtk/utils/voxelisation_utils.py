# -*- coding: utf-8 -*-

"""
Any useful little utilities to do with voxelising a 3D mesh.
"""
import vtk
import numpy as np

# pylint: disable=invalid-name


def convert_poly_data_to_binary_label_map(closed_surface_poly_data,
                                          binary_label_map):
    """
    Converts a 3D mesh into a binary label map.

    :param closed_surface_poly_data: vtkPolyData representing a 3D mesh
    :param binary_label_map: vtkImageData representing a binary label map
    """

    if closed_surface_poly_data.GetNumberOfPoints() < 2 or \
            closed_surface_poly_data.GetNumberOfCells() < 2:
        raise ValueError("Cannot create binary label map from surface "
                         "with number of points: "
                         f"{closed_surface_poly_data.GetNumberOfPoints()}"
                         " and number of cells: "
                         f"{closed_surface_poly_data.GetNumberOfCells()}")

    # Compute poly data normals.
    normal_filter = vtk.vtkPolyDataNormals()
    normal_filter.SetInputData(closed_surface_poly_data)
    normal_filter.ConsistencyOn()

    # Make sure that we have a clean triangle poly data.
    triangle = vtk.vtkTriangleFilter()
    triangle.SetInputConnection(normal_filter.GetOutputPort())

    # Convert to triangle strip.
    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(triangle.GetOutputPort())

    # Convert poly data to stencil.
    poly_data_to_image_stencil = vtk.vtkPolyDataToImageStencil()
    poly_data_to_image_stencil.SetInputConnection(stripper.GetOutputPort())
    poly_data_to_image_stencil.SetOutputSpacing(binary_label_map.GetSpacing())
    poly_data_to_image_stencil.SetOutputOrigin(binary_label_map.GetOrigin())
    poly_data_to_image_stencil.SetOutputWholeExtent(
        binary_label_map.GetExtent())
    poly_data_to_image_stencil.Update()

    # Convert stencil to image.
    image_stencil_to_image = vtk.vtkImageStencilToImage()
    image_stencil_to_image.SetInputConnection(
        poly_data_to_image_stencil.GetOutputPort())
    image_stencil_to_image.SetOutsideValue(0)
    image_stencil_to_image.SetInsideValue(1)
    image_stencil_to_image.Update()

    # Save result to output.
    binary_label_map.DeepCopy(image_stencil_to_image.GetOutput())


def voxelise_3d_mesh(poly_data, voxel_resolution_x, voxel_resolution_y,
                     voxel_resolution_z):
    """
    Voxelises a 3D mesh.

    :param poly_data: vtkPolyData containing the input 3D mesh
    :param voxel_resolution_x: Voxel grid dimension x
    :param voxel_resolution_y: Voxel grid dimension y
    :param voxel_resolution_z: Voxel grid dimension z

    :return: vtkGlyph3DMapper containing the resulting voxels from the mesh
    """

    out_val = 0

    # Compute bounds for poly data.
    bounds = poly_data.GetBounds()

    # vtkImageData for voxel representation storage.
    voxel_image = vtk.vtkImageData()

    # Specify the size of the image data.
    voxel_image.SetDimensions(voxel_resolution_x, voxel_resolution_y,
                              voxel_resolution_z)

    # Desired volume spacing,
    spacing = np.zeros(3)
    spacing[0] = 1.0 / voxel_resolution_x
    spacing[1] = 1.0 / voxel_resolution_y
    spacing[2] = 1.0 / voxel_resolution_z
    voxel_image.SetSpacing(spacing)

    origin = np.zeros(3)
    origin[0] = bounds[0] + spacing[0] / 2
    origin[1] = bounds[2] + spacing[1] / 2
    origin[2] = bounds[4] + spacing[2] / 2
    voxel_image.SetOrigin(origin)
    voxel_image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

    # Fill the image with baCkground voxels.
    voxel_image.GetPointData().GetScalars().Fill(out_val)

    # Convert to voxel image.
    convert_poly_data_to_binary_label_map(poly_data, voxel_image)

    # Visualization

    # Create point data for visualization via vtkGlyph3DMapper
    # based on the example code from
    # https://www.vtk.org/Wiki/VTK/Examples/Cxx/Visualization/Glyph3DMapper
    points = vtk.vtkPoints()

    for x in range(voxel_resolution_x):
        for y in range(voxel_resolution_y):
            for z in range(voxel_resolution_z):
                pixel_value = voxel_image.GetPointData().GetScalars().GetTuple1(
                    x + voxel_resolution_x * (y + voxel_resolution_y * z))

                if pixel_value != out_val:
                    points.InsertNextPoint([x, y, z])

    poly_data = vtk.vtkPolyData()
    poly_data.SetPoints(points)

    cube_source = vtk.vtkCubeSource()

    glyph_3d_mapper = vtk.vtkGlyph3DMapper()
    glyph_3d_mapper.SetSourceConnection(cube_source.GetOutputPort())
    glyph_3d_mapper.SetInputData(poly_data)
    glyph_3d_mapper.Update()

    return glyph_3d_mapper


def voxelise_3d_mesh_from_file(mesh_filename, voxel_resolution_x,
                               voxel_resolution_y, voxel_resolution_z):
    """
    Voxelises a 3D mesh loaded from a file.

    :param mesh_filename: Input 3D mesh filename
    :param voxel_resolution_x: Voxel grid dimension x
    :param voxel_resolution_y: Voxel grid dimension y
    :param voxel_resolution_z: Voxel grid dimension z

    :return: vtkGlyph3DMapper containing the resulting voxels from the mesh
    """

    # Load stl file.
    reader = vtk.vtkSTLReader()
    reader.SetFileName(mesh_filename)
    reader.Update()

    poly_data = vtk.vtkPolyData()
    poly_data.DeepCopy(reader.GetOutput())

    return voxelise_3d_mesh(poly_data, voxel_resolution_x, voxel_resolution_y,
                            voxel_resolution_z)

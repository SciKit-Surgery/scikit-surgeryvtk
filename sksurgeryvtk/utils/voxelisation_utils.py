# -*- coding: utf-8 -*-

"""
Any useful little utilities to do with voxelising a 3D mesh.
"""
import vtk
from vtk.util import colors
import numpy as np
from sksurgeryvtk.models.vtk_surface_model import VTKSurfaceModel

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


def voxelise_3d_mesh(mesh_filename, voxel_spacings):
    """
    Voxelises a 3D mesh.

    :param mesh_filename: Input 3D mesh filename
    :param voxel_spacings: [w, h, d], voxel grid spacings in x-, y-, z-axis

    :return: voxel_image: vtkImageData containing the resulting voxels from mesh
             glyph_3d_mapper: vtkGlyph3DMapper for rendering the voxels
    """

    model = VTKSurfaceModel(mesh_filename, colors.english_red)
    poly_data = model.source

    # Compute bounds for mesh poly data.
    bounds = poly_data.GetBounds()

    # vtkImageData for voxel representation storage.
    voxel_image = vtk.vtkImageData()

    # Specify the resolution of the image data.
    voxel_dimensions = [0, 0, 0]
    voxel_dimensions[0] = int((bounds[1] - bounds[0]) / voxel_spacings[0])
    voxel_dimensions[1] = int((bounds[3] - bounds[2]) / voxel_spacings[1])
    voxel_dimensions[2] = int((bounds[5] - bounds[4]) / voxel_spacings[2])
    voxel_image.SetDimensions(voxel_dimensions)

    # Desired volume spacing,
    voxel_image.SetSpacing(voxel_spacings)

    origin = np.zeros(3)
    origin[0] = bounds[0]
    origin[1] = bounds[2]
    origin[2] = bounds[4]
    voxel_image.SetOrigin(origin)
    voxel_image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

    # Fill the image with background voxels.
    out_val = 0
    voxel_image.GetPointData().GetScalars().Fill(out_val)

    # Convert to voxel image.
    convert_poly_data_to_binary_label_map(poly_data, voxel_image)

    # Visualisation

    # Create point data for visualization via vtkGlyph3DMapper
    # based on the example code from
    # https://www.vtk.org/Wiki/VTK/Examples/Cxx/Visualization/Glyph3DMapper
    points = vtk.vtkPoints()

    for x in range(voxel_dimensions[0]):
        for y in range(voxel_dimensions[1]):
            for z in range(voxel_dimensions[2]):
                pixel_value = voxel_image.GetPointData().GetScalars().GetTuple1(
                    x + voxel_dimensions[0] * (y + voxel_dimensions[1] * z))

                if pixel_value != out_val:
                    points.InsertNextPoint([x * voxel_spacings[0],
                                            y * voxel_spacings[1],
                                            z * voxel_spacings[2]])

    poly_data = vtk.vtkPolyData()
    poly_data.SetPoints(points)

    cube_source = vtk.vtkCubeSource()
    cube_source.SetCenter(origin[0], origin[1], origin[2])
    cube_source.SetXLength(voxel_spacings[0])
    cube_source.SetYLength(voxel_spacings[1])
    cube_source.SetZLength(voxel_spacings[2])

    glyph_3d_mapper = vtk.vtkGlyph3DMapper()
    glyph_3d_mapper.SetSourceConnection(cube_source.GetOutputPort())
    glyph_3d_mapper.SetInputData(poly_data)
    glyph_3d_mapper.Update()

    return voxel_image, glyph_3d_mapper

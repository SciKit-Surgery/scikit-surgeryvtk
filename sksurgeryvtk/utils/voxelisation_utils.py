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


def voxelise_3d_mesh(mesh_filename,
                     voxel_dimensions,
                     voxel_spacings=None):
    """
    Voxelises a 3D mesh.

    :param mesh: Input 3D mesh
    :param voxel_dimensions: [w, h, d], voxel grid dimensions in x-, y-, z-axis
    :param voxel_spacings: [w, h, d], voxel grid spacings in x-, y-, z-axis.
                           If None, spacings are set as 1/voxel_dimensions.

    :return: voxel_image: vtkImageData containing the resulting voxels from mesh
             glyph_3d_mapper: vtkGlyph3DMapper for rendering the voxels
    """

    out_val = 0

    # Load stl file.
    reader = vtk.vtkSTLReader()
    reader.SetFileName(mesh_filename)
    reader.Update()

    pd = vtk.vtkPolyData()
    pd.DeepCopy(reader.GetOutput())

    # Compute the centroid of the mesh to move it to the centroid.
    centre_of_mass_filter = vtk.vtkCenterOfMass()
    centre_of_mass_filter.SetInputData(pd)
    centre_of_mass_filter.SetUseScalarsAsWeights(False)
    centre_of_mass_filter.Update()
    centre = centre_of_mass_filter.GetCenter()
    centre = np.array(centre)

    # Need to scale down the liver model to be enclosed in the voxel grid.
    points = vtk.vtkPoints()
    number_of_points = pd.GetNumberOfPoints()

    # Current scale factor is empirically set.
    # The liver model is not scaled.
    scale = 0.005

    for i in range(number_of_points):
        point = pd.GetPoint(i)
        point = point - centre
        points.InsertNextPoint([point[0] * scale,
                                point[1] * scale,
                                point[2] * scale])

    pd.SetPoints(points)

    # Compute bounds for stl mesh poly data.
    bounds = pd.GetBounds()

    # vtkImageData for voxel representation storage.
    voxel_image = vtk.vtkImageData()

    # Specify the size of the image data.
    voxel_image.SetDimensions(voxel_dimensions)

    # Desired volume spacing,
    if voxel_spacings is None:
        voxel_spacings = np.zeros(3)
        voxel_spacings[0] = 1.0 / voxel_dimensions[0]
        voxel_spacings[1] = 1.0 / voxel_dimensions[1]
        voxel_spacings[2] = 1.0 / voxel_dimensions[2]

    voxel_image.SetSpacing(voxel_spacings)

    origin = np.zeros(3)
    origin[0] = bounds[0] + voxel_spacings[0] / 2
    origin[1] = bounds[2] + voxel_spacings[1] / 2
    origin[2] = bounds[4] + voxel_spacings[2] / 2
    voxel_image.SetOrigin(origin)
    voxel_image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

    # Fill the image with background voxels.
    voxel_image.GetPointData().GetScalars().Fill(out_val)

    # Convert to voxel image.
    convert_poly_data_to_binary_label_map(pd, voxel_image)

    # Visualization

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
                    points.InsertNextPoint([x, y, z])

    poly_data = vtk.vtkPolyData()
    poly_data.SetPoints(points)

    cube_source = vtk.vtkCubeSource()

    glyph_3d_mapper = vtk.vtkGlyph3DMapper()
    glyph_3d_mapper.SetSourceConnection(cube_source.GetOutputPort())
    glyph_3d_mapper.SetInputData(poly_data)
    glyph_3d_mapper.Update()

    return voxel_image, glyph_3d_mapper

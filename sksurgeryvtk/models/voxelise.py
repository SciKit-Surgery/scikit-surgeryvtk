""" Re-impelmentaiton of voxeilsation code from
https://gitlab.com/nct_tso_public/Volume2SurfaceCNN
"""

import logging
import math
from typing import Union
import os
import vtk
import numpy as np

LOGGER = logging.getLogger(__name__)

# Not being as strict with linting on this file, as it has all been copied
# from the original repo.
#pylint:disable=invalid-name, unused-variable, too-many-branches

def distanceField(surfaceMesh, targetGrid, targetArrayName: str, signed=False):
    """Create a distance field between a vtkStructuredGrid and a surface.

    :param surfaceMesh: Outer polygonal surface
    :param targetGrid: Grid array of points
    :type targetGrid: vtk.vtkStructuredGrid
    :param targetArrayName: The distance field values will be stored in the
    target grid, with this array name.
    :type targetArrayName: str
    :param signed: Signed/unsigned distance field, defaults to False (unsigned)
    :type signed: bool, optional
    """
    # Initialize distance field:
    df = vtk.vtkDoubleArray()
    df.SetNumberOfTuples(targetGrid.GetNumberOfPoints())
    df.SetName(targetArrayName)

    # Data structure to quickly find cells:
    cellLocator = vtk.vtkCellLocator()
    cellLocator.SetDataSet(surfaceMesh)
    cellLocator.BuildLocator()

    for i in range(0, targetGrid.GetNumberOfPoints()):
        # Take a point from the target...
        testPoint = [0] * 3
        targetGrid.GetPoint(i, testPoint)
        # ... find the point in the surface closest to it
        cID, subID, dist2 = vtk.mutable(0), vtk.mutable(0), vtk.mutable(0.0)
        closestPoint = [0] * 3
        cellLocator.FindClosestPoint(
            testPoint, closestPoint, cID, subID, dist2)
        dist = math.sqrt(dist2)

        df.SetTuple1(i, dist)

    if signed:
        pts = vtk.vtkPolyData()
        pts.SetPoints(targetGrid.GetPoints())

        enclosedPointSelector = vtk.vtkSelectEnclosedPoints()
        enclosedPointSelector.CheckSurfaceOn()
        enclosedPointSelector.SetInputData(pts)
        enclosedPointSelector.SetSurfaceData(surfaceMesh)
        enclosedPointSelector.SetTolerance(1e-9)
        enclosedPointSelector.Update()
        enclosedPoints = enclosedPointSelector.GetOutput()

        for i in range(0, targetGrid.GetNumberOfPoints()):
            if enclosedPointSelector.IsInside(i):
                df.SetTuple1(i, -df.GetTuple1(i))     # invert sign

    targetGrid.GetPointData().AddArray(df)


def distanceFieldFromCloud(surfaceCloud, targetGrid, targetArrayName):
    """Create a distance field between a vtkStructuredGrid and a point cloud.

    :param surfaceMesh: Pointcloud of surface
    :param targetGrid: Grid array of points
    :type targetGrid: vtk.vtkStructuredGrid
    :param targetArrayName: The distance field values will be stored in the
    target grid, with this array name.
    """
    # Initialize distance field:
    df = vtk.vtkDoubleArray()
    df.SetNumberOfTuples(targetGrid.GetNumberOfPoints())
    df.SetName(targetArrayName)

    # Data structure to quickly find cells:
    pointLocator = vtk.vtkPointLocator()
    pointLocator.SetDataSet(surfaceCloud)
    pointLocator.BuildLocator()

    for i in range(0, targetGrid.GetNumberOfPoints()):
        # Take a point from the target...
        testPoint = [0] * 3
        targetGrid.GetPoint(i, testPoint)
        # ... find the point in the surface closest to it
        cID, subID, dist2 = vtk.mutable(0), vtk.mutable(0), vtk.mutable(0.0)
        closestPoint = [0] * 3

        closestPointID = pointLocator.FindClosestPoint(testPoint)
        closestPoint = [0] * 3
        surfaceCloud.GetPoint(closestPointID, closestPoint)
        #closestPoint = [0]*3
        #surfaceMesh.GetPoint( closestPointID, closestPoint )
        dist = math.sqrt(
            vtk.vtkMath.Distance2BetweenPoints(
                testPoint, closestPoint))
        #dist = math.sqrt(dist2)
        df.SetTuple1(i, dist)

    targetGrid.GetPointData().AddArray(df)


def createGrid(total_size: float, grid_elements: int):
    """Returns a vtkStrucutredGrid.

    :param total_size: Total size of the grid i.e. How long is each dimension.
    Each indivdual element has size equal to total_size/grid_dims
    :type size: float
    :param grid_dims: Number of grid points in x/y/z
    :type grid_dims: [type]
    :return: [description]
    :rtype: [type]
    """
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions((grid_elements, grid_elements, grid_elements))
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(grid_elements**3)
    pID = 0
    start = -total_size / 2
    d = total_size / (grid_elements - 1)
    for i in range(0, grid_elements):
        for j in range(0, grid_elements):
            for k in range(0, grid_elements):
                x = start + d * k
                y = start + d * j
                z = start + d * i
                points.SetPoint(pID, x, y, z)
                pID += 1
    grid.SetPoints(points)
    return grid


def storeTransformationMatrix(grid, tf):
    """ Store a transformation matrix inside a vtk grid array."""
    mat = tf.GetMatrix()
    matArray = vtk.vtkDoubleArray()
    matArray.SetNumberOfTuples(16)
    matArray.SetNumberOfComponents(1)
    matArray.SetName("TransformationMatrix")
    for row in range(0, 4):
        for col in range(0, 4):
            matArray.SetTuple1(row * 4 + col, mat.GetElement(row, col))
    grid.GetFieldData().AddArray(matArray)


def loadTransformationMatrix(grid):
    """ Extract a transformation matrix fom a vtk grid array."""
    matArray = grid.GetFieldData().GetArray("TransformationMatrix")
    if matArray:
        tf = vtk.vtkTransform()
        mat = vtk.vtkMatrix4x4()
        for i in range(0, 16):
            val = matArray.GetTuple1(i)
            mat.SetElement(int(i / 4), i % 4, val)
        tf.SetMatrix(mat)
        return tf

    raise IOError("No 'TransformationMatrix' array found in field data.")


def unstructuredGridToPolyData(ug):
    """ Convert vtk unstructured grid to vtk poly data."""
    geometryFilter = vtk.vtkGeometryFilter()
    geometryFilter.SetInputData(ug)
    geometryFilter.Update()
    return geometryFilter.GetOutput()


def extractSurface(inputMesh):
    """ Extract surface of a mesh. """
    surfaceFilter = vtk.vtkDataSetSurfaceFilter()
    surfaceFilter.SetInputData(inputMesh)
    surfaceFilter.Update()
    surface = surfaceFilter.GetOutput()

    return surface


def load_points_from_file(filename):
    """ Extract vtk mesh from input file.
    :returns: Vtk mesh. """
    print(os.getcwd())
    if not os.path.exists(filename):
        raise ValueError(f'File {filename} does not exist')

    fileType = filename[-4:].lower()

    if fileType == ".stl":
        reader = vtk.vtkSTLReader()
    elif fileType == ".obj":
        reader = vtk.vtkOBJReader()
    elif fileType == ".vtk":
        reader = vtk.vtkUnstructuredGridReader()
    elif fileType == ".vtu":
        reader = vtk.vtkXMLUnstructuredGridReader()
    elif fileType == ".vtp":
        reader = vtk.vtkXMLPolyDataReader()

    else:
        raise IOError(
            "Mesh should be .vtk, .vtu, .vtp, .obj, .stl file!")

    reader.SetFileName(filename)
    reader.Update()
    mesh = reader.GetOutput()
    return mesh

def voxelise(input_mesh: Union[np.ndarray, str],
             array_name: str = "",
             output_grid: str = "voxelised.vts",
             size: float = 0.3,
             grid_elements: int = 64,
             move_input: float = None,
             center: bool = False,
             scale_input: float = None,
             reuse_transform: bool = False,
             signed_df: bool = True
             ):
    """Creates a voxelised distance field and writes to disk, stored as an array
     in a vtkStructuredGrid.

    :param input_mesh: Input mesh/points. Can be path to model file,
     or numpy array.
    :type input_mesh: Union[np.ndarray, str]
    :param array_name: Name of array in which to store distance field,
     defaults to ""
    :type array_name: str, optional
    :param output_grid: Output file name, defaults to "voxelised.vts"
    :type output_grid: str, optional
    :param size: Grid size, defaults to 0.3
    :type size: float, optional
    :param grid_elements: Number of x/y/z elements in grid, defaults to 64
    :type grid_elements: int, optional
    :param move_input: Move the input before transforming to distance field
     (movement is applied before scaling! defaults to None
    :type move_input: float, optional
    :param center: Center the data around the origin. defaults to False
    :type center: bool, optional
    :param scale_input: Scale the input before transforming to distance field
    (movement is applied before scaling!) defaults to None
    :type scale_input: float, optional
    :param reuse_transform: Reuse transformation already stored in the grid.
    Use this if you want to center mesh 1 and then apply the same transformation
     to mesh 2.
     Mutually exclusive with center, scale_input and move_input.
     defaults to False
    :type reuse_transform: bool, optional
    :param signed_df: Calcualte signed or unsigned distance field.
     defaults to True
    :type signed_df: bool, optional
    :return grid: Grid containing distance field.
    :rtype: vtk.vtkStructuredGrid
    """

    input_is_point_cloud = False
    if isinstance(input_mesh, str):
        mesh = load_points_from_file(input_mesh)

    else:
        input_is_point_cloud = True

        pts = vtk.vtkPoints()
        verts = vtk.vtkCellArray()
        for i in range(input_mesh.shape[0]):
            pts.InsertNextPoint(input_mesh[i][0],
                                input_mesh[i][1],
                                input_mesh[i][2])

            verts.InsertNextCell(1, (i,))
        mesh = vtk.vtkPolyData()
        mesh.SetPoints(pts)
        mesh.SetVerts(verts)
        input_is_point_cloud = True

    # If no array name was given, use sensible defaults:
    if array_name == "":
        if signed_df:
            array_name = "preoperativeSurface"
        else:
            array_name = "intraoperativeSurface"

    if not output_grid.endswith(".vts"):
        raise IOError("Output grid needs to be .vts!")

    if reuse_transform and (center or move_input or scale_input):
        raise IOError(
            "reuse_transform may not be used together with center, \
             moveInput or --scaleInput!")

    mesh = unstructuredGridToPolyData(mesh)

    bounds = [0] * 6
    mesh.GetBounds(bounds)
    print(
        "Resulting bounds: \
        ({:.3f}-{:.3f}, {:.3f}-{:.3f}, {:.3f}-{:.3f})".format(*bounds))

    ####################################################
    # Load the output mesh:
    if os.path.exists(output_grid):
        reader = vtk.vtkXMLStructuredGridReader()
        reader.SetFileName(output_grid)
        reader.Update()
        grid = reader.GetOutput()
        if grid.GetPointData().GetArray(array_name):
            err = "The output file {} already has a field named {}!".format(
                output_grid, array_name)
            raise IOError(err)
        b = grid.GetBounds()
        size = b[1] - b[0]
        grid_elements = grid.GetDimensions()[0]
    else:
        grid = createGrid(size, grid_elements)

    ####################################################
    # Transform input mesh:
    tf = vtk.vtkTransform()
    if scale_input is not None:
        print("Scaling point cloud by:", scale_input)
        tf.Scale([scale_input] * 3)
    if move_input is not None:
        print("Moving point cloud by:", move_input)
        tf.Translate(move_input)
    if center:
        bounds = [0] * 6
        mesh.GetBounds(bounds)
        dx = -(bounds[1] + bounds[0]) * 0.5
        dy = -(bounds[3] + bounds[2]) * 0.5
        dz = -(bounds[5] + bounds[4]) * 0.5
        print("Moving point cloud by:", (dx, dy, dz))
        tf.Translate((dx, dy, dz))
    if reuse_transform:
        try:
            tf = loadTransformationMatrix(grid)
        except BaseException:
            print("Warning: reuse_transform was set, but no previous \
                   transformation found in grid. \
                   Won't apply any transformation.")

    tfFilter = vtk.vtkTransformFilter()
    tfFilter.SetTransform(tf)
    tfFilter.SetInputData(mesh)
    tfFilter.Update()
    mesh = tfFilter.GetOutput()
    print("Applied transformation before voxelization:", tf.GetMatrix())

    ####################################################
    # Compute the (signed) distance field on the output grid:
    print("Will save results in array '" + array_name + "'.")
    print("Voxelization")
    if not input_is_point_cloud:
        surface = extractSurface(mesh)
        if signed_df:
            distanceField(surface, grid, array_name, signed=True)
        else:
            distanceField(surface, grid, array_name, signed=False)
    else:
        distanceFieldFromCloud(mesh, grid, array_name)

    ####################################################
    # Write the applied transform into a field data array:
    storeTransformationMatrix(grid, tf)

    ####################################################
    # Write the applied transform into a field data array:
    outputFolder = os.path.dirname(output_grid)
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    print("Writing to {}".format(output_grid))
    writer = vtk.vtkXMLStructuredGridWriter()
    writer.SetFileName(output_grid)
    writer.SetInputData(grid)
    writer.Update()

    return grid

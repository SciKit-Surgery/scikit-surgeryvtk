""" Re-impelmentaiton of voxeilsation code from
https://gitlab.com/nct_tso_public/Volume2SurfaceCNN
"""

import logging
import math
from typing import Union, Tuple
import os
import vtk
from vtk.util import numpy_support
import numpy as np

LOGGER = logging.getLogger(__name__)

# Not being as strict with linting on this file, as it has all been copied
# from the original repo.
# pylint:disable=invalid-name, unused-variable, too-many-branches
# pylint:disable=logging-too-many-args, logging-not-lazy
# pylint:disable=logging-format-interpolation

def distanceField(surfaceMesh, targetGrid, targetArrayName: str, signed=False):
    """Create a distance field between a vtkStructuredGrid and a surface.

    :param surfaceMesh: Outer polygonal surface
    :param targetGrid: Grid array of points
    :type targetGrid: vtk.vtkStructuredGrid
    :param targetArrayName: The distance field values will be stored in the \
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
    :param targetArrayName: The distance field values will be stored in the \
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

    :param total_size: Total size of the grid i.e. How long is each dimension. \
    Each indivdual element has size equal to total_size/grid_dims
    :type size: float
    :param grid_dims: Number of grid points in x/y/z
    :type grid_dims: int
    :return: grid
    :rtype: vtkStructuredGrid
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
    if not os.path.exists(filename):
        raise ValueError(f'File {filename} does not exist')

    fileType = filename[-4:].lower()

    if fileType == ".stl":
        reader = vtk.vtkSTLReader()
    elif fileType == ".obj":
        reader = vtk.vtkOBJReader()
    elif fileType == ".vtk":
        reader = vtk.vtkPolyDataReader()
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

def voxelise(input_mesh: Union[np.ndarray, vtk.vtkDataObject, str],
             output_grid: Union[vtk.vtkStructuredGrid, str] \
                 = None,
             array_name: str = "",
             size: float = 0.3,
             grid_elements: int = 64,
             move_input: float = None,
             center: bool = False,
             scale_input: float = None,
             reuse_transform: bool = False,
             signed_df: bool = True
             ):
    """ Creates a voxelised distance field, stores it in a vtkStructuredGrid,\
        optinally writes to disk.

    :param input_mesh: Input mesh/points. Can be path to model file, \
     or numpy array. Units of mesh should be in metres.
    :type input_mesh: Union[np.ndarray, str]
    :param output_grid: Either a vtkStrucutredGrid object, or a file that
    contains one (or will be created), if not specified, a grid will be created.
    :type output_grid: Union[vtk.vtkStructuredGrid, str], optional
    :param array_name: Name of array in which to store distance field, \
     if not specified, defaults to preoperativeSurface for if signed_df = True,
     else intraoperativeSurface
    :type array_name: str, optional
    :param size: Grid size, defaults to 0.3
    :type size: float, optional
    :param grid_elements: Number of x/y/z elements in grid, defaults to 64 \
    :type grid_elements: int, optional
    :param move_input: Move the input before transforming to distance field \
     (movement is applied before scaling! defaults to None
    :type move_input: float, optional
    :param center: Center the data around the origin. defaults to False
    :type center: bool, optional
    :param scale_input: Scale the input before transforming to distance field \
    (movement is applied before scaling!). Input is expected to be in metres, \
        if it is in mm, set scale_input to 0.001 defaults to None
    :type scale_input: float, optional
    :param reuse_transform: Reuse transformation already stored in the grid. \
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

    elif isinstance(input_mesh, vtk.vtkDataObject):
        mesh = input_mesh

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

    output_grid_is_file = isinstance(output_grid, str)
    output_grid_is_vtkgrid = isinstance(output_grid, vtk.vtkStructuredGrid)

    if output_grid_is_file and not output_grid.endswith(".vts"):
        raise IOError("Output grid file needs to be .vts!")

    if reuse_transform and (center or move_input or scale_input):
        raise IOError(
            "reuse_transform may not be used together with center, \
             moveInput or --scaleInput!")

    mesh = unstructuredGridToPolyData(mesh)

    bounds = [0] * 6
    mesh.GetBounds(bounds)
    LOGGER.debug(
        "Resulting bounds: \
        ({:.3f}-{:.3f}, {:.3f}-{:.3f}, {:.3f}-{:.3f})".format(*bounds))

    ####################################################
    # Load the output mesh if it is a file, otherwise it is a vtkStructuredGrid:
    if output_grid_is_file:
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

    elif output_grid_is_vtkgrid:
        grid = output_grid
        b = grid.GetBounds()
        size = b[1] - b[0]
        grid_elements = grid.GetDimensions()[0]

    # We don't already have a grid, create one
    else:
        grid = createGrid(size, grid_elements)

    ####################################################
    # Transform input mesh:
    tf = vtk.vtkTransform()

    if scale_input is not None:
        LOGGER.debug("Scaling point cloud by: %s", scale_input)
        tf.Scale([scale_input] * 3)
    if move_input is not None:
        LOGGER.debug("Moving point cloud by: %s", move_input)
        tf.Translate(move_input)
    if center:
        bounds = [0] * 6
        mesh.GetBounds(bounds)
        dx = -(bounds[1] + bounds[0]) * 0.5
        dy = -(bounds[3] + bounds[2]) * 0.5
        dz = -(bounds[5] + bounds[4]) * 0.5
        LOGGER.debug("Moving point cloud by: %s", (dx, dy, dz))
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
    LOGGER.debug("Applied transformation before voxelization:")
    LOGGER.debug(tf.GetMatrix())

    # Remove previous array with the same name, if it exists
    if grid.GetPointData().GetArray(array_name):
        grid.GetPointData().RemoveArray(array_name)

    ####################################################
    # Compute the (signed) distance field on the output grid:
    LOGGER.debug("Will save results in array '" + array_name + "'.")
    LOGGER.info("Voxelization")
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


    if output_grid_is_file:
        LOGGER.debug("Writing grid to file %s", output_grid)
        outputFolder = os.path.dirname(output_grid)
        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)

        write_grid_to_file(grid, output_grid)

    return grid

def write_grid_to_file(grid: vtk.vtkStructuredGrid,
                       output_grid: str):
    """Write vtkStructuredGrid to file

    :param grid: Grid to write
    :type grid: vtk.vtkStructuredGrid
    :param output_grid: File path
    :type output_grid: str
    """
    LOGGER.debug("Writing to {}".format(output_grid))
    writer = vtk.vtkXMLStructuredGridWriter()
    writer.SetFileName(output_grid)
    writer.SetInputData(grid)
    writer.Update()

def extract_array_from_grid_file(input_grid_file: str,
                                 array_name: str) -> np.ndarray:
    """ Read an array from vtkStructuredGrid file

    :param input_grid_file: Input file, should be a vtkStructuredGrid file
    :type input_grid_file: str
    :param array_name: Array to extract from grid
    :type array_name: str
    :return: Extracted array
    :rtype: np.ndarray
    """

    reader = vtk.vtkXMLStructuredGridReader()
    reader.SetFileName(input_grid_file)
    reader.Update()
    input_grid = reader.GetOutput()

    return extract_array_from_grid(input_grid, array_name)


def extract_array_from_grid(input_grid: vtk.vtkStructuredGrid,
                            array_name: str) -> np.ndarray:
    """Read an array from a vtkStructuredGrid object

    :param input_grid: Input data grid
    :type input_grid: vtk.vtkStructuredGrid
    :param array_name: Array to extract from grid
    :type array_name: str
    :return: Extracted array
    :rtype: np.ndarray
    """
    data = input_grid.GetPointData()
    array = numpy_support.vtk_to_numpy(data.GetArray(array_name))

    return array

def extract_surfaces_for_v2snet(input_grid: vtk.vtkStructuredGrid) \
    -> Tuple[np.ndarray, np.ndarray]:
    """Conveience function to extract the pre and intraoperative surfaces,
    to pass to V2SNet.

    :param input_grid: Grid containing pre and intraoperative surfaces
    :type input_grid: vtk.vtkStructuredGrid
    :return: pre and intraoperative surfaces as numpy arrays
    :rtype: Tuple[np.ndarray, np.ndarray]
    """
    preop = extract_array_from_grid(input_grid, 'preoperativeSurface')
    intraop = extract_array_from_grid(input_grid, 'intraoperativeSurface')

    return preop, intraop

def save_displacement_array_in_grid(array: np.ndarray,
                                    out_grid: Union[vtk.vtkStructuredGrid, str],
                                    array_name: str = "estimatedDisplacement"):
    """ Save numpy data as an array within a vtkStructuredGrid.
    Mainly used for storing calculated displacement field.

    :param array: Numpy array
    :type array: np.ndarray
    :param out_grid: Grid in which to store array
    :type out_grid: Union[vtk.vtkStructuredGrid, str]
    :param array_name: Array name, defaults to "estimatedDisplacement"
    :type array_name: str, optional
    """

    grid_is_file = isinstance(out_grid, str)

    if grid_is_file:
        grid = load_structured_grid(out_grid)
    else:
        grid = out_grid

    df = numpy_support.numpy_to_vtk(array)
    df.SetName( array_name )
    if grid.GetPointData().HasArray(array_name):
        grid.GetPointData().RemoveArray(array_name)
        LOGGER.debug("Warning: Overwriting array {}".format(array_name))
    grid.GetPointData().AddArray(df)

    if grid_is_file:
        write_grid_to_file(grid, out_grid)

def load_structured_grid(input_file: str):
    """Load vtkStructuredGrid from file

    :param input_file: Path to vtk structured grid file
    :type input_file: str
    :raises TypeError:
    :return: Loaded grid
    :rtype: vtk.vtkStructuredGrid
    """
    if input_file[-4:].lower() != ".vts":
        raise TypeError("Input file should be .vts type")

    reader = vtk.vtkXMLStructuredGridReader()
    reader.SetFileName(input_file)
    reader.Update()
    grid = reader.GetOutput()

    return grid


def applyTransformation(dataset, tf):
    """Apply a transformation to each data array stored in vtk object.

    :param dataset: Vtk object containing array(s)
    :param tf: Transform
    :type tf: vtk.vtkTransform
    """
    for i in range(dataset.GetPointData().GetNumberOfArrays()):
        arr = dataset.GetPointData().GetArray(i)
        if arr.GetNumberOfComponents() == 3:
            for j in range(arr.GetNumberOfTuples()):
                data = arr.GetTuple3(j)
                transformed = tf.TransformVector(data)
                arr.SetTuple3(
                    j,
                    transformed[0],
                    transformed[1],
                    transformed[2])


def apply_displacement_to_mesh(mesh: Union[vtk.vtkDataObject, str],
                               field: Union[vtk.vtkStructuredGrid, str],
                               save_mesh: Union[bool, str] = False,
                               disp_array_name: str = 'estimatedDisplacement'):
    """Apply a displacement field to a mesh.
    The displacement field is stored as an array within a vtkStructuredGrid.

    :param mesh: Mesh to deform, can either be path to file or vtk object.
    :type mesh: Union[vtk.vtkDataObject, str]
    :param field: Grid containing displacement field, can either be path \
        to file or vtk object.
    :type field: Union[vtk.vtkStructuredGrid, str]
    :param save_mesh: If a file name is passed, the deformed mesh is saved \
        to disk, defaults to False
    :type save_mesh: Union[bool, str], optional
    :param disp_array_name: Name of array within vtkStructuredGrid containing \
        the displacement field, defaults to 'estimatedDisplacement'
    :type disp_array_name: str, optional
    :return: Displaced mesh
    :rtype: vtk.vtkPolyData
    """

    if isinstance(mesh, str):
        mesh = load_points_from_file(mesh)
    if isinstance(field, str):
        field = load_structured_grid(field)

    # In case the field data was transformed, also transform the test data:
    scale = 1  # default
    try:
        tf = loadTransformationMatrix(field)
        tf.Inverse()
        LOGGER.debug("Applying transform")
        tfFilter = vtk.vtkTransformFilter()
        tfFilter.SetTransform(tf)
        tfFilter.SetInputData(field)
        tfFilter.Update()
        field = tfFilter.GetOutput()

        # Apply transformation also to all vector fields:
        applyTransformation(field, tf)

        scale = tf.GetMatrix().GetElement(0, 0)

    #pylint:disable=broad-except
    except Exception as e:
        print(e)
        print("Could not find or apply transformation. Skipping.")

    # Threshold to ignore all points outside of field i.e.
    # Points outside of the model:
    threshold = vtk.vtkThreshold()
    threshold.SetInputArrayToProcess(
        0,
        0,
        0,
        vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS,
        "preoperativeSurface")
    threshold.ThresholdByLower(0)
    threshold.SetInputData(field)
    threshold.Update()
    fieldInternal = threshold.GetOutput()

    # Interpolate displacement field to points on mesh
    kernel = vtk.vtkGaussianKernel()
    kernel.SetRadius(0.01 * scale)
    kernel.SetKernelFootprintToRadius()

    interpolator = vtk.vtkPointInterpolator()
    interpolator.SetKernel(kernel)
    interpolator.SetNullPointsStrategyToMaskPoints()
    interpolator.SetValidPointsMaskArrayName("validInternalPoints")

    interpolator.SetSourceData(fieldInternal)
    interpolator.SetInputData(mesh)
    interpolator.Update()
    output = interpolator.GetOutput()

    # Actually displace the points in the mesh by adding the displacement
    # to the point coordinates
    displaced_points = vtk.vtkPoints()
    for i in range(output.GetNumberOfPoints()):
        p = output.GetPoint(i)
        displaced_points.InsertNextPoint(p)

    validInternalPoints = output.GetPointData().GetArray("validInternalPoints")

    displacement = output.GetPointData().GetArray(disp_array_name)

    np_disp = numpy_support.vtk_to_numpy(displacement)
    np_vip = numpy_support.vtk_to_numpy(validInternalPoints)

    for i in range(output.GetNumberOfPoints()):
        validity = validInternalPoints.GetTuple1(i)

        if validity > 0.5:

            p = output.GetPoint(i)
            p = np.asarray(p)
            d = displacement.GetTuple3(i)
            d = np.asarray(d)
            p_d = p + d

            displaced_points.SetPoint(i, p_d[0], p_d[1], p_d[2])

    output.SetPoints(displaced_points)

    if save_mesh:
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetInputData(output)
        writer.SetFileName(save_mesh)
        writer.Update()

    # Undo transformation so that field is 'reset' for future use
    tf = loadTransformationMatrix(field)
    LOGGER.debug("Reversing transform")
    tfFilter = vtk.vtkTransformFilter()
    tfFilter.SetTransform(tf)
    tfFilter.SetInputData(field)
    tfFilter.Update()
    field = tfFilter.GetOutput()

    # Apply transformation also to all vector fields:
    applyTransformation(field, tf)

    return output

# class NonRigidAlignment:
    ## Example wrapper class
#     def __init__(self,
#                  preop_surface: Union[np.ndarray, str],
#                  displacement_estimator = None,
#                  scale_input: float = None):

#         self.displacement_estimator = displacement_estimator

#         self.grid = \
#             voxelise(preop_surface,
#                      signed_df=True,
#                      center = True,
#                      scale_input = scale_input)

#     def load_surface(self, intraop_surface):
#         self.grid = \
#             voxelise(intraop_surface,
#                      output_grid=self.grid,
#                      signed_df=False,
#                      reuse_transform=True)

#     def calculate_displacement(self):
#         displacement = self.displacement_estimator.get_displacement(self.grid)
#         save_displacement_array_in_grid(displacement, self.grid)

#     def displace_model(self, model, save_mesh=None):

#         return apply_displacement_to_mesh(model, self.grid, save_mesh)

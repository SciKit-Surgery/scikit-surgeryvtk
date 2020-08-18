import logging
import math
from typing import Union
import os
import vtk
import numpy as np

""" Re-impelmentaiton of voxeilsation code from 
https://gitlab.com/nct_tso_public/Volume2SurfaceCNN
"""

LOGGER = logging.getLogger(__name__)

def checkInside( p, surfPoint, n ):
    pInside = [0]*3
    pOutside = [0]*3
    pOutside[0] = surfPoint[0] + n[0]
    pOutside[1] = surfPoint[1] + n[1]
    pOutside[2] = surfPoint[2] + n[2]
    pInside[0] = surfPoint[0] - n[0]
    pInside[1] = surfPoint[1] - n[1]
    pInside[2] = surfPoint[2] - n[2]
    dist2PointOutside = vtk.vtkMath.Distance2BetweenPoints( p, pOutside )
    dist2PointInside = vtk.vtkMath.Distance2BetweenPoints( p, pInside )
    return dist2PointInside <= dist2PointOutside

def distanceField( surfaceMesh, targetGrid, targetArrayName, signed=False ):

    # Initialize distance field:
    df = vtk.vtkDoubleArray()
    df.SetNumberOfTuples( targetGrid.GetNumberOfPoints() )
    df.SetName(targetArrayName)

    # Data structure to quickly find cells:
    cellLocator = vtk.vtkCellLocator()
    cellLocator.SetDataSet( surfaceMesh )
    cellLocator.BuildLocator()
    
    for i in range(0, targetGrid.GetNumberOfPoints() ):
        # Take a point from the target...
        testPoint = [0]*3
        targetGrid.GetPoint( i, testPoint )
        # ... find the point in the surface closest to it
        cID, subID, dist2 = vtk.mutable(0), vtk.mutable(0), vtk.mutable(0.0)
        closestPoint = [0]*3
        cellLocator.FindClosestPoint( testPoint, closestPoint, cID, subID, dist2 )
        dist = math.sqrt(dist2)

        df.SetTuple1( i, dist )

    if signed:
        pts = vtk.vtkPolyData()
        pts.SetPoints( targetGrid.GetPoints() )

        enclosedPointSelector = vtk.vtkSelectEnclosedPoints()
        enclosedPointSelector.CheckSurfaceOn()
        enclosedPointSelector.SetInputData( pts )
        enclosedPointSelector.SetSurfaceData( surfaceMesh )
        enclosedPointSelector.SetTolerance( 1e-9 )
        enclosedPointSelector.Update()
        enclosedPoints = enclosedPointSelector.GetOutput()

        for i in range(0, targetGrid.GetNumberOfPoints() ):
            if enclosedPointSelector.IsInside(i):
                df.SetTuple1( i, -df.GetTuple1(i) )     # invert sign

    targetGrid.GetPointData().AddArray( df )

def distanceFieldFromCloud( surfaceCloud, targetGrid, targetArrayName ):

    # Initialize distance field:
    df = vtk.vtkDoubleArray()
    df.SetNumberOfTuples( targetGrid.GetNumberOfPoints() )
    df.SetName(targetArrayName)

    # Data structure to quickly find cells:
    pointLocator = vtk.vtkPointLocator()
    pointLocator.SetDataSet( surfaceCloud )
    pointLocator.BuildLocator()

    for i in range(0, targetGrid.GetNumberOfPoints() ):
        # Take a point from the target...
        testPoint = [0]*3
        targetGrid.GetPoint( i, testPoint )
        # ... find the point in the surface closest to it
        cID, subID, dist2 = vtk.mutable(0), vtk.mutable(0), vtk.mutable(0.0)
        closestPoint = [0]*3
        
        closestPointID = pointLocator.FindClosestPoint( testPoint )
        closestPoint = [0]*3
        surfaceCloud.GetPoint( closestPointID, closestPoint )
        #closestPoint = [0]*3
        #surfaceMesh.GetPoint( closestPointID, closestPoint )
        dist = math.sqrt( vtk.vtkMath.Distance2BetweenPoints( testPoint, closestPoint ) )
        #dist = math.sqrt(dist2)
        df.SetTuple1( i, dist )

    targetGrid.GetPointData().AddArray( df )

def createGrid( size, gridSize ):
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions( (gridSize,gridSize,gridSize) )
    points = vtk.vtkPoints()
    points.SetNumberOfPoints( gridSize**3 )
    pID = 0
    start = -size/2
    d = size/(gridSize-1)
    for i in range( 0, gridSize ):
        for j in range( 0, gridSize ):
            for k in range( 0, gridSize ):
                x = start + d*k
                y = start + d*j
                z = start + d*i
                points.SetPoint( pID, x, y, z )
                pID += 1
    grid.SetPoints( points )
    return grid

def storeTransformationMatrix( grid, tf ):
    mat = tf.GetMatrix()
    matArray = vtk.vtkDoubleArray()
    matArray.SetNumberOfTuples(16)
    matArray.SetNumberOfComponents(1)
    matArray.SetName( "TransformationMatrix" )
    for row in range(0,4):
        for col in range(0,4):
            matArray.SetTuple1( row*4+col, mat.GetElement( row, col ) )
    grid.GetFieldData().AddArray(matArray)

def loadTransformationMatrix( grid ):
    matArray = grid.GetFieldData().GetArray( "TransformationMatrix" )
    if matArray:
        tf = vtk.vtkTransform()
        mat = vtk.vtkMatrix4x4()
        for i in range( 0, 16 ):
            val = matArray.GetTuple1( i )
            mat.SetElement( int(i/4), i % 4, val )
        tf.SetMatrix( mat )
        return tf
    else:
        raise IOError("No 'TransformationMatrix' array found in field data.")

def unstructuredGridToPolyData( ug ):
    geometryFilter = vtk.vtkGeometryFilter()
    geometryFilter.SetInputData( ug )
    geometryFilter.Update()
    return geometryFilter.GetOutput()

def extractSurface( inputMesh ):
    surfaceFilter = vtk.vtkDataSetSurfaceFilter()
    surfaceFilter.SetInputData( inputMesh )
    surfaceFilter.Update()
    surface = surfaceFilter.GetOutput()

    return surface

def load_points_from_file(filename):
    print(os.getcwd())
    if not os.path.exists(filename):
        raise ValueError(f'File {filename} does not exist')

    input_is_point_cloud = False
    fileType = filename[-4:].lower()

    if fileType == ".pcd":
        input_is_point_cloud = True
        if signed_df:
            raise IOError("Input file is .pcd, cannot compute signed distance function (use --DF instead)")

        pc = pcl.load( input_mesh )
        pts = vtk.vtkPoints()
        verts = vtk.vtkCellArray()
        for i in range( pc.size ):
            pts.InsertNextPoint( pc[i][0], pc[i][1], pc[i][2] )
            verts.InsertNextCell( 1, (i,) )
        mesh = vtk.vtkPolyData()
        mesh.SetPoints( pts )
        mesh.SetVerts( verts )
        return mesh, input_is_point_cloud


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
        raise IOError("Mesh should be .vtk, .vtu, .vtp, .obj, .stl or .pcd file!")

    reader.SetFileName( filename )
    reader.Update()
    mesh = reader.GetOutput()
    return mesh, input_is_point_cloud

def voxelise(input_mesh: Union[np.ndarray, str],
             array_name: str = "",
             output_grid: str ="voxelised.vts",
             size: float = 0.3,
             grid_size: int = 64,
             move_input: float= None,
             center: bool = False,
             scale_input: float = None,
             reuse_transform: bool = False,
             signed_df: bool = True
             ):

    if isinstance(input_mesh, str):
        mesh, input_is_point_cloud = load_points_from_file(input_mesh)
    
    else:
        pts = vtk.vtkPoints()
        verts = vtk.vtkCellArray()
        for i in range(input_mesh.shape[0]):
            pts.InsertNextPoint(input_mesh[i][0],
                                input_mesh[i][1],
                                input_mesh[i][2] )

            verts.InsertNextCell( 1, (i,) )
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
        raise IOError("reuse_transform may not be used together with center, moveInput or --scaleInput!")

    mesh = unstructuredGridToPolyData(mesh)

    bounds = [0]*6;
    mesh.GetBounds(bounds)
    print("Resulting bounds: ({:.3f}-{:.3f}, {:.3f}-{:.3f}, {:.3f}-{:.3f})".format(*bounds))

    ####################################################
    # Load the output mesh:
    if os.path.exists(output_grid):
        reader = vtk.vtkXMLStructuredGridReader()
        reader.SetFileName(output_grid)
        reader.Update() 
        grid = reader.GetOutput()
        if grid.GetPointData().GetArray( array_name ):
            err = "The output file {} already has a field named {}!".format(output_grid,array_name)
            raise IOError(err)
        b = grid.GetBounds()
        size = b[1]-b[0]
        grid_size = grid.GetDimensions()[0]
    else:
        grid = createGrid( size, grid_size )


    ####################################################
    ## Transform input mesh:
    tf = vtk.vtkTransform()
    if scale_input is not None:
        print("Scaling point cloud by:", scale_input)
        tf.Scale( [scale_input]*3 )
    if move_input is not None:
        print("Moving point cloud by:", move_input)
        tf.Translate(move_input)
    if center:
        bounds = [0]*6;
        mesh.GetBounds(bounds)
        dx = -(bounds[1]+bounds[0])*0.5
        dy = -(bounds[3]+bounds[2])*0.5
        dz = -(bounds[5]+bounds[4])*0.5
        print("Moving point cloud by:", (dx,dy,dz) )
        tf.Translate( (dx,dy,dz) )
    if reuse_transform:
        try:
            tf = loadTransformationMatrix( grid )
        except:
            print("Warning: reuse_transform was set, but no previous transformation found in grid. Won't apply any transformation.")

    tfFilter = vtk.vtkTransformFilter()
    tfFilter.SetTransform(tf)
    tfFilter.SetInputData(mesh)
    tfFilter.Update()
    mesh = tfFilter.GetOutput()
    print("Applied transformation before voxelization:", tf.GetMatrix())

    ####################################################
    ## Compute the (signed) distance field on the output grid:
    print("Will save results in array '" + array_name + "'.")
    print("Voxelization")
    if not input_is_point_cloud:
        surface = extractSurface( mesh )
        if signed_df:
            distanceField( surface, grid, array_name, signed=True )
        else:
            distanceField( surface, grid, array_name, signed=False )
    else:
        distanceFieldFromCloud( mesh, grid, array_name )

    ####################################################
    # Write the applied transform into a field data array:
    storeTransformationMatrix( grid, tf )

    ####################################################
    # Write the applied transform into a field data array:
    outputFolder = os.path.dirname( output_grid )
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    print("Writing to {}".format( output_grid ))
    writer = vtk.vtkXMLStructuredGridWriter()
    writer.SetFileName( output_grid )
    writer.SetInputData( grid )
    writer.Update()

    return grid



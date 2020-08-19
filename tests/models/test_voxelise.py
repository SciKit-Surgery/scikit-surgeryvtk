import os
import pytest
import numpy as np
from sksurgeryvtk.models import voxelise
from vtk.util import numpy_support

""" These are regression tests to ensure that we get the same result(s) as
running the standalone code from the original repository.
This is not by any means a thorough set of tests, just confirming the
functionality we want it for at present (August 2020). """

if not os.path.exists('tests/data/output/voxelise'):
    os.makedirs('tests/data/output/voxelise')

def test_liver_stl_voxelisation():

    #Tutorial-section-1-start
    input_mesh = 'tests/data/voxelisation/liver_downsample.stl'
    output_grid = "tests/data/output/voxelise/voxelised.vts"

    # Voxelisation will throw an error if the file already exists with a preoperative surface array.
    if os.path.exists(output_grid):
        os.remove(output_grid)

    signed_df = True
    center = True
    scale_input = 0.001
    size = 0.3
    grid_elements = 64
    #Tutorial-section-1-end

    #Tutorial-section-2-start
    grid = voxelise.voxelise(input_mesh=input_mesh,
                            output_grid=output_grid,
                            signed_df=signed_df,
                            center=center,
                            scale_input=scale_input,
                            size=size,
                            grid_elements=64)
    #Tutorial-section-2-end

    point_data = grid.GetPointData()

    # Check dimensions correct
    point_array = point_data.GetArray(0)
    cell_dims = [0, 0, 0]
    grid.GetCellDims(cell_dims)
    assert cell_dims == [63, 63, 63]

    # Check array name is correct
    assert(point_data.GetArrayName(0) == 'preoperativeSurface')

    data_array = point_data.GetArray(0)
    numpy_data = numpy_support.vtk_to_numpy(data_array)

    # Cells 'inside' the liver have negative values, so this should be
    # consistent
    cells_in_liver = numpy_data < 0
    assert np.count_nonzero(cells_in_liver) == 14628

#TODO: Doesn't seem to work with vtk poly data?

def test_intraop_surface_voxelisation():
    """ test_liver_stl_voxelisation needs to have run successfully for this
    to work correctly. """
    #Tutorial-section-3-start
    input_mesh = 'tests/data/voxelisation/intraop_surface.stl'
    output_grid = "tests/data/output/voxelise/voxelised.vts"

    # If the output_grid doesn't exist, we can't run this test
    assert os.path.exists(output_grid)

    signed_df = False
    reuse_transform = True
    size = 0.3
    grid_elements = 64

    grid = voxelise.voxelise(input_mesh=input_mesh,
                            output_grid=output_grid,
                            signed_df=signed_df,
                            reuse_transform=reuse_transform,
                            size=size,
                            grid_elements=grid_elements
                            )
    #Tutorial-section-3-end
    point_data = grid.GetPointData()

    # Check dimensions correct
    point_array = point_data.GetArray(0)
    cell_dims = [0, 0, 0]
    grid.GetCellDims(cell_dims)
    assert cell_dims == [63, 63, 63]

    # Check array name is correct
    assert(point_data.GetArrayName(1) == 'intraoperativeSurface')

    data_array = point_data.GetArray(1)
    numpy_data = numpy_support.vtk_to_numpy(data_array)

    # Cells on the intraop surface should have a value between 0 and the voxel size
    voxel_size = size/grid_elements
    cells_on_surface = numpy_data < voxel_size

    assert np.count_nonzero(cells_on_surface) == 2059
    
def test_intraop_from_numpy():
    """ test_liver_stl_voxelisation needs to have run successfully for this
    to work correctly. """

    # Using a different name here so that we don't have to remove 
    # the 'intraoperativeSurface' that was made by the previous test.
    # Normally, we wouldn't specify this new name.
    array_name = "point_intraoperativeSurface"
    output_grid = "tests/data/output/voxelise/voxelised.vts"

    # If the output_grid doesn't exist, we can't run this test
    assert os.path.exists(output_grid)

    signed_df = False
    reuse_transform = True
    size = 0.3
    grid_elements = 64
    # Same surface as the previous test, but saved as points rather than surface
    #Tutorial-section-4-start

    input_mesh = 'tests/data/voxelisation/intraop_surface.xyz'
    numpy_mesh = np.loadtxt(input_mesh)

    grid = voxelise.voxelise(input_mesh=numpy_mesh,
                            array_name=array_name,
                            output_grid=output_grid,
                            signed_df=signed_df,
                            reuse_transform=reuse_transform,
                            size=size,
                            grid_elements=grid_elements
                            )
    #Tutorial-section-4-end

    point_data = grid.GetPointData()

    # Check dimensions correct
    point_array = point_data.GetArray(0)
    cell_dims = [0, 0, 0]
    grid.GetCellDims(cell_dims)
    assert cell_dims == [63, 63, 63]

    # Check array name is correct
    array_idx = 2
    assert(point_data.GetArrayName(array_idx) == array_name)

    data_array = point_data.GetArray(array_idx)
    numpy_data = numpy_support.vtk_to_numpy(data_array)

    # Cells on the intraop surface should have a value between 0 and the voxel size
    voxel_size = size/grid_elements
    cells_on_surface = numpy_data < voxel_size
    print(cells_on_surface)
    assert np.count_nonzero(cells_on_surface) == 1956
    
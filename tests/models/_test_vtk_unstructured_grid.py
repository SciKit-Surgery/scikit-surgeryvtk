import sksurgeryvtk.models.vtk_grid_model as GM
import vtk
import numpy as np

def test_load_from_vtu():

    model = "tests/data/models/unstructured_grid.vtu"
    neonate_model = GM.VTKUnstructuredGridModel(model)

    array_min, array_max = neonate_model.get_cell_array_bounds()
    neonate_model.threshold_between(array_min, array_max)

def test_load_from_vtk():

    model = "tests/data/models/unstructured_grid.vtk"
    neonate_model = GM.VTKUnstructuredGridModel(model)

    array_min, array_max = neonate_model.get_cell_array_bounds()
    neonate_model.threshold_between(array_min, array_max)



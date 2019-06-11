# -*- coding: utf-8 -*-


"""
Utilities for operations on vtk polydata
"""

from vtk import vtkMassProperties, vtkBooleanOperationPolyDataFilter

def check_overlapping_bounds(polydata_0, polydata_1):
    """
    Checks whether two polydata have overlapping bounds

    :param polydata_0: vtkPolyData representing a 3D mesh
    :param polydata_1: vtkPolyData representing a 3D mesh

    :return : True if bounding boxes overlap, False otherwise
    """

    bounds_0 = polydata_0.GetBounds()
    bounds_1 = polydata_1.GetBounds()
    overlapping = True
    for i in range(0, 3):
        #This assumes that GetBounds always returns lower, upper
        if bounds_0[i*2] > bounds_1[i*2+1]:
            overlapping = False
        else:
            if bounds_1[i*2] > bounds_0[i*2+1]:
                overlapping = False

    return overlapping


def two_polydata_dice(polydata_0, polydata_1):
    """
    Calculates the DICE score for two polydata.
    Will probably struggle with complex topologies,
    but should be fine for vaguely spherical shape.
    This function uses vtk.vtkMassProperties() so does not
    convert polydata to image data

    :param polydata_0: vtkPolyData representing a 3D mesh
    :param polydata_1: vtkPolyData representing a 3D mesh

    :return dice: The DICE score
    :return volume_0: The enclosed volume of polydata_0
    :return volume_1: The enclosed volume of polydata_1
    :return volume_01: The enclosed volume of the intersection
    """
    measured_polydata = vtkMassProperties()
    measured_polydata.SetInputData(polydata_0)
    volume_0 = measured_polydata.GetVolume()

    measured_polydata.SetInputData(polydata_1)
    volume_1 = measured_polydata.GetVolume()

    intersector = vtkBooleanOperationPolyDataFilter()
    intersector.SetOperationToIntersection()

    intersector.SetInputData(0, polydata_0)
    intersector.SetInputData(1, polydata_1)

    if check_overlapping_bounds(polydata_0, polydata_1):
        intersector.Update()
        intersection = intersector.GetOutput()
        measured_polydata.SetInputData(intersection)
        volume_01 = measured_polydata.GetVolume()
    else:
        volume_01 = 0.0
        dice = 0.0

    dice = 2 *  volume_01 / (volume_0 + volume_1)
    return dice, volume_0, volume_1, volume_01

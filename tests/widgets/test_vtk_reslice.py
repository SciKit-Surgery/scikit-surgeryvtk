import pytest
from sksurgeryvtk.widgets import vtk_reslice_widget

def test_slice_viewer(qtbot):

    dicom_path = 'tests/data/dicom/LegoPhantom_3slices'
    reslice = vtk_reslice_widget.VTKSliceViewer(dicom_path)

    qtbot.addWidget(reslice)

    reslice.update_slice_positions(1,1,1)

def test_mouse_scroll_slice_viewer(qtbot):

    dicom_path = 'tests/data/dicom/LegoPhantom_3slices'
    reslice = vtk_reslice_widget.MouseWheelSliceViewer(dicom_path)

    qtbot.addWidget(reslice)

    reslice.update_slice_positions(1,1,1)


# -*- coding: utf-8 -*-

from sksurgeryvtk.widgets import vtk_reslice_widget


def test_slice_viewer(qtbot):
    dicom_path = 'tests/data/dicom/LegoPhantom_10slices'
    reslice = vtk_reslice_widget.VTKSliceViewer(dicom_path)

    qtbot.addWidget(reslice)

    reslice.update_slice_positions_pixels(1, 1, 1)


def test_mouse_scroll_slice_viewer(qtbot):
    dicom_path = 'tests/data/dicom/LegoPhantom_10slices'
    reslice = vtk_reslice_widget.MouseWheelSliceViewer(dicom_path)

    qtbot.addWidget(reslice)

    reslice.update_slice_positions_pixels(1, 1, 1)

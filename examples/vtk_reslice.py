import sys

from PySide2 import QtWidgets
from sksurgeryvtk.widgets.vtk_reslice_widget import TrackedSliceViewer
from sksurgeryarucotracker.arucotracker import ArUcoTracker

qApp = QtWidgets.QApplication([])

dicom_path = 'tests/data/dicom/LegoPhantom'

tracker = ArUcoTracker({})
tracker.start_tracking()

slice_viewer = TrackedSliceViewer(dicom_path, tracker)
slice_viewer.start()

qApp.exec_()


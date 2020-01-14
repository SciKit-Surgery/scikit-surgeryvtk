""" Example usage of using the vtk reslice widgets.

`python vtk_reslice.py` - loads Viewer with mouse wheel scrolling.
'python vtk_reslice.py tracked' - loads Viewer with ArUco tracker for
    slice control.

NB: scikit-surgeryaruco is not installed by default with scikit-surgeryvtk
You should pip install it manually to run the tracked demo.
"""
import sys

from PySide2 import QtWidgets
from sksurgeryvtk.widgets.vtk_reslice_widget import TrackedSliceViewer, \
     MouseWheelSliceViewer
from sksurgeryarucotracker.arucotracker import ArUcoTracker

qApp = QtWidgets.QApplication([])

dicom_path = 'tests/data/dicom/LegoPhantom_10slices'

n_args = len(sys.argv)
if n_args > 1 and sys.argv[1] == "tracked":
    tracker = ArUcoTracker({})
    tracker.start_tracking()

    slice_viewer = TrackedSliceViewer(dicom_path, tracker)

else:
    slice_viewer = MouseWheelSliceViewer(dicom_path)

slice_viewer.start()

qApp.exec_()

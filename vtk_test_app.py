
# cd /home/mxochicale/repositories/Scikit-Surgery/scikit-surgeryvtk
# export PYTHONPATH=/home/mxochicale/repositories/Scikit-Surgery/scikit-surgeryvtk/ &&
# conda activate scikit-surgeryvtkVE
# && python vtk_test_app.py

# export PYTHONPATH=/home/mxochicale/repositories/Scikit-Surgery/scikit-surgeryvtk/ && conda activate scikit-surgeryvtkVE && python vtk_test_app.py
# pytest -v -s tests/widgets/test_vtk_overlay_window.py

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow
# import vtk

if __name__ == '__main__':
    # first we create an application
    app = QApplication(['Is it working?'])
    window = QMainWindow()
    widget = QWidget()

    vtk_overlay = VTKOverlayWindow(offscreen=False, init_widget=False)
    window.setCentralWidget(vtk_overlay)
    vtk_overlay.Initialize()
    vtk_overlay.Start()
    widget.show()

    try:
        app.exec()
    except AttributeError:
        app.exec()

    print("Finalizing")
    vtk_overlay.close()


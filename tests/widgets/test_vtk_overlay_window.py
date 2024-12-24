# -*- coding: utf-8 -*-

import numpy as np
import pytest
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer
)
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import sksurgeryvtk.models.vtk_point_model as pm
import sksurgeryvtk.models.vtk_surface_model as sm


def test_vtk_render_window_settings(setup_vtk_overlay_window):
    widget, _vtk_std_err, _pyside_qt_app = setup_vtk_overlay_window

    assert not widget.GetRenderWindow().GetStereoRender()
    assert not widget.GetRenderWindow().GetStereoCapableWindow()
    assert widget.GetRenderWindow().GetAlphaBitPlanes()
    assert widget.GetRenderWindow().GetMultiSamples() == 0
    widget.close()


def test_vtk_render_window_settings_no_init(setup_vtk_overlay_window_no_init):
    widget, _vtk_std_err, _pyside_qt_app = setup_vtk_overlay_window_no_init

    assert not widget.GetRenderWindow().GetStereoRender()
    assert not widget.GetRenderWindow().GetStereoCapableWindow()
    assert widget.GetRenderWindow().GetAlphaBitPlanes()
    assert widget.GetRenderWindow().GetMultiSamples() == 0
    widget.close()


def test_vtk_foreground_render_settings(setup_vtk_overlay_window):
    widget, _vtk_std_err, _pyside_qt_app = setup_vtk_overlay_window

    layer = widget.get_foreground_renderer().GetLayer()
    assert widget.get_foreground_renderer().GetLayer() == 1
    assert widget.get_foreground_renderer().GetUseDepthPeeling()
    widget.close()


def test_vtk_background_render_settings(setup_vtk_overlay_window):
    widget, _vtk_std_err, _pyside_qt_app = setup_vtk_overlay_window

    assert widget.get_background_renderer().GetLayer() == 0
    assert not widget.get_background_renderer().GetInteractive()
    widget.close()


def test_image_importer(setup_vtk_overlay_window):
    widget, _vtk_std_err, _pyside_qt_app = setup_vtk_overlay_window

    width, height, _number_of_scalar_components = widget.rgb_input.shape
    expected_extent = (0, height - 1, 0, width - 1, 0, 2)
    actual_extent = widget.rgb_image_importer.GetDataExtent()

    assert actual_extent == expected_extent
    assert widget.rgb_image_importer.GetDataScalarTypeAsString() == "unsigned char"
    assert widget.rgb_image_importer.GetNumberOfScalarComponents() == 3
    widget.close()


def test_frame_pixels(setup_vtk_overlay_window):
    widget, _vtk_std_err, _pyside_qt_app = setup_vtk_overlay_window

    pixel = widget.rgb_frame[0, 0, :]
    expected_pixel = [1, 1, 1]
    assert np.array_equal(pixel, expected_pixel)
    widget.close()


def test_basic_pyside_vtk_pipeline():
    """
    Local test of a basic vtk pipeline with pyside
    Not really a unit test as it does not assert anything.
    But at least it might throw an error if something else changes.
    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """

    # Check if already an instance of QApplication is present or not
    if not QApplication.instance():
        _pyside_qt_app = QApplication([])
    else:
        _pyside_qt_app = QApplication.instance()

    window_qwidget = QWidget()
    window_qwidget.show()
    layout = QVBoxLayout()
    window_qwidget.setLayout(layout)

    colors = vtkNamedColors()

    cone = vtkConeSource()
    cone.SetResolution(100)
    cone.SetCenter(-2, 0, 0)

    coneMapper = vtkPolyDataMapper()
    coneMapper.SetInputConnection(cone.GetOutputPort())

    coneActor = vtkActor()
    coneActor.SetMapper(coneMapper)
    coneActor.GetProperty().SetColor(colors.GetColor3d("Tomato"))
    coneActor.RotateZ(60.0)

    coneActor = vtkActor()
    coneActor.SetMapper(coneMapper)
    coneActor.GetProperty().SetColor(colors.GetColor3d("Tomato"))
    coneActor.RotateZ(60.0)

    ren = vtkRenderer()
    ren.AddActor(coneActor)

    qvtk_render_window_interactor = QVTKRenderWindowInteractor()
    qvtk_render_window_interactor.GetRenderWindow().AddRenderer(ren)
    qvtk_render_window_interactor.resize(100, 100)

    layout.addWidget(qvtk_render_window_interactor)

    # To exit window using 'q' or 'e' key
    qvtk_render_window_interactor.AddObserver("ExitEvent", lambda o, e, a=_pyside_qt_app: a.quit())
    qvtk_render_window_interactor.Initialize()
    qvtk_render_window_interactor.Start()

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    qvtk_render_window_interactor.close()


def test_basic_cone_overlay(vtk_overlay_with_gradient_image):
    """
    Not really a unit test as it does not assert anything.
    But at least it might throw an error if something else changes.
    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """
    image, widget, _vtk_std_err, _pyside_qt_app = vtk_overlay_with_gradient_image

    widget.resize(image.shape[1], image.shape[0])

    cone = vtkConeSource()
    cone.SetResolution(60)
    cone.SetCenter(-2, 0, 0)
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(cone.GetOutputPort())
    actor = vtkActor()
    actor.SetMapper(mapper)

    widget.add_vtk_actor(actor)
    widget.AddObserver("ExitEvent", lambda o, e, a=_pyside_qt_app: a.quit())

    widget.show()
    widget.Initialize()
    widget.Start()

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    widget.close()


def test_point_set_overlay(vtk_overlay_with_gradient_image):
    """
    Not really a unit test as it does not assert anything.
    But at least it might throw an error if something else changes.
    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """
    _image, widget, _vtk_std_err, _pyside_qt_app = vtk_overlay_with_gradient_image

    points = np.zeros((4, 3), dtype=float)
    points[1][0] = 1
    points[2][1] = 1
    points[3][2] = 1
    colours = np.zeros((4, 3), dtype=np.uint8)
    colours[0][0] = 255
    colours[0][1] = 255
    colours[0][2] = 255
    colours[1][0] = 255
    colours[2][1] = 255
    colours[3][2] = 255

    vtk_models = [pm.VTKPointModel(points, colours)]
    widget.add_vtk_models(vtk_models)
    widget.AddObserver("ExitEvent", lambda o, e, a=_pyside_qt_app: a.quit())

    widget.show()
    widget.Initialize()
    widget.Start()

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    widget.close()


def test_surface_model_overlay(vtk_overlay_with_gradient_image):
    """
    Not really a unit test as it does not assert anything.
    But at least it might throw an error if something else changes.
    For local test, remember to uncomment `_pyside_qt_app.exec()` at the end of this module
    """
    _image, widget, _vtk_std_err, _pyside_qt_app = vtk_overlay_with_gradient_image
    surface = [sm.VTKSurfaceModel('tests/data/models/Liver/liver.vtk', (1.0, 1.0, 1.0))]
    widget.add_vtk_models(surface)
    widget.resize(512, 256)
    widget.AddObserver("ExitEvent", lambda o, e, a=_pyside_qt_app: a.quit())

    widget.show()
    widget.Initialize()
    widget.Start()

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    widget.close()


def test_add_model_to_background_renderer_raises_error(vtk_overlay_with_gradient_image):
    surface = [sm.VTKSurfaceModel('tests/data/models/Liver/liver.vtk', (1.0, 1.0, 1.0))]
    _image, widget, _vtk_std_err, _pyside_qt_app = vtk_overlay_with_gradient_image

    with pytest.raises(ValueError):
        widget.add_vtk_models(surface, layer=0)

    with pytest.raises(ValueError):
        widget.add_vtk_models(surface, layer=2)

    widget.close()


def test_add_models_to_foreground_renderer(vtk_overlay_with_gradient_image):
    liver = [sm.VTKSurfaceModel('tests/data/models/Liver/liver.vtk', (1.0, 1.0, 1.0))]
    tumors = [sm.VTKSurfaceModel('tests/data/models/Liver/liver_tumours.vtk', (1.0, 1.0, 1.0))]
    image, widget, _vtk_std_err, _pyside_qt_app = vtk_overlay_with_gradient_image

    # If no layer is specified, default is 0
    widget.add_vtk_models(liver)

    foreground_actors = widget.get_foreground_renderer().GetActors()
    assert foreground_actors.GetNumberOfItems() == 1

    # Explicitly specify use of foreground renderer
    widget.add_vtk_models(tumors, 1)

    foreground_actors = widget.get_foreground_renderer().GetActors()
    assert foreground_actors.GetNumberOfItems() == 2

    # Check overlay renderer is empty
    overlay_renderer_actors = widget.get_overlay_renderer().GetActors()
    assert overlay_renderer_actors.GetNumberOfItems() == 0
    widget.close()


def test_add_models_to_overlay_renderer(vtk_overlay_with_gradient_image):
    liver = [sm.VTKSurfaceModel('tests/data/models/Liver/liver.vtk', (1.0, 1.0, 1.0))]
    tumors = [sm.VTKSurfaceModel('tests/data/models/Liver/liver_tumours.vtk', (1.0, 1.0, 1.0))]
    _image, widget, _vtk_std_err, _pyside_qt_app = vtk_overlay_with_gradient_image

    widget.add_vtk_models(liver, 4)

    overlay_actors = widget.get_overlay_renderer().GetActors()
    assert overlay_actors.GetNumberOfItems() == 1

    widget.add_vtk_models(tumors, 4)

    overlay_actors = widget.get_overlay_renderer().GetActors()
    assert overlay_actors.GetNumberOfItems() == 2

    # Check foreground is empty
    foreground_actors = widget.get_foreground_renderer().GetActors()
    assert foreground_actors.GetNumberOfItems() == 0
    widget.close()


def test_add_and_remove_models_from_layers(vtk_overlay_with_gradient_image):
    liver = [sm.VTKSurfaceModel('tests/data/models/Liver/liver.vtk', (1.0, 1.0, 1.0))]
    tumors = [sm.VTKSurfaceModel('tests/data/models/Liver/liver_tumours.vtk', (1.0, 1.0, 1.0))]
    image, widget, _vtk_std_err, _pyside_qt_app = vtk_overlay_with_gradient_image

    # If no layer is specified, default is 0
    widget.add_vtk_models(liver, 1)

    foreground_actors = widget.get_foreground_renderer(layer=1).GetActors()
    assert foreground_actors.GetNumberOfItems() == 1

    # Now choose a different renderer.
    widget.add_vtk_models(tumors, 3)

    # Check we have one actor in each layer.
    foreground_actors = widget.get_foreground_renderer(layer=1).GetActors()
    assert foreground_actors.GetNumberOfItems() == 1
    foreground_actors = widget.get_foreground_renderer(layer=3).GetActors()
    assert foreground_actors.GetNumberOfItems() == 1

    # Then remove them, and check we have zero actors in each layer.
    widget.remove_all_models_from_renderer()
    foreground_actors = widget.get_foreground_renderer(layer=1).GetActors()
    assert foreground_actors.GetNumberOfItems() == 0
    foreground_actors = widget.get_foreground_renderer(layer=3).GetActors()
    assert foreground_actors.GetNumberOfItems() == 0

    # Check overlay renderer is empty
    overlay_renderer_actors = widget.get_overlay_renderer().GetActors()
    assert overlay_renderer_actors.GetNumberOfItems() == 0
    widget.close()

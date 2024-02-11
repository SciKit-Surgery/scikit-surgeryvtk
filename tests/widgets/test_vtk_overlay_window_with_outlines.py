# -*- coding: utf-8 -*-

import sksurgeryvtk.models.vtk_surface_model as sm


def test_surface_without_outline(vtk_overlay_with_gradient_image):
    """
    If we're not using outline rendering get_outline_actor
    should run but return None, so we can call add_vtk_actor(None)
    and not break anything.
    """
    image, widget, _, app = vtk_overlay_with_gradient_image
    surface = [sm.VTKSurfaceModel('tests/data/models/Liver/liver.vtk', (1.0, 1.0, 1.0),
                                  opacity=0.1, outline=False)]
    widget.add_vtk_models(surface)
    outline_actor = surface[0].get_outline_actor(
        widget.get_foreground_renderer().GetActiveCamera())

    foreground_actors = widget.get_foreground_renderer().GetActors()
    assert foreground_actors.GetNumberOfItems() == 1

    widget.add_vtk_actor(outline_actor)

    foreground_actors = widget.get_foreground_renderer().GetActors()
    assert foreground_actors.GetNumberOfItems() == 1

    widget.resize(512, 256)
    widget.show()
    widget.Render()

    # You don't really want this in a unit test, :-)
    # otherwise you can't exit. It's kept here for interactive testing.
    # app.exec()


def test_surface_outline_overlay(vtk_overlay_with_gradient_image):
    """
    If we're using outline rendering get_outline_actor
    should run but return an actor, which we can then add to the
    scene
    """
    image, widget, _, app = vtk_overlay_with_gradient_image
    surface = [sm.VTKSurfaceModel('tests/data/models/Liver/liver.vtk', (1.0, 1.0, 1.0),
                                  opacity=0.1, outline=True)]
    widget.add_vtk_models(surface)

    foreground_actors = widget.get_foreground_renderer().GetActors()
    assert foreground_actors.GetNumberOfItems() == 2

    widget.resize(512, 256)
    widget.show()
    widget.Render()

    # You don't really want this in a unit test, :-)
    # otherwise you can't exit. It's kept here for interactive testing.
    # app.exec()

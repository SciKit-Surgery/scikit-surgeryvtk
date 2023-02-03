# coding=utf-8

from sksurgeryvtk.text.text_overlay import VTKLargeTextCentreOfScreen


def test_position_correct(setup_vtk_overlay_window):
    # Create a window, and check the text position
    # is correct.
    vtk_overlay_window, _, _ = setup_vtk_overlay_window

    vtk_text = VTKLargeTextCentreOfScreen("Some text")
    vtk_text.set_parent_window(vtk_overlay_window)

    text_x, text_y = vtk_text.text_actor.GetPosition()

    window_width, window_height = vtk_overlay_window._RenderWindow.GetSize()

    assert text_x == window_width / 2
    assert text_y == window_height / 2

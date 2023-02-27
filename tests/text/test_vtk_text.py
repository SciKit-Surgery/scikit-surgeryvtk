# coding=utf-8

import platform

import pytest

from sksurgeryvtk.text.text_overlay import VTKText

## Skipif maker for all OSs
skip_pytest_in_oss = pytest.mark.skipif(
    platform.system()=='Linux' or platform.system()=='Windows' or platform.system() == 'Darwin',
    reason="Skipping pytest for OSs due to issues with VTK pipelines and pyside workflows"
    )

@pytest.fixture
def vtk_text():
    text = "hello world"
    x = 100
    y = 200

    return VTKText(text, x, y)


def test_text_set_correctly(vtk_text):
    assert vtk_text.text_actor.GetInput() == "hello world"


def test_position_set_correctly(vtk_text):
    x, y = vtk_text.text_actor.GetPosition()

    assert x == 100
    assert y == 200


def test_set_font_size(vtk_text):
    desired_size = 10
    vtk_text.set_font_size(desired_size)

    actual_size = vtk_text.text_actor.GetTextProperty().GetFontSize()
    assert actual_size == desired_size


def test_set_colour(vtk_text):
    r, g, b = 1.0, 1.0, 1.0

    vtk_text.set_colour(r, g, b)

    r_out, g_out, b_out = vtk_text.text_actor.GetTextProperty().GetColor()

    assert r_out == r
    assert g_out == g
    assert b_out == b


def test_invalid_text(vtk_text):
    with pytest.raises(TypeError):
        invalid_input = 1234
        vtk_text.set_text_string(invalid_input)

    assert vtk_text.text_actor.GetInput() == "hello world"


def test_invalid_position(vtk_text):
    invalid_position = 'a'

    with pytest.raises(TypeError):
        vtk_text.set_text_position(invalid_position, 1)
    with pytest.raises(TypeError):
        vtk_text.set_text_position(1, invalid_position)

    x, y = vtk_text.text_actor.GetPosition()

    assert x == 100
    assert y == 200

@skip_pytest_in_oss
def test_window_resize(vtk_text, setup_vtk_overlay_window):
    """
    Create a window, resize it, and check the text position has been correctly updated.

    For local test, you might like to uncomment `_pyside_qt_app.exec()` at the end of this module
    """

    vtk_overlay_window, _, _pyside_qt_app = setup_vtk_overlay_window
    vtk_overlay_window.show()
    vtk_overlay_window.Initialize()  # Allows the interactor to initialize itself.

    original_size_w, original_size_h = 640, 480
    vtk_overlay_window.setFixedSize(original_size_w, original_size_h)
    win_size = vtk_overlay_window.GetSize()
    print(f' win_size: {win_size}')

    # Add model to window
    vtk_text.set_parent_window(vtk_overlay_window)

    # Resize window
    new_size_w, new_size_h = 320, 240
    vtk_overlay_window.setFixedSize(new_size_w, new_size_h)

    # Trigger the resize callback manually, as VTK doesn't do it, presumably
    # because we aren't running an actual GUI app
    vtk_text.callback_update_position_in_window(None, None)

    resized_win_size = vtk_overlay_window.GetSize()
    print(f' resized_win_size: {resized_win_size}')

    # # BUG: On the Mac CI machine, the window size doesn't change, so don't run the following tests
    # # if the window size hasn't been updated
    if resized_win_size != (original_size_w, original_size_h):
        print(vtk_text.x, vtk_text.y)
        new_x, new_y = vtk_text.x, vtk_text.y

        # There will be some error due to imperfect positioning when resizing
        acceptable_pixel_error = 10
        assert abs(new_x - 50) < acceptable_pixel_error
        assert abs(new_y - 100) < acceptable_pixel_error

    else:
        pytest.skip("Window not resizing.. skipping")

    # You don't really want this in a unit test, otherwise you can't exit.
    # If you want to do interactive testing, please uncomment the following line
    # _pyside_qt_app.exec()
    vtk_overlay_window.close()

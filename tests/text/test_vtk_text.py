
import platform
import pytest
import logging
from sksurgeryvtk.text.text_overlay import VTKText
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow


@pytest.fixture
def vtk_text():
    text = "hello world"
    x = 100
    y = 200

    return VTKText(text, x, y)

def test_text_set_correctly(vtk_text):
    
    assert vtk_text.text_actor.GetInput() == "hello world"

def test_position_set_correctly(vtk_text):

    x,y = vtk_text.text_actor.GetPosition()

    assert x == 100
    assert y == 200

def test_set_font_size(vtk_text):
    
    desired_size = 10
    vtk_text.set_font_size(desired_size)

    actual_size = vtk_text.text_actor.GetTextProperty().GetFontSize()
    assert  actual_size == desired_size

def test_set_colour(vtk_text):
    
    r, g, b = 1.0, 1.0, 1.0

    vtk_text.set_colour(r,g,b)

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

    x,y = vtk_text.text_actor.GetPosition()

    assert x == 100
    assert y == 200

def test_window_resize(vtk_text, setup_qt):
    """
     Create a window, resize it, and check the text position
    has been correctly updated.
    """
    
    # There is an issue with this test on Mac runner
    if platform.system() == 'Darwin':
        pytest.skip("Skipping Mac test")

    # Explcitly set the window size to avoid any ambiguity
    vtk_overlay_window = VTKOverlayWindow()
    original_size = (640, 480)
    vtk_overlay_window._RenderWindow.SetSize(original_size)

    # Add model to window
    vtk_text.set_parent_window(vtk_overlay_window)
    original_x, original_y = vtk_text.x, vtk_text.y

    # Resize window    
    new_size = (320, 240)
    vtk_overlay_window._RenderWindow.SetSize(new_size)
    # Trigger the resize callback manually, as VTK doesn't do it, presumably
    # because we aren't running an actual GUI app
    vtk_text.callback_update_position_in_window(None, None)

    resized_win_size = vtk_overlay_window._RenderWindow.GetSize()
    # BUG: On the Mac CI machine, the window size doesn't change, so don't run the following tests
    # if the window size hasn't been updated
    if resized_win_size != original_size:
        new_x, new_y = vtk_text.x, vtk_text.y

        # There will be some error due to imperfect positioning when resizing
        acceptable_pixel_error = 10
        assert abs(new_x - 50) < acceptable_pixel_error
        assert abs(new_y - 100) < acceptable_pixel_error
    
    else:
        pytest.skip("Window not resizing.. skipping")



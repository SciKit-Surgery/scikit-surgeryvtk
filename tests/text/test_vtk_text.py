import pytest

from sksurgeryvtk.text.text_overlay import VTKText
from sksurgeryvtk.widgets.vtk_overlay_window import VTKOverlayWindow


@pytest.fixture
def vtk_model():
    text = "hello world"
    x = 10
    y = 20

    return VTKText(text, x, y)

def test_text_set_correctly(vtk_model):
    
    assert vtk_model.text_actor.GetInput() == "hello world"

def test_position_set_correctly(vtk_model):

    x,y = vtk_model.text_actor.GetPosition()

    assert x == 10
    assert y == 20

def test_set_font_size(vtk_model):
    
    desired_size = 10
    vtk_model.set_font_size(desired_size)

    actual_size = vtk_model.text_actor.GetTextProperty().GetFontSize()
    assert  actual_size == desired_size

def test_set_colour(vtk_model):
    
    r, g, b = 1.0, 1.0, 1.0

    vtk_model.set_colour(r,g,b)

    r_out, g_out, b_out = vtk_model.text_actor.GetTextProperty().GetColor()

    assert r_out == r
    assert g_out == g
    assert b_out == b

def test_invalid_text(vtk_model):

    with pytest.raises(TypeError):
        invalid_input = 1234
        vtk_model.set_text_string(invalid_input)

    assert vtk_model.text_actor.GetInput() == "hello world"

def test_invalid_position(vtk_model):
    
    invalid_position = 'a'

    with pytest.raises(TypeError):
        vtk_model.set_text_position(invalid_position, 1)
    with pytest.raises(TypeError):
        vtk_model.set_text_position(1, invalid_position)

    x,y = vtk_model.text_actor.GetPosition()

    assert x == 10
    assert y == 20

def test_window_resize(vtk_model):
    """
     Create a window, resize it, and check the text position
    has been correctly updated.
    """
    
    # Explcitly set the window size to avoid any ambiguity
    vtk_overlay_window = VTKOverlayWindow()
    original_size = (640, 480)
    vtk_overlay_window._RenderWindow.SetSize(original_size)

    # Add model to window
    vtk_model.set_parent_window(vtk_overlay_window)
    original_x, original_y = vtk_model.x, vtk_model.y

    # Resize window    
    new_size = (320, 240)
    vtk_overlay_window._RenderWindow.SetSize(new_size)

    # Trigger the resize callback manually, as VTK doesn't do it, presumably
    # because we aren't running an actual GUI app
    vtk_model.callback_update_position_in_window(None, None)

    new_x, new_y = vtk_model.x, vtk_model.y
    
    assert(new_x == 5)
    assert(new_y == 10)



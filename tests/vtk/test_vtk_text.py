import pytest

from sksurgeryoverlay.vtk.vtk_text import VTKText

@pytest.fixture
def vtk_model():
    text = "hello world"
    x = 10
    y = 10

    return VTKText(text, x, y)

def test_text_set_correctly(vtk_model):
    
    assert vtk_model.text_actor.GetInput() == "hello world"

def test_position_set_correctly(vtk_model):

    x,y = vtk_model.text_actor.GetPosition()

    assert x == 10
    assert y == 10

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
        vtk_model.set_text(invalid_input)

    assert vtk_model.text_actor.GetInput() == "hello world"

def test_invalid_position(vtk_model):

    with pytest.raises(TypeError):
        invalid_position = 'a'
        vtk_model.set_position(invalid_position, 1)
        vtk_model.set_position(1, invalid_position)

    x,y = vtk_model.text_actor.GetPosition()

    assert x == 10
    assert y == 10





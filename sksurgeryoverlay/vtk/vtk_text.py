#coding=utf-8
import vtk
import PySide2
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

class VTKText:
    """ VTK Text Actor """

    def __init__(self, text, x, y):
        """ Create a VTK Text actor. """

        self.text_actor = vtk.vtkTextActor()

        self.set_text(text)
        self.set_position(x,y)
        self.set_font_size(24)
        self.set_colour(1.0, 0, 0)

    def set_text(self, text):
        """ Set the text string."""
        self.validate_text_input(text)
        self.text_actor.SetInput(text)

    def set_position(self, x, y):
        """ Set the x,y coordinates of the text (bottom-left)"""
        self.validate_x_y_inputs(x, y)
        self.text_actor.SetPosition(x,y)

    def set_font_size(self, size):
        """ Set the font size."""
        self.text_actor.GetTextProperty().SetFontSize(size)

    def set_colour(self, r, g, b):
        """ Set the text colour."""
        self.text_actor.GetTextProperty().SetColor(r, g, b)

    def validate_text_input(self, text):
        """ Check text input is a valid string. """

        if isinstance(text, str):
            return True

        raise TypeError('Text input to VTKText is not a string.')

    def validate_x_y_inputs(self, x, y):
        """ Check that coordinate inputs are valid. """
        
        valid_types = (int, float)

        if not isinstance(x, valid_types):
            raise TypeError('x input to VTKText is not a valid number')

        if not isinstance(y, valid_types):
            raise TypeError('y input to VTKText is not a valid number')

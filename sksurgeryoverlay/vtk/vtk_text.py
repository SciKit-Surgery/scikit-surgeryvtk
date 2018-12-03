#coding=utf-8
import vtk
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

class VTKText:
    """ VTK Text Actor """

    def __init__(self, text, x, y, font_size=24, colour=(1.0, 0, 0)):
        """ Create a VTK Text actor. """

        self.text_actor = vtk.vtkTextActor()
        self.text_actor.SetTextScaleModeToViewport()
        
        self.set_text(text)
        self.set_position(x,y)
        self.set_font_size(font_size)


        r, g, b = colour
        self.set_colour(r, g, b)

    def calculate_relative_position_in_window(self, width, height):
        """ Calculate position relative to the size of the screen.
        Can then be used to re-set the position if the window is 
        resized. """

        self.x_relative = self.x/width
        self.y_relative = self.y/height
    
    def set_relative_position_in_window(self, width, height):
        """ Set the text position, independent of the window size.
        """
        x = self.x_relative * width
        y = self.y_relative * height

        self.set_position(x,y)

    def set_text(self, text):
        """ Set the text string."""
        self.validate_text_input(text)
        self.text_actor.SetInput(text)

    def set_position(self, x, y):
        """ Set the x,y coordinates of the text (bottom-left)"""
        if self.validate_x_y_inputs(x, y):
            self.text_actor.SetPosition(x,y)

            self.x = x
            self.y = y

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

        return True
   
#coding=utf-8
"""
Classes to implement text overlay.
Includes Corner Annotation, Large Centered Text and
generic text overlay.
"""


import logging
import vtk

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

#pylint:disable = invalid-name, no-member, attribute-defined-outside-init
#pylint:disable = no-self-use

class VTKCornerAnnotation:
    """
    Wrapper for vtkCornerAnnotaiton class.

    """

    def __init__(self):

        self.text_actor = vtk.vtkCornerAnnotation()

    def set_text(self, text_list):
        """Set the text in each of the four corners

        :param text_list: Text to display, clockwise from top-left.
        :type text_list: List of 4 strings.
        """

        self.validate_input(text_list)

        for idx, item in enumerate(text_list):
            self.text_actor.SetText(idx, item)

    def validate_input(self, text_list):
        """Check that the text_list input is a list of four strings.

        :param text_list: input to check.
        """

        if not isinstance(text_list, list):
            raise TypeError('text_list is not a list')

        if not len(text_list) == 4:
            raise ValueError('Incorrect number of elements in text_list')

        for idx, item in enumerate(text_list):
            if not isinstance(item, str):
                raise ValueError('Item at position {} not a string'.format(idx))


class VTKTextBase:
    """
    Wrapper around vtkTextActor class to set position,
    colour, size etc.
    """

    def set_text_string(self, text):
        """
        Set the text string.
        :param text: text to display."""
        self.validate_text_input(text)
        self.text_actor.SetInput(text)

    def set_text_position(self, x, y):
        """
        Set the x,y coordinates of the text (bottom-left)
        :param x: x location in pixels
        :param y: y locaiton in pixels
        """
        if self.validate_x_y_inputs(x, y):
            self.text_actor.SetPosition(x, y)

            self.x = x
            self.y = y

    def set_font_size(self, size):
        """
        Set the font size.
        :param size: size in points"""
        self.text_actor.GetTextProperty().SetFontSize(size)

    def set_colour(self, r, g, b):
        """
        Set the text colour.
        :param r: Red (0.0 - 1.0)
        :param g: Green (0.0 - 1.0)
        :param b: Blue (0.0 - 1.0)
        """
        self.text_actor.GetTextProperty().SetColor(r, g, b)

    def validate_text_input(self, text):
        """
        Check text input is a valid string.
        :param text: Input to validate. """

        if isinstance(text, str):
            return True

        raise TypeError('Text input to VTKText is not a string.')

    def validate_x_y_inputs(self, x, y):
        """
        Check that coordinate inputs are valid.
        :param x: x location.
        :param y: y location """

        valid_types = (int, float)

        if not isinstance(x, valid_types):
            raise TypeError('x input to VTKText is not a valid number')

        if not isinstance(y, valid_types):
            raise TypeError('y input to VTKText is not a valid number')

        return True


class VTKText(VTKTextBase):

    """
    VTKText object that can be placed following a left click event.
    Text will rescale if the window resizes, to try and maintain relative
    positioning.

    :param text: text to display.
    :param    x: x position (pixels)
    :param    y: y position (pixels)
    :param font_size: Font size
    param colour: Colour, RGB tuple

    """

    def __init__(self, text, x, y, font_size=24, colour=(1.0, 0, 0)):
        """ Create a VTK text actor.
        """

        self.text_actor = vtk.vtkTextActor()
        self.text_actor.SetTextScaleModeToViewport()

        self.set_text_string(text)
        self.set_text_position(x, y)
        self.set_font_size(font_size)

        r, g, b = colour
        self.set_colour(r, g, b)

    def set_parent_window(self, parent_window):
        """
        Link the object to a VTKOverlayWindow
        and set up callbacks.
        :param parent_window: VTKOverlayWindow
        """
        self.parent_window = parent_window
        self.calculate_relative_position_in_window()

        self.parent_window.AddObserver('ModifiedEvent',
                                       self.callback_update_position_in_window)

    def calculate_relative_position_in_window(self):
        """
        Calculate position relative to the middle of the screen.
        Can then be used to re-set the position if the window is
        resized.
        """

        width, height = self.parent_window.GetRenderWindow().GetSize()

        middle_x = width // 2
        middle_y = height // 2

        self.original_aspect_ratio = width/height
        self.x_relative = (self.x - middle_x) / width
        self.y_relative = (self.y - middle_y) / height

    def callback_update_position_in_window(self, _obj_unused, _ev_unused):
        """
        Update position, maintaing relative distance to the centre
        of the background image.
        """
        width, height = self.parent_window.GetRenderWindow().GetSize()

        middle_x = width // 2
        middle_y = height // 2

        current_aspect_ratio = width / height

        if current_aspect_ratio == self.original_aspect_ratio:
            x = middle_x + \
                self.x_relative * (height * self.original_aspect_ratio)
            y = middle_y + \
                self.y_relative * (width / self.original_aspect_ratio)

        else:
            # Too wide - height sets the x position
            if width > height * self.original_aspect_ratio:
                x = middle_x + \
                    self.x_relative * (height * self.original_aspect_ratio)
                y = middle_y + self.y_relative * height

            # Too tall, width sets the y position
            else:
                y = middle_y + \
                    self.y_relative * (width / self.original_aspect_ratio)
                x = middle_x + self.x_relative * width

        self.set_text_position(x, y)


class VTKLargeTextCentreOfScreen(VTKTextBase):
    """
    Display large text in the centre of the screen.
    Useful for error messages/warnings etc.

    :param text: text to display.
    """

    def __init__(self, text):

        self.text_actor = vtk.vtkTextActor()
        self.text_actor.SetTextScaleModeToProp()
        self.text_actor.GetTextProperty().SetJustificationToCentered()
        self.text_actor.GetTextProperty().SetVerticalJustificationToCentered()

        self.set_text_string(text)


    def set_parent_window(self, parent_window):
        """
        Attach text to a particular window.
        :param parent_window: VTKOverlayWindow that message will
                     be displayed in.
        """

        self.parent_window = parent_window
        self.parent_window.AddObserver('ModifiedEvent',
                                       self.calculate_text_size)
        self.calculate_text_size(None, None)



    def calculate_text_size(self, _obj_unused, _ev_unused):
        """
        Calculate the position and size of the text.
        Text should span the central half (x & y) of the window.

        """
        #pylint:disable=unused-argument

        width, height = self.parent_window.GetRenderWindow().GetSize()

        self.set_text_position(width/2, height/2)
        self.text_actor.SetMinimumSize(width, height)

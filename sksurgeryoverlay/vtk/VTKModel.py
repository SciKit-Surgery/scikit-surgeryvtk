#coding=utf-8
import vtk
import PySide2
import logging
import os

from PySide2.QtWidgets import QCheckBox
from vtk.util import colors

LOGGER = logging.getLogger(__name__)

def get_VTK_data(VTK_dir):
    """ Create VTK model objects for all .vtk files in a given dir"""
    # TODO: Might be better to put list of files to read and the desired
    # colours in an external file?
    empty_model_array = []

    try:
        files = os.listdir(VTK_dir)

    except FileNotFoundError:
        LOGGER.info("Invalid VTK directory given")
        return empty_model_array

    VTK_files = []

    valid_extensions = ('vtk', '.stl', '.ply')
    for idx, file in enumerate(files):
        if file.endswith(valid_extensions):
            VTK_files.append(file)

    if not VTK_files:
        LOGGER.info("No VTK files in given directory")
        return empty_model_array

    VTK_models = []

    colours = [colors.red, colors.blue, colors.green,
               colors.black, colors.white, colors.yellow,
               colors.brown, colors.grey, colors.purple,
               colors.pink]

    for idx, file in enumerate(VTK_files):
        LOGGER.info("Reading file %s, colour: %s", file, colours[idx])
        # Create a new VTK actor for each file, changing the colour for each
        # one
        full_path = os.path.join(VTK_dir, file)
        VTK_models.append(VTKModel(full_path, colours[idx]))

    return VTK_models


class VTKModel:
    """
    Class to read in VTK model data from a file, and store it.
    """

    def __init__(self, filename, colour):
        """Read VTK model from file and return a VTK actor"""

        self.source_file = filename
        self.visible = True

        self.read_source_file()
        self.setup_mapper()
        self.setup_actor()
        self.set_colour(colour)

        # In order to enable toggling opacity, store the desired opacity
        # separately from the actual opacity, which can be accessed
        # through GetProperty().GetOpacity()
        max_opacity = 1
        self.update_desired_opacity(max_opacity)

    def read_source_file(self):
        """ Run VTK commands to read from a .vtk file"""
        self.reader = self.get_reader_by_filetype()
        self.reader.SetFileName(self.source_file)
        self.reader.Update()
        self.output = self.reader.GetOutput()

    def get_reader_by_filetype(self):
        """Return a renderer based on input filetype"""
        if self.source_file.endswith('.vtk'):
            return vtk.vtkPolyDataReader()

        if self.source_file.endswith('.stl'):
            return vtk.vtkSTLReader()

        if self.source_file.endswith('.ply'):
            return vtk.vtkPLYReader()

        #pylint: disable=line-too-long
        raise ValueError('File type not supported for model loading: {}'.format(self.source_file))

    def setup_mapper(self):
        """Create and set a mapper"""
        self.mapper = vtk.vtkDataSetMapper()
        self.mapper.SetInputData(self.output)

    def setup_actor(self):
        """Create and setup actor"""
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)

    def set_colour(self, colour):
        """Set the colour of the model"""
        self.actor.GetProperty().SetColor(colour)

    def update_desired_opacity(self, opacity):
        """Update opacity variable, don't actually set the opacity
        if the model is currently invisble"""
        self.desired_opacity = opacity

        if self.visible:
            self.set_opacity(self.desired_opacity)

    def set_opacity(self, opacity):
        """Set the opacity"""
        self.actor.GetProperty().SetOpacity(opacity)

    def toggle_visible(self):
        """Toggle visiblity on/off"""

        # If the model is visible, set opacity to 0
        if self.visible:
            # There is a bug, which means we can't set opacity here to 0
            # See issue #24 on gitlab
            suitably_low_opacity = 0.005
            self.set_opacity(suitably_low_opacity)
            self.visible = False

        # Otherwise, it must already be invisible, restore the previous opacity
        # value
        else:
            self.set_opacity(self.desired_opacity)
            self.visible = True

    def create_qcheckbox(self):
        """"Returns a qcheckbox object for this actor"""
        # The filename is used as button text
        filename_no_path = os.path.basename(self.source_file)
        name, _ = os.path.splitext(filename_no_path)
        button_text = name.capitalize()

        checkbox = QCheckBox(button_text)
        checkbox.setStyleSheet("QCheckBox {font: 12pt}")

        checkbox.setChecked(True)

        return checkbox

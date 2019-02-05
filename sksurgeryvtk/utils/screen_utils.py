# coding=utf-8
""" Any useful utilities relating to displays/screens. """
#pylint:disable=no-name-in-module

import logging
from PySide2.QtGui import QGuiApplication

LOGGER = logging.getLogger(__name__)

#pylint: disable=useless-object-inheritance


class ScreenController(object):
    """ This class detects the connected screens/monitors, and
    returns the primary screen and a list of any secondary screens.
    """

    def __init__(self):
        self.screens = QGuiApplication.screens()
        self.primary = QGuiApplication.primaryScreen()

        if self.primary in self.screens:
            self.screens.remove(self.primary)

    def list_of_screens(self):  # pylint: disable=no-self-use
        """Return the primary screen and list of other available screens"""

        return self.primary, self.screens

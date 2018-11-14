import pytest
from PySide2.QtWidgets import QApplication

@pytest.fixture(scope="session")
def setup_qt():
    """ Create the QT appliation"""
    app = QApplication([])

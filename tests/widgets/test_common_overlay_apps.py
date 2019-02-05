# -*- coding: utf-8 -*-
import pytest
import sksurgeryvtk.widgets.common_overlay_apps as coa

def test_OverlayOnVideoFeed(setup_qt):
    """
    Test will only run if there is a camera avilable.
    """
    try:
        overlay_app = coa.OverlayOnVideoFeed(0)
        overlay_app.add_vtk_models_from_dir('tests/data/models/Liver')
        overlay_app.start()
        overlay_app.update()
        overlay_app.stop()

    except IndexError:
        # No cameras availble
        return

def test_OverlayBaseAppRaisesNotImplementedError(setup_qt):
    """
    Test will only run if there is a camera avilable
    """
    class ErrorApp(coa.OverlayBaseApp):

        def something(self):
            pass

    with pytest.raises(NotImplementedError):
        overlay_app = ErrorApp(0)
        overlay_app.update()


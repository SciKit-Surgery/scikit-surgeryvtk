# -*- coding: utf-8 -*-

"""
Any useful little utilities to do with what platform we are on.
"""

import os
import platform


def validate_can_run():
    """
    Returns False if CI_PROJECT_DIR exists and platform is Windows, and
    True otherwise.
    """
    if 'CI_PROJECT_DIR' in os.environ and platform.system() == 'Windows':
        return True

    return True

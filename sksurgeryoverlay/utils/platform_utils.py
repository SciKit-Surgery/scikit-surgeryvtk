# -*- coding: utf-8 -*-

import os
import platform


def validate_can_run_on_this_platform():

    if 'CI_PROJECT_DIR' in os.environ and platform.system() == 'Windows':
        return False
    else:
        return True


# coding=utf-8

"""scikit-surgeryoverlay tests"""

from sksurgeryoverlay.ui.sksurgeryoverlay_demo import run_demo

# Unittest style test case
from unittest import TestCase

class Testsksurgeryoverlay(TestCase):
    def test_using_unittest_sksurgeryoverlay(self):
        return_value = run_demo(True, "Hello world")
        self.assertTrue(return_value)


# Pytest style

def test_using_pytest_sksurgeryoverlay():
    assert run_demo(True, "Hello World") == True


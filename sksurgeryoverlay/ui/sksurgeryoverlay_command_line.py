# coding=utf-8

"""Command line processing"""


import argparse
from sksurgeryoverlay import __version__
from sksurgeryoverlay.ui.sksurgeryoverlay_demo import run_demo


def main(args=None):
    """Entry point for scikit-surgeryoverlay application"""

    parser = argparse.ArgumentParser(description='scikit-surgeryoverlay')

    parser.add_argument("-t", "--text",
                        required=False,
                        default="This is scikit-surgeryoverlay",
                        type=str,
                        help="Text to display")

    parser.add_argument("--console", required=False,
                        action='store_true',
                        help="If set, scikit-surgeryoverlay "
                             "will not bring up a graphical user interface")

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='scikit-surgeryoverlay version ' + friendly_version_string)

    args = parser.parse_args(args)

    run_demo(args.console, args.text)

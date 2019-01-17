# coding=utf-8

"""Command line processing"""

import argparse
from sksurgeryvtk import __version__
from sksurgeryvtk.ui.sksurgeryrendermodelslikecamera_demo import run_demo


def main(args=None):
    """Entry point for rendermodelslikecamera application"""

    default_camera_interval = 33
    default_screen_interval = 15

    parser = argparse.ArgumentParser(description='scikit-surgeryrendermodelslikecamera')

    parser.add_argument("-x", "--x_size",
                        required=False,
                        default=640,
                        type=int,
                        help="Image width")

    parser.add_argument("-y", "--y_size",
                        required=False,
                        default=480,
                        type=int,
                        help="Image height")

    parser.add_argument("-f", "--image_file",
                        required=False,
                        default=None,
                        type=str,
                        help="Background image")

    parser.add_argument("-m", "--models",
                        required=False,
                        default=None,
                        type=str,
                        help='Models Directory')

    parser.add_argument("-e", "--extrinsic_matrix",
                        required=False,
                        default=None,
                        type=str,
                        help="extrinsic matrix file")

    parser.add_argument("-i", "--intrinsic_matrix",
                        required=False,
                        default=None,
                        type=str,
                        help="intrinsic matrix file")

    parser.add_argument("-p", "--points_file",
                        required=False,
                        default=None,
                        type=str,
                        help="File of points to render")

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='scikit-surgeryvtk version ' + friendly_version_string)

    args = parser.parse_args(args)

    run_demo(   args.image_file,
                args.x_size,
                args.y_size,
                args.models,
                args.extrinsic_matrix,
                args.intrinsic_matrix,
                args.points_file)

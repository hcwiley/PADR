from math import floor
import shutil
from PIL import Image
import numpy as np
import os
import sys
import argparse

import imageUtils
py_arg = argparse.ArgumentParser()

py_arg.add_argument('--image')
py_arg.add_argument('--width', default='640')
py_arg.add_argument('--height', default='640')
py_arg.add_argument('--resize_width', default=None)
py_arg.add_argument('--resize_height', default=None)
py_arg.add_argument('--x_splits', default='2')
py_arg.add_argument('--y_splits', default='2')
py_arg.add_argument('--crop_size', default=None)
py_arg.add_argument('--random_seed', default=42)
py_arg.add_argument('--border', default=0.05)
py_arg.add_argument('--input_dir')
py_arg.add_argument('--output_dir', default=None)
py_arg.add_argument('--clear_output', default=False)

args = py_arg.parse_args()


def main():
  # scale and crop the image / images in the input directory
  if 'image' in args:
    print("loading image: {}".format(args.image))


if __name__ == '__main__':
  if 'help' in args:
    py_arg.print_help()

  for arg in vars(args):
    print('{}: {}'.format(arg, getattr(args, arg)))

  print('main show')
  main()

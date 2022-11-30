from math import floor
import glob
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
py_arg.add_argument('--x', default='0')
py_arg.add_argument('--y', default='0')
py_arg.add_argument('--resize_width', default=None)
py_arg.add_argument('--resize_height', default=None)
py_arg.add_argument('--input_dir')
py_arg.add_argument('--output_dir', default=None)
py_arg.add_argument('--clear_output', default=False)
py_arg.add_argument('--overwrite', default=False, action='store_true')

args = py_arg.parse_args()


def main():

  # FIXME: DRY this code out. copy/paste from imageBatchSlicer.py

  # get the input and output directories
  input_dir = args.input_dir
  output_dir = args.output_dir

  # check if we are saving inplace
  if output_dir is None:
    output_dir = input_dir
  else:
    # check if we are clearing the output directory
    if args.clear_output and output_dir != input_dir:
      # clean use shutil.rmtree
      shutil.rmtree(output_dir, ignore_errors=True)
    # make sure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

  # get the width and height of the desired output image
  crop_width = int(args.width)
  crop_height = int(args.height)
  x = int(args.x)
  y = int(args.y)

  # get the images with a variety of extensions
  extensions = ["jpg", "jpeg", "png", "tif", "tiff"]
  img_paths = []
  for ext in extensions:
    ext_imgs = glob.glob('{}/*.{}'.format(input_dir, ext))
    img_paths.extend(ext_imgs)

  if args.image is not None:
    img_paths.append(args.image)

  # loop over the images
  for img_path in img_paths:
    img_no_ext = os.path.splitext(os.path.basename(img_path))[0]

    # load the image
    img = Image.open(img_path, 'r')

    # make sure it's RGB
    img = imageUtils.convertToRGB(img)

    # check if we need to resize the image
    resize_width = None
    resize_height = None
    if args.resize_width is not None:
      resize_width = int(args.resize_width)
    if args.resize_height is not None:
      resize_height = int(args.resize_height)

    if resize_width is not None or resize_height is not None:
      # if either is None, use the other dimension to calculate the new size
      if resize_width is None:
        resize_width = int(floor(img.width * resize_height / img.height))
      if resize_height is None:
        resize_height = int(floor(img.height * resize_width / img.width))

      # resize the image PIL
      img = img.resize((resize_width, resize_height), Image.ANTIALIAS)

    # ok image has been resized, now crop it

    # crop the image
    crop = imageUtils.cropImage(img, x, y, crop_width, crop_height)

    # construct the path to the output image
    out_path = ""
    if args.overwrite:
      out_path = img_path
    else:
      out_path = os.path.join(output_dir, '{}_{}-{}_{}-{}.jpg'.format(
          img_no_ext, x, y, x+crop_width, y+crop_height))

    # write the cropped image to disk
    crop.save(out_path)


if __name__ == '__main__':
  if 'help' in args:
    py_arg.print_help()

  for arg in vars(args):
    print('{}: {}'.format(arg, getattr(args, arg)))

  print('main show')
  main()

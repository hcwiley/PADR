from math import floor
import glob
import shutil
from PIL import Image
import numpy as np
import os
import sys
import argparse
import cv2

import imageUtils

py_arg = argparse.ArgumentParser()

py_arg.add_argument('--width', default=None)
py_arg.add_argument('--height', default=None)
py_arg.add_argument('--resize_width', default=None)
py_arg.add_argument('--resize_height', default=None)
py_arg.add_argument('--x_splits', default='2')
py_arg.add_argument('--y_splits', default='2')
py_arg.add_argument('--crop_size', default=None)
py_arg.add_argument('--input_dir')
py_arg.add_argument('--output_dir', default=None)
py_arg.add_argument('--clear_output', default=False)

args = py_arg.parse_args()


def getImageCords(img_path):
  img_no_ext = os.path.splitext(os.path.basename(img_path))[0]

  # pull the x y cords from the file name
  # '{}_{}-{}_{}-{}'.format(img_no_ext, x, y, x+crop_width, y+crop_height)
  orig_name, xy0, xy1 = img_no_ext.split('_')
  x0, y0 = xy0.split('-')
  x1, y1 = xy1.split('-')
  x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)

  return x0, y0, x1, y1


def main():
  # do something crazy
  print('main')

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
  width = height = 0
  if args.width is not None:
    width = int(args.width)
  if args.height is not None:
    height = int(args.height)

  # get the images with a variety of extensions
  extensions = ["jpg", "jpeg", "png", "tif", "tiff"]
  img_paths = []
  maxX = 0
  maxY = 0
  for ext in extensions:
    ext_imgs = glob.glob('{}/*.{}'.format(input_dir, ext))
    img_paths.extend(ext_imgs)

  # check if width and height are not set
  if width == 0 and height == 0:
    for img_path in img_paths:
      x0, y0, x1, y1 = getImageCords(img_path)
      if maxX < x1:
        maxX = x1
      if maxY < y1:
        maxY = y1

    width = maxX
    height = maxY

  full_img_path = '{}/full.jpg'.format(output_dir)
  print("compiling a full image of size {}x{} to {}".format(
      width, height, full_img_path))

  # make the full image the size of the width and height
  # a blank cv2 mat filled to white with the size of the width and height
  full_img = np.zeros((height, width, 3), np.uint8)
  # full_img[:] = (255, 255, 255)

  # loop over the images
  for img_path in img_paths:
    x0, y0, x1, y1 = getImageCords(img_path)

    # open the image
    img = cv2.imread(img_path)

    # write the img to the full image
    full_img[y0:y1, x0:x1] = img

  # save the full image
  cv2.imwrite(full_img_path, full_img)


if __name__ == '__main__':
  if 'help' in args:
    py_arg.print_help()

  for arg in vars(args):
    print('{}: {}'.format(arg, getattr(args, arg)))

  print('main show')
  main()

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
py_arg.add_argument('--crop_size', default=None)
py_arg.add_argument('--resize', default=0)
py_arg.add_argument('--x_splits', default=2)
py_arg.add_argument('--y_splits', default=2)
py_arg.add_argument('--input_dir')
py_arg.add_argument('--output_dir', default=None)
py_arg.add_argument('--output_name', default=None)
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

  resize = int(args.resize)
  x_splits = int(args.x_splits)
  y_splits = int(args.y_splits)

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

  # check if we are scaling the dst coords
  x_scale = 1
  y_scale = 1
  if resize != 0:
    # (512/(900/3))*900
    x_scale = (resize / (width / x_splits))
    y_scale = (resize / (height / y_splits))
    width *= x_scale
    height *= y_scale

  # ensure ints
  width = int(width)
  height = int(height)


  img_name = "full"
  if args.output_name is not None:
    img_name = args.output_name

  full_img_path = '{}/{}.jpg'.format(output_dir,img_name)
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

    # check if we are scaling the dst coords
    if resize != 0:
      x0 *= x_scale
      y0 *= y_scale
      x1 *= x_scale
      y1 *= y_scale

    # ensure ints for all the units
    x0 = int(x0)
    y0 = int(y0)
    x1 = int(x1)
    y1 = int(y1)

    dst_width = x1 - x0
    dst_height = y1 - y0

    # print('x0: {}, y0: {}, x1: {}, y1: {}, dst_width: {}, dst_height: {}'
    #       .format(
    #           x0, y0, x1, y1, dst_width, dst_height))

    if img.shape[0] != dst_height or img.shape[1] != dst_width:
      img = cv2.resize(img, (dst_width, dst_height))

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

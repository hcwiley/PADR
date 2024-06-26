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

py_arg.add_argument('--width', default='640')
py_arg.add_argument('--height', default='640')
py_arg.add_argument('--resize_width', default=None)
py_arg.add_argument('--resize_height', default=None)
py_arg.add_argument('--x_splits', default='2')
py_arg.add_argument('--y_splits', default='2')
py_arg.add_argument('--crop_size', default="-1")
py_arg.add_argument('--random_seed', default=42)
py_arg.add_argument('--border', default=0.05)
py_arg.add_argument('--input_dir', default=None)
py_arg.add_argument('--input_image', default=None)
py_arg.add_argument('--output_dir', default=None)
py_arg.add_argument('--clear_output', default=False)

args = py_arg.parse_args()

Image.MAX_IMAGE_PIXELS = None


def main():
  # the main function

  if args.input_dir is None and args.input_image is None:
    print("Please specify an input directory or image")
    sys.exit(1)

  img_paths = []
  input_dir = None
  if args.input_image is not None:
    img_paths.append(args.input_image)
    os.path.abspath(os.path.dirname(img_paths[0]))
  else:
    # get the input and output directories
    input_dir = args.input_dir
    # get the images with a variety of extensions
    extensions = ["jpg", "jpeg", "png", "tif", "tiff"]
    img_paths = []
    for ext in extensions:
      ext_imgs = glob.glob('{}/*.{}'.format(input_dir, ext))
      img_paths.extend(ext_imgs)

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
  width = int(args.width)
  height = int(args.height)

  # get the number of splits
  # check for auto first
  if args.x_splits == 'auto':
    # need to get the y_splits
    x_splits = 'auto'
  else:
    x_splits = int(args.x_splits)
  if args.y_splits == 'auto':
    y_splits = 'auto'
  else:
    y_splits = int(args.y_splits)

  # check if crop_size is set
  crop_size = None
  if int(args.crop_size) > 0:
    crop_size = int(args.crop_size)

  # loop over the images
  for img_path in img_paths:

    img_no_ext = os.path.splitext(os.path.basename(img_path))[0]

    # load the image
    img = Image.open(img_path, 'r')

    # check if either x_splits or y_splits is auto
    if x_splits == 'auto':
      # get the y_splits resulting y height per square and match the x_splits
      # first determine the resulting height per square
      y_height = int(floor(img.height / y_splits))
      # calculate the x_splits based on the y_height to get the closest to a square
      x_splits = (img.width / y_height)
      # if x_splits is a float pad the image left and right to make it an int
      if x_splits % 1 != 0:
        # calculate the padding needed
        padding = int(floor((x_splits % 1) * y_height))
        print('padding: {}'.format(padding))
        # resize image to be the new width
        img.crop((padding, 0, img.width + padding, img.height))
        x_splits = int(x_splits) + 1
    elif y_splits == 'auto':
      # get the x_splits resulting x width per square and match the y_splits
      # first determine the resulting width per square
      x_width = int(floor(img.width / x_splits))
      # calculate the y_splits based on the x_width to get the closest to a square
      y_splits = (img.height / x_width)
      # if y_splits is a float pad the image top and bottom to make it an int
      if y_splits % 1 != 0:
        # calculate the padding needed
        padding = int(floor((y_splits % 1) * x_width))
        print('padding: {}'.format(padding))
        # resize image to be the new width
        img.crop((0, padding, img.width, img.height + padding))
        y_splits = int(y_splits) + 1

    # ensure x_splits and y_splits are ints
    x_splits = int(x_splits)
    y_splits = int(y_splits)

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

    # check if we need to crop the border out
    if args.border is not None:
      border = float(args.border)
      border_right = int(floor(img.width * border))
      border_top = int(floor(img.height * border))
      border_left = img.width - border_right
      border_bottom = img.height - border_top
      border_rect = (border_right, border_top, border_left, border_bottom)
      print('border_rect: {}'.format(border_rect))
      img = img.crop(border_rect)

    # get the dimensions of the image
    img_width = img.width
    img_height = img.height

    # iterate over the splits
    for i_x in range(x_splits):
      for i_y in range(y_splits):
        crop_height = 0
        crop_width = 0

        # determine the crop height and width
        if crop_size is not None:
          crop_height = crop_size
          crop_width = crop_size
        else:
          # compute the width and height of the crop
          crop_width = int(img_width / x_splits)
          crop_height = int(img_height / y_splits)

        # calculate the x,y start coordinates by determining the percent i_x and i_x are into their total split
        x = int(floor((float(i_x) / float(x_splits)) * float(img_width)))
        y = int(floor((float(i_y) / float(y_splits)) * float(img_height)))

        # now add/subtract the random_seed
        random_seed = int(args.random_seed)
        if random_seed > 0:
          x += np.random.randint(-random_seed, random_seed)
          y += np.random.randint(-random_seed, random_seed)

        # clip to make sure we don't go out of bounds
        x = np.clip(x, 0, img_width - crop_width)
        y = np.clip(y, 0, img_height - crop_height)

        # print all the params to cropImage to make sure we're good
        print('{} x: {}, y: {}, width: {}, height: {}'.format(img_no_ext,
                                                              x, y, crop_width, crop_height))

        # crop the image
        crop = imageUtils.cropImage(img, x, y, crop_width, crop_height)

        # construct the path to the output image
        p = os.path.join(output_dir, '{}_{}-{}_{}-{}.jpg'.format(
            img_no_ext, x, y, x+crop_width, y+crop_height))

        # write the cropped image to disk
        crop.save(p)


if __name__ == '__main__':
  if 'help' in args:
    py_arg.print_help()

  for arg in vars(args):
    print('{}: {}'.format(arg, getattr(args, arg)))

  print('main show')
  main()

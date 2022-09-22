from email.policy import default
from math import floor
import shutil
from PIL import Image
import numpy as np
import os
import sys
# append a path to the system path
my_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(my_dir, '../../CycleGAN-Tensorflow-2'))

import pylib as py  # nopep8
import imlib as im  # nopep8


# ==============================================================================
# =                                   param                                    =
# ==============================================================================

py.arg('--width', default='640')
py.arg('--height', default='640')
py.arg('--resize_width', default=None)
py.arg('--resize_height', default=None)
py.arg('--x_splits', default='2')
py.arg('--y_splits', default='2')
py.arg('--crop_size', default=None)
py.arg('--random_seed', default=42)
py.arg('--border', default=0.05)
py.arg('--input_dir')
py.arg('--output_dir', default=None)
py.arg('--clear_output', default=False)

args = py.args()

# helper to check if var is a percent or int


def convertPercentToPixel(var, dimension):
  # first check to see if var is float or int
  if isinstance(var, float):
    # if float, check if it's between 0 and 1
    if var < 1.0 and var > 0.0:
      # the x should be converted to pixel space
      var = int(floor(var * dimension))
  # ok, var is now good either way
  return int(var)

# function to crop a specific region of an image given the desired width, height, and x, y coordinates


def cropImage(img, orig_x, orig_y, width, height):

  # fix and x and y incase they are percentages
  img_width = img.width
  img_height = img.height
  x = convertPercentToPixel(orig_x, img_width)
  y = convertPercentToPixel(orig_y, img_height)

  # crop the image
  return img.crop((x, y, x + width, y + height))

# the main function


def main():
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
    py.mkdir(output_dir)

  # get the width and height of the desired output image
  width = int(args.width)
  height = int(args.height)

  # get the number of splits
  x_splits = int(args.x_splits)
  y_splits = int(args.y_splits)

  # check if crop_size is set
  crop_size = None
  if args.crop_size is not None:
    crop_size = int(args.crop_size)

  # get the images with a variety of extensions
  extensions = ["jpg", "jpeg", "png", "tif", "tiff"]
  img_paths = []
  for ext in extensions:
    ext_imgs = py.glob(input_dir, '*.{}'.format(ext))
    img_paths.extend(ext_imgs)

  # loop over the images
  for img_path in img_paths:

    img_no_ext = os.path.splitext(os.path.basename(img_path))[0]

    # load the image
    img = Image.open(img_path, 'r')
    # check if it's RGBA
    if img.mode in ('RGBA', 'LA'):
      # convert the transparency to white
      fill_color = (255, 255, 255)
      background = Image.new(img.mode[:-1], img.size, fill_color)
      background.paste(img, img.split()[-1])  # omit transparency
      img = background

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
      border_x = int(floor(img.width * border))
      border_y = int(floor(img.height * border))
      img = img.crop((border_x, border_y, img.width -
                     border_x, img.height - border_y))

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
        x += np.random.randint(-args.random_seed, args.random_seed)
        y += np.random.randint(-args.random_seed, args.random_seed)

        # clip to make sure we don't go out of bounds
        x = np.clip(x, 0, img_width - crop_width)
        y = np.clip(y, 0, img_height - crop_height)

        # print all the params to cropImage to make sure we're good
        print('{} x: {}, y: {}, width: {}, height: {}'.format(img_no_ext,
                                                              x, y, crop_width, crop_height))

        # crop the image
        crop = cropImage(img, x, y, crop_width, crop_height)

        # construct the path to the output image
        p = py.join(output_dir, '{}_{}-{}_{}-{}.jpg'.format(
            img_no_ext, x, y, x+crop_width, y+crop_height))

        # write the cropped image to disk
        crop.save(p)


if __name__ == '__main__':
  main()

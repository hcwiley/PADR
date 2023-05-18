import re
import os
import glob
import cv2
import numpy as np
import argparse
import sys

import imageUtils

# append the linedraw module to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'linedraw'))
# autopep8 don't move this line
import linedraw  # noqa: E402

py_arg = argparse.ArgumentParser()

py_arg.add_argument('--image')
py_arg.add_argument('--input_dir')
py_arg.add_argument('--save_debug', default=False)
py_arg.add_argument('--output', default=None)
py_arg.add_argument('--thresh', default=175)

args = py_arg.parse_args()

input_image = args.image
input_dir = args.input_dir
save_debug = args.save_debug


def main(image_path):
  output_path = args.output if args.output is not None else image_path
  output_dir = None

  # check if output path is a directory
  if os.path.isdir(output_path):
    output_dir = output_path
    # make sure the output directory exists
    os.makedirs(output_path, exist_ok=True)
    output_path = os.path.join(output_path, os.path.basename(image_path))
  else:
    # set the output_dir to the parent directory
    output_dir = os.path.dirname(output_path)

  # make sure output path is an SVG
  if not output_path.endswith('.svg'):
    # use regex to make sure the last . to end of line is replaced
    output_path = re.sub(r'\.[^.]*$', '.svg', output_path)

  img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

  # apply a sharpening filter
  # img = imageUtils.sharpenImg(img)
  # if save_debug:
  #   cv2.imwrite(output_path+'.sharpened.png', img)

  # convert img to grey
  img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  # get threshold image
  ret, thresh_img = cv2.threshold(
      img_grey, int(args.thresh), 255, cv2.THRESH_BINARY)

  # save the debug image
  if save_debug:
    cv2.imwrite(output_path+'.threshed.png', thresh_img)

  # run a dilate and erode to fill in the gaps
  thresh_img = imageUtils.erodeAndDilate(thresh_img, 5, 3)
  if save_debug:
    cv2.imwrite(output_path+'.erode-dilate.png', thresh_img)

  output_raster_path = output_path+'.png'
  cv2.imwrite(output_raster_path, thresh_img)

  # find contours
  linedraw.draw_contours = True
  linedraw.draw_hatch = False
  linedraw.export_path = output_path
  contours = linedraw.sketch(output_raster_path)

  if not save_debug:
    os.remove(output_raster_path)


if __name__ == '__main__':
  if 'help' in args:
    py_arg.print_help()

  for arg in vars(args):
    print('{}: {}'.format(arg, getattr(args, arg)))

  # get the images with a variety of extensions
  extensions = ["jpg", "jpeg", "png", "tif", "tiff"]
  img_paths = []

  # set input path to image path or input_dir if input_image is None and input_dir is not None
  if input_image is not None:
    img_paths.append(input_image)
  elif input_dir is not None:
    for ext in extensions:
      ext_imgs = glob.glob('{}/*.{}'.format(input_dir, ext))
      img_paths.extend(ext_imgs)
  else:
    print('no input path specified')
    py_arg.print_help()
    sys.exit(1)

  # loop over the images
  for img_path in img_paths:
    main(img_path)

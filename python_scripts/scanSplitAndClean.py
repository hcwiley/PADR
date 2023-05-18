from math import floor
import glob
import shutil
# from PIL import Image
import numpy as np
import cv2
import os
import sys
import argparse

import imageUtils

py_arg = argparse.ArgumentParser()

py_arg.add_argument('--width', default='640')
py_arg.add_argument('--height', default='640')
py_arg.add_argument('--resize_width', default=None)
py_arg.add_argument('--resize_height', default=None)
py_arg.add_argument('--x_split', default=None)
py_arg.add_argument('--y_split', default=None)
py_arg.add_argument('--crop_size', default=None)
py_arg.add_argument('--random_seed', default=42)
py_arg.add_argument('--border', default=0.05)
py_arg.add_argument('--input_dir', default=None)
py_arg.add_argument('--input_image', default=None)
py_arg.add_argument('--output_dir', default=None)
py_arg.add_argument('--clear_output', default=False)

args = py_arg.parse_args()

# function to detect black regions below a thresh hold and crop the image down to the area that does not include that region
def cropBlackRegion(image, thresh=35):
  # use opencv to do a threshold drop where everything below thresh is black
  # make a grayscale image
  image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  # make the mask
  mask = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY)
  # get the contours
  contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  # get the bounding box
  x, y, w, h = cv2.boundingRect(contours[0])
  # crop the image
  image = image[y:y + h, x:x + w]
  # return the image
  return image


def main():
  # the main function
  
  # get the input and output directories
  input_dir = args.input_dir
  output_dir = args.output_dir

  # get the images with a variety of extensions
  extensions = ["jpg", "jpeg", "png", "tif", "tiff"]
  img_paths = []
  for ext in extensions:
    if input_dir is not None:
      ext_imgs = glob.glob('{}/*.{}'.format(input_dir, ext))
      img_paths.extend(ext_imgs)

  if args.input_image is not None:
    img_paths.append(args.input_image)

  # check if we are saving inplace
  if output_dir is None:
    # set the default to the first img_path parent directory
    output_dir = os.path.dirname(img_paths[0])
  else:
    # check if we are clearing the output directory
    if args.clear_output and output_dir != input_dir:
      # clean use shutil.rmtree
      shutil.rmtree(output_dir, ignore_errors=True)
    # make sure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

  # loop over the images
  for img_path in img_paths:

    img_no_ext = os.path.splitext(os.path.basename(img_path))[0]

    # load the image using opencv
    img = cv2.imread(img_path)
    
    # detect the black region and crop it out
    # print('crop {} to remove black regions'.format(img_path))
    # TODO: debug and fix this function
    # cropped = cropBlackRegion(img)

    img_splits = []

    # check for y splits
    if args.y_split is not None:
      y_split = args.y_split.split(',')
      # parse the string into a list of ints
      y_split = [int(i) for i in y_split]
      # split the image
      print('split {} into {}'.format(img_path, y_split))
      # split the image by creating a roi from 0 to x_split[0] and x_split[1] to image width
      s = 0
      for split in y_split:
        start_y = 0
        end_y = split
        if s == 0:
          start_y = 0
          end_y = split
        elif s == len(y_split) - 1:
          end_y = img.shape[0]
          start_y = split
          # -1 at the end means don't save the last split
          if split == -1:
            break
        else:
          start_y = y_split[s - 1]
        s += 1
        roi = img[start_y:end_y, 0:img.shape[1]]
        img_splits.append(roi)

      
    # repeat with the x splits
    if args.x_split is not None:
      x_split = args.x_split.split(',')
      # parse the string into a list of ints
      x_split = [int(i) for i in x_split]
      # split the image
      print('split {} into {}'.format(img_path, x_split))
      # split the image by creating a roi from 0 to x_split[0] and x_split[1] to image width
      s = 0
      for split in x_split:
        start_x = 0
        end_x = split
        if s == 0:
          start_x = 0
          end_x = split
        elif s == len(x_split) - 1:
          end_x = img.shape[1]
          start_x = split
          # -1 at the end means don't save the last split
          if split == -1:
            break
        else:
          start_x = x_split[s - 1]
        s += 1
        roi = img[0:img.shape[0], start_x:end_x]
        img_splits.append(roi)
      
  
    # loop over the splits
    i = 0
    for img_split in img_splits:
      # construct the path to the output image
      p = os.path.join(output_dir, '{}_{}.jpg'.format(img_no_ext, i))
      # write the split image to disk
      cv2.imwrite(p, img_split)
      i += 1


if __name__ == '__main__':
  if 'help' in args:
    py_arg.print_help()

  for arg in vars(args):
    print('{}: {}'.format(arg, getattr(args, arg)))

  print('main show')
  main()

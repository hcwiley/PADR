import re
import os
import cv2
import numpy as np
import argparse
import sys

import imageUtils

# append the linedraw module to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'linedraw'))

import linedraw

py_arg = argparse.ArgumentParser()

py_arg.add_argument('--image')
# get the output path
py_arg.add_argument('--output', default=None)
py_arg.add_argument('--thresh', default=175)

args = py_arg.parse_args()

image_path = args.image
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
img = imageUtils.sharpenImg(img)
cv2.imwrite(output_path+'.sharpened.png', img)

# convert img to grey
img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# get threshold image
ret, thresh_img = cv2.threshold(img_grey, args.thresh, 255, cv2.THRESH_BINARY)

# save the debug image
cv2.imwrite(output_path+'.threshed.png', thresh_img)

# run a dilate and erode to fill in the gaps
thresh_img = imageUtils.erodeAndDilate(thresh_img, 5, 3)
cv2.imwrite(output_path+'.erode-dilate.png', thresh_img)

output_raster_path = output_path+'.png'
cv2.imwrite(output_raster_path, thresh_img)

# find contours
linedraw.draw_contours = True
linedraw.draw_hatch = False
linedraw.export_path = output_path
contours = linedraw.sketch(output_raster_path)

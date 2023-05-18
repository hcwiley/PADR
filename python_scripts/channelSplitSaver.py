#!/bin/python

# python script using opencv to take an input image from the comamand line and split it into 768 frames where the first 256 frames are the red channel, the next 256 frames are the green channel, and the last 256 frames are the blue channel. The frames are then saved as .jpg files in the current directory.
import cv2
import sys
import numpy as np
import os

# get the input image from the command line
input_image = sys.argv[1]

# read the input image
img = cv2.imread(input_image)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# split the image into the red, green, and blue channels
b, g, r = cv2.split(img)

# create a list of the red, green, and blue channels
channels = [r, g, b]

# iterate through the channels
for i, channel in enumerate(channels):
  channel_name = 'red'
  if i == 1:
    channel_name = 'green'
  elif i == 2:
    channel_name = 'blue'

  cv2.imwrite('output/image-{}.jpg'.format(channel_name), channel)
  
  output_dir = 'output/{}'.format(channel_name)
  # make sure the output directory exists
  os.makedirs(output_dir, exist_ok=True)

  # iterate over all the mask values
  for j in range(255):
    # mask the channel with the current mask value
    lower_red = np.array([0])
    red_upper = 0
    blue_upper = 0
    green_upper = 0
    if i == 0:
      red_upper = j
    elif i == 1:
      green_upper = j
    elif i == 2:
      blue_upper = j

    upper_red = np.array([j])
    
    mask = cv2.inRange(channel, lower_red, upper_red)
    # new_img = np.where(channel == j, 255, 0)
    new_img = cv2.bitwise_and(channel, channel, mask= mask)
    # save the image as a .jpg file with a 4 zero padded number
    cv2.imwrite('{}/image{:04d}.jpg'.format(output_dir, i * 256 + j), new_img)
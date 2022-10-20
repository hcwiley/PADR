import cv2
import numpy as np
import scipy


def gaussianBlur(img, kernel_size=3):
  # blur the image
  return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)


def sharpenImg(img, kernel_size=5):
  kernel = np.array([[0, -1, 0],
                     [-1, kernel_size, -1],
                     [0, -1, 0]])

  return cv2.filter2D(src=img, ddepth=-1, kernel=kernel)
  # # sharpen the image
  # kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
  # return cv2.filter2D(img, -1, kernel)


def erodeAndDilate(img, kernel_size=3, iterations=1):
  # erode and dilate the image
  kernel = np.ones((kernel_size, kernel_size), np.uint8)
  return cv2.dilate(cv2.erode(img, kernel, iterations=1), kernel, iterations=1)


def smoothContours(contours):
  # pulled from here: https://gist.github.com/shubhamwagh/b8148e65a8850a974efd37107ce3f2ec

  smoothened = []
  countor_idx = 0
  for contour in contours:
    x, y = contour.T
    # Convert from numpy arrays to normal arrays
    x = x.tolist()[0]
    y = y.tolist()[0]
    # check and make sure x and y are > 3
    if len(x) > 3 and len(y) > 3:
      try:
        # https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.interpolate.splprep.html
        tck, u = scipy.interpolate.splprep([x, y], u=None, s=1.0, per=1)
        # https://docs.scipy.org/doc/numpy-1.10.1/reference/generated/numpy.linspace.html
        u_new = np.linspace(u.min(), u.max(), 25)
        # https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.interpolate.splev.html
        x_new, y_new = scipy.interpolate.splev(u_new, tck, der=0)
        # Convert it back to numpy format for opencv to be able to display it
        res_array = [[[int(i[0]), int(i[1])]] for i in zip(x_new, y_new)]
        smoothened.append(np.asarray(res_array, dtype=np.int32))
      except:
        print('error smoothing contour {}/{}'.format(countor_idx, len(contours)))
        smoothened.append(contour)
    else:
      # we cannot smooth a line of <=3 points, so just add it
      smoothened.append(contour)
    countor_idx += 1
  return smoothened


def convertPercentToPixel(var, dimension):
  # helper to check if var is a percent or int
  # first check to see if var is float or int
  if isinstance(var, float):
    # if float, check if it's between 0 and 1
    if var < 1.0 and var > 0.0:
      # the x should be converted to pixel space
      var = int(floor(var * dimension))
  # ok, var is now good either way
  return int(var)


def cropImage(img, orig_x, orig_y, width, height):
  # function to crop a specific region of an image given the desired width, height, and x, y coordinates

  # fix and x and y incase they are percentages
  img_width = img.width
  img_height = img.height
  x = convertPercentToPixel(orig_x, img_width)
  y = convertPercentToPixel(orig_y, img_height)

  # crop the image
  return img.crop((x, y, x + width, y + height))


def scaleImage(img, width, height):
  # resize the image PIL
  return img.resize((width, height), Image.ANTIALIAS)


def cropAndScale(img, width, height, mode):
  # get the original dimensions of the image
  init_width = img.width
  init_height = img.height

  scale_width = width
  scale_height = height

  # check if mode is cover or contain
  if mode == 'cover':
    # image is clipped to fit into the crop size after scaling
    if init_width >= init_height:
      # landscape
      scale_height = int(floor(init_height * (width / init_width)))
    else:
      # portrait
      scale_width = int(floor(init_width * (height / init_height)))

  # scale the image
  img = scaleImage(img, scale_width, scale_height)
  # crop the image
  img = cropImage(img, 0, 0, width, height)


def convertToRGB(img):
  # check if it's RGBA
  if img.mode in ('RGBA', 'LA'):
    # convert the transparency to white
    fill_color = (255, 255, 255)
    background = Image.new(img.mode[:-1], img.size, fill_color)
    background.paste(img, img.split()[-1])  # omit transparency
    img = background

  # TODO: handle other modes, i.e. grayscale?

  return img

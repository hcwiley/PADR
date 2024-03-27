import os
from PIL import Image

def get_divisible_squares(image_path):
  # Open the image
  image = Image.open(image_path)

  # Get the width and height of the image
  width, height = image.size
  has_divisible_square = False

  # Find the maximum square size that evenly divides both width and height
  max_size = min(width, height)
  for size in range(max_size, 0, -1):
    if width % size == 0 and height % size == 0:
      x_splits = width // size
      y_splits = height // size
      print(f"The image can be divided into {size} {x_splits}x{y_splits} squares.")
      has_divisible_square = True

  # If no evenly divisible square is found, return None
  return has_divisible_square

# get image path from first command line argument
image_path = os.path.abspath(os.path.expanduser(os.path.expandvars(os.sys.argv[1])))
divisible_square_size = get_divisible_squares(image_path)

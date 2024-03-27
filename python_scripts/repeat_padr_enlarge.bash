#!/bin/bash

# set the input image to the first argument
input_image=$1

x_splits=27
y_splits=18

# run this loop 10 times
for i in {1..4}; do
  python3 slicePadrCompile.py --input_image $input_image --x_splits $x_splits --y_splits $y_splits --resize 512

  # get the input_image name no ext
  input_image_name=$(basename $input_image)
  input_image_name_no_ext=${input_image_name%%.*}
  output_dir=$(find $(dirname $input_image)/$input_image_name_no_ext -type d -name output)
  echo "Output dir: $output_dir"

  # if there's no output_dir bail
  if [ -z "$output_dir" ]; then
    echo "No output dir found, exiting"
    exit 1
  fi

  new_image=$(find $output_dir -type f ! -name "*-drawing-*")
  echo "New image: $new_image"

  # copy that image to the working dir
  cp $new_image $(dirname $input_image)
  # set the input image to the new image in the working dir
  input_image="$(dirname $input_image)/$(basename $new_image)"

  # increase the number of splits by 4 and 3
  x_splits=$((x_splits+3))
  y_splits=$((y_splits+2))

  echo "Copied new image: $input_image with $x_splits x $y_splits splits"
  # exit 0
done

echo "Done!"
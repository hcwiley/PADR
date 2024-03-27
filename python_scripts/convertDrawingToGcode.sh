#!/bin/bash
# convertDrawingToGcode.sh
# This script takes an SVG file and converts it to Gcode for PADR

# set the default vars
: "${VARIABLE:=DEFAULT_VALUE}"
: "${OUT_DOC_SIZE:=104.17inx104.17in}"
: "${MARGINS:=0.01in}"
: "${FLAVORFILE:=/Users/hcwiley/cws-git/internal/pitr/juicy-gcode-1.0.0.0/flavorfile.yaml}"
: "${JUICY_GCODE:=/Users/hcwiley/cws-git/internal/pitr/juicy-gcode-1.0.0.0/juicy-gcode}"
: "${AUTO_ROTATE:=false}"
# : "${LANDSCAPE:= }" # portrait
: "${LANDSCAPE:=--landscape }" # landscape
# set a auto resize long edge to 1024px
: "${AUTO_RESIZE:=4096}"
: "${PEN_THICKNESS:=0.7}"
: "${CLEAR_WORK_DIR:=true}"

: "${PRINT_SIZE:=}"      # 44in 66in
: "${CROP_TOP:=0in}"    # 0in 39
: "${CROP_LEFT:=0in}"    # 0in
: "${CROP_WIDTH:=0in}"  # 0in
: "${CROP_HEIGHT:=0in}" # 0in 27

# set the input file
in_image=$1

export PATH=/Applications/autotrace.app/Contents/MacOS/:/Users/hcwiley/miniforge3/bin:/opt/homebrew-m1/bin:$PATH

# make a working dir at the path ofthe image with no extension
working_dir="${in_image%.*}/"
if [ $CLEAR_WORK_DIR = true ]; then
  rm -rf $working_dir
fi
mkdir -p $working_dir
echo "Working dir is $working_dir"

image_name=$(basename $in_image)

# set the output file if it exists
if [ -z "$2" ]; then
  out_path="$working_dir/${image_name%.*}.gcode"
else
  out_path=$2
fi

# first mark in_image as orig by adding .orig between the name and extension
orig_path=$working_dir/${image_name%.*}.orig.${image_name##*.}
cp $in_image $orig_path

# check if we AUTO_ROTATE
if [ $AUTO_ROTATE = true ]; then
  # check if the image is horizontal or vertical
  # if horizontal, rotate it
  # if vertical, do nothing
  image_width=$(identify -format "%w" $in_image)
  image_height=$(identify -format "%h" $in_image)

  # check if $LANDSCAPE is not ""
  if [ "$LANDSCAPE" != "" ]; then
    # if so, we are in portrait mode
    # so we want to rotate if the image is wider than it is tall
    if [ $image_height -gt $image_width ]; then
      echo "Rotating $in_image to portrait"
      convert $in_image -rotate 90 $in_image
    fi
  elif [ $image_width -gt $image_height ]; then
    echo "Rotating $in_image to landscape"
    convert $in_image -rotate 90 $in_image
  fi
fi

# check if $AUTO_RESIZE is set and greater than 0
# if so, resize the image
if [ $AUTO_RESIZE -gt 0 ]; then
  echo "Resizing $in_image to $AUTO_RESIZE"
  convert $in_image -resize $AUTO_RESIZE $in_image
fi

svg_path=$working_dir/${image_name%.*}.svg

use_vpype_trace=false
use_potrace=false

# check if we need to generate the svg
if [ -f $svg_path ]; then
  echo "Found $svg_path, skipping conversion"
else
  if [ $use_vpype_trace = true ]; then
    echo "Using vpype to convert $in_image to $svg_path"
    echo "which vpype: $(which vpype)"
    vpype iread $in_image write $svg_path
  elif [ $use_potrace = true ]; then
    echo "Using potrace to convert $in_image to $svg_path"
    # do the initial conversion from image to SVG
    convert $in_image pgm: |
      mkbitmap -f 32 -t 0.4 - -o - |
      potrace -t 600 --fillcolor=#ffffff \
        -a 1.5 -O 0.7 \
        --svg -o $svg_path
  else
    echo "Using autotrace to convert $in_image to $svg_path"
    ppm_path=$working_dir/${image_name%.*}.ppm
    convert $in_image -brightness-contrast -35x90 -threshold 205 $ppm_path
    autotrace $ppm_path \
      -centerline -filter-iterations 11 \
      -despeckle-level 350 \
      -color-count 2 -corner-threshold 95 \
      -report-progress \
      --output-file $svg_path -output-format svg
  fi
fi

echo "Converting $in_image to $out_path with margins $MARGINS and doc size $OUT_DOC_SIZE and pen thickness $PEN_THICKNESS in landscape $LANDSCAPE"

opti_svg_path=$working_dir/${image_name%.*}.optimized.svg

# scale it first
# check if $PRINT_SIZE is not ""
if [ "$PRINT_SIZE" = "" ]; then
  echo "PRINT_SIZE is not set, skipping scaling"
else
  echo "Scaling $svg_path to $PRINT_SIZE"
  # need to set dim to be $PRINT_SIZE but repalce the space with x
  vpype read $svg_path scaleto $PRINT_SIZE write -p ${PRINT_SIZE// /x} $svg_path
fi

# use vpype to optimize the SVG
vpype_cmd="vpype read --parallel \
  $svg_path propset \
  --global --type float vp_pen_width ${PEN_THICKNESS}mm "

# if crop width and height are not "" then crop
if [ "$CROP_WIDTH" != "" ] && [ "$CROP_HEIGHT" != "" ]; then
  echo "Cropping |$CROP_WIDTH| x |$CROP_HEIGHT| from |$CROP_LEFT| x |$CROP_TOP|"
  vpype_cmd="$vpype_cmd \
  crop $CROP_LEFT $CROP_TOP $CROP_WIDTH $CROP_HEIGHT"
fi
vpype_cmd="$vpype_cmd \
  layout $LANDSCAPE --fit-to-margins $MARGINS \
  --valign center $OUT_DOC_SIZE "
vpype_cmd="$vpype_cmd \
  linemerge -t 15.0 linesort reloop \
  linesimplify -t 2 \
  filter --min-length 6mm \
  write $opti_svg_path"

echo "Running vpype command: $vpype_cmd"
eval $vpype_cmd

# check if the command was successful
if [ $? -eq 0 ]; then
  echo "vpype command successful"
else
  echo "vpype command failed"
  exit 1
fi

echo $opti_svg_path

# use juicy-gcode to convert the SVG to Gcode
$JUICY_GCODE $opti_svg_path -f $FLAVORFILE -o $out_path --tolerance $PEN_THICKNESS

# replace the original back
work_image=$working_dir/${image_name%.*}.auto.${image_name##*.}
mv $in_image $work_image
cp $orig_path $in_image

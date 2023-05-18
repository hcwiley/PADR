import subprocess
import os
import glob
import argparse
import datetime

import imageUtils

'''
example usages:

from intel imac:
$ python screen_record_to_ml_video.py \
  --ml_model_dir ../../CycleGAN-Tensorflow-2/saved_models/landscape2cole_sliced_v3 \
  --ml_python_path $(which python) \
  --path_to_cyclegan ../../CycleGAN-Tensorflow-2 \

from main m1 macbook pro:
input_image='/Users/hcwiley/Dropbox/art/ml/source-videos/IMG_6117.mp4'
python screen_record_to_ml_video.py --input_image $input_image
'''

py_arg = argparse.ArgumentParser()

# TODO: add env vars for:
#   - ml_model_dir
#   - ml_python_path
#   - path_to_cyclegan
#   - ffmpeg_path

py_arg.add_argument('--input_image')
py_arg.add_argument('--output_dir', default=None)
py_arg.add_argument('--work_dir', default=None)
py_arg.add_argument('--clean', default=False, action='store_true')
py_arg.add_argument('--dry_run', default=False, action='store_true')
py_arg.add_argument(
    '--ml_model_dir', default='/Users/hcwiley/ml-models/hcwiley/landscape2cole_sliced_v3')
py_arg.add_argument('--path_to_cyclegan',
                    default='/Users/hcwiley/cws-git/internal/CycleGAN-Tensorflow-2')
py_arg.add_argument('--ml_python_path',
                    # my ml python path is the default miniforge.
                    # NOTE: this is a DIFFERENT path than what this script takes to run.
                    default='/Users/hcwiley/miniforge3/bin/python')
py_arg.add_argument('--x_splits', default='2')
py_arg.add_argument('--y_splits', default='2')

args = py_arg.parse_args()

# make sure everything absolute path just to avoid confusion
input_image = os.path.abspath(args.input_image)
ml_model_dir = os.path.abspath(args.ml_model_dir)

path_to_cyclegan = os.path.abspath(args.path_to_cyclegan)
python_path = args.ml_python_path
if python_path is None:
  python_path = 'python'

image_name, image_ext = os.path.splitext(os.path.basename(input_image))[0:2]
input_image_path = os.path.dirname(input_image)

if args.work_dir is None:
  # use the {input_image}/{image_name}/datetime.date-datetime.time
  work_dir = os.path.join(
      input_image_path, image_name, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
else:
  work_dir = args.work_dir
work_dir = os.path.abspath(work_dir)

if args.output_dir is None:
  output_dir = os.path.join(work_dir, 'output')
else:
  output_dir = os.path.abspath(args.output_dir)
output_images_slices = os.path.join(work_dir, 'output_images_slices')
output_images_ml = os.path.join(work_dir, 'output_images_ml')
output_images_ml_drawing = os.path.join(output_images_ml, 'drawing')
output_images_ml_painting = os.path.join(output_images_ml, 'painting')

x_splits = args.x_splits
y_splits = args.y_splits


# print all the variables we've made so far
py_scripts_dir = os.path.dirname(os.path.abspath(__file__))
print('py_scripts_dir: {}'.format(py_scripts_dir))
print("input_image: {}".format(input_image))
print("output_dir: {}".format(output_dir))
print("work_dir: {}".format(work_dir))
print("ml_model_dir: {}".format(ml_model_dir))


if input_image is None:
  print("input_image is required")
  exit(1)

# check if input_image has a "_ or " in  it since our slicer uses those
if '_' in input_image or ' ' in input_image:
  os.makedirs(work_dir, exist_ok=True)
  # replace them with a -
  orig_input_image = input_image
  input_image = orig_input_image.replace('_', '-').replace(' ', '-')
  new_input_image_path = os.path.join(
      work_dir, os.path.basename(input_image))
  # and copy the original file to the new path
  subprocess.run(['cp', orig_input_image, new_input_image_path])
  input_image = new_input_image_path


# check if the CycleGAN path is legit
if not os.path.exists(path_to_cyclegan) or not os.path.isfile(os.path.join(path_to_cyclegan, 'run.py')):
  print("path_to_cyclegan is not a valid path")
  exit(1)

####
# setup all our commands
####

# imageBatchSlicer
slicer_cmd = 'python {}/imageBatchSlicer.py --input_image {} --x_splits {} --y_splits {} --random_seed 0 --border 0 --output_dir {} --clear_output 1'.format(py_scripts_dir,
                                                                                                                                                             input_image, x_splits, y_splits, output_images_slices)

# convert images to ml images
run_ml_cmd = '{} {}/run.py --models_dir {} --input_dir {} --output_dir {}'.format(
    python_path, path_to_cyclegan, ml_model_dir, output_images_slices, output_images_ml)

# split the ml images into painting and drawing
split_cmd = 'for img in $(find {dir} -name "*.jpg") ; do convert $img -crop 512x512+512+0 {dir}/drawing/$(basename $img) ; convert $img -crop 512x512+1024+0 {dir}/painting/$(basename $img) ; done'.format(dir=output_images_ml)

# compile the slices
compile_drawing_cmd = 'python {py_scripts}/compileSlices.py --input_dir {dir} --output_dir {dir}'.format(
    py_scripts=py_scripts_dir,
    dir=output_images_ml_drawing)

compile_painting_cmd = 'python {py_scripts}/compileSlices.py --input_dir {dir} --output_dir {dir}'.format(
    py_scripts=py_scripts_dir,                          dir=output_images_ml_painting)

cmds = [slicer_cmd, run_ml_cmd, split_cmd,
        compile_drawing_cmd, compile_painting_cmd]

# getting ready to make a bunch stuff. let's get into position
if args.clean and os.path.exists(work_dir):
  print("cleaning up work_dir: {}".format(work_dir))
  os.removedirs(work_dir)


def makeWorkDirs():
  # make the work directories
  print("making work directories")
  os.makedirs(work_dir, exist_ok=True)
  os.makedirs(output_images_ml, exist_ok=True)
  os.makedirs(output_images_ml_drawing, exist_ok=True)
  os.makedirs(output_images_ml_painting, exist_ok=True)
  os.makedirs(output_images_slices, exist_ok=True)


makeWorkDirs()
os.chdir(work_dir)
print("About to start working in: {}".format(work_dir))

for cmd in cmds:
  print("running: {}".format(cmd))
  if not args.dry_run:
    subprocess.run(cmd, shell=True)

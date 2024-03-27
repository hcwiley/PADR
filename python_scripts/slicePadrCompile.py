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
py_arg.add_argument('--random_seed', default=0)
py_arg.add_argument('--border', default=0.0)
py_arg.add_argument('--crop_size', default=-1)
py_arg.add_argument('--resize', default='512')
py_arg.add_argument('--circle', default=0)


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

slice_pattern = '{}x{}'.format(args.x_splits, args.y_splits)

if args.work_dir is None:
  # use the {input_image}/{image_name}/datetime.date-datetime.time
  work_dir = os.path.join(
      input_image_path, image_name, slice_pattern, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
else:
  work_dir = args.work_dir
work_dir = os.path.abspath(work_dir)

log_dir = os.path.join(work_dir, 'logs')

if args.output_dir is None:
  output_dir = os.path.join(work_dir, 'output')
else:
  output_dir = os.path.abspath(args.output_dir)
output_images_slices = os.path.join(work_dir, 'output_images_slices')
output_images_ml = os.path.join(work_dir, 'output_images_ml')
output_images_ml_drawing = os.path.join(output_images_ml, 'drawing')
output_images_ml_painting = os.path.join(output_images_ml, 'painting')

x_splits = int(args.x_splits)
y_splits = int(args.y_splits)


# print all the variables we've made so far
py_scripts_dir = os.path.dirname(os.path.abspath(__file__))
print('py_scripts_dir: {}'.format(py_scripts_dir))
print("input_image: {}".format(input_image))
print("output_dir: {}".format(output_dir))
print("work_dir: {}".format(work_dir))
print("ml_model_dir: {}".format(ml_model_dir))


out_dirs = [
    os.path.join(
      input_image_path, image_name),
    work_dir,
    output_dir,
    log_dir,
]

# ensure work_dir and output_dir exist
for dir in out_dirs:
  os.makedirs(dir, exist_ok=True)
  # also touch the dirs so they're most recently modified
  subprocess.run(['touch', dir])


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

image_name = os.path.splitext(os.path.basename(input_image))[0]
# strip extension
image_name = os.path.splitext(image_name)[0]

# check if the CycleGAN path is legit
if not os.path.exists(path_to_cyclegan) or not os.path.isfile(os.path.join(path_to_cyclegan, 'run.py')):
  print("path_to_cyclegan is not a valid path")
  exit(1)

####
# setup all our commands
####

# imageBatchSlicer
random_seed = int(args.random_seed)
border = float(args.border)
crop_size = int(args.crop_size)
resize = args.resize
circle = int(args.circle)

if x_splits > 1 or y_splits > 1:
  slicer_cmd = 'python {}/imageBatchSlicer.py --input_image {} --x_splits {} --y_splits {} --random_seed {} --border {} --crop_size {} --output_dir {} --clear_output 1'.format(
      py_scripts_dir,
      input_image,
      x_splits,
      y_splits,
      random_seed,
      border,
      crop_size,
      output_images_slices)
else:
  slicer_cmd = 'cp {} {}'.format(input_image, output_images_slices)

resize_cmd = 'echo "not resizing"'
if resize != '0':
  resize_cmd = 'for img in $(find {dir} -name "*.jpg") ; do convert $img -resize {resize}x{resize}! $img ; done'.format(
      dir=output_images_slices, resize=args.resize)

# circle crop the images
circle_cmd = 'echo "not circling"'
if circle > 0:
  mask = os.path.join(work_dir, 'circle_mask.png')

  circle_cmd = "convert -size {c}x{c} xc:Black -fill White -draw 'circle {r} {r} {r} 1' -alpha Copy {mask} ; ".format(
      c=circle, r=circle/2, mask=mask)

  # use imagemagick to circle crop the images keeping the inside of the circle and turning the outside $outside_color
  circle_cmd += 'for img in $(find {dir} -name "*.jpg") ; do  \
      magick $img \( +clone -threshold 101% -fill white -draw \'circle %[fx:int(w/2)],%[fx:int(h/2)] %[fx:int(w/2)],%[fx:{radius}+int(h/2)]\' \) -channel-fx \'| gray=>alpha\'   $img.png ; \
      convert $img.png -background white -flatten $img ; \
      done'.format(
      dir=output_images_slices, radius=circle/2)

# convert images to ml images
run_ml_cmd = '{} {}/run.py --models_dir {} --input_dir {} --output_dir {}'.format(
    python_path, path_to_cyclegan, ml_model_dir, output_images_slices, output_images_ml)

# split the ml images into painting and drawing
split_cmd = 'for img in $(find {dir} -name "*.jpg") ; do convert $img -crop 512x512+512+0 {dir}/drawing/$(basename $img) ; convert $img -crop 512x512+1024+0 {dir}/painting/$(basename $img) ; done'.format(dir=output_images_ml)

# compile the slices
if x_splits > 1 or y_splits > 1:
  compile_drawing_cmd = 'python {py_scripts}/compileSlices.py --input_dir {dir} --output_dir {output_dir} --output_name {image_name} --resize {resize} --x_splits {x_splits} --y_splits {y_splits}'.format(
      py_scripts=py_scripts_dir,
      dir=output_images_ml_drawing,
      output_dir=output_dir,
      image_name="{}-drawing-{}".format(image_name, slice_pattern),
      resize=resize,
      x_splits=x_splits,
      y_splits=y_splits
  )
else:
  compile_drawing_cmd = 'cp {dir}/*.jpg {output_dir}/{image_name}-drawing-{slice_pattern}.jpg'.format(
      dir=output_images_ml_drawing,
      output_dir=output_dir,
      image_name=image_name,
      slice_pattern=slice_pattern
  )

compile_painting_cmd = compile_drawing_cmd.replace(
    output_images_ml_drawing, output_images_ml_painting)
compile_painting_cmd = compile_painting_cmd.replace(
    '-drawing-', '-painting-')

speak_cmd = 'say -r 210 -v "Karen" "OK! im finished now"'

cmds = [slicer_cmd, resize_cmd,
        circle_cmd,
        run_ml_cmd, split_cmd,
        'echo fix_resize',
        compile_drawing_cmd,
        compile_painting_cmd,
        speak_cmd]

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

i = 0
for cmd in cmds:
  print("running: {}".format(cmd))
  success = True
  if not args.dry_run:
    # send stdout and stderr to files
    cmd_name = cmd[0:cmd.find(' ', cmd.find(' ')+1)].replace(' ', '_').replace(
        '/', '_').replace('.', '_').replace('-', '_')
    stdout_file = os.path.join(log_dir, '{}-stdout.txt'.format(cmd_name))
    stderr_file = os.path.join(log_dir, '{}-stderr.txt'.format(cmd_name))
    # get the start time
    start_time = datetime.datetime.now()
    ret = subprocess.run(cmd, shell=True, stdout=open(
        stdout_file, 'w'), stderr=open(stderr_file, 'w'))
    # get the end time
    end_time = datetime.datetime.now()
    # get the duration
    duration = end_time - start_time

    if ret.returncode != 0:
      success = False

  if success:
    # print in green that we ran the command
    print("\n{g}success running: {i} of {total} in {min}min {sec}sec\n{c}".format(
        g="\033[92m", i=i, total=len(cmds), c="\033[0m",
        min=duration.seconds // 60, sec=duration.seconds % 60
        ))
  else:
    print("error running:\n\t\t{}. Check log for details:\n\t{}\n\t{}".format(
        cmd, stdout_file, stderr_file))
    exit(1)
  i += 1

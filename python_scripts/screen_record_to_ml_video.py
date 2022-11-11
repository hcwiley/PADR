import subprocess
import os
import glob
import argparse
import datetime

import imageUtils

py_arg = argparse.ArgumentParser()

# get environment variables or fallback to defaults
py_arg.add_argument('--input_video')
py_arg.add_argument('--output_video', default=None)
py_arg.add_argument('--work_dir', default=None)
py_arg.add_argument('--fps', default=15)
py_arg.add_argument('--img_size', default=512)
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
py_arg.add_argument('--ffmpeg_path',
                    # My default is weird, you probably want this:
                    # default='/usr/local/bin/ffmpeg'
                    default='/opt/homebrew-m1/bin/ffmpeg'
                    )

args = py_arg.parse_args()

# make sure everything absolute path just to avoid confusion
input_video = os.path.abspath(args.input_video)
ml_model_dir = os.path.abspath(args.ml_model_dir)
fps = args.fps
img_size = args.img_size

path_to_cyclegan = os.path.abspath(args.path_to_cyclegan)
python_path = args.ml_python_path
if python_path is None:
  python_path = 'python'

ffmpeg_path = args.ffmpeg_path
if ffmpeg_path is None:
  ffmpeg_path = 'ffmpeg'

video_name, video_ext = os.path.splitext(os.path.basename(input_video))[0:2]
input_video_path = os.path.dirname(input_video)

if args.work_dir is None:
  # use the {input_video}/{video_name}/datetime.date-datetime.time
  work_dir = os.path.join(
      input_video_path, video_name, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
else:
  work_dir = args.work_dir
work_dir = os.path.abspath(work_dir)

if args.output_video is None:
  output_video = os.path.join(work_dir, 'output.mp4')
else:
  output_video = os.path.abspath(args.output_video)
output_images_vid = os.path.join(work_dir, 'output_images_vid')
output_images_ml = os.path.join(work_dir, 'output_images_ml')


# print all the variables we've made so far
print("input_video: {}".format(input_video))
print("output_video: {}".format(output_video))
print('video_name: {} video_ext: {}'.format(video_name, video_ext))
print("fps: {}".format(fps))
print("work_dir: {}".format(work_dir))
print("ml_model_dir: {}".format(ml_model_dir))


if input_video is None:
  print("input_video is required")
  exit(1)

# check if the CycleGAN path is legit
if not os.path.exists(path_to_cyclegan) or not os.path.isfile(os.path.join(path_to_cyclegan, 'run.py')):
  print("path_to_cyclegan is not a valid path")
  exit(1)

####
# setup all our commands
####

# convert video to images
ffmpeg_vid2img_cmd = "{} -i {input} -vf 'fps=15,scale={img_size}:{img_size}' {output}/%06d.jpg".format(
    ffmpeg_path, input=input_video, img_size=img_size, output=output_images_vid)

# convert images to video
ffmpeg_img2vid_cmd = "{} -framerate {} -pattern_type glob -i '{}/*.jpg' -c:v libx264 -pix_fmt yuv420p -y {}".format(
    ffmpeg_path, fps, output_images_ml, output_video)

# convert images to ml images
run_ml_cmd = '{} {}/run.py --models_dir {} --input_dir {} --output_dir {}'.format(
    python_path, path_to_cyclegan, ml_model_dir, output_images_vid, output_images_ml)


# getting ready to make a bunch stuff. let's get into position
if args.clean and os.path.exists(work_dir):
  print("cleaning up work_dir: {}".format(work_dir))
  os.removedirs(work_dir)


def makeWorkDirs():
  # make the work directories
  print("making work directories")
  os.makedirs(work_dir, exist_ok=True)
  os.makedirs(output_images_ml, exist_ok=True)
  os.makedirs(output_images_vid, exist_ok=True)


makeWorkDirs()
os.chdir(work_dir)
print("About to start working in: {}".format(work_dir))

# convert video to images
print("running: {}".format(ffmpeg_vid2img_cmd))
if not args.dry_run:
  subprocess.run(ffmpeg_vid2img_cmd, shell=True)

# convert images to ml images
print("running: {}".format(run_ml_cmd))
if not args.dry_run:
  subprocess.run(run_ml_cmd, shell=True)

# convert images to video
print("running: {}".format(ffmpeg_img2vid_cmd))
if not args.dry_run:
  subprocess.run(ffmpeg_img2vid_cmd, shell=True)

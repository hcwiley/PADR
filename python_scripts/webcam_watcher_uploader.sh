#!/bin/bash

# source the ./.env file
source ./.env

# make a datestr command
datestr=$(date +%Y-%m-%d_%H-%M-%S)

dst_host=ubuntu@$WEB_HOST
dst_dir=/var/www/html/latest.jpg
local_dir=$HOME/jobs/$datestr

mkdir -p $local_dir

img_num=0

vid_src="/dev/video6"

# make a filename by zero padding the img_num into the local_dir
local_dst=$local_dir/$(printf "%05d" $img_num).jpg
img_num=$((img_num+1))

# run ffmpeg in background and overwrite the same image every time and keep running til killed
ffmpeg -f v4l2 -framerate 30 -video_size 1280x720 -i $vid_src -update -y $local_dst &


# get the pid of the ffmpeg process
ffmpeg_pid=$!

# register to kill the ffmpeg process on exit
trap "kill $ffmpeg_pid" EXIT

while true; do
  scp $local_dst $dst_host:$dst_dir
  sleep 3
done

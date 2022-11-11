

Common setup vars:

```bash
inpt=some_video.mp4
outpt=output_video.mp4
```

## cropping and time editing video

ffmpeg command to 
- `-ss` offset the start time to 8 minutes and 50 seconds
- `-t` only create a 15 second long clip
- `-filter:v ` video filter
  - "crop=width:height:x_offset:y_offset" crop input video down to width X height, with a x and y offset number of pixels from top left

```bash
ffmpeg -ss 8:50 -t 15 -i $inpt -filter:v "crop=650:650:15:20" -y $outpt
```

## convert video to images

You can do this by adding the same argument -vf fps but with different values. You can extract images at a constant time interval by using fractions. For example, -vf fps=1/4 will output an image every 4 seconds.

```bash
ffmpeg -i input.mp4 -vf fps=1/4 %04d.png
```

Similarly, -vf fps=2/4 will output 2 images every 4 seconds.


Set fps to 15 and scale the images to 512x512

```bash
ffmpeg -i $inpt -vf fps=15 -vf scale=512:512 test/%06d.jpg
```

## convert images to video


```bash
ffmpeg -framerate 15 -pattern_type glob -i '*.jpg' -c:v libx264 -pix_fmt yuv420p -y $outpt
```

## convert video to bounce gif

```bash
ffmpeg -i painting.mp4 -filter_complex "[0]reverse[r];[0][r]concat=n=2:v=1:a=0,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" painting.gif
```

## Workflow

- convert video to images a set `FPS`
  - crop the video to the active part of the screen record when relevant
  - resize images to 512x512 for use with ML system
- run images through run.py
  - takes path to model, input, and output dirs
- make video from ML images
  - currently making a:
    - triptych (input, drawing, painting)
    - single channel drawing
    - single channel painting
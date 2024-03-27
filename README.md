# PADR

this is a repo of scripts, notes, utilities for PADR.

PADR? Painting and drawing robot.

A variety of machine learning, computer vision, mechantronics, firmware, and other fun stuff are involved!

Checkout my [Notion build page](https://hcwiley.notion.site/PADR-Painting-and-Drawing-robot-c70cd32c0473466198f514929353a43b?pvs=4)


## Setup

Pretty sure this is the guide i used for setting up my m1 mac: https://betterprogramming.pub/installing-tensorflow-on-apple-m1-with-new-metal-plugin-6d3cb9cb00ca

I've installed all my conda reqs to a env named `ldm`

```bash
conda activate ldm
```

## python_scripts

Collection of python scripts to run various ML and CV operations in batches.

Also some more bash helpers.

`convertDrawingToGcode.sh` is a very handy script that is okly documented. It relies on the env variables at the top which are easy to modify in the source or you can set the env variables in your terminal session depending on how you want to work. You need to install:
- [Autotrace](https://autotrace.sourceforge.net/)
- [vpype](https://github.com/abey79/vpype)
- [ImageMagick](https://imagemagick.org/index.php)
- [Juicy GCode](https://github.com/domoszlai/juicy-gcode)

## Repos i'm into right now
- https://github.com/hcwiley/CycleGAN-Tensorflow-2
- https://github.com/hcwiley/pytorch-CycleGAN-and-pix2pix
- https://github.com/bfirsh/stable-diffusion/tree/apple-silicon-mps-support

## Sources

- linedraw: https://github.com/LingDong-/linedraw

#!/usr/bin/env python3
#
# Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import sys
import argparse
import cv2
from jetson_inference import poseNet
from jetson_utils import videoSource, videoOutput, logUsage, cudaFromNumpy, cudaAllocMapped, cudaConvertColor, cudaDeviceSynchronize

net = poseNet("densenet121-body", sys.argv, 0.1)
output = videoOutput("", argv=sys.argv)

def poseDetect(frame):

    # process frames until the user exits
    # capture the next image
    img = frame
    bgr_img = cudaFromNumpy(img, isBGR=True)
    # convert from BGR -> RGB
    rgb_img = cudaAllocMapped(width=bgr_img.width,height=bgr_img.height, format='rgb8')

    cudaConvertColor(bgr_img, rgb_img)
    # perform pose estimation (with overlay)
    poses = net.Process(rgb_img, "links,keypoints")

    # print the pose results
    print("detected {:d} objects in image".format(len(poses)))

    print(net.GetNumKeypoints())
        
    for pose in poses:
        keyset = set()
        for keypoint in pose.Keypoints:
            keyset.add(keypoint.ID)
        if 0 not in keyset:
            print("baby sleep on stomach!!!!!\n\n\n\n")
        if 11 in keyset or 11 in keyset or 12 in keyset or 13 in keyset or\
            14 in  keyset or 15 in keyset or 16 in keyset:
            print("blanket is removed\n\n\n")

    # render the image
    output.Render(rgb_img)

    # update the title bar
    #output.SetStatus("{:s} | Network {:.0f} FPS".format(opt.network, net.GetNetworkFPS()))

    # print out performance info
    net.PrintProfilerTimes()

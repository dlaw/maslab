#!/usr/bin/python2.7

import cv, numpy as np, color, blobs, walls, kinect, time

color_defs = [('red', 175, 1./15, 1./150, 1./250),
              ('yellow', 30, 1./15, 1./150, 1./250),
              ('green', 52, 1./15, 1./150, 1./250)]

constants = np.vstack([[hue, 255., 255., hue_c, sat_c, val_c]
                       for name, hue, hue_c, sat_c, val_c in color_defs])

def process_video():
    t, image, depth = kinect.get_images()
    colors = color.identify(image, constants)
    blobs.find_blobs(colors, depth, 0)
    blobs.find_blobs(colors, depth, 1)
    blobs.find_blobs(colors, depth, 2)

def spin():
    for i in range(10):
        t = time.time()
        for i in range(20):
            process_video()
        print(20 / (time.time() - t))

import cProfile
process_video()
cProfile.run('spin()')

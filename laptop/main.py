#!/usr/bin/python2.7

import cv, numpy as np, arduino, kinect, color, blobs
from states import *

color_defs = [('red', 175, 1./15, 1./150, 1./250),
              ('yellow', 23, 1./10, 1./100, 1./140),
              ('green', 50, 1./15, 1./250, 1./350)]
constants = np.vstack([[hue, 255., 255., hue_c, sat_c, val_c]
                       for name, hue, hue_c, sat_c, val_c in color_defs])

time.sleep(.1)
assert arduino.is_alive()
state = FieldBounce()

i, st = 0, time.time()
while True:
    i += 1
    if i == 30:
        print('{0} fps'.format(30 / (time.time() - st)))
        i, st = 0, time.time()
    t, image, depth = kinect.get_images()
    colors = color.identify(image, constants)
    balls = blobs.find_blobs(colors, depth, color=0)
    yellow_walls = blobs.find_blobs(colors, depth, color=1, min_size=10)
    green_walls = blobs.find_blobs(colors, depth, color=2, min_size=10)
    state = state.next(balls, yellow_walls, green_walls)
    

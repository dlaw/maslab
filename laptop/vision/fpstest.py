#!/usr/bin/python2.7

import cv, numpy as np, color, blobs, walls, kinect, time

color_defs = {'red': (175, 15, 150, 250),
              'yellow': (30, 15, 150, 250),
              'green': (60, 15, 150, 250),
              'blue': (114, 15, 150, 250)}
maxv = {}
const = {}
for c in color_defs:
    maxv[c + '_hue'] = 180
    const[c + '_hue'] = color_defs[c][0]
    maxv[c + '_hue_c'] = 100
    const[c + '_hue_c'] = color_defs[c][1]
    maxv[c + '_sat_c'] = 400
    const[c + '_sat_c'] = color_defs[c][2]
    maxv[c + '_val_c'] = 400
    const[c + '_val_c'] = color_defs[c][3]

def process_video():
    t, image, depth = kinect.get_images()
    colors = np.array([[const['red_hue'], 1./const['red_hue_c'],
                        255, 1./const['red_sat_c'],
                        255, 1./const['red_val_c']],
                       [const['yellow_hue'], 1./const['yellow_hue_c'],
                        255, 1./const['yellow_sat_c'],
                        255, 1./const['yellow_val_c']],
                       [const['green_hue'], 1./const['green_hue_c'],
                        255, 1./const['green_sat_c'],
                        255, 1./const['green_val_c']],
                       [const['blue_hue'], 1./const['blue_hue_c'],
                        255, 1./const['blue_sat_c'],
                        255, 1./const['blue_val_c']]], 'float64')
    result = color.identify(image, colors)
    top, bottom, wallcolor = walls.identify(result, 1)
    blob_data = blobs.find_blobs(result, depth, 10, 0)

def spin():
    for i in range(10):
        t = time.time()
        for i in range(20):
            process_video()
        print(20 / (time.time() - t))

import cProfile
process_video()
cProfile.run('spin()')

#!/usr/bin/python2.7

import cv, numpy as np, color, blobs, walls, kinect, time

maxv = {'target_hue': 180,
        'hue_c': 50,
        'sat_c': 400,
        'val_c': 400,
        'min_area': 300,
        'wall_target_hue': 180,
        'wall_hue_c': 50,
        'wall_sat_c': 400,
        'wall_val_c': 400,
        'wall_pixel_height': 15}
const = {'target_hue': 175,
         'hue_c': 15,
         'sat_c': 150,
         'val_c': 200,
         'min_area': 100,
         'wall_target_hue': 114,
         'wall_hue_c': 15,
         'wall_sat_c': 150,
         'wall_val_c': 200,
         'wall_pixel_height': 4}

def process_video():
    t, image, depth = kinect.get_images()
    colors = np.array([[const['target_hue'],const['hue_c'],
                        255, const['sat_c'],
                        255, const['val_c']],
                       [const['wall_target_hue'], const['wall_hue_c'],
                        255,  const['wall_sat_c'],
                        255, const['wall_val_c']]], dtype=np.int16)
    result = np.empty_like(image[...,0], 'int32')
    color.identify(image, colors, result)
    wall = walls.filter_by_column(result, 1, const['wall_pixel_height'], -1)
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_HSV2BGR)
    image /= 2
    blob_data = blobs.find_blobs(result, depth, const['min_area'])
    for blob in blob_data:
        cv.Circle(cv.fromarray(image), (int(blob['col'][0]), int(blob['row'][0])),
                  int((blob['size'] / 3.14)**0.5), [255, 255, 255])
    for i in range(image.shape[1]):
        cv.Line(cv.fromarray(image), (i,wall[i]+const['wall_pixel_height']), (i,wall[i]), [255,255,255])

def spin():
    for i in range(10):
        t = time.time()
        for i in range(20):
            process_video()
        print(20 / (time.time() - t))

import cProfile
cProfile.run('spin()')

#!/usr/bin/python2.7

import arduino, freenect, cv, numpy as np
from vision import color, blobs, kinect, walls

const = {'target_hue': 175,
         'hue_c': 15,
         'sat_c': 150,
         'val_c': 200,
         'min_area': 100, #might need to bump this up to avoid false positives
         'wall_target_hue': 114,
         'wall_hue_c': 15,
         'wall_sat_c': 150,
         'wall_val_c': 200,
         'kinect_fov': np.pi/2, #fix this constant
         'depth_scaler': 0.001, #fix this constant
         'small_angle': 0.1 } #fix this constant

colors = np.array([[const['target_hue'], 1./const['hue_c'],
                    255, 1./const['sat_c'],
                    255, 1./const['val_c']],
                   [const['wall_target_hue'], 1./const['wall_hue_c'],
                    255,  1./const['wall_sat_c'],
                    255, 1./const['wall_val_c']]], 'float64')

def move():
    t, image, depth = kinect.get_images()
    result = color.identify(image, colors)
    top, bottom, c = walls.identify(result, 1, [])
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_HSV2BGR)
    image /= 2
    blob_data = blobs.find_blobs(result, depth, const['min_area'])
    if not len(blob_data): #no blobs found
        arduino.rotate(2*np.pi)
    else: #track blob closest to center
        blob_to_track = max(blob_data, key = lambda blob: abs(160-blob['col'][0]))
        angle = const['kinect_fov'] / 320. * (160 - blob_to_track['col'][0])
        if abs(angle) < small_angle: #move towards it
            dist = const['depth_scaler'] * blob_to_track['depth'][0]
            arduino.drive(dist, angle)
        else: #rotate only (don't drive)
            arduino.rotate(angle)

if __name__ == '__main__':
    while True:
        move()


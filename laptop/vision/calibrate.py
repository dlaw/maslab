#!/usr/bin/python2.7

import cv, numpy as np, color, blobs, kinect, walls, prefs

color_defs = [('red', 175, 1./15, 1./150, 1./250),
              ('yellow', 30, 1./15, 1./150, 1./250),
              ('green', 52, 1./15, 1./150, 1./250),
              ('blue', 114, 1./15, 1./150, 1./250)]

constants = np.vstack([[hue, 255., 255., hue_c, sat_c, val_c]
                       for name, hue, hue_c, sat_c, val_c in color_defs])
trackbars = []

cv.NamedWindow('Video', cv.CV_WINDOW_NORMAL)
cv.NamedWindow('Depth', cv.CV_WINDOW_NORMAL)
cv.NamedWindow('Constants')

def trackbar(index, color, prop, maxval, invert=False, window='Constants'):
    def update(value):
        constants[index] = 1./value if invert else value
    trackbar_name = '{0}_{1}'.format(color, prop)
    cv.CreateTrackbar(trackbar_name, window,
                      int(1./constants[index] if invert else constants[index]),
                      maxval, update)
    trackbars.append((trackbar_name, window))

for i, (name, hue, hue_c, sat_c, val_c) in enumerate(color_defs):
    trackbar((i, 0), name, 'hue', 180)
    trackbar((i, 3), name, 'hue_c', 40, True)
    trackbar((i, 4), name, 'sat_c', 500, True)
    trackbar((i, 5), name, 'val_c', 500, True)

def show_video():
    t, image, depth = kinect.get_images()
    colors = color.identify(image, constants)
    top, bottom, wallcolor = walls.identify(colors, 3)
    blob_data = blobs.find_blobs(colors, depth, 10, 0)
    color.colorize(image, constants, colors)
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_HSV2BGR)
    for blob in blob_data:
        cv.Circle(cv.fromarray(image), (int(blob['col'][0]), int(blob['row'][0])),
                  int((blob['size'] / 3.14)**0.5), [255, 255, 255])
    cv.ShowImage('Video', cv.fromarray(image))
    cv.ShowImage('Depth', cv.fromarray(depth << 5))

if __name__ == '__main__':
    while True:
        show_video()
        prefs.process(cv.WaitKey(10), trackbars, "calibrate.pkl")


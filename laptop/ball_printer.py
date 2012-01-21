#!/usr/bin/python2.7

import cv, numpy as np, color, blobs, kinect

color_defs = [('red', 175, 1./15, 1./150, 1./250),
              ('yellow', 23, 1./10, 1./100, 1./140),
              ('green', 50, 1./15, 1./250, 1./350)]
constants = np.vstack([[hue, 255., 255., hue_c, sat_c, val_c]
                       for name, hue, hue_c, sat_c, val_c in color_defs])
trackbars = []

cv.NamedWindow('Video', cv.CV_WINDOW_NORMAL)
cv.NamedWindow('Depth', cv.CV_WINDOW_NORMAL)
cv.NamedWindow('Constants')

def width(variance):
    return np.sqrt(1 + 12 * variance)

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
    trackbar((i, 4), name, 'sat_c', 600, True)
    trackbar((i, 5), name, 'val_c', 600, True)
# col is small when we need to turn left, and large when we need to turn right
def show_video():
    t, image, depth = kinect.get_images()
    colors = color.identify(image, constants)
    balls = blobs.find_blobs(colors, depth, color=0, min_size = 7)
    yellow_walls = blobs.find_blobs(colors, depth, color=1, min_size=10)
    green_walls = blobs.find_blobs(colors, depth, color=2, min_size=10)
    color.colorize(image, constants, colors)
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_HSV2BGR)
    cv.ShowImage('Video', cv.fromarray(image))
    cv.ShowImage('Depth', cv.fromarray(depth << 5))
    return balls

if __name__ == '__main__':
    while True:
        balls = show_video()
        if cv.WaitKey(10) == 27:
            for ball in balls:
                print(ball)
                
        


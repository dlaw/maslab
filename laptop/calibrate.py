#!/usr/bin/python2.7

import cv, numpy as np, color, blobs, kinect

cv.NamedWindow('Video', cv.CV_WINDOW_NORMAL)
cv.NamedWindow('Depth', cv.CV_WINDOW_NORMAL)
cv.NamedWindow('Constants')

def width(variance):
    return np.sqrt(1 + 12 * variance)

trackbars = []
def trackbar(index, color, prop, maxval, invert=False, window='Constants'):
    def update(value):
        kinect.constants[index] = 1./value if invert else value
    trackbar_name = '{0}_{1}'.format(color, prop)
    cv.CreateTrackbar(trackbar_name, window,
                      int(1./kinect.constants[index] if invert else kinect.constants[index]),
                      maxval, update)
    trackbars.append((trackbar_name, window))

for i, name in enumerate(['red', 'yellow', 'green']):
    trackbar((i, 0), name, 'hue', 180)
    trackbar((i, 3), name, 'hue_c', 40, True)
    trackbar((i, 4), name, 'sat_c', 600, True)
    trackbar((i, 5), name, 'val_c', 600, True)

def show_video():
    kinect.process_frame()
    color.colorize(kinect.image, kinect.constants, kinect.colors)
    for ball in kinect.balls:
        cv.Circle(cv.fromarray(kinect.image),
                  (int(ball['col'][0] + .5), int(ball['row'][0] + .5)),
                  int(1.5 + np.sqrt(ball['size'] / 3.14)),
                  (0, 0, 255))
    for wall in kinect.yellow_walls:
        cx, wx = wall['col'][0], width(wall['col'][1])/2
        cy, wy = wall['row'][0], width(wall['row'][1])/2
        cv.Rectangle(cv.fromarray(kinect.image),
                     (int(cx - wx + .5), int(cy - wy + .5)),
                     (int(cx + wx + .5), int(cy + wy + .5)),
                     (0, 0, 255))
    cv.CvtColor(cv.fromarray(kinect.image), cv.fromarray(kinect.image), cv.CV_HSV2BGR)
    cv.ShowImage('Video', cv.fromarray(kinect.image))
    cv.ShowImage('Depth', cv.fromarray(kinect.depth << 5))

if __name__ == '__main__':
    while True:
        show_video()
        key = cv.WaitKey(10)
        if key == ord('s') or key == 1048691:
            np.save('calibrate_out.npy', kinect.constants)


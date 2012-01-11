#!/usr/bin/env python
import freenect
import cv
import frame_convert
import numpy as np

threshold = 0

def change_threshold(value):
    global threshold
    threshold = value

def show_depth():
    d = freenect.sync_get_depth()[0]
    d = d < threshold
    d = d.astype('uint8')
    d = d * 255
    cv.ShowImage('Depth', cv.fromarray(d))

def show_video():
    cv.ShowImage('Video', frame_convert.video_cv(freenect.sync_get_video()[0]))

cv.NamedWindow('Depth')
cv.NamedWindow('Video')
cv.CreateTrackbar('Threshold depth (closer=white, farther=black)', 'Depth', threshold, 3000, change_threshold)

print('Press ESC in window to stop')

while 1:
    show_depth()
    show_video()
    if cv.WaitKey(10) == 27:
        break


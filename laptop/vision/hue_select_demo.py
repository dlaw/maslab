#!/usr/bin/env python
import hue_select
import freenect
import cv
import frame_convert
import numpy as np

current_hue = 0
threshold = 10
max_sq_dist_from_true = 45000

def change_hue(value):
    global current_hue
    current_hue = value

def change_threshold(value):
    global threshold
    threshold = value

def change_max_dist(value):
    global max_sq_dist_from_true
    max_sq_dist_from_true = value

def show_hue():
    rgb = freenect.sync_get_video()[0]
    filtered = hue_select.hue_select(rgb, target_hue = current_hue, hue_tolerance = threshold, sat_val_tolerance = max_sq_dist_from_true)
    mask = np.array([current_hue, 255, 255])
    np.resize(mask, (rgb.shape[0], rgb.shape[1], 3))
    #multiply by hsv to get original colors, or by mask to get current_hue 
    colored = filtered[:,:,np.newaxis] * mask
    colored = colored.astype(np.uint8)
    display = colored.copy()
    cv.CvtColor(cv.fromarray(colored), cv.fromarray(display), cv.CV_HSV2BGR)
    cv.ShowImage('Hue', cv.fromarray(display))

def show_video():
    cv.ShowImage('Video', frame_convert.video_cv(freenect.sync_get_video()[0]))

cv.NamedWindow('Hue')
cv.NamedWindow('Video')
cv.CreateTrackbar('Target hue (0-180)', 'Hue', current_hue, 180, change_hue)
cv.CreateTrackbar('Hue tolerance (+/-)', 'Hue', threshold, 90, change_threshold)
cv.CreateTrackbar('Max squared distance from true color', 'Hue', max_sq_dist_from_true, 100000, change_max_dist)

print('Press ESC in window to stop')

while 1:
    show_hue()
    show_video()
    if cv.WaitKey(10) == 27:
        break


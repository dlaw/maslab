#!/usr/bin/env python
import freenect
import cv
import frame_convert
import numpy as np

threshold = 10
current_hue = 0
min_sat = 0
min_val = 0

def change_threshold(value):
    global threshold
    threshold = value

def change_hue(value):
    global current_hue
    current_hue = value

def change_min_sat(value):
    global min_sat
    min_sat = value

def change_min_val(value):
    global min_val
    min_val = value

def show_hue():
    rgb = freenect.sync_get_video()[0]
    hsv = rgb.copy()
    cv.CvtColor(cv.fromarray(rgb), cv.fromarray(hsv), cv.CV_RGB2HSV)
    hue = hsv[:,:,0]
    hue = hue.astype(np.int16) #to prevent overflow error
    differences = np.mod(hue - current_hue, 180)
    filtered = np.logical_or(
                  differences <= threshold,
                  differences >= 180-threshold
               )
    sat = hsv[:,:,1]
    sat = sat > min_sat
    val = hsv[:,:,2]
    val = val > min_val
    filtered = filtered * sat * val
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
cv.CreateTrackbar('Min saturation', 'Hue', min_sat, 255, change_min_sat)
cv.CreateTrackbar('Min value', 'Hue', min_val, 255, change_min_val)

print('Press ESC in window to stop')

while 1:
    show_hue()
    show_video()
    if cv.WaitKey(10) == 27:
        break


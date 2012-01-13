#!/usr/bin/env python
import color, freenect, cv, numpy

hue = 175
hue_c = 30
sat_c = 200
val_c = 200

def change_hue(x):
    global hue
    hue = x
def change_hue_c(x):
    global hue_c
    hue_c = x
def change_sat_c(x):
    global sat_c
    sat_c = x
def change_val_c(x):
    global val_c
    val_c = x

def show_video():
    image = freenect.sync_get_video()[0]
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_RGB2HSV)
    image *= color.select(image, [hue, 255, 255], [hue_c, sat_c, val_c])[...,None]
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_HSV2BGR)
    cv.ShowImage('Video', cv.fromarray(image))

cv.NamedWindow('Video')
cv.NamedWindow('Sliders')
cv.CreateTrackbar('Target hue', 'Sliders', hue, 180, change_hue)
cv.CreateTrackbar('Hue const', 'Sliders', hue_c, 300, change_hue_c)
cv.CreateTrackbar('Sat const', 'Sliders', sat_c, 300, change_sat_c)
cv.CreateTrackbar('Val const', 'Sliders', val_c, 300, change_val_c)

if __name__ == '__main__':
    while True:
        show_video()
        if cv.WaitKey(10) == 27:
            break


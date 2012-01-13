import blob_select
import freenect
import cv
import frame_convert
import numpy as np

current_hue = 0
threshold = 10
max_sq_dist_from_true = 450000
sat_const = 12
val_const = 8
min_area = 1000
max_area = 35000
color_fill = None

def change_hue(value):
    global current_hue, color_fill
    current_hue = value
    hsv_pixel = np.array([[[current_hue, 255, 255]]], dtype='uint8')
    color_fill = hsv_pixel.copy()
    cv.CvtColor(cv.fromarray(hsv_pixel), cv.fromarray(color_fill), cv.CV_HSV2RGB)
change_hue(0)

def change_threshold(value):
    global threshold
    threshold = value

def change_max_dist(value):
    global max_sq_dist_from_true
    max_sq_dist_from_true = value

def change_sat_const(value):
    global sat_const
    sat_const = value

def change_val_const(value):
    global val_const
    val_const = value

def change_min_area(value):
    global min_area
    min_area = value

def change_max_area(value):
    global max_area
    max_area = value

def show_blobs():
    rgb = freenect.sync_get_video()[0]
    depth = freenect.sync_get_depth()[0].astype('float32')
    blob_data, filtered = blob_select.blob_select(rgb, depth, target_hue = current_hue, hue_tolerance = threshold, sat_val_tolerance = max_sq_dist_from_true, sat_c = sat_const, val_c = val_const, min_blob_area = min_area, max_blob_area = max_area)
    colored = filtered[:,:,np.newaxis] * color_fill[...,::-1]
    colored = colored.astype(np.uint8)
    cv.ShowImage('Filtered', cv.fromarray(colored))
    draw_img = np.zeros((rgb.shape[0], rgb.shape[1], 3))
    for color, size, avg_r, avg_c, avg_d, var_d in blob_data:
        cv.Circle(cv.fromarray(draw_img), (int(avg_c), int(avg_r)), int((1.0*size/np.pi)**0.5), cv.RGB(color_fill[0,0,0], color_fill[0,0,1], color_fill[0,0,2]))
    cv.ShowImage('Blobs', cv.fromarray(draw_img))

def show_video():
    cv.ShowImage('Video', frame_convert.video_cv(freenect.sync_get_video()[0]))

cv.NamedWindow('Video')
cv.NamedWindow('Filtered')
cv.NamedWindow('Blobs')
cv.NamedWindow('Controls')
cv.CreateTrackbar('Target hue (0-180)', 'Controls', current_hue, 180, change_hue)
cv.CreateTrackbar('Hue tolerance (+/-)', 'Controls', threshold, 90, change_threshold)
cv.CreateTrackbar('Max squared distance from true color', 'Controls', max_sq_dist_from_true, 1000000, change_max_dist)
cv.CreateTrackbar('Saturation constant (x10)', 'Controls', sat_const, 30, change_sat_const)
cv.CreateTrackbar('Value constant (x10)', 'Controls', val_const, 30, change_val_const)
cv.CreateTrackbar('Min blob area', 'Controls', min_area, 3000, change_min_area)
cv.CreateTrackbar('Max blob area', 'Controls', max_area, 100000, change_max_area)

print('Press ESC in window to stop')

while 1:
    show_blobs()
    show_video()
    if cv.WaitKey(10) == 27:
        break


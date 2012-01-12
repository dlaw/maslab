import blob_select
import freenect
import cv
import frame_convert
import numpy as np

current_hue = 0
threshold = 10
max_sq_dist_from_true = 45000
min_area = 1000
max_area = 35000
color_fill = None

def change_hue(value):
    global current_hue, color_fill
    current_hue = value
    hsv_pixel = np.array([[[current_hue, 255, 255]]], dtype='uint8')
    rgb_pixel = hsv_pixel.copy()
    cv.CvtColor(cv.fromarray(hsv_pixel), cv.fromarray(rgb_pixel), cv.CV_HSV2RGB)
    color_fill = cv.RGB(rgb_pixel[0,0,0], rgb_pixel[0,0,1], rgb_pixel[0,0,2])
change_hue(0)

def change_threshold(value):
    global threshold
    threshold = value

def change_max_dist(value):
    global max_sq_dist_from_true
    max_sq_dist_from_true = value

def change_min_area(value):
    global min_area
    min_area = value

def change_max_area(value):
    global max_area
    max_area = value

def show_blobs():
    rgb = freenect.sync_get_video()[0]
    depth = freenect.sync_get_depth()[0].astype('float32')
    blob_data = blob_select.blob_select(rgb, depth, target_hue = current_hue, hue_tolerance = threshold, sat_val_tolerance = max_sq_dist_from_true, min_blob_area = min_area, max_blob_area = max_area)
    draw_img = np.zeros((rgb.shape[0], rgb.shape[1], 3))
    for color, size, avg_r, avg_c, avg_d, var_d in blob_data:
        cv.Circle(cv.fromarray(draw_img), (int(avg_c), int(avg_r)), int((1.0*size/np.pi)**0.5), color_fill)
    cv.ShowImage('Blobs', cv.fromarray(draw_img))

def show_video():
    cv.ShowImage('Video', frame_convert.video_cv(freenect.sync_get_video()[0]))

cv.NamedWindow('Blobs')
cv.NamedWindow('Video')
cv.CreateTrackbar('Target hue (0-180)', 'Blobs', current_hue, 180, change_hue)
cv.CreateTrackbar('Hue tolerance (+/-)', 'Blobs', threshold, 90, change_threshold)
cv.CreateTrackbar('Max squared distance from true color', 'Blobs', max_sq_dist_from_true, 100000, change_max_dist)
cv.CreateTrackbar('Min blob area', 'Blobs', min_area, 3000, change_min_area)
cv.CreateTrackbar('Max blob area', 'Blobs', max_area, 100000, change_max_area)

print('Press ESC in window to stop')

while 1:
    show_blobs()
    show_video()
    if cv.WaitKey(10) == 27:
        break


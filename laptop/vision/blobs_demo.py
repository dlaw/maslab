import freenect, cv, numpy as np, color, blobs

hue = 175
hue_c, sat_c, val_c = 30, 200, 200
min_area, max_area = 200, 30000

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
def change_min_area(x):
    global min_area
    min_area = x
def change_max_area(x):
    global max_area
    max_area = x

def show_video():
    image = freenect.sync_get_video()[0]
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_RGB2HSV)
    depth = freenect.sync_get_depth()[0].astype('float32')
    good = color.select(image, [hue,255,255], [hue_c,sat_c,val_c]).astype('uint32')
    blob_data = blobs.find_blobs(good, depth, min_area, max_area)
    image[:] = 0
    for size, blob_color, (avg_r, var_r), (avg_c, var_c), (avg_d, var_d) in blob_data:
        cv.Circle(cv.fromarray(image), (int(avg_c), int(avg_r)), int((1.0*size/3.14)**0.5), [255,255,255])
    cv.ShowImage('Video', cv.fromarray(image))

cv.NamedWindow('Video', cv.CV_WINDOW_NORMAL)
cv.NamedWindow('Sliders')
cv.CreateTrackbar('Target hue', 'Sliders', hue, 180, change_hue)
cv.CreateTrackbar('Hue const', 'Sliders', hue_c, 300, change_hue_c)
cv.CreateTrackbar('Sat const', 'Sliders', sat_c, 300, change_sat_c)
cv.CreateTrackbar('Val const', 'Sliders', val_c, 300, change_val_c)
cv.CreateTrackbar('Min blob area', 'Sliders', min_area, 3000, change_min_area)
cv.CreateTrackbar('Max blob area', 'Sliders', max_area, 100000, change_max_area)

i = 0
t = None
while True:
    i += 1
    if i == 20:
        if t: print((time.time() - t) / 20)
        t = time.time()
        i = 0
    show_video()
    if cv.WaitKey(10) == 27:
        break


#!/usr/bin/python

import freenect, cv, numpy as np, color, blobs

maxv = {'target_hue': 180,
        'hue_c': 50,
        'sat_c': 400,
        'val_c': 400,
        'min_area': 300}
const = {'target_hue': 175,
         'hue_c': 15,
         'sat_c': 150,
         'val_c': 200,
         'min_area': 100}
def updater(name):
    def update(value):
        const[name] = value
    return update

def show_video():
    image = freenect.sync_get_video()[0]
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_RGB2HSV)
    depth = freenect.sync_get_depth()[0].astype('float32')
    good = (color.select(image, [const['target_hue'], 255, 255],
                         [const['hue_c'], const['sat_c'], const['val_c']])
            .astype('uint32'))
    blob_data = blobs.find_blobs(good, depth, const['min_area'])
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_HSV2BGR)
    image[:] /= 2
    for size, blob_color, row, col, depth in blob_data:
        cv.Circle(cv.fromarray(image), (int(col[0]), int(row[0])),
                  int((size / 3.14)**0.5), [255, 255, 255])
    cv.ShowImage('Video', cv.fromarray(image))

cv.NamedWindow('Video', cv.CV_WINDOW_NORMAL)
cv.NamedWindow('Constants')
for c in const:
    cv.CreateTrackbar(c, 'Constants', const[c], maxv[c], updater(c))

if __name__ == '__main__':
    while True:
        show_video()
        if cv.WaitKey(10) == 27:
            break


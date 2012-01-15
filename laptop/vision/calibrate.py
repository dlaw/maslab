#!/usr/bin/python2.7

import cv, numpy as np, color, blobs, kinect

maxv = {'target_hue': 180,
        'hue_c': 50,
        'sat_c': 400,
        'val_c': 400,
        'min_area': 300,
        'wall_target_hue': 180,
        'wall_hue_c': 50,
        'wall_sat_c': 400,
        'wall_val_c': 400,
        'wall_pixel_height': 30}
const = {'target_hue': 175,
         'hue_c': 15,
         'sat_c': 150,
         'val_c': 200,
         'min_area': 100,
         'wall_target_hue': 105,
         'wall_hue_c': 15,
         'wall_sat_c': 150,
         'wall_val_c': 200,
         'wall_pixel_height': 5}

def updater(name):
    def update(value):
        const[name] = value
    return update

def show_video():
    #t, image, depth = kinect.get_images()
    image = np.empty((480,640,3), dtype='uint8')
    cv.CvtColor(cv.LoadImage("rb.png"), cv.fromarray(image), cv.CV_BGR2HSV)
    depth = np.random.randint(0,2047,(480, 640)).astype('uint16')

    targets = np.array([
        [const['target_hue'], 255, 255],
        [const['wall_target_hue'], 255, 255]
        ], dtype=np.uint8)
    scalers = np.array([
        [const['hue_c'], const['sat_c'], const['val_c']],
        [const['wall_hue_c'], const['wall_sat_c'], const['wall_val_c']],
        ], dtype=np.uint16)
    colors = color.select(image, targets, scalers)
    wall = color.filter_by_column(colors, 0, 1, const['wall_pixel_height'], -1)
    colors = colors.astype(np.uint32)
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_HSV2BGR)
    image /= 2 - colors[...,None]
    blob_data = blobs.find_blobs(colors, depth, const['min_area'])
    for size, row, col, d in blob_data:
        cv.Circle(cv.fromarray(image), (int(col[0]), int(row[0])),
                  int((size / 3.14)**0.5), [255, 255, 255])
    for i in range(image.shape[1]):
        cv.Line(cv.fromarray(image), (i,wall[i]+const['wall_pixel_height']), (i,wall[i]), [255,255,255])
    cv.ShowImage('Video', cv.fromarray(image))
    cv.ShowImage('Depth', cv.fromarray(depth << 5))
        
cv.NamedWindow('Video', cv.CV_WINDOW_NORMAL)
cv.NamedWindow('Depth', cv.CV_WINDOW_NORMAL)
cv.NamedWindow('Constants')
for c in const:
    cv.CreateTrackbar(c, 'Constants', const[c], maxv[c], updater(c))

if __name__ == '__main__':
    while True:
        show_video()
        if cv.WaitKey(10) == 27:
            break


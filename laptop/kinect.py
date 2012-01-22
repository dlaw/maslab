import freenect, numpy, cv, color, blobs

image = numpy.empty((120, 160, 3), dtype='uint8')
depth = numpy.empty((120, 160), dtype='uint16')
colors = numpy.empty((120, 160), dtype='int32')

initialized = False

constants = numpy.load('color_defs.npy')

def process_frame():
    # Get the raw frames
    raw_image = freenect.sync_get_video()[0]
    raw_depth = freenect.sync_get_depth()[0]

    # Downsample and convert the image frame
    cv.Resize(cv.fromarray(raw_image), cv.fromarray(image), cv.CV_INTER_AREA)
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_RGB2HSV)
    
    # Downsample the depth frame using nearest-neighbor to make sure 
    # invalid pixels are handled properly.
    cv.Resize(cv.fromarray(raw_depth), cv.fromarray(depth), cv.CV_INTER_NN)
    
    # Do the object recognition
    color.identify(image, constants, colors)
    global balls, yellow_walls, green_walls
    balls = blobs.find_blobs(colors, depth, color=0)
    yellow_walls = blobs.find_blobs(colors, depth, color=1, min_size=10)
    green_walls = blobs.find_blobs(colors, depth, color=2, min_size=10)

# Work around an initialization bug for synchronous image
try:
    ctx = freenect.init()
    dev = freenect.open_device(ctx, 0)
    if not dev:
        raise Exception
    freenect.start_video(dev) # sync_get_video hangs if we don't do this
    freenect.start_depth(dev) # sync_get_depth hangs if we don't do this
    freenect.stop_depth(dev)
    freenect.stop_video(dev)
    freenect.close_device(dev) # close the device so that c_sync can open it
    freenect.shutdown(ctx)
    process_frame()
    initialized = True
except:
    pass

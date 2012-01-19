import freenect, numpy, cv

video = numpy.empty((120, 160, 3), dtype='uint8')
depth = numpy.empty((120, 160), dtype='uint16')
initialized = False

# Work around an initialization bug for synchronous video
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
    initialized = True
except:
    print "Error initializing Kinect"

def get_images():
    """
    Returns the tuple (timestamp, video, depth) from the Kinect.
    timestamp is in seconds relative to an arbitrary zero time.
    video is a (120,160,3)-array of uint8s in HSV format.
    depth is a (120,160)-array of uint16s.
    """
    if not initialized:
        raise Exception

    # Get the raw frames
    raw_video, timestamp = freenect.sync_get_video()
    raw_depth = freenect.sync_get_depth()[0]

    # Downsample and convert the video frame
    cv.Resize(cv.fromarray(raw_video), cv.fromarray(video), cv.CV_INTER_AREA)
    cv.CvtColor(cv.fromarray(video), cv.fromarray(video), cv.CV_RGB2HSV)
    
    # Downsample the depth frame using nearest-neighbor to make sure 
    # invalid pixels are handled properly.
    cv.Resize(cv.fromarray(raw_depth), cv.fromarray(depth), cv.CV_INTER_NN)
    
    # Convert timestamp from Kinect processor cycles to seconds
    return timestamp / 60008625., video, depth

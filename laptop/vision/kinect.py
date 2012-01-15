import freenect, numpy, cv

shape = (240, 320)
video = numpy.empty(shape + (3,), dtype='uint8')
depth = numpy.empty(shape, dtype='uint16')

# Work around an initialization bug for synchronous video
dev = freenect.open_device(freenect.init(), 0)
freenect.start_video(dev) # sync_get_video hangs if we don't do this
freenect.start_depth(dev) # sync_get_depth hangs if we don't do this
freenect.close_device(dev) # close the device so that c_sync can open it

def get_images():
    """
    Returns the tuple (timestamp, video, depth) from the Kinect.
    timestamp is in seconds relative to an arbitrary zero time.
    video is a (320,240,3)-array of uint8s in HSV format.
    depth is a (320,240)-array of uint16s.
    """
    raw_video, timestamp = freenect.sync_get_video()
    raw_depth = freenect.sync_get_depth()[0]
    cv.Resize(cv.fromarray(raw_video), cv.fromarray(video))
    cv.CvtColor(cv.fromarray(video), cv.fromarray(video), cv.CV_RGB2HSV)
    # Must use nearest-neighbor for depth because of 2047 values
    cv.Resize(cv.fromarray(raw_depth), cv.fromarray(depth), cv.CV_INTER_NN)
    return timestamp / 60008625., video, depth # convert to seconds

get_images()
print("done")

import freenect, numpy, cv

video = numpy.empty((120, 160, 3), dtype='uint8')
depth = numpy.empty((120, 160), dtype='uint16')

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
    # Get the raw frames
    raw_video, timestamp = freenect.sync_get_video()
    raw_depth = freenect.sync_get_depth()[0]

    # Downsample and convert the video frame
    cv.Resize(cv.fromarray(raw_video), cv.fromarray(video), cv.CV_INTER_AREA)
    cv.CvtColor(cv.fromarray(video), cv.fromarray(video), cv.CV_RGB2HSV)
    
    # Depth downsampling is tricky.  We replace invalid pixels with
    # 2^15.  After 4x4 downsampling, every invalid pixel contributes
    # 2^11 to the average.  Since valid pixel values are always less
    # than 2^11, we can just mod out by 2^11 to ignore invalid pixels.
    # Downsampled regions with no valid depth pixels now have the
    # value zero.
    raw_depth[:] = numpy.where(raw_depth == 2047, 2**15, raw_depth)
    cv.Resize(cv.fromarray(raw_depth), cv.fromarray(depth), cv.CV_INTER_AREA)
    
    # Convert timestamp from Kinect processor cycles to seconds
    return timestamp / 60008625., video, depth % (2**11)

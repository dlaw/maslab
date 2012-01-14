import freenect

def init():
    ctx = freenect.init()
    dev = freenect.open_device(ctx, 0)
    freenect.start_video(dev)
    freenect.stop_video(dev)
    freenect.close_device(dev)
    freenect.shutdown(ctx)


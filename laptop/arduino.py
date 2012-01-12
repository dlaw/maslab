import serial, struct

port = serial.Serial('/dev/ttyACM0', 500000, timeout=.01) # 500k baud

def raw_command(response_fmt, data_fmt, *data):
    """Send a command to the arduino and receive a response."""
    port.flushInput() # clear out old crap
    port.write(struct.pack(data_fmt, *data))
    response_data = port.read(struct.calcsize(response_fmt))
    try: return struct.unpack(response_fmt, response_data)
    except: return None

def is_alive():
    """Check whether the arduino is responding to commands."""
    return raw_command('<B', '<B', 0) == (0,)

def set_motors(left, right):
    """Set the drive motors.  Speeds range from -1.0 to 1.0."""
    return raw_command('<B', '<Bbb', 1, int(127*left), int(127*right)) == (0,)

def get_ir(channel):
    """Ask for an ir reading from CHANNEL"""
    return raw_command('<B', '<Bb', 2, channel)

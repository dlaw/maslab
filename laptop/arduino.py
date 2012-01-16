import serial, struct

port = serial.Serial('/dev/ttyACM0', 500000, timeout=.01) # 500k baud

def raw_command(response_fmt, data_fmt, *data):
    """Send a command to the arduino and receive a response."""
    port.flushInput() # clear out old crap
    port.write(struct.pack('>' + data_fmt, *data))
    response_data = port.read(struct.calcsize(response_fmt))
    try: return struct.unpack('<' + response_fmt, response_data)
    except: return None

def is_alive():
    """Check whether the arduino is responding to commands."""
    return raw_command('B', 'B', 0) == (0,)

def set_motors(left, right):
    """Set the drive motors.  Speeds range from -1.0 to 1.0."""
    return raw_command('B', 'Bbb', 1, int(127*left), int(127*right)) == (0,)

def get_ir(channel):
    """Ask for an ir reading from CHANNEL"""
    return raw_command('B', 'Bb', 2, channel)[0]

def rotate(angle):
    return raw_command('B', 'Bi', 3, int(angle * 2**16)) == (0,)

def drive(distance, angle):
    return raw_command('B', 'Bii', 4, int(angle * 2**16), int(distance)) == (0,)

def ask_angle():
    return float(raw_command('i', 'B', 5)[0]) / 2**16

def ask_distance():
    return raw_command('i', 'B', 6)[0]

def change_param(param, newval):
    pass

def get_ticks():
    return raw_command('hh', 'B', 8)

def ask_voltage():
    return raw_command('H', 'B', 9)[0] * 15 / 2**10

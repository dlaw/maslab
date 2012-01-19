import serial, struct

port = serial.Serial('/dev/ttyACM0', 500000, timeout=.01) # 500k baud
debug = False

def format_bytes(bytes):
    return ' '.join([hex(ord(b)) for b in bytes])

def raw_command(response_fmt, data_fmt, *data):
    """Send a command to the arduino and receive a response."""
    port.flushInput() # clear out old crap
    output = struct.pack('>' + data_fmt, *data)
    if debug: print('Sending {0}'.format(format_bytes(output)))
    port.write(output)
    response_data = port.read(struct.calcsize(response_fmt))
    if debug: print('Received {0}'.format(format_bytes(response_data)))
    try:
        return struct.unpack('>' + response_fmt, response_data)
    except:
        if debug: print("Invalid response")
        return None

def is_alive():
    """Check whether the arduino is responding to commands."""
    return raw_command('B', 'B', 0) == (0,)

def set_motors(left, right):
    """Set the drive motors.  Speeds range from -1.0 to 1.0."""
    return raw_command('B', 'Bbb', 1, int(127*left), int(127*right)) == (0,)

def set_speeds(left, right):
    """Set motor speeds in rotations per second."""
    left_period = int(1e6 / (140.76 * left)) # usecs between encoder ticks
    right_period = int(1e6 / (140.76 * right))
    return raw_command('B', 'Bii', 10, left_period, right_period) == (0,)

def get_ir(channel):
    """Ask for an ir reading from CHANNEL"""
    return raw_command('B', 'Bb', 2, channel)[0]

def change_param(param, newval):
    pass

def get_ticks():
    return raw_command('hh', 'B', 8)

def get_voltage():
    return raw_command('B', 'B', 9)[0] * 15 / 2**10

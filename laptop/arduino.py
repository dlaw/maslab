import serial, subprocess, struct, constants, numpy as np

debug = False

names = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/tty.usbmodem621']
for name in names:
    try:
        port = serial.Serial(name, 500000, timeout=.01) # 500k baud
        if port != name[-1]: # if we're on Linux
            subprocess.call(['stty', '-F', name, '-clocal'])
        break
    except:
        continue

def format_bytes(bytes):
    return ' '.join([hex(ord(b)) for b in bytes])

def raw_command(response_fmt, data_fmt, *data):
    """Send a command to the arduino and receive a response."""
    port.flushInput() # clear out old crap
    output = struct.pack('>' + data_fmt, *data)
    if debug: print('Sending {0}'.format(format_bytes(output)))
    try:
        port.write(output)
    except:
        print("Arduino I/O error... reinitializing")
        connect()
        time.sleep(1) # arduino must reboot
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
    try: return raw_command('B', 'B', 0) == (0,)
    except: return False

def set_led(value):
    return raw_command('B', 'BB', 7, value) == (0,)

def set_motors(left, right):
    """Set the drive motors.  Speeds range from -1.0 to 1.0."""
    left = np.clip(left, -1, 1)
    right = np.clip(right, -1, 1)
    return raw_command('B', 'Bbb', 1, int(127*left), int(127*right)) == (0,)

def drive(fwd, turn):
    return set_motors(fwd + turn, fwd - turn)

def get_analog(channel):
    """Ask for an analog reading."""
    return raw_command('B', 'Bb', 2, channel)[0]

def get_ir():
    return [get_analog(i) / constants.ir_max[j] for i, j in 
            zip([3, 2, 0, 1], range(4))]

def get_voltage():
    return get_analog(4) * 0.0693

def get_switch():
    return bool(raw_command('B', 'B', 3)[0])

def set_sucker(value):
    return raw_command('B', 'BBB', 5, 1, value) == (0,)

def set_helix(value):
    return raw_command('B', 'BBB', 5, 0, value) == (0,)

def set_door(value):
    return raw_command('B', 'BBB', 5, 2, value) == (0,)

def get_bump():
    bumps = raw_command('B', 'B', 4)[0]
    return [not bool(bumps & (1 << i)) for i in range(4)]

def get_new_ball_count():
    return raw_command('B', 'B', 6)[0]

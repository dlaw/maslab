import serial, struct

port = serial.Serial('/dev/ttyACM0', 500000, timeout=0) # 500k baud

def send(cmd, *data):
    """Write a 1-byte header followed by some number of 4-byte words."""
    port.write(struct.pack('<B', cmd))
    for word in data:
        port.write(struct.pack('<I', word))

import arduino
import time

while not arduino.set_motors(0, 0):
   time.sleep(.1)

import arduino
import time

time.sleep(2)
assert arduino.is_alive()

for timer in range(150):
    arduino.set_motors(1,-1)
    time.sleep(1)
    arduino.set_motors(-1,1)
    time.sleep(1)

for timer in range(150):
    arduino.set_motors(1,1)
    time.sleep(1)
    arduino.set_motors(-1,-1)
    time.sleep(1)

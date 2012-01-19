import arduino
import time
tsleep = .5
time.sleep(2)
assert arduino.is_alive()
print "arduino is alive"
for timer in range(150):
    arduino.set_motors(1,-1)
    time.sleep(tsleep)
    arduino.set_motors(-1,1)
    time.sleep(tsleep)

for timer in range(150):
    arduino.set_motors(1,1)
    time.sleep(tsleep)
    arduino.set_motors(-1,-1)
    time.sleep(tsleep)

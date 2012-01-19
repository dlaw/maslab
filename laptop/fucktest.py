import arduino
import time

time.sleep(2)
timer=0
if (not arduino.is_alive()):
	print "arduino is dead"
else:	
	while (timer < 150):
		arduino.set_motors(1,-1)
		time.sleep(1)
		arduino.set_motors(-1,1)
		time.sleep(1)
		timer+=1
	timer = 0
	while (timer < 150):
		arduino.set_motors(1,1)
		time.sleep(1)
		arduino.set_motors(1,1)
		time.sleep(1)
		timer+=1

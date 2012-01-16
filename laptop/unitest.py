import arduino
import numpy 
import time

ticks = [0,0]

if (not arduino.is_alive()):
	print "Arduino's dead!"
else:
	print "Arduino is alive \n"
	time.sleep(1)
	for x in numpy.arange(-1,1,.1):
		ticks = arduino.get_ticks()
		print "left ticks:   "+str(ticks[0])
		print "right ticks:  "+str(ticks[1])
		print "set motors "+str(x)+", "+str(x)+": "
		print str(arduino.set_motors(x,x))
		time.sleep(0.3)
	

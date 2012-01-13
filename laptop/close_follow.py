from arduino import *
from time import *

ldist = 0
rdist = 0
drive = 0

while(True):
	set_motors(50,50)
	sleep(1/10.0)
	ldist = get_ir(2)
	set_motors(-50,-50)
	sleep(2/10.0)
	rdist = get_ir(2)
	if (rdist>ldist):
		set_motors(-70,-70)
	else:
		set_motors(70,70)
	sleep(3/2.0)


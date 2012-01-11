import sys, time
sys.path.append("../Libraries/")
import arduino

if __name__=="__main__":
    try:
        ard = arduino.Arduino()
        motor0 = arduino.Motor(ard,0) #0 is the Qik number
        servo = arduino.Servo(ard,3) #3 is the port number
        IRSensor = arduino.AnalogSensor(ard,5)
        bumpSensor = arduino.DigitalSensor(ard,52)
        

        ard.start()
        while not ard.portOpened: True #Wait for the arduino to be ready, before sending commands

        for i in range(30):
            #print "Motor"
            #motor0.setVal(i*5)
            #time.sleep(.1)
            #print "Servo"
            #servo.setAngle(i*3)
            #time.sleep(.1)
            print "IR"
            print IRSensor.getValue()
            #time.sleep(.1)
            print "bump"
            print bumpSensor.getValue()

        ard.close()
    #This is so that when you hit ctrl-C in the terminal, all the arduino threads close. You can do something similar with threads in your program.
    except KeyboardInterrupt:
        print "Ending Program"
        ard.killReceived=True
        

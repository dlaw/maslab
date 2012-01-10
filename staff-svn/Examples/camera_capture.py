import cv

#Initialize the displaying window:
cv.NamedWindow("Capture Example", cv.CV_WINDOW_AUTOSIZE)

#Initialize the camera
capture = cv.CaptureFromCAM(0) 
#The number is the device number, and could be either 0 or 1. The other one is the integrated webcam.

def repeat():
    #Capture an image from the camera
    image = cv.QueryFrame(capture)

    #Get the (B,G,R,alpha?) values from the image, at the position (100,100)
    #This may be useful for analyzing the image
    cv.Get2D(image,100,100)
    
    #Display the image in the window
    cv.ShowImage("Capture Example",image)

    #Wait 10ms, allowing the image to display.
    cv.WaitKey(10)

while True:
    repeat()

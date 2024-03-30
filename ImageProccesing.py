import cv2 as cv
import numpy as np
import os
import subprocess
import signal
from time import sleep
from gpiozero import AngularServo
import math
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

def killgphoto2process():
    p= subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    our, err = p.communicate()
    for line in out.splitlines():
        if b'gvfsd-gphoto3' in line:
            pid = int(line.split(None,1)[0])
            os.kill(pid, signal.SIGKILL)
            
factory = PiGPIOFactory()
servo = AngularServo(18, min_pulse_width=0.4/1000, max_pulse_width=2.5/1000, pin_factory=factory)
servo.angle=-45

path = '/home/tejas/Desktop/capture_preview.jpg'


#Take Base Capture
subprocess.Popen(['gphoto2','--capture-preview','--force-overwrite'])


#Process Base Capture
img = cv.imread(path)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
gray = cv.GaussianBlur(gray, (5, 5), 0)


#Extrapolate Position of Tracking Object
(minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(gray)
origin=(np.array(maxLoc)[0])
print(origin)


sleep(3)


#Take Subsequent Capture
subprocess.Popen(['gphoto2','--capture-preview','--force-overwrite'])


#Pre-Proccess Subsequent Capture
img = cv.imread(path)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
gray = cv.GaussianBlur(gray, (5, 5), 0)


#Extrapolate Position of Tracking Object
(minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(gray)
alter=(np.array(maxLoc)[0])
print(alter)


#Find Difference between Captures
print(origin-alter)


#Servo Movement
x=(origin-alter)*0.1
print(x)
if x>-46 and x<46:
    servo.angle=(x-45)
    print(x-45)
else:
    print("Error:",x,"greater than 45 degrees or less than -45 degrees")




# path=r'/home/tejas/IMG_0011.CR2'
# count = 0
# while (count<2):
# #Image Proccessing
#     img = cv.imread(path)
#     img= cv.resize(img, None, fx=0.25, fy=0.25, interpolation = cv.INTER_CUBIC)
#     gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
#     gray = cv.GaussianBlur(gray, (5, 5), 0)
# 
#     #Finding brightest pixel
#     (minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(gray)
#     cv.circle(img, maxLoc, 5, (255, 0, 0), 2)
#     origin=(np.array(maxLoc)[0])
#     print(origin)
#     count=count+1
#     path=r'/home/tejas/IMG_0019.CR2'
#     str='preview'
#     
#     
#     
# cv.waitKey(0)
# cv.destroyAllWindows()

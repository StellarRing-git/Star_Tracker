import os
import sys
import cv2 as cv
import numpy as np
import fileinput
import os.path
import re
from time import sleep

def replace():
    file_handle = open('Stel_Sim.ssc', 'r')
    file_string = file_handle.read()
    file_handle.close()

    angle = 2
    subst = str('var a = '+ str(angle))
    print(subst)
    file_string = (re.sub('var a = angle_replace', subst, file_string))
    print(file_string)

    file_handle = open('Stel_Sim.ssc', 'w')
    file_handle.write(file_string)
    file_handle.close()

    print('Replaced')
    sleep(10)


    file_string = (re.sub(subst, 'var a = angle_replace', file_string))

    file_handle = open('Stem_sim.ssc', 'w')
    file_handle.write(file_string)
    file_handle.close()


# angle =  1
# angle_replace = str(angle)

# for i, line in enumerate(fileinput.input('Stel_Sim.ssc', inplace=True)):
#     print line.replace('angle_replace', angle_replace))  

# print('Replaced')
# sleep(20)

# for i, line in enumerate(fileinput.input('Stel_Sim.ssc', inplace=True)):
#     sys.stdout.write(line.replace(angle_replace, 'angle_replace'))  

# file = 'Stel_Sim.ssc'
# f = open(file)
# for line in f:
#     if line.contains('foo'):
#         newline = line.replace('foo', 'bar')
#         # how to write this newline back to the file

replace()
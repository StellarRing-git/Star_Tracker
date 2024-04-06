
import sys
import fileinput
import os
from time import sleep
import numpy as np

negative = False
angle = 10 
count = int(angle*1/1.8)
list = [1,2,3,4]

if angle < 0 and negative == False:
    list.reverse()
    count = -count
    for i in range(count+1):
        list.append(list.pop(0))
    print(list)
    negative = True

elif angle < 0:
    list.reverse()
    print(list)

else:
    for i in range(count):
        list.append(list.pop(0))
print(list)


list_replace = str('/' + str(list[0]) + '/')
print(list_replace)

for i, line in enumerate(fileinput.input('Mtr_Driver.pyi', inplace=1)):
    sys.stdout.write(line.replace('angle_replace', str(angle)))  
for i, line in enumerate(fileinput.input('Mtr_Driver.pyi', inplace=1)):
    sys.stdout.write(line.replace('list_replace', list_replace))  

os.system('cmd /c ampy --port COM5 put Mtr_Driver.pyi')
print('put')
sleep(1)
print('run')
os.system('cmd /c ampy --port COM5 run Mtr_Driver.pyi')

for i, line in enumerate(fileinput.input('Mtr_Driver.pyi', inplace=1)):
    sys.stdout.write(line.replace(str(angle), 'angle_replace'))  
for i, line in enumerate(fileinput.input('Mtr_Driver.pyi', inplace=1)):
    sys.stdout.write(line.replace(list_replace, 'list_replace'))  
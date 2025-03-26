import sys
import fileinput
import os
from time import sleep
import numpy as np

class Trckr():

    def __init__(self):
        self.negative = None
        self.list = [1,2,3,4]
        self.running = True
        while self.running == True:
            angle = float(input('Angle: '))
            count = int((angle*1/1.8)*3)        # To account for angle per step and gear ratio (3:1)
            print(count)
            self.run(angle, count)

    def run(self, angle, count):
        print(self.list)

        if count < 0 and self.negative == None:
            self.negative = 0 
        elif count > 0 and self.negative == None:
            self.negative = 3
                        
        if count < 0 and self.negative == 0:
            self.list.reverse()
            count = -count
            print(self.list)

            for i in range(count+1):
                self.list.append(self.list.pop(0))
                print(self.list)

            self.file_replace(angle)
            print('negative')
            self.negative = 1

        elif count < 0 and self.negative == 1:
            for i in range(count):
                self.list.append(self.list.pop(0))
                print(self.list)
                
            self.file_replace(angle)

        elif count > 0 and self.negative == 3:
            for i in range(count):
                self.list.append(self.list.pop(0))
                print(self.list)
            
            self.negative = 3
            print('positive')
            self.file_replace(angle)

        elif count > 0 and self.negative == 1:
            print('Error: Unexpected change in direction, please check your camera movement')
            self.running = False

        elif count < 0 and self.negative == 3:
            print('Error: Unexpected change in direction, please check your camera movement')
            self.running = False

        print(self.list)

    def file_replace(self, angle):
        angle_replace = str('/' + str(angle) + '/')
        list_replace = str('/' + str(self.list[0]) + '/')

        for i, line in enumerate(fileinput.input('Mtr_Driver.pyi', inplace=1)):
            sys.stdout.write(line.replace('angle_replace', angle_replace))  
        for i, line in enumerate(fileinput.input('Mtr_Driver.pyi', inplace=1)):
            sys.stdout.write(line.replace('list_replace',list_replace))  

        os.system('cmd /c ampy --port COM8 put Mtr_Driver.pyi')
        print('put')
        sleep(1)
        print('run')
        os.system('cmd /c ampy --port COM8 run Mtr_Driver.pyi')

        for i, line in enumerate(fileinput.input('Mtr_Driver.pyi', inplace=1)):
            sys.stdout.write(line.replace(angle_replace, 'angle_replace'))  
        for i, line in enumerate(fileinput.input('Mtr_Driver.pyi', inplace=1)):
            sys.stdout.write(line.replace(list_replace, 'list_replace'))  


    

Trckr = Trckr() 
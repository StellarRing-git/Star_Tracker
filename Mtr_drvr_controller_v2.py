import sys
import fileinput
import os
from time import sleep
import numpy as np

class Trckr():

    def __init__(self):
        self.negative = None
        self.iter = 1
        self.running = True
        while self.running == True:
            angle = float(input('Angle: '))
            count = int((angle*1/1.8)*3)        # To account for angle per step and gear ratio (3:1)
            print('count = ', count)
            self.run(angle, count)

    def run(self, angle, count):

        self.file_replace(angle)
        print(self.iter)
                        
        if count > 0:
            for i in range(count):
                if self.iter < 4:
                    self.iter = self.iter + 1
                else:
                    self.iter = 1
                print(self.iter)

        else:
            count = -count
            for i in range(count):
                if self.iter > 1:
                    self.iter = self.iter - 1
                else:
                    self.iter = 4
                print(self.iter)



    def file_replace(self, angle):
        angle_replace = str('/' + str(angle) + '/')
        iter_replace = str('/' + str(self.iter) + '/')

        for i, line in enumerate(fileinput.input('Mtr_Driver_v2.pyi', inplace=1)):
            sys.stdout.write(line.replace('angle_replace', angle_replace))  
        for i, line in enumerate(fileinput.input('Mtr_Driver_v2.pyi', inplace=1)):
            sys.stdout.write(line.replace('iter_replace',iter_replace))  

        os.system('cmd /c ampy --port COM8 put Mtr_Driver_v2.pyi')
        print('put')
        print('run')
        os.system('cmd /c ampy --port COM8 run Mtr_Driver_v2.pyi')

        for i, line in enumerate(fileinput.input('Mtr_Driver_v2.pyi', inplace=1)):
            sys.stdout.write(line.replace(angle_replace, 'angle_replace'))  
        for i, line in enumerate(fileinput.input('Mtr_Driver_v2.pyi', inplace=1)):
            sys.stdout.write(line.replace(iter_replace, 'iter_replace'))  
        print('Run Complete')

        
Trckr = Trckr() 
import sys
import fileinput
import cv2 as cv
import os.path
import os
import glob
import json
from time import sleep
import numpy as np
from PIL import Image
import requests
from urllib.request import urlopen, Request
from astropy.table import Table
import subprocess
import shutil
import math


class Trckr():
    def json2python(self,data):
        try:
            return json.loads(data)
        except:
            pass
        return None
    
    def __init__(self):
        self.fl = int(input("Focal Length: "))
        self.fov = (360*math.atan(22.3/(2*self.fl)))/math.pi
        print(self.fov)
        self.K = float(input("Constant K: "))
        folder_path = "C:\\Users\\tejas\\OneDrive\\Pictures\\Test\\*.jpg"
        self.files = [os.path.normpath(i) for i in glob.glob(folder_path)]
        i = 0
        ref = True
        self.negative = None
        self.list = [1,2,3,4]
        self.running = True

        while self.running == True:
            files_1 = [os.path.normpath(i) for i in glob.glob(folder_path)]

            try:
                max_file = max(files_1, key=os.path.getctime)
                run = True
                sleep(1)

            except: 
                run = False
                print('No files in folder')
                sleep(1)

            if run == True:
                if max_file in self.files:
                    print("No new files") 
                else:
                    print("Found a file!")
                    i = i + 1
                    self.files = files_1

                if i == 1 and ref == True:
                    ref = False
                    print('ref')
                    self.Astrometry(max_file)
                    self.ref_x = self.pos_x 
                    print('ref_x = ',self.ref_x)
                    sleep(3)

                if i == 2 and ref == False:
                    i = 1
                    print('alt')
                    self.Astrometry(max_file)
                    self.alt_x = self.pos_x 
                    print('alt_x = ',self.alt_x)
                    self.change_x = self.ref_x - self.alt_x
                    self.calc_angle()
                    sleep(3)
                sleep(2)




    def Astrometry(self,filename):
        jpg = cv.imread(filename)
        gray = cv.cvtColor(jpg, cv.COLOR_BGR2GRAY)
        gray = cv.GaussianBlur(gray, (5, 5), 0)
        (minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(gray)
        self.pos_x=(np.array(maxLoc)[0])
        self.width = jpg.shape[1]

    

    def calc_angle(self):
        print("calculating Angle")
        angle = self.K * ((-4.25 * self.fov * self.change_x) /  (2 * self.width)) 
        count = int(angle*1/1.8)
        print(angle)

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

        os.system('cmd /c ampy --port COM5 put Mtr_Driver.pyi')
        print('put')
        print('run')
        os.system('cmd /c ampy --port COM5 run Mtr_Driver.pyi')

        for i, line in enumerate(fileinput.input('Mtr_Driver.pyi', inplace=1)):
            sys.stdout.write(line.replace(angle_replace, 'angle_replace'))  
        for i, line in enumerate(fileinput.input('Mtr_Driver.pyi', inplace=1)):
            sys.stdout.write(line.replace(list_replace, 'list_replace')) 


    def extract_xy(self,data):
        while True:
            if int(data[self.p][0]) > self.width/8 and int(data[self.p][0]) < (self.width/8)*7:
                if int(data[self.p][1]) > self.width/8 and int(data[self.p][1]) < (self.width/8)*7:
                    self.coordinate = [int(data[self.p][0]), int(data[self.p][1])]
                    self.p = self.p + 1
                    break
                else:
                    self.p = self.p + 1
            else:
                self.p = self.p + 1



Trckr = Trckr()
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
        folder_path = "C:\\Users\\tejas\\OneDrive\\Pictures\\Test\\*.CR2"
        self.files = [os.path.normpath(i) for i in glob.glob(folder_path)]
        i = 0
        ref = True
        while True:
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
                    ref = False
                    print('alt')
                    i = 1
                    self.Astrometry(max_file)
                    self.alt_x = self.pos_x 
                    print('alt_x = ',self.alt_x)
                    self.change_x = self.ref_x - self.alt_x
                    self.calc_angle()
                    self.alt_x = self.ref_x
                    sleep(3)
                sleep(2)




    def Astrometry(self,filename):
        img = Image.open(filename)
        self.width = img.width 
        self.height = img.height 
        rgb_img = img.convert('RGB')
        file_name = os.path.basename(filename)
        file_without_ext = os.path.splitext(file_name)[0]
        self.jpg_filename = str("C:\\Users\\tejas\\OneDrive\\Pictures\\Test\\" + file_without_ext + ".jpg")
        rgb_img.save(self.jpg_filename)
        
        jpg = cv.imread(self.jpg_filename)
        gray = cv.cvtColor(jpg, cv.COLOR_BGR2GRAY)
        gray = cv.GaussianBlur(gray, (5, 5), 0)
        (minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(gray)
        self.pos_x=(np.array(maxLoc)[0])

    

    def calc_angle(self):
        print("calculating Angle")
        angle = self.K * ((self.fov * self.change_x) /  self.width) 
        print(angle)

        for i, line in enumerate(fileinput.input('Mtr_Driver.pyi', inplace=1)):
            sys.stdout.write(line.replace('angle_replace', str(angle)))  


        os.system('cmd /c ampy --port COM5 put Mtr_Driver.pyi')
        print('put')
        sleep(1)
        print('run')
        os.system('cmd /c ampy --port COM5 run Mtr_Driver.pyi')

        for i, line in enumerate(fileinput.input('Mtr_Driver.pyi', inplace=1)):
            sys.stdout.write(line.replace(str(angle), 'angle_replace'))  
    

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
#Trckr.__init__()
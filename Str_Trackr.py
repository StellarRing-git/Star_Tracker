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
        self.count_annote = 0
        self.ref_bol = True
        self.list = [1,2,3,4]
        self.negative = None
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

                if i == 1 and self.ref_bol == True:
                    print('ref')
                    self.ref_bol = False
                    self.Astrometry(max_file)
                    print('ref position = ', self.ref)
                    sleep(3)

                if i == 2 and self.ref_bol == False:
                    print('alt')
                    i = 1
                    self.Astrometry(max_file)
                    print('alt position = ', self.alt)
                    self.change = self.ref - self.alt
                    print('delta = ',self.change)
                    self.calc_angle()
                    self.ref = self.alt
                    sleep(3)
                sleep(2)




    def Astrometry(self,filename):
        img = Image.open(filename)
        self.width = img.width 
        print(self.width)
        self.height = img.height 
        rgb_img = img.convert('RGB')
        file_name = os.path.basename(filename)
        file_without_ext = os.path.splitext(file_name)[0]
        self.jpg_filename = str("C:\\Users\\tejas\\OneDrive\\Pictures\\Test\\" + file_without_ext + ".jpg")
        rgb_img.save(self.jpg_filename)
        args_scale_lowerbounds = str('--scale-lower=' + str(self.fl-15))
        args_scale_upperbounds = str('--scale-upper=' + str(self.fl-15))

        #upload file and retrieve jobcode
        args = ['C:/Users/tejas/AppData/Local/Microsoft/WindowsApps/python3.11.exe','c:/Users/tejas/OneDrive/Documents/GitHub/Star_Tracker/client/client.py', '-k', 'klibzlkytzeuqvhj', '-u', self.jpg_filename]

        result = subprocess.run(args, capture_output=True, universal_newlines=True)
        print(result.stderr)

        file = open("C:\\Users\\tejas\\OneDrive\\Documents\\GitHub\\Star_Tracker\\subid.txt", "r+")
        subid = file.read()
        file.close()
        file = open("C:\\Users\\tejas\\OneDrive\\Documents\\GitHub\\Star_Tracker\\subid.txt", "w+")
        file.write('None')
        file.close()
        
        print("Requesting Job ID")
        x = True
        while x == True:
            url = str('http://nova.astrometry.net/api/submissions/' + str(subid))
            R = requests.post(url)
            data = R.content.decode("ascii")
            data = np.array(R.text.split(','))
            n = len(data[5]);
            tillNow = "";
            for i in range(n) :
                    if (ord(data[5][i]) - ord('0') >= 0 and ord(data[5][i]) - ord('0') <= 9) :
                        tillNow += data[5][i];
                    else :
                        if (len(tillNow) > 0) :
                            jobid = int(tillNow)
                            tillNow = "";
                            x = False
                            break
                            
            if (len(tillNow) > 0) :
                jobid = int(tillNow)
                x = False
                break
            sleep(3)

        jobid = str(jobid)


        print("Requesting Annotations")
        while x == False:
            try:
                request = str("http://nova.astrometry.net/api/jobs/" + jobid + "/annotations/")
                f = urlopen(request)
                txt = f.read()
                result = self.json2python(txt)
                dict = result['annotations']
                x = True

            except:
                print("Waiting")
                sleep(2)

        try:
            print(self.index)
            if dict[self.index].get('names') == self.name:
                print('alt1')
                self.alt = dict[self.index].get('pixelx')
                self.index = None
                print(self.alt)

            else:
                for i in range(len(dict)):
                    if dict[i].get('names') == self.name:
                        print('alt2')
                        self.alt = dict[i].get('pixelx')
                        self.index = None
                        print(self.alt)

                    else:
                        print("Error: Unable to find ref star")

        except:
            print('ref')
            if len(dict[0]) == 6:
                y = 10
                for i in range(len(dict)):
                    if dict[i].get('vmag') < y:
                        x = dict[i].get('vmag')
                        self.index = i

            elif len(dict[0]) == 5:
                y = -1
                for i in range(len(dict)):
                    if dict[i].get('radius') > y:
                        x = dict[i].get('radius')
                        self.index = i

            else:
                print("Error: Undefined Annotations")

            self.name = dict[self.index].get('names')
            self.ref = dict[self.index].get('pixelx')

        # fn = "C:\\Users\\tejas\Downloads\\axy.fits"

        # while x == False:

        #     try:
        #         with urlopen(axy_url) as r:
        #             with open(fn, 'wb') as w:
        #                 shutil.copyfileobj(r, w)
        #                 x = True

        #     except Exception as error:
        #         print('Waiting')
        #         sleep(1)
        #         pass

        #     if x == True:
        #         t = Table.read(fn)
        #         t.sort('FLUX')
        #         t.reverse()
        #         self.p = 0
        #         self.extract_xy(t)
        #         self.xy_1 = self.coordinate
        #         self.extract_xy(t)
        #         self.xy_2 = self.coordinate

    

    def calc_angle(self):
        print("calculating Angle")
        angle = self.K * ((self.fov * self.change) /  (2 * self.width)) 
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
            sys.stdout.write(line.replace('self.list_replace',list_replace))  

        os.system('cmd /c ampy --port COM5 put Mtr_Driver.pyi')
        print('put')
        sleep(1)
        print('run')
        os.system('cmd /c ampy --port COM5 run Mtr_Driver.pyi')

        for i, line in enumerate(fileinput.input('Mtr_Driver.pyi', inplace=1)):
            sys.stdout.write(line.replace(angle_replace, 'angle_replace'))  
        for i, line in enumerate(fileinput.input('Mtr_Driver.pyi', inplace=1)):
            sys.stdout.write(line.replace(list_replace, 'self.list_replace'))  
 


Trckr = Trckr()
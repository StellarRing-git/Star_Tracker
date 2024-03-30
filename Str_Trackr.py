from rawkit import raw
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
import subprocess

class Trckr():
    def json2python(self,data):
        try:
            return json.loads(data)
        except:
            pass
        return None
    
    def extract_xy(self,p,data):
            sub_data = np.array(data[p].split(','))
            self.coordinate = str('xy'+str(p-2))
            self.coordinate = [sub_data[3],sub_data[4]]
            for t in sub_data[3].split():
                try:
                    self.coordinate[0] = int((float(t)))
                except ValueError:
                    pass
            for t in sub_data[4].split():
                try:
                    self.coordinate[1] = int((float(t)))
                except ValueError:
                    pass
    
    def __init__(self):
        folder_path = "C:\\Users\\tejas\\OneDrive\\Pictures\\Test\\*.CR2"
        self.files = [os.path.normpath(i) for i in glob.glob(folder_path)]
        i = 0
        ref = True
        while True:
            files_1 = [os.path.normpath(i) for i in glob.glob(folder_path)]

            #try:
            max_file = max(files_1, key=os.path.getctime)
            if max_file in self.files:
                print("No new files") 
            else:
                print("Found a file!")
                i = i + 1
                self.files = files_1

            if i == 1 and ref == True:  #debug  (if i == 1:)
                self.Astrometry(max_file)
                self.ref_xy_1 = np.array(self.xy_1)
                self.ref_xy_2 = np.array(self.xy_2)
                print(self.ref_xy_1)
                print(self.ref_xy_2)
                self.ref_dist = self.ref_xy_1 - self.ref_xy_2
                print(self.ref_dist)
                ref = False

            if i == 2 and ref == False:
                ref = True
                i = 0
                self.Astrometry(max_file)
                self.alt_xy_1 = np.array(self.xy_1)
                self.alt_xy_2 = np.array(self.xy_2)
                print(self.alt_xy_1)
                print(self.alt_xy_2)
                self.alt_dist = self.alt_xy_1 - self.alt_xy_2
                print(self.alt_dist)
                self.change_xy = self.ref_dist - self.alt_dist
                print(self.change_xy)
            sleep(5)

            # except:
            #     print("No files in folder")
            #     sleep(2)



    def Astrometry(self,filename):
        img = Image.open(filename)
        rgb_img = img.convert('RGB')
        file_name = os.path.basename(filename)
        file_without_ext = os.path.splitext(file_name)[0]
        self.jpg_filename = str("C:\\Users\\tejas\\OneDrive\\Pictures\\Test\\" + file_without_ext + ".jpg")
        rgb_img.save(self.jpg_filename)

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
        
        x = True
        while x == True:
            url = str('http://nova.astrometry.net/api/submissions/' + str(subid))
            R = requests.post(url)
            data = R.content.decode("ascii")
            print(data)
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
        annotation_url = str("http://nova.astrometry.net/api/jobs/" + jobid + "/annotations/")

        while x == False:
            R = requests.post(annotation_url)
            data = R.content.decode("ascii")
            data = np.array(R.text.split('}'))
            if data.size == 2:
                sleep(5)
                pass
            else:
                self.extract_xy(3,data)
                self.xy_1 = self.coordinate
                self.extract_xy(2,data)
                self.xy_2 = self.coordinate
                x = True 




Trckr = Trckr()
#Trckr.__init__()
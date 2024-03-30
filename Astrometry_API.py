import requests
import json
from astropy.table import Table
from astropy.io import fits
from astropy.io import ascii
import numpy as np
from urllib.request import urlopen, Request
import shutil
import re

R = requests.post('http://nova.astrometry.net/api/jobs/10259787/annotations/')

data = R.content.decode("ascii")
data = np.array(R.text.split('}'))
print(data.size)
x = data.size-3


def extract_xy(p):
    sub_data = np.array(data[p].split(','))
    coordinate = str('xy'+str(p-2))
    coordinate = [sub_data[3],sub_data[4]]
    for t in sub_data[3].split():
        try:
            coordinate[0] = int((float(t)))
        except ValueError:
            pass
    for t in sub_data[4].split():
        try:
            coordinate[1] = int((float(t)))
        except ValueError:
            pass

    print(coordinate)

extract_xy(3)
extract_xy(2)


#R_1 = str(R.content)
#data = np.rec.array[R_1]
#fits.writeto('jp',data)


import requests
import json
def json2python(data):
    try:
        return json.loads(data)
    except:
        pass
    return None
python2json = json.dumps

from astropy.table import Table
from astropy.io import fits
from astropy.io import ascii
import numpy as np
import requests
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import shutil
import re


request = str('http://nova.astrometry.net/api/jobs/10265390/annotations/')


f = urlopen(request)
txt = f.read()
result = json2python(txt)
dict = result['annotations']


if len(dict[0]) == 6:
    y = 10
    for i in range(len(dict)):
        if dict[i].get('vmag') < y:
            x = dict[i].get('vmag')
            index = i

    print(dict[list[len(list)-1]].get('names'))

elif len(dict[0]) == 5:
    y = -1
    for i in range(len(dict)):
        if dict[i].get('radius') > y:
            x = dict[i].get('radius')
            index = i

    print(dict[index].get('names'))

else:
    print("Error: Undefined Annotations")

x = dict[index].get('pixelx')
print(x)

import sys
import fileinput
import os
from time import sleep

print('start')
for i, line in enumerate(fileinput.input('pico.pyi', inplace=1)):
    sys.stdout.write(line.replace('angle', '25'))  

os.system('cmd /c ampy --port COM5 put pico.pyi')
print('put')
sleep(1)
print('run')
os.system('cmd /c ampy --port COM5 run pico.pyi')

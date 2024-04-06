from time import sleep
from machine import Pin

class drvr():
    def __init__(self):
        self.p18 = Pin(18, Pin.OUT)
        self.p19 = Pin(19, Pin.OUT)
        self.p20 = Pin(20, Pin.OUT)
        self.p21 = Pin(21, Pin.OUT)
        self.p18.on()
        self.p19.off()
        self.p20.on()
        self.p21.off()

    def step(self):
        self.PIN_LOW.off()
        self.PIN_HIGH.on()

    def run(self,angle):
        print(angle)
        count = int(angle*1/1.8)
        list = [1,2,3,4]


        if count < 0:
            count = -count
            list = [4,3,2,1]

        for i in range(count):
            if list[0] == 1:
                self.PIN_LOW = self.p18
                self.PIN_HIGH = self.p19
            if list[0] == 2:
                self.PIN_LOW = self.p20
                self.PIN_HIGH = self.p21
            if list[0] == 3:
                self.PIN_LOW = self.p19
                self.PIN_HIGH = self.p18
            if list[0] == 4:
                self.PIN_LOW = self.p21
                self.PIN_HIGH = self.p20
            self.step()
            list.append(list.pop(0))
            sleep(0.1)




drvr = drvr()

while True:
    key = input("press key: ")
    if key == ',':
        print(',')
        drvr.run(5)
    elif key == '.':
        print('.')
        drvr.run(-5)
    elif key == 'k':
        print('<')
        drvr.run(10)
    elif key == 'l':
        print('>')
        drvr.run(-10)
    else:
        try:
            key = float(key)
            drvr.run(key)
        except:
            print("invalid key")

    sleep(0.01)
    # else:
    #     try:
    #         print('key')
    #         drvr.run(key())
    #     except:
    #         print("Invalid")
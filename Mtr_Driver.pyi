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

    def run(self):
        #angle = float(input("Please enter angle: "))
        angle = float(360)
        count = int(angle*1/1.8)
        list = [1,2,3,4]


        if count < 0:
            count = -count
            list = [4,3,2,1]

        for i in range(count):
            if list[0] == 1:
                self.PIN_LOW = self.p18
                self.PIN_HIGH = self.p19
                print(1)
            if list[0] == 2:
                self.PIN_LOW = self.p20
                self.PIN_HIGH = self.p21
                print(2)
            if list[0] == 3:
                self.PIN_LOW = self.p19
                self.PIN_HIGH = self.p18
                print(3)
            if list[0] == 4:
                self.PIN_LOW = self.p21
                self.PIN_HIGH = self.p20
                print(4)
            self.step()
            list.append(list.pop(0))
            sleep(0.02)

drvr = drvr()
drvr.run()

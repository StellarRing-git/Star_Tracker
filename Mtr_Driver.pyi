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
        angle = 'angle_replace'
        angle = float(angle.replace('/', ''))
        count = int(angle*1/1.8)

        list = [1,2,3,4]
        list_count = 'list_replace'
        list_count = int(list_count.replace('/', ''))

        if count < 0:
            count = -count
            list.reverse()

        for i in range(list_count-1):
            list.append(list.pop(0))

        if list[0] == 1 or list[0] == 4:
            self.p18.on()
            self.p19.off()
            self.p20.on()
            self.p21.off()
            print('1 or 4')

        if list[0] == 2:
            self.p18.off()
            self.p19.on()
            self.p20.off()
            self.p21.on()

        if list[0] == 3:
            self.p18.on()
            self.p19.off()
            self.p20.off()
            self.p21.on()


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
                print('')
            self.step()
            list.append(list.pop(0))
            sleep(1)
drvr = drvr()
drvr.run()

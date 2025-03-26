from time import sleep
from machine import Pin

class drvr():
    def __init__(self):
        self.p18 = Pin(18, Pin.OUT)
        self.p19 = Pin(19, Pin.OUT)
        self.p20 = Pin(20, Pin.OUT)
        self.p21 = Pin(21, Pin.OUT)
    
    def step(self):
        if self.iter == 1:
            self.p18.on()
            self.p19.off()
            self.p20.on()
            self.p21.off()

        if self.iter == 2:
            self.p18.off()
            self.p19.on()
            self.p20.on()
            self.p21.off()

        if self.iter == 3:
            self.p18.off()
            self.p19.on()
            self.p20.off()
            self.p21.on()
        
        if self.iter == 4:
            self.p18.on()
            self.p19.off()
            self.p20.off()
            self.p21.on()
        
        sleep(1)

    def run(self):
        angle = 'angle_replace'  
                                
        angle = float(angle.replace('/', ''))
        count = int((angle*1/1.8)*3)            # To account for angle per step and gear ratio (3:1)
        print('count = ', count )                

        self.iter = 'iter_replace'
        self.iter = int(self.iter.replace('/', ''))
        print(self.iter)

        if count > 0:
            for i in range(count):
                if self.iter < 4:
                    self.iter = self.iter + 1
                else:
                    self.iter = 1
                
                print(self.iter)
                self.step()

        if count < 0:
            count = -count

            for i in range(count):               
                if self.iter > 1:
                    self.iter = self.iter - 1
                else:
                    self.iter = 4

                print(self.iter)
                self.step()

drvr = drvr()
drvr.run()

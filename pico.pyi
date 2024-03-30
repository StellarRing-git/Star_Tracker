from machine import Pin, Timer



led1 = Pin(21, Pin.OUT)
led2 = Pin(20, Pin.OUT)

led2.on()
led1.off()
from machine import Pin, Timer

x = int(angle)

led = Pin(x, Pin.OUT)
timer = Timer()
from time import sleep

def blink():
    led.toggle()

while True:
    blink()
    sleep(0.5)
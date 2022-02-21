import RPi.GPIO as io
import time
io.setmode(io.BCM)

pin = 18

io.setup(pin, io.OUT)
p = io.PWM(pin, 50) # GPIO 18 for PWM with 50Hz
p.start(2.5) # Initialization
time.sleep(1)
p.stop()

try:
  while False:
    p.ChangeDutyCycle(5)
    time.sleep(0.5)
    p.ChangeDutyCycle(7.5)
    time.sleep(0.5)
    p.ChangeDutyCycle(10)
    time.sleep(0.5)
    p.ChangeDutyCycle(7.5)
    time.sleep(0.5)
    p.ChangeDutyCycle(5)
    time.sleep(0.5)
    p.ChangeDutyCycle(2.5)
    time.sleep(0.5)
except:
  p.stop()
  print('pwm stopped')
  io.cleanup()
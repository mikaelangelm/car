import RPi.GPIO as io
import time
io.setmode(io.BCM)

# import Cam, Car # cam = Cam.Cam() # car = Car.Car()
# sens = Car.Sensor()
# print(sens.get_obstacles())

try:
    while True:
        io.setup(17, io.OUT)
        io.output(17, 1)
except KeyboardInterrupt:
    io.cleanup()

while False:   
    cam.get_photo_return_objects()
    print('+')
    time.sleep(3)

# approximity sensor MH-B test

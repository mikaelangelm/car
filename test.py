# import RPi.GPIO as io
# import time
# io.setmode(io.BCM)

import Cam, Car
# cam = Cam.Cam()
# car = Car.Car()
sens = Car.Sensor()
print(sens.get_obstacles())


while False:   
    cam.get_photo_return_objects()
    print('+')
    time.sleep(3)

# approximity sensor MH-B test

# import RPi.GPIO as io
import time
# io.setmode(io.BCM)

import Cam
cam = Cam.Cam()

while True:   
    cam.get_photo_return_objects()
    print('+')
    time.sleep(3)


# out_test=17
# 
# io.setup(15, io.IN)
# io.setup(18, io.IN)
# io.setup(out_test, io.OUT)
# 
# try:
#     io.output(out_test, 1)
#     while True:
#         print(io.input(15), io.input(18))
#         time.sleep(.1)
# except KeyboardInterrupt:
#     io.cleanup()
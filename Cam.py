import cv2
import numpy as np
from PIL import Image
import time, io
from picamera import PiCamera
import requests
cam = None

# net = cv2.dnn.readNet(path + 'yolov3.cfg', path + 'yolov3.weights')

# layer_names = net.getLayerNames()
# out_layers_indexes = net.getUnconnectedOutLayers()
# out_layers = [layer_names[index - 1] for index in out_layers_indexes] # print([index for index in out_layers_indexes])
# 
# with open('coco.names.txt') as f:
#     classes = f.read().split('\n')


def apply_yolo(img, draw_object_=True):
    '''get: array-like img data 
    return: img with wrawed object boxes & boxes'''
    height,width,depth = img.shape
    blob = cv2.dnn.blobFromImage(img, 1/255, (608,608), (0,0,0), swapRB=True, crop=False)
    net.setInput(blob)
    
    _time = time.time()
    outs = net.forward(out_layers)
    print(round(time.time() - _time, 2), 'sec to net.forward')
    
    boxes = []
    class_indexes = []
    class_scores = []

    for out in outs:
        for obj in out:
            #print(obj)
            scores = obj[5:]
            class_index = np.argmax(scores)
            class_score = scores[class_index]
            if class_score > 0: 
                #print(class_index, class_score)
                center_x = int(obj[0] * width)
                center_y = int(obj[1] * height)
                obj_width = int(obj[2] * width)
                obj_height = int(obj[3] * height)

                x = center_x - obj_width // 2
                y = center_y - obj_height // 2

                box = [x,y,obj_width,obj_height]
                boxes.append(box)
                class_indexes.append(class_index)
                class_scores.append(float(class_score))
                
    object_box_list = cv2.dnn.NMSBoxes(boxes, class_scores, 0, 0.35)
    #print(chosen_boxes)
    
    xywh_name_class_list = []    
    for box_index in object_box_list:
#         box_index = box_index[0]
        xywh_name_class_list.append([boxes[box_index] + [classes[class_indexes[box_index]]] + [class_indexes[box_index]]])
        # TODO uncomment 2 debug
        img = draw_object(img, class_indexes[box_index], class_scores[box_index], boxes[box_index])
        
    return img, xywh_name_class_list


def draw_object(img, index, score, box):
    x,y,w,h = box
    start = (x,y)
    end = (x + w, y + h)
    color = (0,255,0)
    width = 1
    
    img = cv2.rectangle(img, start, end, color, width)
    
    start = (x-10, y-10)
    font_size = 1
    font = cv2.FONT_HERSHEY_SIMPLEX
    width = 1
    text = classes[index]
    
    img = cv2.putText(img, text, start, font, font_size, color, width, cv2.LINE_AA)
    
    return img

class Cam(PiCamera):
    def __init__(self):
        super().__init__() # https://picamera.readthedocs.io/en/release-1.13/recipes1.html
        self.path        = '/home/pi/Desktop/Py/car/'
        self.file_name   = 'view.jpg'
        self.file_object = io.BytesIO()
        # Запускаем предпросмотр сигнала с камеры на экране поверх всех окон cam.start_preview() cam.stop_preview()
        time.sleep(3) # AF & WB
        self.brightness = 60
        
    def get_photo_return_objects(self):
        self.brightness = 60
        self.capture(self.file_object, format='rgb')
        return requests.post('http://192.168.0.101:8080/get_objects',
                                 data=self.file_object.getvalue(),
                                 headers={'Content-Type': 'image/jpeg'},
                                 timeout=8).text    


    
# img = Image.open(path + file_name).rotate(180)
# arr = np.array(img)
# arr, xywh_name_class_list = apply_yolo(arr)
# img = Image.fromarray(arr)
# print(xywh_name_class_list)
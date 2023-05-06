# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 17:31:43 2019

@author: thetoolguy
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

#取得輸出層
def get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers

#劃出預測
def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    color = COLORS[class_id]
#    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#設定label names
classes = None
with open('3emotionobj.names', 'r') as f:
    classes = [line.strip() for line in f.readlines()]
    
cap = cv2.VideoCapture(0)
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

net = cv2.dnn.readNet('3emotionyolov3-tiny_last.weights', '3emotionyolov3-tiny.cfg')

windows = tk.Tk()
# mainWindows()
windows.title('臉部辨識系統')
windows.geometry('500x200+50+50')
windows.resizable(False, False)

var1 = tk.StringVar()
e1 = ttk.Entry(windows, textvariable=var1, width=40)
e1.place(x=200, y=70, anchor='center')

def detect():
    ret, image = cap.read()
    Width = image.shape[1]
    Height = image.shape[0]
    scale = 0.00392
    
    blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(get_output_layers(net))
    
    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4
    
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
        
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    for i in indices:
        i = i[0]
        var1.set(str(classes[class_ids[i]]))
        print(str(classes[class_ids[i]]))
        box = boxes[i]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
    windows.after(1, detect)

detect()
windows.mainloop()




cap.release()



# encoding: utf-8

import os, sys, random, globals
import pygame 
from pygame.locals import *
 
from drew2 import *

import cv2
import numpy as np
############################Define the DNN#####################
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
with open('obj.names', 'r') as f:
    classes = [line.strip() for line in f.readlines()]
    
cap = cv2.VideoCapture(0)
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

net = cv2.dnn.readNet('yolov3-tiny_last.weights', 'yolov3-tiny.cfg')
####################################################################

 
# 視窗大小.
canvas_width = 800  #原本800
canvas_height = 600  #原本600
 
# 顏色.
block = (0,0,0)
 
# 磚塊數量串列.
bricks_list = []
 
# 移動速度.
dx =  8
dy = -8
 
# 遊戲狀態.
# 0:等待開球
# 1:遊戲進行中
game_mode = 0
 
#-------------------------------------------------------------------------
# 函數:秀字.
#-------------------------------------------------------------------------
def showFont( text, x, y):
    global canvas    
    text = font.render(text, 1, (255, 0, 0)) 
    canvas.blit( text, (x,y))
 
#-------------------------------------------------------------------------
# 函數:碰撞判斷.
#   x       : x 
#   y       : y 
#   boxRect : 矩形
#-------------------------------------------------------------------------
def isCollision( x, y, boxRect):
    if (x >= boxRect[0] and x <= boxRect[0] + boxRect[2] and y >= boxRect[1] and y <= boxRect[1] + boxRect[3]):
        return True;          
    return False;  
 
#-------------------------------------------------------------------------
# 函數:初始遊戲.
#-------------------------------------------------------------------------
def resetGame():
    # 宣告使用全域變數.
    global game_mode, brick_num, bricks_list, dx, dy, brick_quantity
 

    # 0:等待開球
    game_mode = 0

    # 移動速度.
    dx =  10
    dy = -10
    
    
#臉部偵測
def detect():
    ret, image = cap.read()
    Width = image.shape[1]
    Height = image.shape[0]
    scale = 0.00392
    
    #cv2.imshow("object detection", image) #顯示畫面
    
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
        emotion = str(classes[class_ids[i]])
        print(emotion)
        if  emotion== "neutral":
            return 0
        if emotion == "happy":
            return 10
        if emotion == "surprised":
            return -10
        if emotion == "sad": 
            return -20
        if emotion == "angry": #這個不好偵測，但戴上眼鏡都是angry
            return 20
    return 0
        #print(str(classes[class_ids[i]]))
#            box = boxes[i]
#            x = box[0]
#            y = box[1]
#            w = box[2]
#            h = box[3]
#            draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
#        windowsUnZipFile.after(1, detect)

 
# 初始.
pygame.init()

# 顯示Title.
pygame.display.set_caption(u"打磚塊遊戲")
# 建立畫佈大小.
canvas = pygame.display.set_mode((canvas_width, canvas_height))
# 時脈.
clock = pygame.time.Clock()
 
# 設定字型-黑體.
font = pygame.font.SysFont('simhei', 18)
 
# 底板.
paddle_x = 0
paddle_y = (canvas_height - 48)
paddle = Box(pygame, canvas, "paddle", [paddle_x, paddle_y, 200, 15], (255,255,255))

# 底板2.
paddle2_x = 0
paddle2_y = 48
paddle2 = Box(pygame, canvas, "paddle2", [paddle2_x, paddle2_y, 200, 15], (255,255,255))
 
# 球.
ball_x = paddle_x
ball_y = paddle_y
ball   = Circle(pygame, canvas, "ball", [ball_x, ball_x], 8, (255,255,255))
 


# 初始遊戲.
resetGame()
 
#-------------------------------------------------------------------------    
# 主迴圈.
#-------------------------------------------------------------------------
running = True
while running:
    #---------------------------------------------------------------------
    # 判斷輸入.
    #---------------------------------------------------------------------
    for event in pygame.event.get():
        # 離開遊戲.
        if event.type == pygame.QUIT:
            running = False
        # 判斷按下按鈕
        if event.type == pygame.KEYDOWN:
            # 判斷按下ESC按鈕
            if event.key == pygame.K_ESCAPE:
                running = False
                
        # 底板2判斷Mouse.
        if event.type == pygame.MOUSEMOTION:
            paddle2_x = pygame.mouse.get_pos()[0] - 50
        if event.type == pygame.MOUSEBUTTONDOWN:
            if(game_mode == 0 or game_mode == 2):
                game_mode = 1
    paddle_x += detect() #臉部移動板子
    if paddle_x > canvas_width - paddle.rect[2]:  #不出右邊界
        paddle_x = canvas_width - paddle.rect[2]
    if paddle_x <= 0:  #不出左邊界
        paddle_x = 0
    if paddle2_x > canvas_width - paddle2.rect[2]:  #不出右邊界2
        paddle2_x = canvas_width - paddle2.rect[2]
    if paddle2_x <= 0:  #不出左邊界2
        paddle2_x = 0
                
    #---------------------------------------------------------------------    
    # 清除畫面.
    canvas.fill(block)
    
    
    # 秀板子.
    paddle.rect[0] = paddle_x
    paddle.update()
    
    # 秀板子2
    paddle2.rect[0] = paddle2_x
    paddle2.update()
 
    # 碰撞判斷-球碰板子.
    if(isCollision( ball.pos[0], ball.pos[1], paddle.rect)):        
        # 球反彈.
        dy = -dy;         
    # 碰撞判斷-球碰板子2.
    if(isCollision( ball.pos[0], ball.pos[1], paddle2.rect)):        
        # 球反彈.
        dy = -dy;        
            
    # 球.
    # 0:等待下開球
    if(game_mode == 0):
        ball.pos[0] = ball_x = paddle.rect[0] + ( (paddle.rect[2] - ball.radius) >> 1 )
        ball.pos[1] = ball_y = paddle.rect[1] - ball.radius
    # 2:等待上開球
    elif(game_mode == 2):
        ball.pos[0] = ball_x = paddle2.rect[0] + ( (paddle2.rect[2] - ball.radius) >> 1 )
        ball.pos[1] = ball_y = paddle2.rect[1]+ paddle2.rect[3] + ball.radius
    # 1:遊戲進行中
    elif(game_mode == 1):
        ball_x += dx
        ball_y += dy
        #判斷死亡下.
        if(ball_y + dy > canvas_height - ball.radius):
            game_mode = 2
        #判斷死亡上.
        if(ball_y + dy < ball.radius):
            game_mode = 0
        # 右牆或左牆碰撞.
        if(ball_x + dx > canvas_width - ball.radius or ball_x + dx < ball.radius):
            dx = -dx
        # 下牆或上牆碰撞
#        if(ball_y + dy > canvas_height - ball.radius or ball_y + dy < ball.radius):        
#            dy = -dy
        ball.pos[0] = ball_x
        ball.pos[1] = ball_y
 
    # 更新球.
    ball.update()
 
    # 顯示中文.
    showFont( u"FPS:" + str(clock.get_fps()), 8, 2)    
    # 更新畫面.
    pygame.display.update()
    clock.tick(60)
 
# 離開遊戲.
pygame.quit()
quit()
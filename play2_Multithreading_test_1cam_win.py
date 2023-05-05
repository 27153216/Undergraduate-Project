# encoding: utf-8

import os, sys, random,  threading, time, win32con, win32gui, win32api
import pygame 
from pygame.locals import *
 
from drew import *

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
    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 2)

#設定label names
classes = None
with open('obj.names', 'r') as f:
    classes = [line.strip() for line in f.readlines()]
    
cap0 = cv2.VideoCapture(0)
#COLORS = np.random.uniform(0, 255, size=(len(classes), 3))
COLORS = [(0,0,255),(0,255,255),(0,255,0),(255,0,0),(255,255,0)]

net = cv2.dnn.readNet('yolov3-tiny_last.weights', 'yolov3-tiny.cfg')
####################################################################
#讓聲音不延遲 buffer越大延遲越大 必須放在pygame.init前
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512) 
pygame.mixer.init()
#sound
pointSound = pygame.mixer.Sound("sound/Ice1.wav")
pointSound.set_volume(0.5)
paddleSound = pygame.mixer.Sound("sound/Blow1.wav")
paddleSound.set_volume(0.5)
ballSound = pygame.mixer.Sound("sound/Attack2.wav")
ballSound.set_volume(0.5)
winSound = pygame.mixer.Sound("sound/Win.wav")
winSound.set_volume(0.5)

# 視窗大小.
canvas_width = 800  #原本800
canvas_height = 600  #原本600
 
# 顏色.
block = (0,0,0)
 
# 磚塊數量串列.
bricks_list = []
 
# 移動速度請改下方resetgame
dx =  0
dy = -0
 
# 遊戲狀態.
# 0:等待開球
# 1:遊戲進行中
game_mode = 0
 
#-------------------------------------------------------------------------
# 函數:秀字.
#-------------------------------------------------------------------------
def showFont( text, x, y):
    global canvas    
    text = font.render(text, 1, (255, 255, 255)) 
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
    global game_mode, dx, dy,  Collision, Collision2, scoredown, scoreup
 

    # 0:等待開球
    game_mode = 0

    # 移動速度.
    dx =  5
    dy = -5
    
    Collision = False
    Collision2 = False
    
    #分數
    scoredown = 0
    scoreup = 0
    
#臉部偵測
Width = 0
def detect():
    global game_mode, dx, dy, running, Width
    ret, image = cap0.read()
    image = cv2.flip(image,1) #水平翻轉，使觀看更直覺
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
    returnx = returnx1 = returnx2 = 0
    for i in indices:
        i = i[0]
        emotion = str(classes[class_ids[i]])
        print(emotion)
        box = boxes[i]
        xxx = box[0]
        yyy = box[1]
        www = box[2]
        hhh = box[3]
        draw_prediction(image, class_ids[i], confidences[i], round(xxx), round(yyy), round(xxx+www), round(yyy+hhh))
        
        if emotion== "neutral":
            returnx = 0
        elif emotion == "sad": 
            returnx = -10
        elif emotion == "angry":
            if (game_mode == 0 and xxx+www/2 > Width/2) or (game_mode == 2 and xxx+www/2 < Width/2):
                if game_mode == 0: waitballst(0)
                else: waitballst(1)
                ballSound.play()
                if dx > 0:
                    dx = -dx
                game_mode = 1
            returnx = -10
        elif emotion == "happy":
            returnx = 10
        elif emotion == "surprised":
            if (game_mode == 0 and xxx+www/2 > Width/2) or (game_mode == 2 and xxx+www/2 < Width/2):
                if game_mode == 0: waitballst(0)
                else: waitballst(1)
                ballSound.play()
                if dx < 0:
                    dx = -dx
                game_mode = 1
            returnx = 10
        if xxx+www/2 > Width/2: 
            returnx1 = returnx
        else:
            returnx2 = returnx
    leftimg = image[0:Height, 0:int(Width*0.5)]
    rightimg = image[0:Height,int(Width*0.5):Width]
    cv2.imshow("Down", rightimg) #顯示畫面
    cv2.imshow("Up", leftimg) #顯示畫面
    k = cv2.waitKey(1)
    if k == 27:
        running = False

    return returnx1, returnx2

 
# 初始.
pygame.init()

# 顯示Title.
pygame.display.set_caption(u"臉部表情辨識及其在老態預防上的應用--雙人對戰")
# 建立畫佈大小.
canvas = pygame.display.set_mode((canvas_width, canvas_height))
# 時脈.
clock = pygame.time.Clock()
 
# 設定字型-黑體.
font = pygame.font.Font('font/msjhbd.ttc', 18)
 
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
dps = pygame.time.Clock() #第二個tick避免影響FPS
dps2 = pygame.time.Clock() #第二個tick避免影響FPS
movex = 0 #板子移動距離

#用來優化板子移動順暢
def smoothpaddle():
    global paddle_x, movex
    while running:
        paddle_x += movex
        if paddle_x > canvas_width - paddle.rect[2]:  #不出右邊界
            paddle_x = canvas_width - paddle.rect[2]
        if paddle_x <= 0:  #不出左邊界
            paddle_x = 0
        dps.tick(60) 
t2 = threading.Thread(target = smoothpaddle)
t2.start()

movex2 = 0 #板子移動距離
#用臉部表情判斷板子如何移動
def movepaddle2():
    global paddle2_x, movex2, movex
    while running:
        movex,movex2 = detect() #臉部偵測移動板子距離
        dps2.tick(15) #每秒臉部偵測次數
t_2 = threading.Thread(target = movepaddle2)
t_2.start()
#用來優化板子移動順暢
def smoothpaddle2():
    global paddle2_x, movex2
    while running:
        paddle2_x += movex2
        if paddle2_x > canvas_width - paddle2.rect[2]:  #不出右邊界
            paddle2_x = canvas_width - paddle2.rect[2]
        if paddle2_x <= 0:  #不出左邊界
            paddle2_x = 0
        dps.tick(60) 
t2_2 = threading.Thread(target = smoothpaddle2)
t2_2.start()



window = win32gui.FindWindow(None ,u'臉部表情辨識及其在老態預防上的應用--雙人對戰') #找到遊戲主視窗
windowrect = win32gui.GetWindowRect(window) #抓到主視窗的位置
#抓取螢幕解析度
screenx = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
screeny = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
win32gui.MoveWindow(window, int(screenx/2 - (windowrect[2]-windowrect[0])/2), 100, windowrect[2]-windowrect[0], windowrect[3]-windowrect[1], True) #移動主視窗到指定位置

#移動攝影機視窗
def movewindow():
    while running:
        windowrect = win32gui.GetWindowRect(window)
    #    print(windowrect[0],windowrect[1],windowrect[2],windowrect[3]) #0:左上x 1:左上y 2右下x 3右下y
        #把攝影機畫面移到主視窗旁
        cv2.moveWindow("Down",windowrect[2],windowrect[1])
        cv2.moveWindow("Up",windowrect[0] - int(Width/2) - 20,windowrect[1])
        dps.tick(15)
t3 = threading.Thread(target=movewindow)
t3.start()

def gameover(win):
    global canvas, running
    winSound.play()
    canvas.fill((0,0,0))
    winning = True
    bigfont = pygame.font.Font('font/msjhbd.ttc', 144)
    smallfont = pygame.font.Font('font/msjhbd.ttc', 30)
    while winning:
        if win == 0:
            text = bigfont.render("右方玩家勝", 1, (255, 255, 255)) 
        else:
            text = bigfont.render("左方玩家勝", 1, (255, 255, 255)) 
        stext = smallfont.render("[Enter]重新開始                  [Esc]回主選單", 1, (255, 255, 255))
        canvas.blit( text, (50,180))
        canvas.blit( stext, (100,344))
        if running == False: winning = False
        for event in pygame.event.get():
            # 離開遊戲.
            if event.type == pygame.QUIT:
                running = False
            # 判斷按下按鈕
            if event.type == pygame.KEYDOWN:
                # 判斷按下ESC按鈕
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    resetGame()
                    winning = False
        pygame.display.update()
        dps.tick(30)

def waitballst(x):
    global ball, ball_x, ball_y, paddle
    if x == 0:
        ball.pos[0] = ball_x = paddle.rect[0] + ( (paddle.rect[2] - ball.radius) >> 1 )
        ball.pos[1] = ball_y = paddle.rect[1] - ball.radius
    else:
        ball.pos[0] = ball_x = paddle2.rect[0] + ( (paddle2.rect[2] - ball.radius) >> 1 )
        ball.pos[1] = ball_y = paddle2.rect[1]+ paddle2.rect[3] + ball.radius


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
#        if event.type == pygame.MOUSEMOTION:
#            paddle2_x = pygame.mouse.get_pos()[0] - 50
#        if event.type == pygame.MOUSEBUTTONDOWN:
#            if(game_mode == 0 or game_mode == 2):
#                game_mode = 1

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
    lastCollision = Collision #上次的碰撞
    Collision = isCollision( ball.pos[0], ball.pos[1], paddle.rect) #這次的碰撞
    if(Collision): 
        if lastCollision: #如果上次也是碰撞(卡入板子)直接死亡
            pointSound.play()
            scoreup += 1
            game_mode = 2
            dy = -dy;
        else:
            paddleSound.play()
            # 球反彈.
            dy = -dy;    
            
    # 碰撞判斷-球碰板子2.
    lastCollision2 = Collision2 #上次的碰撞2
    Collision2 = isCollision( ball.pos[0], ball.pos[1], paddle2.rect) #這次的碰撞2
    if(Collision2): 
        if lastCollision2: #如果上次也是碰撞(卡入板子2)直接死亡
            pointSound.play()
            scoredown += 1
            game_mode = 0
            dy = -dy;
        else:
            paddleSound.play()
            # 球反彈.
            dy = -dy;           
            
    # 球.
    # 0:等待下開球
    if(game_mode == 0):
        waitballst(0)
#        ball.pos[0] = ball_x = paddle.rect[0] + ( (paddle.rect[2] - ball.radius) >> 1 )
#        ball.pos[1] = ball_y = paddle.rect[1] - ball.radius
    # 2:等待上開球
    elif(game_mode == 2):
        waitballst(1)
#        ball.pos[0] = ball_x = paddle2.rect[0] + ( (paddle2.rect[2] - ball.radius) >> 1 )
#        ball.pos[1] = ball_y = paddle2.rect[1]+ paddle2.rect[3] + ball.radius
    # 1:遊戲進行中
    elif(game_mode == 1):
        ball_x += dx
        ball_y += dy
        #判斷死亡下.
        if(ball_y + dy > canvas_height - ball.radius):
            pointSound.play()
            scoreup += 1
            game_mode = 2
        #判斷死亡上.
        if(ball_y + dy < ball.radius):
            pointSound.play()
            scoredown += 1
            game_mode = 0
        # 右牆或左牆碰撞.
        if(ball_x + dx > canvas_width - ball.radius or ball_x + dx < ball.radius):
            dx = -dx
        # 下牆或上牆碰撞
#        if(ball_y + dy > canvas_height - ball.radius or ball_y + dy < ball.radius):        
#            dy = -dy
        ball.pos[0] = ball_x
        ball.pos[1] = ball_y
    
    if scoredown >= 11:
        game_mode = 9
        gameover(0)
    elif scoreup >= 11:
        game_mode = 9
        gameover(1)
    
    # 更新球.
    ball.update()
 
    # 顯示FSP.分數
#    showFont( u"FPS:" + str(int(clock.get_fps())), 8, 2)    
#    showFont( u"臉部FPS:" + str(int(dps2.get_fps())), 8, 20)
    showFont( u"得分：" + str(scoredown), canvas_width/2 - 50, canvas_height - 25)
    showFont( u"得分：" + str(scoreup), canvas_width/2 - 50, 2)
    # 更新畫面.
    pygame.display.update()
    clock.tick(60)
 
# 離開遊戲.
pygame.quit()
quit()
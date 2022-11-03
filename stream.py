import threading
import cv2
import imutils
import platform
import numpy as np

from threading import Thread
from queue import Queue

# ==========전역 변수 선언 ==========
capture = None
thread = None
width = 640
height = 480
Q = Queue(maxsize=128)
started = False

# =============함수 정의=============
# 카메라 시작 함수
def runCam(src=0) :
    global capture
    global width
    global height
    global thread
    global started

    if platform.system() == 'Windows' :        
        capture = cv2.VideoCapture(src, cv2.CAP_DSHOW)
    else :
        capture = cv2.VideoCapture(src)
    
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    if thread is None :
            thread = Thread(target=updateVideoFrame, args=())
            thread.daemon = False
            thread.start()
            
    
    started = True

# 카메라 중지 기능
def stopCam() :
    global capture
    global started

    if capture is not None :
        capture.release()
        clearVideoFrame()

# Thread를 통해 영상 데이터를 실시간으로 처리하는 함수
def updateVideoFrame() :
    global capture
    global started
    global Q

    while True :
        if started :
            (ret, frame) = capture.read()

            if ret :
                Q.put(frame)

# Queue에 있는 영상 데이터를 삭제하는 함수
def clearVideoFrame() :
    global Q

    with Q.mutex :
        Q.queue.clear()

# Queue에 있는 영상 데이터를 읽는 함수
def readVideoFrame() :
    global Q

    return Q.get()

# 빈 영상 데이터(검은 화면)를 나타내는 함수
def blankVideo() :
    global width
    global height
    
    return np.ones(shape=[height, width, 3], dtype=np.uint8)

# 영상 데이터를 바이너리 코드로 변환하는 함수
def bytescode() :
    global capture
    global width

    if not capture.isOpened() :
        frame = blankVideo()
    else :
        frame = imutils.resize(readVideoFrame(), width=int(width))
    
    return cv2.imencode('.jpg', frame)[1].tobytes()
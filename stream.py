import threading
import cv2
import imutils
import platform
import numpy as np

from threading import Thread
from queue import Queue

capture = None
thread = None
width = 640
height = 480
stat = False
Q = Queue(maxsize=128)
started = False

def run(src=0) :
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
            thread = Thread(target=update(), args=())
            thread.daemon = False
            thread.start()
    started = True

def stop() :
    global capture
    global started

    if capture is not None :
        capture.release()
        clear()

def update() :
    global capture
    global started
    global Q

    while True :
        if started :
            (ret, frame) = capture.read()

            if ret :
                Q.put(frame)

def clear() :
    global Q

    with Q.mutex :
        Q.queue.clear()

def read() :
    global Q

    return Q.get()

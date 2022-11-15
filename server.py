from flask import Flask, render_template
from flask import request
from flask import Response
from flask import stream_with_context
import queue
from multiprocessing import Pipe, Queue

import cv2
import imutils
import platform
import numpy as np

from threading import Thread

# ====================전역 변수 선언====================
app = Flask(__name__)
capture = None
updateThread = None
readThread = None
width = 640
height = 480
Q = queue.Queue(maxsize=128)
cameraOn = False
videoFrame = None # <========== global video frame

poseEstimationChecked = False
frequentlyMoveChecked = False
blinkDetectionChecked = False

motionFrameQueue = Queue(maxsize=128)
blinkFrameQueue = Queue(maxsize=128)

# main page
@app.route('/')
def index():
    # print('Camera status : ', cameraOn)
    return render_template('index.html')

# streaming page
@app.route('/stream_page')
def stream_page():
    return render_template('stream.html')

# setting page
@app.route('/setting')
def setting():
    return render_template('setting.html')

# setting post function
@app.route('/setting_post', methods=['POST'])
def settingPost() :
    global poseEstimationChecked
    global frequentlyMoveChecked
    global blinkDetectionChecked
    
    if request.method == 'POST' :
        poseEstimationChecked = str(request.form.get('PoseEstimation')) == 'on'
        frequentlyMoveChecked = str(request.form.get('FrequentlyMove')) == 'on'
        blinkDetectionChecked = str(request.form.get('BlinkDetection')) == 'on'
        print('MODE : ', poseEstimationChecked, frequentlyMoveChecked, blinkDetectionChecked)
    return render_template('index.html')

# camera post function
@app.route('/camera_post', methods=['POST'])
def camerapost() :
    if request.method == 'POST' :
        on = str(request.form.get('CameraOn')) == 'on'
        off = str(request.form.get('CameraOff')) == 'off'
    if on and not cameraOn :
        print('========================================Camera ON========================================')
        runCam(0)
    elif off and cameraOn :
        print('========================================Camera OFF========================================')
        stopCam()
    return render_template('index.html')

# stream function
@app.route('/stream')
def stream() :
    try :
        return Response(
                            stream_with_context(stream_gen()),
                            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e :
        print('[Honey]', 'stream error : ', str(e))

# 웹페이지에 바이트 코드를 이미지로 출력하는 함수
def stream_gen() :
    try :
        while True :
            frame = bytescode()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except GeneratorExit :
        print('Back to the main page')
        pass

# 카메라 시작 함수
def runCam(src=0) :
    global capture
    global cameraOn
    global updateThread
    global readThread

    stopCam()
    if platform.system() == 'Windows' :        
        capture = cv2.VideoCapture(src, cv2.CAP_DSHOW)
    else :
        capture = cv2.VideoCapture(src)
    
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    if updateThread is None :
        print('Update Thread Start')
        updateThread = Thread(target=updateVideoFrame, args=(), daemon=False)
        updateThread.start()
    
    if readThread is None :
        print('Read Thread Start')
        readThread = Thread(target=readVideoFrame, args=(), daemon=False)
        readThread.start()
    cameraOn = True

# 카메라 중지 함수
def stopCam() :
    global videoFrame
    global cameraOn

    cameraOn = False

    if capture is not None :
        videoFrame = None
        capture.release()
        clearVideoFrame()

# 영상 데이터를 실시간으로 Queue에 update하는 Thread 내용, 전역변수 cameraOn이 False면
# 빈 while문 진행
def updateVideoFrame() :
    while True :
        if cameraOn :
            (ret, frame) = capture.read()

            if ret :
                Q.put(frame)
                if frequentlyMoveChecked and cameraOn :
                    motionFrameQueue.put(frame)
                if blinkDetectionChecked and cameraOn :
                    blinkFrameQueue.put(frame)

# 영상 데이터를 실시간으로 Queue에서 read하는 Thread 내용, 전역변수 cameraOn이 False면
# 빈 while문 진행
def readVideoFrame() :
    global videoFrame

    while True :
        if cameraOn :
            videoFrame = Q.get()

# Queue에 있는 영상 데이터를 삭제하는 함수
def clearVideoFrame() :
    with Q.mutex :
        Q.queue.clear()

# 검은화면을 출력하는 함수
def blankVideo() :
    return np.ones(shape=[height, width, 3], dtype=np.uint8)

# 이미지 데이터를 바이트 코드로 변환하는 함수
def bytescode() :
    if capture is None or videoFrame is None or not capture.isOpened():
        frame = blankVideo()
    else :
        frame = imutils.resize(videoFrame, width=int(width))
    return cv2.imencode('.jpg', frame)[1].tobytes()
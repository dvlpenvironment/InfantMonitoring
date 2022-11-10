from flask import Flask, render_template
from flask import request
from flask import Response
from flask import stream_with_context
from queue import Queue

import cv2
import imutils
import platform
import numpy as np

from threading import Thread

app = Flask(__name__)
app.secret_key = 'honey_badger'
capture = None
updateThread = None
readThread = None
width = 640
height = 480
Q = Queue(maxsize=128)
cameraOn = False
videoFrame = None # <========== global video frame

@app.route('/')
def index():
    print('Camera status : ', cameraOn)
    return render_template('index.html')

@app.route('/stream_page')
def stream_page():
    return render_template('stream.html')

@app.route('/setting')
def setting():
    return render_template('setting.html')

@app.route('/setting_post', methods=['POST'])
def settingPost() :
    if request.method == 'POST' :
        poseEstimationChecked = str(request.form.get('PoseEstimation')) == 'on'
        frequentlyMoveChecked = str(request.form.get('FrequentlyMove')) == 'on'
        blinkDetectionChecked = str(request.form.get('BlinkDetection')) == 'on'
        print('MODE : ', poseEstimationChecked, frequentlyMoveChecked, blinkDetectionChecked)
    return render_template('index.html')

@app.route('/camera_post', methods=['POST'])
def camerapost() :
    if request.method == 'POST' :
        on = str(request.form.get('CameraOn')) == 'on'
        off = str(request.form.get('CameraOff')) == 'off'
    if on and not cameraOn :
        print('==========Camera ON==========')
        runCam(0)
    elif off and cameraOn :
        print('==========Camera OFF==========')
        stopCam()
    return render_template('index.html')

@app.route('/stream')
def stream() :
    try :
        return Response(
                            stream_with_context(stream_gen()),
                            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e :
        print('[Honey]', 'stream error : ', str(e))

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
        updateThread = Thread(target=updateVideoFrame, args=(), daemon=False)
        updateThread.start()
    
    if readThread is None :
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

# 영상 데이터를 실시간으로 Queue에 update하는 Thread 내용, stop되면
# 그냥 while문 진행
def updateVideoFrame() :
    while True :
        if cameraOn :
            (ret, frame) = capture.read()

            if ret :
                Q.put(frame)

def readVideoFrame() :
    global videoFrame

    while True :
        if cameraOn :
            videoFrame = Q.get()

# Queue에 있는 영상 데이터를 삭제하는 함수
def clearVideoFrame() :
    with Q.mutex :
        Q.queue.clear()

def blankVideo() :
    return np.ones(shape=[height, width, 3], dtype=np.uint8)

def bytescode() :
    if capture is None or videoFrame is None or not capture.isOpened():
        frame = blankVideo()
    else :
        frame = imutils.resize(videoFrame, width=int(width))
    return cv2.imencode('.jpg', frame)[1].tobytes()
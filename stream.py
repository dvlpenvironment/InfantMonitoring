import cv2
import imutils
import platform
import numpy as np

from threading import Thread
from queue import Queue

class Streamer :
    def __init__(self) :
        if cv2.ocl.haveOpenCL() :
            cv2.ocl.setUseOpenCL(True)
        
        self.capture = None
        self.thread = None
        self.width = 640
        self.height = 480
        self.Q = Queue(maxsize=128)
        self.started = False
        self.videoFrame = None

    # 카메라 시작 함수
    def runCam(self, src=0) :
        self.stopCam()

        if platform.system() == 'Windows' :        
            self.capture = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        else :
            self.capture = cv2.VideoCapture(src)
        
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        if self.thread is None :
            self.thread = Thread(target=self.updateVideoFrame, args=(), daemon=False)
            self.thread.start()
        
        self.started = True

    # 카메라 중지 기능
    def stopCam(self) :
        if self.capture is not None :
            self.videoFrame = None
            self.capture.release()
            self.clearVideoFrame()

    # Thread를 통해 영상 데이터를 실시간으로 처리하는 함수
    def updateVideoFrame(self) :
        while True :
            if self.started :
                (ret, frame) = self.capture.read()

                if ret :
                    self.Q.put(frame)

    # Queue에 있는 영상 데이터를 삭제하는 함수
    def clearVideoFrame(self) :
        with self.Q.mutex :
            self.Q.queue.clear()

    # Queue에 있는 영상 데이터를 읽는 함수
    def readVideoFrame(self) :
        return self.Q.get()

    # 빈 영상 데이터(검은 화면)를 나타내는 함수
    def blankVideo(self) :
        return np.ones(shape=[self.height, self.width, 3], dtype=np.uint8)

    # 영상 데이터를 바이너리 코드로 변환하는 함수
    def bytescode(self) :
        if not self.capture.isOpened() :
            frame = self.blankVideo()
        else :
            self.videoFrame = self.readVideoFrame()
            frame = imutils.resize(self.videoFrame, width=int(self.width))
        
        return cv2.imencode('.jpg', frame)[1].tobytes()
    
    def __exit__(self) :
        print('=====Streamer class exit=====')
        self.capture.release()
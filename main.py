from server import app, motionFrameQueue
from models.MotionDetect import motionDetect
#from models.BlinkDetect import blinkDetect
#from models.posenet import poseDetect
from multiprocessing import Process

# poseDetect rendering
import sys
from jetson_utils import videoOutput

output = videoOutput("", argv=sys.argv)

if __name__ == '__main__':
    print('CV on')
    motionProcess = Process(target=motionDetect, args=(motionFrameQueue,), daemon=False)
    motionProcess.start()

    #blinkProcess = Process(target=blinkDetect, args=(blinkFrameQueue,), daemon=False)
    #blinkProcess.start()

    #poseProcess = Process(target=poseDetect, args=(poseFrameQueue,), daemon=False)
    #poseProcess.start()

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    print('main close')

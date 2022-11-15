from server import app, motionFrameQueue
from MotionDetect import motionDetect
from multiprocessing import Process

if __name__ == '__main__':
    print('CV on')
    motionProcess = Process(target=motionDetect, args=(motionFrameQueue,), daemon=False)
    motionProcess.start()

    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    print('main close')
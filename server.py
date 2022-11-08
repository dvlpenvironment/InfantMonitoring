from flask import Flask, render_template
from flask import request
from flask import Response
from flask import stream_with_context

from stream import Streamer

app = Flask(__name__)
streamer = Streamer()

poseEstimationChecked = False
frequentlyMoveChecked = False
blinkDetectionChecked = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream_page')
def stream_page():
    return render_template('stream.html')

@app.route('/setting')
def setting():
    return render_template('setting.html')

@app.route('/setting_post', methods=['POST'])
def settingPost() :
    global poseEstimationChecked
    global frequentlyMoveChecked
    global blinkDetectionChecked

    if request.method == 'POST' :
        poseEstimationChecked = str(request.form.get('PoseEstimation')) == 'on'
        frequentlyMoveChecked = str(request.form.get('FrequentlyMove')) == 'on'
        blinkDetectionChecked = str(request.form.get('BlinkDetection')) == 'on'
        print(poseEstimationChecked, frequentlyMoveChecked, blinkDetectionChecked)
    return render_template('index.html')

@app.route('/stream')
def stream() :
    global poseEstimationChecked
    global frequentlyMoveChecked
    global blinkDetectionChecked

    src = request.args.get('src', default=0, type=int)

    try :
        return Response(
                            stream_with_context(stream_gen(src, poseEstimationChecked, frequentlyMoveChecked, blinkDetectionChecked)),
                            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e :
        print('[Honey]', 'stream error : ', str(e))

def stream_gen(src, poseEstimationChecked, frequentlyMoveChecked, blinkDetectionChecked) :
    try :
        streamer.runCam(src)

        if(poseEstimationChecked) :
            print('PoseEstimation Start')
        else :
            print('PoseEstimation Stop')

        if(frequentlyMoveChecked) :
            print('FrequentlyMove Start')
        else :
            print('FrequentlyMove Stop')

        if(blinkDetectionChecked) :
            print('BlinkDetection Start')
        else :
            print('BlinkDetection Stop')

        while True :
            frame = streamer.bytescode()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except GeneratorExit :
        streamer.stopCam()
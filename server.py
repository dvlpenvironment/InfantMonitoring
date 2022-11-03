import threading
from flask import Flask, render_template
from flask import request
from flask import Response
from flask import stream_with_context

from stream import *
from threading import Thread

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream_page')
def stream_page():
    return render_template('stream.html')

@app.route('/setting')
def setting():
    return render_template('setting.html')

@app.route('/stream')
def stream() :
    src = request.args.get('src', default=0, type=int)

    try :
        return Response(
                            stream_with_context(stream_gen(src)),
                            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e :
        print('[Honey]', 'stream error : ', str(e))
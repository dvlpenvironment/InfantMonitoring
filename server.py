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
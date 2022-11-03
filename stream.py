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

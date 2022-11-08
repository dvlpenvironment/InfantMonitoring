import imutils
import cv2
import numpy as np
import time
from collections import deque
from queue import Queue
# =============================================================================
# USER-SET PARAMETERS
# =============================================================================

# Number of frames to pass before changing the frame to compare the current
# frame against
FRAMES_TO_PERSIST = 10

# Minimum boxed area for a detected motion to count as actual motion
# Use to filter out noise or small objects
MIN_SIZE_FOR_MOVEMENT = 2000

# Minimum length of time where no motion is detected it should take
# (in program cycles) for the program to declare that there is no movement
# MOVEMENT_DETECTED_PERSISTENCE = 100

# =============================================================================
# CORE PROGRAM
# =============================================================================

class MotionDetecter :
    # Create capture object
    # cap = cv2.VideoCapture(5)  # Flush the stream
    # cap.release()
    # cap = cv2.VideoCapture(0)  # Then start the webcam

    def __init__(self) :
        # Init frame variables
        self.first_frame = None
        self.next_frame = None

        # Init display font and timeout counters
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.delay_counter = 0
        self.queue = deque()
        self.next_block_flag = False
        self.start_time = time.time()
        self.Q = Queue(maxsize=128)
        self.checked = False
    
    def updateVideoFrame(self, frame) :
        self.Q.put(frame)
    
    def readVideoFrame(self) :
        return self.Q.get()
    
    def clearVideoFrame(self) :
        self.Q.queue.clear()

    def initializationChecked(self, check) :
        self.checked = check

    def detect(self) :
        # LOOP!
        while True:
            if self.checked :
                # Set transient motion detected as false
                transient_movement_flag = False
                block_movement_flag = False

                if self.next_block_flag:
                    self.start_time = time.time()
                    self.next_block_flag = False
                # Read frame
                frame = self.readVideoFrame() # <======================
                text = "Unoccupied"

                # If there's an error in capturing
                # if not ret:
                #     print("CAPTURE ERROR")
                #     continue

                # Resize and save a greyscale version of the image
                frame = imutils.resize(frame, width=750)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Blur it to remove camera noise (reducing false positives)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)

                # If the first frame is nothing, initialise it
                if self.first_frame is None: self.first_frame = gray

                self.delay_counter += 1

                # Otherwise, set the first frame to compare as the previous frame
                # But only if the counter reaches the appriopriate value
                # The delay is to allow relatively slow motions to be counted as large
                # motions if they're spread out far enough
                if self.delay_counter > FRAMES_TO_PERSIST:
                    self.delay_counter = 0
                    self.first_frame = self.next_frame

                # Set the next frame to compare (the current frame)
                self.next_frame = gray

                # Compare the two frames, find the difference
                frame_delta = cv2.absdiff(self.first_frame, self.next_frame)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

                # Fill in holes via dilate(), and find contours of the thesholds
                thresh = cv2.dilate(thresh, None, iterations=2)
                cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # loop over the contours
                for c in cnts:
                    # Save the coordinates of all found contours
                    (x, y, w, h) = cv2.boundingRect(c)

                    # If the contour is too small, ignore it, otherwise, there's transient
                    # movement
                    if cv2.contourArea(c) > MIN_SIZE_FOR_MOVEMENT:
                        transient_movement_flag = True

                        # Draw a rectangle around big enough movements
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # The moment something moves momentarily, reset the persistent
                # movement timer.
                if time.time() - self.start_time > 5:
                    print('\n\n\n한블락지남\n\n\n')

                    if transient_movement_flag == True:
                        block_movement_flag = True
                    if  len(self.queue) == 3:
                        self.queue.popleft()

                    self.queue.append(block_movement_flag)
                    print('FIFO', self.queue)
                    self.next_block_flag = True

                if sum(self.queue) == 3:
                    print("\n\n\n자주 움직임\n\n\n")
                    text = "Frequently Movement Detected "
                else:
                    text = "No Movement Detected"
                cv2.putText(frame, str(text), (10, 35), self.font, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

                # For if you want to show the individual video frames
                #    cv2.imshow("frame", frame)
                #    cv2.imshow("delta", frame_delta)

                # Convert the frame_delta to color for splicing
                frame_delta = cv2.cvtColor(frame_delta, cv2.COLOR_GRAY2BGR)

                # Splice the two video frames together to make one long horizontal one
                cv2.imshow("frame", np.hstack((frame_delta, frame)))

                # Interrupt trigger by pressing q to quit the open CV program
                ch = cv2.waitKey(1)
                if ch & 0xFF == ord('q'):
                    break
            
            # # Cleanup when closed
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            # cap.release()
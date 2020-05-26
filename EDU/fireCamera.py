# **************************************************
# This class is used to capture an image from the Raspberry Camera and
# to detect the presence of fire
# It exploits the OpenCV, Numpy and Matplotlib libraries
# Author      : Daniel G. Costa
# E-mail      : danielgcosta@uefs.br
# Date        : 12/05/2020
# **************************************************

import cv2
import numpy as np
import matplotlib.pyplot as plt
import time

class Camera:
    
    def __init__(self):

        # Object to access the camera
        self.myCamera = cv2.VideoCapture(0)
        
        # Basic configuration for the detection of fire
        # This is a simple calibration since we are not using
        # artifical inteligence for automatic detection
        self.lower_bound = np.array([10,10,100])
        self.upper_bound = np.array([100,255,255])

    def detect(self): 
        # Initialize de camera
            
        ret, frame = self.myCamera.read()
            
        # Basic configurations of the captured image
        frame = cv2.resize(frame,(480,480))
        frame = cv2.flip(frame,1)  # Flip the camera in 180 grades

        # Configuraitons for the detection of fire
        frame_smooth = cv2.GaussianBlur(frame,(7,7),0)
        mask = np.zeros_like(frame)
        mask[0:480, 0:480] = [255,255,255]
        img_roi = cv2.bitwise_and(frame_smooth, mask)

        # Processing the captured image
        frame_hsv = cv2.cvtColor(img_roi,cv2.COLOR_BGR2HSV)
        image_binary = cv2.inRange(frame_hsv, self.lower_bound, self.upper_bound)

        check_if_fire_detected = cv2.countNonZero(image_binary)
   
        if int(check_if_fire_detected) >= 20000:
        # Fire is detected!
            return True
        else:
            # No fire
            return False

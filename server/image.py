import numpy as np
import cv2

import base64
import io

import model

def createVisual(frame, color = cv2.COLORMAP_COOL):
    return cv2.applyColorMap(cv2.normalize(frame, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8U), color)

def matLikeToBase64JPG(mat):
    depth_encode = cv2.imencode('.jpg', mat)[1] 
  
    # Converting the image into numpy array 
    data_encode = np.array(depth_encode) 
    
    # Converting the array to bytes. 
    byte_encode = data_encode.tobytes() 
    depth_img = base64.encodebytes(byte_encode)
    
    return depth_img.decode()
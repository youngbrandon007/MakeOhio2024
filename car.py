import cv2
from time import time
import numpy as np
import requests
from datetime import datetime
from time import time
import serial

ENDPOINT = "http://192.168.1.11:8080/process"
ser = serial.Serial( #Serial COM configuration
    port='/dev/ttyACM0',
    baudrate=115200,
    timeout=1
  )
if not ser.is_open:
    ser.open()

def sendImage(frame):
    imencoded = cv2.imencode(".jpg", frame)[1]
    now = datetime.now()
    seq = now.strftime("%Y%m%d%H%M%S")
    file = {'file': (seq+'.jpg', imencoded.tobytes(), 'image/jpeg')}
    try:
        response = requests.post(ENDPOINT, files=file, timeout=5)
        print(response)
        data = response.json() 
        toWrite = f"{data['left']} {data['right']}\n"
        print(toWrite)
        ser.write(toWrite.encode('utf-8'))
    except Exception as e:
        print(e)

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Attempt to set camera to 1080p resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

while True:
    # Read a frame from the webcam
    start_time = time()
    ret, frame = cap.read()
    if not ret:
        break
    sendImage(frame)

    print(f'Frame took {time() - start_time:.4f}s')

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and destroy all OpenCV windows
cap.release()
cv2.destroyAllWindows()

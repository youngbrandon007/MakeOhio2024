import flask, flask_socketio, base64
from flask_cors import CORS, cross_origin
import model
import numpy as np
import cv2
import image
import json
import matplotlib.pyplot as plt
import exampleimages
cors_urls = ["http://localhost:5173", "https://TO REPLACE-8080.use.devtunnels.ms", "https://TO REPLACE-5173.use.devtunnels.ms"]

app = flask.Flask(__name__)
cors = CORS(app,resources={r"/api/*":{"origins":", ".join(cors_urls)}})
socketio = flask_socketio.SocketIO(app, cors_allowed_origins=cors_urls)

remote_control_only = False
remote_control_state = { "left": 0, "right": 0}
remote_result_state = "Go"
remote_result_reset = 0

# Ping Functions
@app.route('/')
@cross_origin()
def hello():
    return 'Hello, World!'
 
@socketio.on('test')
def socketioTest():
    flask_socketio.emit('test')  

# Remote Control Functions
@socketio.on("mode")
def socketioMode(mode):
    global remote_control_only
    if mode == "remote":
        remote_control_only = True
    else:
        remote_control_only = False

@socketio.on("remote")
def socketioRemote(left, right):
    remote_control_state["left"] = left
    remote_control_state["right"] = right

# Main Process Function
@app.route('/process', methods=['post'])
def receiveImage():
    global remote_result_reset
    global remote_result_state
    global remote_control_state
    global remote_control_only
    
    file = flask.request.files['file']
    data = file.stream.read()
    
    img = base64.encodebytes(data)
    socketio.emit('image', ("base", img.decode()))

    if remote_control_only:
        return remote_control_state
    
    nparr = np.fromstring(data, np.uint8)
    img_np = cv2.imdecode(nparr, flags=1)
    
    depth, danger_image_left, danger_image_right, out_danger_from_left, out_danger_from_right, hit_left, hit_right = model.compute(img_np)
    
    score = max(hit_left, hit_right)
    # print(hit_left, hit_right)
    
    if(score > 150):
        remote_result_state = "Slow"
        remote_result_reset = 6
    elif remote_result_reset > 0:
        remote_result_reset -= 1
        if remote_result_reset == 0:
            remote_result_state = "Go"
    
    socketio.emit('image', ("image1", image.matLikeToBase64JPG(image.createVisual(depth))))
    socketio.emit('image', ("image2", image.matLikeToBase64JPG(image.createVisual(danger_image_left))))
    socketio.emit('image', ("image3", image.matLikeToBase64JPG(image.createVisual(danger_image_right))))
    socketio.emit('data', (json.dumps(out_danger_from_left), json.dumps(out_danger_from_right)))
    socketio.emit('status', (remote_result_state))
    
    slow_speed = 150
    
    output = {"left": remote_control_state["left"], "right": remote_control_state["right"]}
    
    if remote_result_state == "Slow":
        scale = slow_speed / max(output["left"], output["right"], slow_speed)
        output["left"] = output["left"] * scale
        output["right"] = output["right"] * scale
    
    return output

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
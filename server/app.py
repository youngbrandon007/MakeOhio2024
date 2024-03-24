import flask, flask_socketio, base64
from flask_cors import CORS, cross_origin
from valuegenoptimized2 import createVisuals

cors_urls = ["http://localhost:5173", "https://bananabreadmakeohio2024.web.app"]

app = flask.Flask(__name__)
cors = CORS(app,resources={r"/api/*":{"origins":", ".join(cors_urls)}})
socketio = flask_socketio.SocketIO(app, cors_allowed_origins=cors_urls)

remote_control_only = False
remote_control_state = { "left": 0, "right": 0}

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
    file = flask.request.files['file']
    data = b''
    
    data = file.stream.read()
    
    img = base64.encodebytes(data)
    socketio.emit('image', ("base", img.decode()))

    if remote_control_only:
        return remote_control_state
    
    # computedImg = createVisuals(img)
    # socketio.emit('image', ("distance", computedImg.decode()))
    
    return {"left": 0, "right": 0}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO, emit
import pyaudio
import cv2
import numpy as np

from picamera import PiCamera
from picamera.array import PiRGBArray

app = Flask(__name__)
socketio = SocketIO(app)
camera = cv2.VideoCapture(0)
p = pyaudio.PyAudio()



# Define the audio stream callback function
def audio_callback(in_data, frame_count, time_info, status):
    # Process the audio data here
    return None, pyaudio.paContinue

# Open an audio stream
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, output=False, stream_callback=audio_callback)



def generate_frames(focus):
    while True:
        success, frame = camera.read()

        
        if not success:
            break
        else:

            ### Detect movement
            if focus:
                success2, frame2 = camera.read()
                if success2:
                    diff = cv2.absdiff(frame, frame2)
                    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                    blur = cv2.GaussianBlur(diff_gray, (5, 5), 0)
                    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
                    dilated = cv2.dilate(thresh, None, iterations=3)
                    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                    mx = []
                    for contour in contours:
                        (x, y, w, h) = cv2.boundingRect(contour)
                        if cv2.contourArea(contour) < 900:
                            continue
                        mx.append(x + w/2)

                    if len(mx) > 0:
                        test = int(sum(mx) / len(mx))
                        # print(test)
                        cv2.line(frame, (test,1), (test, 100), (255, 0, 0), 2)


            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(True), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera_turn', methods=['POST'])
def camera_turn():
    if request.method == 'POST':
        print(request.form.get('value'))
        return ('', 204)

@app.route('/camera_focus', methods=['POST'])
def camera_focus():
    if request.method == 'POST':
        print('')
        return ('', 204)

@socketio.on('audio')
def handle_audio(audio_data):
    # Convert the audio data to a NumPy array
    audio_array = np.frombuffer(audio_data, dtype=np.int16)

    # Process the audio data here, for example:
    stream.write(audio_array)

    # Emit the audio data to all clients except the sender
    emit('audio', audio_data, broadcast=True, include_self=False)

if __name__=='__main__':
        socketio.run(app,
        host='0.0.0.0',
        port=5000,
        debug=False,
    )
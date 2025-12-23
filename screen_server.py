from flask import Flask, Response
import cv2
import numpy as np
import mss
import time

app = Flask(__name__)

def generate_frames():
    # MSS MUST be created inside the thread (Windows requirement)
    with mss.mss() as sct:
        monitor = sct.monitors[0]  # full virtual screen

        while True:
            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            frame = cv2.resize(frame, (1280, 720))

            ok, buffer = cv2.imencode(
                ".jpg",
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), 70]
            )

            if not ok:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + buffer.tobytes()
                + b"\r\n"
            )

            time.sleep(0.03)

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Screen Share</title>
        <style>
            body { margin:0; background:black; }
            img { width:100vw; height:100vh; object-fit:contain; }
        </style>
    </head>
    <body>
        <img src="/stream">
    </body>
    </html>
    """

@app.route("/stream")
def stream():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True,
        debug=False,
        use_reloader=False
    )

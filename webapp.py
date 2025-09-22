from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

def create_app(output):
    def generate_frames():
        while True:
            with output.condition:
                output.condition.wait()
                frame = output.frame
            if frame is None:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/video_feed')
    def video_feed():
        return Response(generate_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/distance')
    def distance():
        with output.condition:
            dist = output.distance
        if dist is None:
            return jsonify(distance=None)
        return jsonify(distance=round(dist, 2))

    return app

def run_server(output, host='0.0.0.0', port=5000, debug=False, threaded=True):
    app = create_app(output)
    app.run(host=host, port=port, debug=debug, threaded=threaded)
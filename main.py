import io
import threading
import time
from threading import Condition, Event
from picamera2 import Picamera2
import cv2 as cv

from webapp import run_server

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.distance = None   # closest object distance (meters)
        self.condition = Condition()

    def update(self, buf: bytes, distance):
        with self.condition:
            self.frame = buf
            self.distance = distance
            self.condition.notify_all()

# Detection / distance helpers
KNOWN_DISTANCE_M = 50.0
KNOWN_WIDTH_M = 1.8
CALIB_WIDTH_PX = 30
FOCAL_LENGTH = (CALIB_WIDTH_PX * KNOWN_DISTANCE_M) / KNOWN_WIDTH_M

def find_distance(focal_length, known_width, observed_width):
    if observed_width == 0:
        return 0
    return (known_width * focal_length) / observed_width

def annotate_cars(frame_bgr, cascade):
    gray = cv.cvtColor(frame_bgr, cv.COLOR_BGR2GRAY)
    cars = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=6,
        minSize=(30, 30),
        maxSize=(300, 300)
    )
    distances = []
    for (x, y, w, h) in cars:
        cv.rectangle(frame_bgr, (x, y), (x + w, y + h), (0, 0, 255), 2)
        distance = find_distance(FOCAL_LENGTH, KNOWN_WIDTH_M, w)
        distances.append(distance)
        label = f"{distance:.1f}m"
        label_size = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv.rectangle(frame_bgr,
                     (x, y - label_size[1] - 8),
                     (x + label_size[0], y),
                     (0, 0, 255), -1)
        cv.putText(frame_bgr, label, (x, y - 5),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    closest = min(distances) if distances else None
    return frame_bgr, closest

def frame_producer(picam2, output, stop_event, cascade, target_fps=12):
    frame_interval = 1.0 / target_fps
    while not stop_event.is_set():
        t0 = time.time()
        frame = picam2.capture_array()
        frame_bgr = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
        frame_bgr, closest = annotate_cars(frame_bgr, cascade)
        ok, jpeg = cv.imencode(".jpg", frame_bgr, [int(cv.IMWRITE_JPEG_QUALITY), 85])
        if ok:
            output.update(jpeg.tobytes(), closest)
        dt = time.time() - t0
        if dt < frame_interval:
            time.sleep(frame_interval - dt)

def main():
    picam2 = Picamera2()
    config = picam2.create_video_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    cascade = cv.CascadeClassifier('cars.xml')
    if cascade.empty():
        raise FileNotFoundError("Could not load 'cars.xml'.")

    output = StreamingOutput()
    stop_event = Event()

    producer_thread = threading.Thread(
        target=frame_producer,
        args=(picam2, output, stop_event, cascade),
        daemon=True
    )
    
    producer_thread.start()

    try:
        run_server(output)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        producer_thread.join(timeout=2)
        picam2.stop()
        picam2.close()

if __name__ == '__main__':
    main()
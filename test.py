import cv2 as cv
import time

known_distance = 50  # meters - distance when calibrating
known_width = 1.8    # meters - average car width


def calc_focal_length(known_distance, known_width, img_width):
    focal_length = (img_width * known_distance) / known_width
    return focal_length


def find_distance(focal_length, known_width, img_width):
    distance = (known_width * focal_length) / img_width
    return distance


# calibrate with car at known distance
# testing w/ a car at 50m appears 30 pixels wide
focal_length = calc_focal_length(known_distance, known_width, 30)


def find_cars(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    cars = car_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=6,
        minSize=(30, 30),
        maxSize=(300, 300)
    )
    for (x, y, w, h) in cars:
        # label identified car
        cv.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # calculate distance to car
        distance = find_distance(focal_length, known_width, w)

        # label distance
        label = f"{distance:.1f}m"
        label_size = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        cv.rectangle(img, (x, y - label_size[1] - 10), (x + label_size[0], y), (0, 0, 255), -1)
        cv.putText(img, label, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return img


car_detector = cv.CascadeClassifier('cars.xml')
video = cv.VideoCapture('test_content/dashcam1.mp4')

# video properties for saving
frame_width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))
fps = video.get(cv.CAP_PROP_FPS)

out = cv.VideoWriter('output_with_detections.mp4', cv.VideoWriter_fourcc(
    *'mp4v'), fps, (frame_width, frame_height))

while video.isOpened():
    ret, frame = video.read()
    if not ret:
        break
    frame_with_detections = find_cars(frame)
    cv.imshow("Car Detection", frame_with_detections)
    out.write(frame_with_detections)  # save frame to output video
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
out.release()
cv.destroyAllWindows()

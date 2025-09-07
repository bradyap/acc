import cv2 as cv

car_detector = cv.CascadeClassifier('cars.xml')

def find_cars(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    cars = car_detector.detectMultiScale(gray, 1.1, 1)
    for (x, y, w, h) in cars:
        cv.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    return img

img = cv.imread('car.jpg')
img_with_detections = find_cars(img)
cv.imshow("Cars Detected", img_with_detections)
k = cv.waitKey(0)
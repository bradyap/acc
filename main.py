def main():
    import cv2 as cv
    
    img = cv.imread('car.jpg')

    cv.imshow("Display window", img)
    k = cv.waitKey(0)

if __name__ == '__main__':
    main()
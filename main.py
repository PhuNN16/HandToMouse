# import pyautogui as pag

# print(pag.moveTo(1000, 1000, 0.1))

import cv2 as cv

capture = cv.VideoCapture(0)

while True:
    isTrue, frame = capture.read()

    frame = cv.flip(frame, 1) # 0 is z axis, 1 is y, -1 is x
    frame = cv.resize(frame, (750, 750), interpolation=cv.INTER_AREA)
    cv.imshow("Video", frame)

    if cv.waitKey(20) & 0xFF == ord('d'):
        break

capture.release()
cv.destroyAllWindows()
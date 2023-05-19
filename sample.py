import cv2 as cv
import HandTrackingModule
lmList =[]
tipIds=[4,8,12,16,20]
if len(lmList) !=0:
    fingers = []

    #thumb
    if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
        fingers.append(1)
    else:
        fingers.append(0)
    #4 fingers
    for id in range(1,5):
        if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]:
            fingers.append(1)
        else:
            fingers.append(0)

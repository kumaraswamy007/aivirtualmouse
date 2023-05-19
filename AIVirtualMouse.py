import cv2 as cv
import numpy as np
import HandTrackingModule as htm
import autopy
import time
import math
import pycaw
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyautogui

####################################################################
import tkinter
import customtkinter
from PIL import ImageTk, Image

customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

app = customtkinter.CTk()  # creating cutstom tkinter window
app.geometry("800x640")
app.title('AI VIRTUAL MOUSE')

def button_function():
    img_guide = cv.imread("guide.png")
    img_guide = cv.resize(img_guide,(0,0),None,0.75,0.75)
    cv.imshow("Giude",img_guide)
    cv.waitKey(0)



img1 = ImageTk.PhotoImage(Image.open("bgimg.jpeg"))
l1 = customtkinter.CTkLabel(master=app, image=img1)
l1.pack()


# creating custom frame
frame = customtkinter.CTkFrame(master=l1, width=320, height=450, corner_radius=15)
frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

l2 = customtkinter.CTkLabel(master=frame, text="AI VIRTUAL MOUSE", font=('Century Gothic', 20))
l2.place(x=75, y=45)

entry1 = customtkinter.CTkEntry(master=frame, width=220, placeholder_text='Your Name')
entry1.place(x=50, y=110)

entry2 = customtkinter.CTkEntry(master=frame, width=220, placeholder_text='Registration Number')
entry2.place(x=50, y=165)

def submit():
    name = entry1.get()
    reg = entry2.get()
    print("Your Name : ",name)
    print("Registration Number : ",reg)



button1 = customtkinter.CTkButton(master=frame,width=220,text="Submit",command=submit,corner_radius=6)
button1.place(x=50, y=240)

button2 = customtkinter.CTkButton(master=frame, width=220, text="Guide", command=button_function, corner_radius=6)
button2.place(x=50, y=290)




#Range of volume is -65 to 0 ,65 is min volume 0 is max volume


def mouse_function():
    ####################
    wCam, hCam = 1640, 1280
    smoothening = 7
    ####################

    ptime = 0
    plocX, plocY = 0, 0
    clocX, clocY = 0, 0
    active = 0
    mode = ''

    cap = cv.VideoCapture(0)
    cap.set(3, 1640)
    cap.set(4, 1280)
    detector = htm.handDetector(maxHands=1, detectionCon=0.7)
    wScr, hScr = autopy.screen.size()
    # print(wScr,hScr)

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    # volume.GetMute()
    # volume.GetMasterVolumeLevel()
    volRange = volume.GetVolumeRange()

    minVol = volRange[0]
    maxVol = volRange[1]

    while True:
        #1. Find the hand Landmarks
        success, img = cap.read()
        img = cv.flip(img,1)
        img = detector.findHands(img)
        lmList, bbox = detector.findposition(img)


        #2. Get the tip of the index and middle finger
        if len(lmList)!=0:
            x1,y1 = lmList[8][1:]#Index Finger
            x2,y2 = lmList[12][1:]#Middle Fingeer
            #print(x1,y1,x2,y2)
            fingers = detector.fingersUp()
            x4,y4 = lmList[4][1],lmList[4][2]
            x5, y5 = lmList[8][1], lmList[8][2]
            mx, my = (x4 + x1) // 2, (y4 + y1) // 2
            if fingers[0]==1 and fingers[1]==1 :
                cv.circle(img,(x4,y4),15,(255,0,255),cv.FILLED)
                cv.line(img,(x4,y4),(x1,y1),(255,0,255),3)
                cv.circle(img, (mx, my), 15, (255, 0, 255), cv.FILLED)
                length = math.hypot(x1-x4,y1-y4)

                #Hand range max is 300 and min is 50
                #Volume range is -65 to 0

                vol = np.interp(length,[50,300],[minVol, maxVol])
                volume.SetMasterVolumeLevel(vol, None)

                if length<50:
                    cv.circle(img, (mx, my), 15, (255, 255, 255), cv.FILLED)


            #3. Check which fingers are upcv.circle(img, (x4, y4), 15, (255, 0, 255), cv.FILLED)

            #print(fingers)
            cv.rectangle(img, (100, 100), (wCam - 500, hCam - 650), (255, 0, 255), 2)
            #4. Only Index Finger : Moving Mode
            if fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 0 and fingers[4]==0:
                #5. Convert Coordinates
                x3 = np.interp(x1,(100,wCam-500),(0,wScr))
                y3 = np.interp(y1, (100, hCam-650), (0, hScr))
                #6. Smoothen Values
                clocX = plocX+(x3-plocX) / smoothening
                clocY = plocY + (y3 - plocX) / smoothening
                #7. Move Mouse
                autopy.mouse.move(x3, y3)
                cv.circle(img,(x1,y1),15,(255,0,255),cv.FILLED)
                plocX,plocY=clocX,clocY
            #8.Both index and middle are up : Clicking mode
            if fingers[1] == 1 and fingers[2] == 1:
                # 9.Find distance between fingers
                length,img, lineInfo =  detector.findDistance(8,12,img)
                #print(length)
                # 10.Click mouse if distance is small
                if length < 60:
                    cv.circle(img,(lineInfo[4],lineInfo[5]),15,(0,255,0),cv.FILLED)
                    autopy.mouse.click()
            #Scrolling
            if fingers[4] == 1 and fingers[1]==0:
                x6, y6 = lmList[20][1:]
                cv.circle(img, (x6, y6), 15, (255, 0, 255), cv.FILLED)
                pyautogui.scroll(300)
            if fingers[4] == 1 and fingers[1]==1:
                x6, y6 = lmList[20][1:]
                x7, y7 = lmList[8][1:]
                cv.circle(img, (x6, y6), 15, (255, 0, 255), cv.FILLED)
                cv.circle(img, (x7, y7), 15, (255, 0, 255), cv.FILLED)
                pyautogui.scroll(-300)
            if fingers[0]==0 and fingers[1]==0 and fingers[2]==0 and fingers[3]==0 and fingers[4]==0:
                pyautogui.click(button='right')


        #11.Frame Rate

        ctime = time.time()
        fps = 1/(ctime-ptime)
        ptime = ctime
        cv.putText(img,str(int(fps)),(20,50),cv.FONT_HERSHEY_PLAIN,3,(255,0,0),3)

        #12.Display
        cv.imshow("Image", img)

        if cv.waitKey(35) & 0xff == ord('f'):
            break
    cap.release()
    cv.destroyAllWindows()

def win_destroy():
    app.destroy()

button3 = customtkinter.CTkButton(master=frame, width=220, text="Activate Mouse", command=mouse_function, corner_radius=6)
button3.place(x=50, y=340)
button4 = customtkinter.CTkButton(master=frame,width=220,text="Exit",command=win_destroy,corner_radius=6)
button4.place(x=50, y=390)
name=entry1.get()
reg = entry2.get()
print(name)
print(reg)

app.mainloop()
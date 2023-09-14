import os
import pickle
import face_recognition as fr
from cv2 import cv2 as cv
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db
from datetime import datetime


""" Please Note All Images must be of size 216x216 pixels"""

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://visual-attendance-system-default-rtdb.firebaseio.com/',
    'storageBucket': 'visual-attendance-system.appspot.com'
    })

bucket = storage.bucket()

capture = cv.VideoCapture(0)
capture.set(3, 640)    # Width
capture.set(4,  480)     # Height

imgBG = cv.imread('./resource/bg_app.png')  # Main BG of the UI

# Importing Mode Images
modePath = './resource/Mode'
modePathList = os.listdir(modePath)
imgMode = []

for path in modePathList:
    imgMode.append(cv.imread(os.path.join(modePath, path)))

# print(len(imgMode))

# Load the encoding file
print('**** Loading Encode File ****')
file = open('EncodeFile.p', 'rb')
encodeListKnownIds = pickle.load(file=file)
file.close()
encodeListKnown, studentIDs = encodeListKnownIds
# print(studentIDs)
print('**** Encode File Loaded ****')

modeType = 0
counter = 0
regNum = -1
imgStudent = []

# image = Image.open(imgStudent)
# imgStudent = image.resize(216, 260)
# imgStudent.save(imgStudent)

while True:
    isTrue, frame = capture.read()

    imgS = cv.resize(frame, (0, 0), None, 1, 1)   # Scaling down image by 4 (Takes lesser computing power)
    imgS = cv.cvtColor(imgS, cv.COLOR_BGR2RGB)

    faceCurrentFrame = fr.face_locations(imgS)
    encodeCurrentFrame = fr.face_encodings(imgS, faceCurrentFrame)  # Compare encodings of image & live feed

    # frame = cv.flip(frame, 1)   # Flips the webcam image on the Y-axis
    imgBG[162:162+480, 55:55+640] = frame
    imgBG[44:44+633, 808:808+414] = imgMode[modeType]

    # Comparing Each Image with Live feed from the camera
    if faceCurrentFrame:

        for encodeFace, faceLocation in zip(encodeCurrentFrame, faceCurrentFrame):
            matches = fr.compare_faces(encodeListKnown, encodeFace)
            faceDist = fr.face_distance(encodeListKnown, encodeFace)    # Difference between the live feed and image in Database
            # print("Match", matches)
            # print("Dist", faceDist)

            matchIndex = np.argmin(faceDist)
            # print('Match Index', matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIDs[matchIndex])     # Prints student Registration Number
                y1, x2, y2, x1 = faceLocation
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4     # Upsizing the image as it was downsized by 4 before
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                # imgBG = cvzone.cornerRect(imgBG, bbox=bbox, rt=1)

                regNum = studentIDs[matchIndex]
                # print(regNum)

                if counter == 0:
                    cvzone.putTextRect(imgBG, 'Loading...', (275, 400))
                    cv.imshow("Visual Attendance System", imgBG)
                    cv.waitKey(1)
                    counter = 1
                    modeType = 1

            if counter != 0:
                if counter == 1:
                    # Getting the data
                    studentInfo = db.reference(f'Students/{regNum}').get()
                    # print(studentInfo)

                    # Get the Image from Storage
                    blob = bucket.get_blob(f'img/{regNum}.png')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv.imdecode(array, cv.COLOR_BGRA2RGB)

                    # Updating the data
                    datetimeObject = datetime.strptime(studentInfo['lastAttendanceTime'], '%Y-%m-%d %H:%M:%S')
                    secElapsed = (datetime.now() - datetimeObject).total_seconds()
                    print(secElapsed)

                    # Time difference between first & second image reading
                    if secElapsed > 20:

                        ref = db.reference(f'Students/{regNum}')
                        studentInfo['totalAttendance'] += 1
                        ref.child('totalAttendance').set(studentInfo['totalAttendance'])
                        ref.child('lastAttendanceTime').set(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

                    else:
                        modeType = 3
                        counter = 0
                        imgBG[44:44+633, 808:808+414] = imgMode[modeType]

            if modeType != 3:


                if 10 < counter < 20:
                    modeType = 2
                    imgBG[44:44+633, 808:808+414] = imgMode[modeType]

                if counter <= 10:

                    cv.putText(imgBG, str(studentInfo['totalAttendance']), (861, 125),
                               cv.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)  # Displaying Student Attendance over the UI

                    cv.putText(imgBG, str(regNum), (1006, 493),
                               cv.FONT_HERSHEY_COMPLEX, 0.50, (50, 50, 50), 1)  # Displaying Student Registration Number over the UI

                    cv.putText(imgBG, str(studentInfo['Year']), (1006, 550),
                               cv.FONT_HERSHEY_COMPLEX, 0.50, (50, 50, 50), 1)  # Displaying Student Year over the UI

                    (w, h), _ = cv.getTextSize(studentInfo['Name'], cv.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2

                    cv.putText(imgBG, str(studentInfo['Name']), (808 + offset, 445),
                               cv.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)  # Displaying Student Name over the UI

                    imgBG[175: 175 + 216, 909:909 + 216] = imgStudent

                counter += 1
                    # else:
                    # print("Stranger")

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBG[44:44+633, 808:808+414] = imgMode[modeType]
    else:
        modeType = 0
        counter = 0
    # cv.imshow("Webcam", frame)
    cv.imshow("Visual Attendance System", imgBG)
    cv.waitKey(1)

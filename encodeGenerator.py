from cv2 import cv2 as cv
import os
import face_recognition as fr
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://visual-attendance-system-default-rtdb.firebaseio.com/',
    'storageBucket': 'visual-attendance-system.appspot.com'
})


# Importing Student Images
imgPath = 'img'
imgPathList = os.listdir(imgPath)
imgList = []
studentIDs = []

for path in imgPathList:
    imgList.append(cv.imread(os.path.join(imgPath, path)))
    studentIDs.append(os.path.splitext(path)[0])    # Splitting the extension, then only taking ID & adding to studentID
    # print(os.path.splitext(path)[0])
    # print(os.path.splitext(path))

    fileName = os.path.join(imgPath, path)
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


def findEncodings(imageList):

    encodeList = []

    for img in imageList:
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        encode = fr.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


print("**** Encoding Started ****")
encodeListKnown = findEncodings(imageList=imgList)
encodeListKnownIds = [encodeListKnown, studentIDs]
print(encodeListKnown)
print("**** Encoding Completed ****")

# Dumping Encodings in the pickle file
file = open('EncodeFile.p', 'wb')
pickle.dump(encodeListKnownIds, file)
file.close()
print('**** File Saved ****')

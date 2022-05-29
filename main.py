import cv2
import numpy as np
import os
import face_recognition
from datetime import datetime

path='images'
images=[]
personName=[]
myList=os.listdir(path)
for c in myList:
    curImg=cv2.imread(f'{path}/{c}')
    images.append(curImg)
    personName.append(os.path.splitext(c)[0])
print(personName)

def faceEncodings(images):
    encodeList=[]
    for img in images:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode=face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encoded_list=faceEncodings(images)

def attendance(name):
    with open('attendance.xlsx','r+',errors="ignore") as f:
        myDataList=f.readlines()
        nameList=[]
        for line in myDataList:
            entry=line.split(',')
            nameList.append(entry[0])

        if name not in nameList:
            time_now=datetime.now()
            tstr= time_now.strftime('%H:%M:%S')
            dstr=time_now.strftime('%d/%m/%Y')
            f.writelines(f'{name},{tstr},{dstr}')
cap=cv2.VideoCapture(0)

while True:
    ret,frame=cap.read()
    #cv2.imshow('video',frame)
    faces=cv2.resize(frame,(0,0),None,0.25,0.25)
    faces=cv2.cvtColor(faces,cv2.COLOR_BGR2RGB)

    faces_current_frame=face_recognition.face_locations(faces)
    encodes_current_frame= face_recognition.face_encodings(faces,faces_current_frame)

    for encodeFace,faceLoc in zip(encodes_current_frame,faces_current_frame):
        matches=face_recognition.compare_faces(encoded_list, encodeFace)
        faceDis=face_recognition.face_distance (encoded_list, encodeFace)

        matchIndex=np.argmin(faceDis)
        if matches[matchIndex]:
            name=personName[matchIndex].upper()
            print(name)
            y1,x2,y2,x1=faceLoc
            y1,x2,y2,x1=y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(frame,(x1,y1),(x2,y2),(230,230,250),2)
            cv2.rectangle(frame,(x1,y1-20),(x2,y1),(230,230,250),cv2.FILLED)
            cv2.putText(frame, name, (x1+2, y1 - 8),
				cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,0,0), 2)
    
            attendance(name)
            print("added name to excel")
    cv2.imshow('Webcam',frame)
    if cv2.waitKey(10)==13:
        break

cap.release()
cv2.destroyAllWindows()

            

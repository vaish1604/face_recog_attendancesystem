import re
import os
from flask import Flask, Response, render_template, request,redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import os
import face_recognition
from datetime import datetime


UPLOAD_FOLDER='C:\\Users\\VAISHNAVI SHUKLA\\attendance\\images'
DOWNLOAD_FOLDER='C:\\Users\\VAISHNAVI SHUKLA\\attendance'
app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///attendance.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

path='images'
images=[]
personName=[]
myList=os.listdir(path)
def list():
    for c in myList:
        curImg=cv2.imread(f'{path}/{c}')
        images.append(curImg)
        personName.append(os.path.splitext(c)[0])


def faceEncodings(images):
    encodeList=[]
    for img in images:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode=face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encoded_list=faceEncodings(images)

def attendance(name):
    with open('attendance.csv','r+',newline = '',errors="ignore") as f:
        myDataList=f.readlines()
        nameList=[]
        for line in myDataList:
            entry=line.split(',')
            nameList.append(entry[0])

        if name not in nameList:
            time_now=datetime.now()
            tstr= time_now.strftime('%H:%M:%S')
            dstr=time_now.strftime('%d/%m/%Y')
            f.writelines(f'{name},{tstr},{dstr}\n')
        
    f.close()

class classroom(db.Model):
    stid=db.Column(db.String(200),primary_key=True)
    name=db.Column(db.String(200))
    dept=db.Column(db.String(200))
    yoa=db.Column(db.Integer)
    yog=db.Column(db.Integer)
    img=db.Column(db.String(200))

    def __repr__(self) -> str:
        return f"{self.stid} - {self.name}"

class teacher(db.Model):
    tid=db.Column(db.String(200),primary_key=True)
    pas=db.Column(db.String(200))
    name=db.Column(db.String(200))
    sub=db.Column(db.String(200))
    classes=db.Column(db.String(200))

    def __repr__(self) -> str:
        return f"{self.tid} - {self.name}"

def gen_frames():
    cap=cv2.VideoCapture(0,cv2.CAP_DSHOW)
    while True:
        ret,frame=cap.read()
        if not ret:
            break
        else:
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

                    students=classroom.query.all()
                    for s in students:
                        if name==(s.name).upper():
                            attendance(name)
            ret1, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()
    cv2.destroyAllWindows()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="POST":
        id=request.form['username']
        p=request.form['pass']
        for t in db.engine.execute("select pas from teacher where tid like '"+id+"';"):
            t=str(t)[2:7]
            print('executed till here')
            print(p)
            print(t)
            if t==p:
                return redirect('/action')
            else:
                
                return redirect('/login')

    return render_template('login.html')

@app.route('/show')
def classshow():
    all=classroom.query.all()
    return render_template('class.html',all=all)

@app.route('/register', methods=["GET","POST"])
def register():
    if request.method=="POST":
        stid=request.form.get('stid',False)
        name=request.form['name']
        dept=request.form['dept']
        yoa=request.form['yoa']
        yog=request.form['yog']
        img=request.files['img']
        filename = secure_filename(img.filename)
        dir=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img.save(dir)
        newst=classroom(stid=stid,name=name,dept=dept,yoa=yoa,yog=yog,img=dir)
        db.session.add(newst)
        db.session.commit()
        list()
        return redirect('/show')
    
    s=classroom.query.all()
    return render_template('register.html')


@app.route('/update/<stid>',methods=['GET','POST'])
def update(stid):
    if request.method=="POST":
        stid=request.form['stid']
        name=request.form['name']
        dept=request.form['dept']
        yoa=request.form['yoa']
        yog=request.form['yog']
        img=request.files['img']
        filename = secure_filename(img.filename)
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        u=classroom.query.filter_by(stid=stid).first()
        u.stid=stid
        u.name=name
        u.dept=dept
        u.yoa=yoa
        u.yog=yog
        u.img=os.path.join(app.config['UPLOAD_FOLDER'], filename)  
        db.session.add(u)
        db.session.commit()
        return redirect('/show')

    s=classroom.query.filter_by(stid=stid).first()
    return render_template('update.html',s=s)

# @app.route('/login/validate',methods=['GET','POST'])
# def validate():
    

@app.route('/delete/<stid>')
def delete(stid):
    d=classroom.query.filter_by(stid=stid).first()
    db.session.delete(d)
    db.session.commit()
    return redirect('/show')

@app.route('/attendance')
def attend():
    return render_template('attend.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/attendance/download',methods=['GET','POST'])
def download():
    f='attendance.csv'
    return send_file(f,as_attachment=True)

@app.route('/action')
def classlist():
    all=teacher.query.all()
    return render_template('classlist.html',all=all)

if __name__=="__main__":
    app.run(debug=True)

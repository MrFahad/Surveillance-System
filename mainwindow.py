from datetime import datetime,timedelta
from functools import partial
from PyQt5.QtCore import Qt, QRect, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QFileDialog,QHBoxLayout,QVBoxLayout,QWidget, QLabel, QDialog, QLineEdit, QPushButton,QDateTimeEdit,
QGridLayout, QSlider, QComboBox, QTableWidget, QTableWidgetItem,QMessageBox,QProgressBar,QScrollArea,QTabWidget,QSizePolicy)
from PyQt5 import QtGui, QtCore
import cv2
#import imutils
from imutils.face_utils import FaceAligner
from imutils.face_utils import rect_to_bb
from Database import mydb,PurgeDatabase
import time
import os
import dlib
import numpy as np
from skimage.feature import local_binary_pattern
# from sklearn.multiclass import OneVsRestClassifier
# from sklearn.svm import LinearSVC,SVC
# from sklearn.externals import joblib
import shutil
import queue
from utils import getFeatures,getDistance,getImagedist
import time
import xlsxwriter
import face_recognition as face_recognition
from language import Language
from camera import AddIPCamera,AddUSBCamera
databasehandler = mydb()
# databasehandler.insertUser('unknown')
LANGUAGE=Language()

class MySwitch(QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent)
        print('init')
        self.setCheckable(True)
        self.setMinimumWidth(66)
        self.setMinimumHeight(22)
    def paintEvent(self, event):
        label = LANGUAGE.YES if self.isChecked() else LANGUAGE.NO
        bg_color = Qt.green if self.isChecked() else Qt.red
        radius = 10
        width = 32
        center = self.rect().center()

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(center)
        painter.setBrush(QtGui.QColor(0,0,0))

        pen = QtGui.QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawRoundedRect(QRect(-width, -radius, 2*width, 2*radius), radius, radius)
        painter.setBrush(QtGui.QBrush(bg_color))
        sw_rect = QRect(-radius, -radius, width + radius, 2*radius)
        if not self.isChecked():
            sw_rect.moveLeft(-width)
        painter.drawRoundedRect(sw_rect, radius, radius)
        painter.drawText(sw_rect, Qt.AlignCenter, label)
class MainWindow(QWidget):
    def __init__(self, parent,language):
        super(MainWindow, self).__init__()

        if(language==0):
            LANGUAGE.setENGLISH()
        else:
            LANGUAGE.setARABIC()
        tempPath='data/temp'
        if(os.path.isdir(tempPath)):
            try:
                shutil.rmtree(shutil.rmtree(tempPath))
                os.mkdir(tempPath)
            except:
                print('exception removing tempdir')
        if(os.path.isdir(tempPath) == False):
            try:
                os.mkdir(tempPath)
            except:
                print('exception in making dir')
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.parent = parent
        self.detectedlist=[]
        self.undectedlist=[]
        self.cameralist=[]
        self.camInUse=[]
        self.createGUI()
        self.show()
    def createGUI(self):
        self.parent.statusBar().showMessage('Intializing')
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.topBar = QWidget()
        self.rightMenu = QWidget()
        self.leftMenu = QWidget()
        self.bottomMenu = QWidget()

        # self.topBar.setContentsMargins(0,0,0,0)
        self.cameraScreen = QLabel() 
        self.cameraScreen.setStyleSheet("background-color:black;")
        self.cameraScreen.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.cameraScreen.setText("No Camera")
        
        
        
        # self.bottomMenu.setStyleSheet("border:2px solid white;")
        self.layout.addWidget(self.topBar,          1, 1, 1, 6)
        self.layout.addWidget(self.leftMenu,        2, 1, 10, 1)
        self.layout.addWidget(self.cameraScreen,    2, 2, 10, 4)
        self.layout.addWidget(self.rightMenu,       2, 6, 10, 1)
        self.layout.addWidget(self.bottomMenu,      13, 1, 6, 6)
        

        self.cameras=QWidget()
        self.cameralayout = QHBoxLayout(self.cameras)
        self.cameralayout.setContentsMargins(0,0,0,0)
        self.cameralayout.setAlignment(Qt.AlignTop)
        self.scrollAreacameras = QScrollArea(self.cameras)
        
        self.scrollAreacameras.setWidgetResizable(True)
        self.scrollAreaWidgetContentscameras = QWidget()
        self.gridLayoutcameras = QVBoxLayout(self.scrollAreaWidgetContentscameras)
        self.scrollAreacameras.setWidget(self.scrollAreaWidgetContentscameras)
        self.gridLayoutcameras.setContentsMargins(0,0,0,0)
        self.cameralayout.addWidget(self.scrollAreacameras)
        self.gridLayoutcameras.setAlignment(Qt.AlignTop)

        self.leftMenuTitle=QLabel(LANGUAGE.CAMERA)
        self.leftMenuLayout=QGridLayout(self.leftMenu)
        self.leftMenuLayout.setContentsMargins(0,0,0,0)
        self.leftMenuLayout.addWidget(self.leftMenuTitle,1,1,1,1)
        self.leftMenuLayout.addWidget(self.cameras,2,1,1,10)

        # check,name,cam,camDirection = True,'test',0,'IN'
        # if check:
        #     self.cameraScreen = Camera(self,name=name,source=cam,camType="USB",camDirection=camDirection)
        #     self.cameralist.append(self.cameraScreen)
        #     self.gridLayoutcameras.insertWidget(0,self.cameraScreen)
        #     self.camInUse.append(cam)
        

        self.notDetectedFace=QWidget()
        self.notDetectedlayout = QHBoxLayout(self.notDetectedFace)
        self.notDetectedlayout.setContentsMargins(0,0,0,0)
        self.scrollAreaNotDetected = QScrollArea(self.notDetectedFace)
        self.scrollAreaNotDetected.setWidgetResizable(True)
        self.scrollAreaWidgetContentsNotDetected = QWidget()
        self.gridLayoutNotDetected = QVBoxLayout(self.scrollAreaWidgetContentsNotDetected)
        self.scrollAreaNotDetected.setWidget(self.scrollAreaWidgetContentsNotDetected)
        self.notDetectedlayout.addWidget(self.scrollAreaNotDetected)
        self.gridLayoutNotDetected.setAlignment(Qt.AlignTop)
        self.gridLayoutNotDetected.setContentsMargins(0,0,0,0)
        

        self.rightMenuTitle=QLabel(LANGUAGE.FACENOTRECOGNIZED)
        self.undetectedclear= QPushButton(LANGUAGE.CLEAR)
        self.recognitionbtn = MySwitch()
        self.recognitionbtn.setChecked(True)
        self.recognitionbtn.clicked.connect(self.toggleUnrecognized)
        self.undetectedclear.clicked.connect(self.clearUndetected)
        self.rightMenuLayout=QGridLayout(self.rightMenu)
        self.rightMenuLayout.addWidget(self.rightMenuTitle,1,1,1,1)
        self.rightMenuLayout.addWidget(self.undetectedclear,1,2,1,1)
        self.rightMenuLayout.addWidget(self.recognitionbtn,1,3,1,1)
        self.rightMenuLayout.addWidget(self.notDetectedFace,2,1,3,10)
        self.rightMenuLayout.setContentsMargins(0,0,0,0)

        
        self.DetectedFace=QWidget()
        self.Detectedlayout = QHBoxLayout(self.DetectedFace)
        self.Detectedlayout.setContentsMargins(0,0,0,0)
        self.scrollAreaDetected = QScrollArea(self.DetectedFace)
        self.scrollAreaDetected.setWidgetResizable(True)
        self.scrollAreaWidgetContentsDetected = QWidget()
        self.gridLayoutDetected = QHBoxLayout(self.scrollAreaWidgetContentsDetected)
        self.scrollAreaDetected.setWidget(self.scrollAreaWidgetContentsDetected)
        self.Detectedlayout.addWidget(self.scrollAreaDetected)
        self.gridLayoutDetected.setAlignment(Qt.AlignLeft)
        self.gridLayoutDetected.setContentsMargins(0,0,0,0)



        self.bottomMenuTitle=QLabel(LANGUAGE.FACERECOGNIZED)
        self.detectedclear= QPushButton(LANGUAGE.CLEAR)
        self.detectedclear.clicked.connect(self.clearDetected)

        self.bottomMenuLayout=QGridLayout(self.bottomMenu)
        self.bottomMenuLayout.setContentsMargins(0,0,0,0)
        self.bottomMenuLayout.addWidget(self.bottomMenuTitle,   1,1,1,1)
        self.bottomMenuLayout.addWidget(self.detectedclear,     1,2,1,1)
        self.bottomMenuLayout.addWidget(self.DetectedFace,   2,1,5,10)


        self.topLayout = QGridLayout(self.topBar)
        
        self.logo= QLabel('asdas')
        self.logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.logo.setMaximumHeight(200)
        self.logo.setMaximumWidth(400)
        # self.logo.setStyleSheet("border-color:black; border:2px;")
        pixmap = QtGui.QPixmap('logo.png')
        pixmap = pixmap.scaled(300, 300, QtCore.Qt.KeepAspectRatio)
        self.logo.setPixmap(pixmap)
        self.logo.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.topLayout.addWidget(self.logo,1,1,1,2)
        self.addUsbCamera = QPushButton(LANGUAGE.ADDUSBCAMERA)
        self.addIpCamera = QPushButton(LANGUAGE.ADDIPCAMERA)
        self.trainBtn = QPushButton(LANGUAGE.TRAIN)
        self.viewAttend = QPushButton(LANGUAGE.VIEWATTENDANCE)
        self.logout = QPushButton(LANGUAGE.LOGOUT)
        self.purge = QPushButton(LANGUAGE.PURGE)
        self.purge.clicked.connect(self.showPurgeMenu)
        self.topLayout.addWidget(self.addIpCamera,1,3,1,1)
        self.topLayout.addWidget(self.addUsbCamera,1,4,1,1)
        self.topLayout.addWidget(self.trainBtn,1,5,1,1)
        self.topLayout.addWidget(self.viewAttend,1,6,1,1)
        self.topLayout.addWidget(self.purge,1,7,1,1)
        self.topLayout.addWidget(self.logout,1,8,1,1)
        self.topLayout.setContentsMargins(0,0,0,0)
        self.addUsbCamera.clicked.connect(self.AddUSBCamera)
        self.addIpCamera.clicked.connect(self.AddIpCamera)
        self.trainBtn.clicked.connect(self.TrainModel)
        self.viewAttend.clicked.connect(self.viewAttendance)
        self.parent.statusBar().showMessage('Done')
        self.Trainer = Trainer()
        # for i in range(100):
        #     face = FaceCard(self,name=str(i))
        #     self.notDetected(face)
        # for i in range(100):
        #     face = FaceCard(self,name=str(i),match=90)
        #     self.addDetected(face)
        # newCam=Camera(self,'Cam0',0,"USB",camDirection="IN")
        # self.AddCameraTab(newCam,'Cam0')
        # check,name,cam,camDirection = True,'test',0,'IN'
        # if check:
        #     newCam = Camera(self,name=name,source=cam,camType="USB",camDirection=camDirection)
        #     self.cameralist.append(newCam)
        #     index=self.cameraScreen.addTab(newCam,name)
        #     newCam.setTabIndex(index)
        #     self.camInUse.append(cam)
    def toggleUnrecognized(self):
        checkUnrecognized = self.recognitionbtn.isChecked()
        for cams in self.cameralist:
            cams.setUnRecognized(checkUnrecognized)
    def clearDetected(self):
        for c in self.cameralist:
            try:
                c.clearDetected()
            except:
                print('deletion failed')
        for c in self.detectedlist:
            try:
                c.deleteLater()
            except:
                print('deletion failed')
        self.detectedlist=[]
    def clearUndetected(self):
        for c in self.cameralist:
            try:
                c.clearUnDetected()
            except:
                print('deletion failed')
        for c in self.undectedlist:
            try:
                c.deleteLater()
            except:
                print('deletion failed')
        self.undectedlist=[]
    def viewme(self,widget):
        for c in self.cameralist:
            c.isViewing = False
            c.name.setStyleSheet("color:white;")
            if c.iserror:
                c.name.setStyleSheet("color:red;")
        widget.isViewing = True
        widget.name.setStyleSheet("color:blue;")
        if(widget.iserror):
            self.cameraScreen.setStyleSheet("background-color:black;")
            self.cameraScreen.setText("There is Problem with this Camera CLose and Try Re-Adding")
    def draw(self,rgbImage):
        w = self.cameraScreen.width()
        h = self.cameraScreen.height()
        convertToQtFormat = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],QtGui.QImage.Format_RGB888)
        q = convertToQtFormat.scaled(w, h, Qt.KeepAspectRatio)
        self.cameraScreen.setPixmap(QtGui.QPixmap.fromImage(q))
    def cameraclosed(self):
        check=False
        if len(self.cameralist)>0:
            for cam in self.cameralist:
                if (cam.isViewing):
                    check = True
            if check == False:
                camworking = self.cameralist[0]
                camworking.isViewing = True
        else:
            self.cameraScreen.setStyleSheet("background-color:black;")
            self.cameraScreen.setText("No Camera")



    def showMessage(self,msg):
        self.parent.statusBar().showMessage(str(msg))
    def addDetected(self,widget):
        self.detectedlist.append(widget)
        self.gridLayoutDetected.insertWidget(0,widget)
    def notDetected(self,widget):
        self.undectedlist.append(widget)
        self.gridLayoutNotDetected.insertWidget(0,widget)
    def AddUSBCamera(self):
        camdialogue=AddUSBCamera(self,LANGUAGE)
        # print(camdialogue.newCam)
        check,name,cam,camDirection = camdialogue.newCam
        if check:
            newCam = Camera(self,name=name,source=cam,camType="USB",camDirection=camDirection,UnRecognized=self.recognitionbtn.isChecked())
            self.cameralist.append(newCam)
            self.gridLayoutcameras.insertWidget(0,newCam)
            self.camInUse.append(cam)
            self.viewme(newCam)
        camdialogue.deleteLater()
    def AddIpCamera(self):
        camdialogue=AddIPCamera(self,LANGUAGE)
        check,name,cam,camDirection = camdialogue.newCam
        if check:
            newCam = Camera(self,name=name,source=cam,camType="IP",camDirection=camDirection,UnRecognized=self.recognitionbtn.isChecked())
            self.cameralist.append(newCam)
            self.gridLayoutcameras.insertWidget(0,newCam)
            self.viewme(newCam)

    def TrainModel(self):
        self.Trainer = Trainer()
        self.Trainer.showTrainingDialogue(self)
    def reloadmodels(self):
        for f in self.cameralist:
            try:
                f.cameraThread.load()
            except:
                print('exception in loading model')
    def viewAttendance(self):
        viewatt=ViewAttendance()
        print(viewatt)
    def showPurgeMenu(self):
        pdialouge=QDialog()
        pdialouge.setWindowTitle(LANGUAGE.PURGE)
        pdialouge.setMinimumHeight(100)
        pdialouge.setMinimumWidth(100)
        layout=QGridLayout(pdialouge)
        closebtn=QPushButton(LANGUAGE.NO)
        closebtn.clicked.connect(lambda :pdialouge.accept())
        purgebtn=QPushButton(LANGUAGE.YES)
        purgebtn.clicked.connect(partial(self.purgesystem,pdialouge))
        layout.addWidget(QLabel(LANGUAGE.QUESTIONPURGE),1,1,1,6)
        layout.addWidget(purgebtn,2,1,1,3)
        layout.addWidget(closebtn,2,4,1,3)
        pdialouge.exec_()
    
    def purgesystem(self,dialouge):
        PurgeDatabase()
        modelpath="data/model/model.pkl"
        datapath="data/person"
        tempPath="data/temp"
        if(os.path.isfile(modelpath)):
            try:
                os.remove(modelpath)
            except:
                print('exception removing path')
        for mydir in os.listdir(datapath):
            if(mydir == "unknown"):
                pass
            else:
                try:
                    shutil.rmtree(datapath+'/'+mydir)
                except:
                    print('exception dir',mydir)
            
        if(os.path.isdir(tempPath)):
            try:
                shutil.rmtree(shutil.rmtree(tempPath))
                
            except:
                print('exception removing tempdir')
        if(os.path.isdir(tempPath) ==  False):
            try:
                os.mkdir(tempPath)
            except:
                print('exception createing tempdir')
            
             
        for i in self.detectedlist:
            try:
                i.deleteLater()
            except:
                print('exception deleting facecard')
        
        for i in self.undectedlist:
            try:
                i.deleteLater()
            except:
                print('exception deleting facecard')
        for c in self.cameralist:
            try:
                c.close()
                c.deleteLater()
            except:
                print('exception deleting camera')
        dialouge.accept()
        # for i in self.detectedlist:

        
        
class ViewAttendance(QDialog):
    def __init__(self):
        super(ViewAttendance,self).__init__()
        self.exportlist=[]
        self.setWindowTitle(LANGUAGE.ATTENDANCE)
        self.setMinimumHeight(100)
        self.setMinimumWidth(300)
        dialogueLayout      = QGridLayout(self)
        dialogueCloseBtn    = QPushButton(LANGUAGE.CLOSE)

        self.startdate           = QDateTimeEdit()
        self.startdate.setCalendarPopup(True)
        sdt=datetime.now()
        sdt=datetime(year=sdt.year,month=sdt.month,day=sdt.day,hour=0,minute=0)
        self.startdate.setMinimumDateTime(datetime(year=2018,month=6,day=1,hour=0,minute=0))
        self.startdate.setDateTime(sdt)
        self.startdate.dateTimeChanged.connect(self.check_for_change)


        self.enddate = QDateTimeEdit()
        self.enddate.setCalendarPopup(True)
        self.enddate.setMinimumDateTime(datetime(year=2018,month=6,day=1,hour=0,minute=0))
        edt=datetime.now()
        edt=datetime(year=edt.year,month=edt.month,day=edt.day,hour=23,minute=59)
        self.enddate.setDateTime (edt)
        self.enddate.dateTimeChanged.connect(self.check_for_change)

        self.export = QPushButton('Export')
        dialogueCloseBtn.clicked.connect(lambda : self.accept())
        self.export.setEnabled(True)
        self.attendanceTable=QTableWidget(0,7)
        self.attendanceTable.setHorizontalHeaderLabels(['User','InTime','OutTime','Camera IN','Camera Out','Time(minutes)','User Total Time(minutes)'])
        dialogueLayout.addWidget(QLabel('Start Date'),1,6,1,1)
        dialogueLayout.addWidget(self.startdate,1,8,1,1)
        dialogueLayout.addWidget(QLabel('End Date'),1,9,1,1)
        dialogueLayout.addWidget(self.enddate,1,10,1,1)
        dialogueLayout.addWidget(self.startdate,1,7,1,1)
        dialogueLayout.addWidget(self.attendanceTable,2,1,10,12)
        dialogueLayout.addWidget(dialogueCloseBtn,12,9,1,1)
        dialogueLayout.addWidget(self.export,12,8,1,1)
        self.export.clicked.connect(self.openfile)
        self.attendanceTable.setRowCount(0)
        self.check_for_change()
        self.exec_()

    def openfile(self):
        
        dirname = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if(dirname):
            print('dirname' ,dirname)
            workbook = xlsxwriter.Workbook(dirname+'/'+str(datetime.now()).replace(':','').replace(' ','_').replace('.','')+'.xlsx')
            worksheet = workbook.add_worksheet("Attendance")
            row = 0
            header=['User','InTime','OutTime','Camera IN','Camera Out','Time','User Total Time']
            worksheet.write(row, 0, header[0])
            worksheet.write(row, 1, header[1])
            worksheet.write(row, 2, header[2])
            worksheet.write(row, 3, header[3])
            worksheet.write(row, 4, header[4])
            worksheet.write(row, 5, header[5])
            worksheet.write(row, 6, header[6])
            row = 1 
            # Iterate over the data and write it out row by row. 
            for user in self.exportlist:
                for u in user['attendance']:
                    # self.attendanceTable.setRowCount(count+1)
                    worksheet.write(row,0,u[0])
                    worksheet.write(row,1,u[1])
                    worksheet.write(row,2,u[2])
                    worksheet.write(row,3,u[3])
                    worksheet.write(row,4,u[4])
                    worksheet.write(row,5,u[5])
                    worksheet.write(row,6,str(user['totaltime']))
                    row=row+1
            workbook.close()  
            # self.showMessage('File Saved')
        else:
            print('Invalid Directory')
    def check_for_change(self):
        print('change starts')
        self.attendanceTable.setRowCount(0)
        self.exportlist=[]
        for user in databasehandler.getAllUsers():
            # self.startdate.dateTime
            sdate = self.startdate.dateTime().toPyDateTime()
            edate = self.enddate.dateTime().toPyDateTime()

            delta = edate - sdate
            print("num days=",delta.days)
            listdays=[]
            previousday=None
            for i in range(delta.days + 1):
                day = sdate + timedelta(days=i)
                if(previousday is not None):
                    listdays.append((previousday,day))
                # print(previousday)
                previousday=day
            if(len(listdays)==0):
                listdays.append((sdate,edate))
            # print('Days List',listdays)
            
            totalminute_overall=0
            outlist=[]
            for dates in listdays:
                # print ('iterating day ',dates)
                start=datetime(year=dates[0].year,month=dates[0].month,day=dates[0].day,hour=0,minute=0)
                end  =datetime(year=dates[1].year,month=dates[1].month,day=dates[1].day,hour=23,minute=59,second=59)
                # print('user is ',user.name)
                # print(start,'     to  ',end)
                uenter,uexit = databasehandler.getuserinout(user.id,start,end)
                print(uenter,'             ',uexit)
                if uenter is not None and uexit is not None:
                    totaltimeminutes =  int((uexit.datetime - uenter.datetime).total_seconds() / 60.0)
                    totalminute_overall+=totaltimeminutes
                    out=[user.username,str(uenter.datetime.strftime("%m-%d-%Y %H:%M")),str(uexit.datetime.strftime("%m-%d-%Y %H:%M")),uenter.cam,uexit.cam,str(totaltimeminutes)]
                    outlist.append(out)
                elif(uenter is not None and uexit is None):
                    totaltimeminutes = 0
                    out=[user.username,str(uenter.datetime.strftime("%m-%d-%Y %H:%M")),str(None),uenter.cam,str(None),str(totaltimeminutes)]
                    outlist.append(out)
                else:
                    out=[user.username,"NOT PRESENT",str(None),"NONE",str(None),str(None)]
                    outlist.append(out)

            if(len(outlist)>0):
                data={'user':user,'attendance':outlist,'totaltime':totalminute_overall}
                totalminute_overall=0
                self.exportlist.append(data)
        count=0
        # print(exportlist)
        for user in self.exportlist:
            for u in user['attendance']:
                self.attendanceTable.setRowCount(count+1)
                self.attendanceTable.setItem(count,0,QTableWidgetItem(u[0]))
                self.attendanceTable.setItem(count,1,QTableWidgetItem(u[1]))
                self.attendanceTable.setItem(count,2,QTableWidgetItem(u[2]))
                self.attendanceTable.setItem(count,3,QTableWidgetItem(u[3]))
                self.attendanceTable.setItem(count,4,QTableWidgetItem(u[4]))
                self.attendanceTable.setItem(count,5,QTableWidgetItem(u[5]))
                self.attendanceTable.setItem(count,6,QTableWidgetItem(str(user['totaltime'])))
                count+=1
        if(count>0):
            self.export.setEnabled(True)
        width = self.attendanceTable.verticalHeader().width()
        width += self.attendanceTable.horizontalHeader().length()
        if self.attendanceTable.verticalScrollBar().isVisible():
            width += self.attendanceTable.horizontalScrollBar().width()
        width += self.attendanceTable.frameWidth() * 3
        print('width is ',width)
        self.attendanceTable.setFixedWidth(width)
        print(self.exportlist)

class Trainer(QThread):
    def __init__(self):
        super(Trainer,self).__init__()
        # self.layout=QGridLayout(self)
        self.close = QPushButton(LANGUAGE.CLOSE)
        self.modelpath="data/model/model.pkl"
        self.datapath='data/person'
        self.trainingProgress=QProgressBar()
        self.trainingProgress.setValue(int(0))
        self.trainingProgress.setFormat(LANGUAGE.CLICKTOSTARTTRAINING)
        
        # self.trainingProgress.setTextVisible(False)
    def run(self):

        databasehandler.deleteAllFeature()
        if(len(os.listdir(self.datapath))<1):
            self.trainingProgress.setFormat(LANGUAGE.HALTEDNOTENOUGHDATA)
            return
        self.trainingProgress.setFormat('Training')
        self.trainingProgress.setValue(int(45))
        # print('data check done')
        for mydir in os.listdir(self.datapath):
            # print('loading dir',mydir)
            temp=os.path.join(self.datapath, mydir)
            user=databasehandler.getUser(mydir)
            if(user ==None):
                user= databasehandler.insertUser(mydir)
            # print('database operation done')
            if (os.path.isfile(temp)==False):
                count=0
                # print('file loaded')
                for sample in os.listdir(temp):
                    picturepath=os.path.join(temp,sample)
                    if(os.path.isfile(picturepath)==True):
                        img = cv2.imread(picturepath)
                        f=getFeatures(img)
                        if type(f) is not type(None):
                            databasehandler.insertFeature(user.id,f)
                # print('files loaded')
                if(count<10):
                    print ("warning for some persons images are not enough")
        # print('out of loop')
        # self.trainingProgress.setFormat('Processing Data')
        # self.trainingProgress.setValue(int(25))
        # model=OneVsRestClassifier(SVC(kernel='linear',probability=True))
        # print('model created')
        # self.trainingProgress.setValue(int(40))
        # self.trainingProgress.setFormat('Training')
        # print('model training')
        # model.fit(features, labelsnames)
        # print('model training completed')
        # joblib.dump(model, self.modelpath)
        # print('model saved')
        self.trainingProgress.setFormat('Completed')
        self.trainingProgress.setValue(int(100))
        self.parent.reloadmodels()
    # def run(self):
    #     labelsnames=[]
    #     features=[]
    #     self.trainingProgress.setFormat('Loading Data')
    #     self.trainingProgress.setValue(int(5))
    #     if(len(os.listdir(self.datapath))<2):
    #         self.trainingProgress.setFormat('Halted Not Enough Data')
    #         return
    #     self.trainingProgress.setValue(int(20))
    #     # print('data check done')
    #     for mydir in os.listdir(self.datapath):
    #         # print('loading dir',mydir)
    #         temp=os.path.join(self.datapath, mydir)
    #         user=databasehandler.getUser(mydir)
    #         # print('database operation done')
    #         if (os.path.isfile(temp)==False):
    #             count=0
    #             # print('file loaded')
    #             for sample in os.listdir(temp):
    #                 picturepath=os.path.join(temp,sample)
    #                 if(os.path.isfile(picturepath)==True):
    #                     img = cv2.imread(picturepath)
    #                     f=getFeatures(img)
    #                     databasehandler.insertFeature(user.id,feature)
    #                     if type(f) is not type(None):
    #                         features.append(f)
    #                         labelsnames.append(mydir)
    #                         count=count+1
    #             # print('files loaded')
    #             if(count<10):
    #                 print ("warning for some persons images are not enough")
    #     print('out of loop')
    #     # self.trainingProgress.setFormat('Processing Data')
    #     # self.trainingProgress.setValue(int(25))
    #     model=OneVsRestClassifier(SVC(kernel='linear',probability=True))
    #     print('model created')
    #     self.trainingProgress.setValue(int(40))
    #     self.trainingProgress.setFormat('Training')
    #     print('model training')
    #     model.fit(features, labelsnames)
    #     print('model training completed')
    #     joblib.dump(model, self.modelpath)
    #     print('model saved')
    #     self.trainingProgress.setFormat('Completed')
    #     self.trainingProgress.setValue(int(100))
    #     self.parent.reloadmodels()
    def showTrainingDialogue(self,parent):
        self.parent=parent
        self.dialogue = QDialog(parent)
        self.dialogue.setWindowTitle("Training Model")
        # self.dialogue.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.dialogue.setMinimumHeight(300)
        self.dialogue.setMinimumWidth(300)
        self.dialogueLayout   = QGridLayout(self.dialogue)
        self.dialogueCloseBtn = QPushButton(LANGUAGE.CLOSE,self.dialogue)
        self.dialogueTrain    = QPushButton(LANGUAGE.TRAIN,self.dialogue)
        self.dialogueCloseBtn.clicked.connect(lambda : self.dialogue.accept())
        self.dialogueTrain.setEnabled(False)
        self.dialogueTrain.clicked.connect(self.startTraining)

        self.Person=QWidget()
        self.Personlayout = QHBoxLayout(self.Person)
        self.scrollAreaDetected = QScrollArea(self.Person)
        self.scrollAreaDetected.setWidgetResizable(True)
        self.scrollAreaWidgetContentsDetected = QWidget()
        self.gridLayoutPerson = QVBoxLayout(self.scrollAreaWidgetContentsDetected)
        self.scrollAreaDetected.setWidget(self.scrollAreaWidgetContentsDetected)
        self.Personlayout.addWidget(self.scrollAreaDetected)
        self.gridLayoutPerson.setAlignment(Qt.AlignTop)
        self.dialogueLayout.addWidget(self.Person,1,1,10,2)
        self.dialogueLayout.addWidget(self.dialogueTrain,11,1,1,1)
        self.dialogueLayout.addWidget(self.dialogueCloseBtn,11,2,1,1)
        self.dialogueLayout.addWidget(self.dialogueTrain,12,1,1,1)
        self.dialogueLayout.addWidget(self.dialogueCloseBtn,12,2,1,1)
        self.dialogueLayout.addWidget(self.trainingProgress,13,1,1,2)
        paths=os.listdir(self.datapath)
        if(len(paths)<1):
            # print('not enough data For Training')
            q=QLabel(LANGUAGE.NOTENOUGHDATAFORTRAINING)
            q.setStyleSheet("color:red;font-size:20;")
            q.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            qwidget=QWidget(self.dialogue)
            qlayout=QGridLayout(qwidget)
            qlayout.addWidget(q,1,1,1,2)
            self.gridLayoutPerson.insertWidget(0,qwidget)
        else:
            self.dialogueTrain.setEnabled(True)
            count=1
            for m in paths:
                if(m != "unknown"):
                    q=QLabel(str(count)+'-'+str(m))
                    p=QPushButton(LANGUAGE.DELETE)
                    p.clicked.connect(partial(self.deletePerson,name=m))
                    qwidget=QWidget(self.dialogue)
                    qlayout=QGridLayout(qwidget)
                    qlayout.addWidget(q,1,1,1,1)
                    qlayout.addWidget(p,1,2,1,1)
                    self.gridLayoutPerson.insertWidget(0,qwidget)
                    count=count+1
        self.dialogue.exec_()
    def deletePerson(self,name):
        try:
            self.dialogue.accept()
            shutil.rmtree(self.datapath+'/'+name)
            user=databasehandler.getUser(name)
            if(user is not None):
                databasehandler.deleteUser(user.id)
        except:
            print('fail to delete')
        self.showTrainingDialogue(self.parent)
    def startTraining(self):
        # print('Training Started')
        self.start()
        
        
class FaceCard(QWidget):
    def __init__(self,parent,imagepath,name="test",match=9,status="OUT 13:00",Detected=False,camName="testCam",dt=datetime.now()):
        super(FaceCard, self).__init__()
        self.parent=parent
        self.startTime = dt
        self.layout = QGridLayout(self)
        self.threshold = 0.10
        self.camNamestr = camName
        self.Detected=Detected
        self.imagepath =[]
        self.imagepath.append(imagepath)
        self.name = name
        self.match = match
        self.status = status
        self.dir = 'data/person'
        self.faces = []
        self.initGui()
        self.isViewing = False
    def initGui(self):
        self.setMaximumWidth(int(self.parent.width()/8))
        self.setMaximumHeight(int(self.parent.height()/5))
        self.image=QLabel()
        self.nameLabel = QLabel(self.name)
        self.nameLabel.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.camName = QLabel(self.camNamestr)
        self.camName.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.progressBar= QProgressBar()
        self.progressBar.setValue(int(self.match))
        self.progressBar.setTextVisible(False)
        self.value = QLabel(str(self.match)+'% MATCH')
        self.statusLabel = QLabel(str(self.status)+' '+self.startTime.strftime("%m-%d-%Y, %H:%M"))
        self.statusLabel.setStyleSheet('color:red;')
        self.viewButton = QPushButton(LANGUAGE.VIEWALLTIME)
        self.viewButton.clicked.connect(self.viewAttendance)
        self.addDb      = QPushButton(LANGUAGE.ADD)
        self.addDb.clicked.connect(self.addImage)
        
        
        # pixmap = QtGui.QPixmap(self.imagepath[0])
        w = 150 #self.image.width()
        h = 150 #self.image.height()
        convertToQtFormat = QtGui.QImage(self.imagepath[0].data, self.imagepath[0].shape[1], self.imagepath[0].shape[0],QtGui.QImage.Format_RGB888)
        q = convertToQtFormat.scaled(w, h, Qt.KeepAspectRatio)
        self.image.setPixmap(QtGui.QPixmap.fromImage(q))
        self.image.setAlignment(Qt.AlignCenter | Qt.AlignVCenter) 
        if self.Detected:
            self.setupLayoutDetected()
        else:
            self.setupLayoutNotDetected()
    
    def setupLayoutNotDetected(self):
        self.layout.addWidget(self.image ,           1,1,2,2)
        self.layout.addWidget(self.camName  ,        3,1,1,1)
        self.layout.addWidget(self.nameLabel  ,      3,2,1,1)
        # self.layout.addWidget(self.progressBar,      4,1,1,2)
        self.layout.addWidget(self.value,            5,1,1,1)
        self.layout.addWidget(self.statusLabel,      5,2,1,1)
        self.layout.addWidget(self.addDb,            6,1,1,2)
    def setupLayoutDetected(self):
        self.layout.addWidget(self.image ,           1,1,2,2)
        self.layout.addWidget(self.camName  ,        3,1,1,1)
        self.layout.addWidget(self.nameLabel  ,      3,2,1,1)
        self.layout.addWidget(self.progressBar,      4,1,1,2)
        self.layout.addWidget(self.value,            5,1,1,1)
        self.layout.addWidget(self.statusLabel,      5,2,1,1)
        self.layout.addWidget(self.viewButton,       6,1,1,2)
    def imagecard(self,index,image):
        widget = QWidget()
        layout = QGridLayout(widget)
        imagehold = QLabel()
        deletebutton=QPushButton(LANGUAGE.DELETE)
        deletebutton.clicked.connect(partial(self.delete,index))
        imagehold.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        w = 150 #self.image.width()
        h = 150 #self.image.height()
        convertToQtFormat = QtGui.QImage(image.data, image.shape[1], image.shape[0],QtGui.QImage.Format_RGB888)
        q = convertToQtFormat.scaled(w, h, Qt.KeepAspectRatio)
        imagehold.setPixmap(QtGui.QPixmap.fromImage(q))
        layout.addWidget(imagehold,1,1,5,5)
        layout.addWidget(deletebutton,6,2,1,1)

        return widget
    
    def delete(self,index):
        self.imagepath.pop(index)
        for c in self.cards:
            try:
                c.deleteLater()
            except:
                print('exception deleting card')
        row = 1
        col = 1
        self.cards=[]
        for i in range(0,len(self.imagepath)):
            if(col>5):
                col=1
                row+=1
            card=self.imagecard(i,self.imagepath[i])
            self.imageAIlayout.addWidget(card,row,col,1,1)
            self.cards.append(card)
            col+=1

    def addImage(self):
        self.isViewing = True
        self.cards=[]
        self.dialogueAI =   QDialog()
        self.dialogueAI.setMinimumHeight(100)
        self.dialogueAI.setMinimumWidth(300)
        self.layoutAI   =   QGridLayout(self.dialogueAI)
        self.imageAI    =   QWidget()
        self.imageAIlayout =QGridLayout(self.imageAI)
        self.dialogueAI.setWindowTitle(LANGUAGE.ADDTODATABASE)

        row = 1
        col = 1
        for i in range(0,len(self.imagepath)):
            if(col>5):
                col=1
                row+=1
            card=self.imagecard(i,self.imagepath[i])
            self.imageAIlayout.addWidget(card,row,col,1,1)
            self.cards.append(card)
            col+=1
        # w = 150 #self.image.width()
        # h = 150 #self.image.height()
        # convertToQtFormat = QtGui.QImage(self.imagepath[0].data, self.imagepath[0].shape[1], self.imagepath[0].shape[0],QtGui.QImage.Format_RGB888)
        # q = convertToQtFormat.scaled(w, h, Qt.KeepAspectRatio)
        # self.imageAI.setPixmap(QtGui.QPixmap.fromImage(q))
        # pixmap = QtGui.QPixmap(self.imagepath[0])
        # pixmap = pixmap.scaled(150, 150, QtCore.Qt.KeepAspectRatio)
        # self.imageAI.setPixmap(pixmap)
        # self.imageAI.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.nameAI     =   QLineEdit()
        self.addAI      =   QPushButton(LANGUAGE.ADD)
        self.closeAI    =   QPushButton(LANGUAGE.CLOSE)
        self.addAI.clicked.connect(self.addimageVerify)
        self.closeAI.clicked.connect(self.close)
        self.layoutAI.addWidget(self.imageAI    ,1,1,8,8)
        self.layoutAI.addWidget(QLabel(LANGUAGE.NAME+':') ,9,3,1,2)
        self.layoutAI.addWidget(self.nameAI     ,9,5,1,2)
        self.layoutAI.addWidget(self.addAI      ,10,3,1,2)
        self.layoutAI.addWidget(self.closeAI    ,10,5,1,2)
        self.dialogueAI.exec_()
    def close(self):
        self.isViewing=False
        self.dialogueAI.accept()
    def addimageVerify(self):
        name=self.nameAI.text()
        if(name == "" or name.isalpha() is False):
            self.nameAI.setStyleSheet("border: 2px solid red;")
            return 
        if (os.path.exists(self.dir+'/'+ name)):
            u=databasehandler.insertUser(name)
            for i in self.imagepath:
                filename= self.dir+'/'+ name + '/' +str(datetime.now()).replace(':','_').replace(' ','_').replace('.','_')+'.jpg'
                cv2.imwrite(filename,cv2.cvtColor(i, cv2.COLOR_RGB2BGR))
        else:
            u=databasehandler.insertUser(name)
            os.mkdir(self.dir+'/'+ name)
            for i in self.imagepath:
                filename= self.dir+'/'+ name + '/' +str(datetime.now()).replace(':','_').replace(' ','_').replace('.','_')+'.jpg'
                cv2.imwrite(filename,cv2.cvtColor(i, cv2.COLOR_RGB2BGR))
        self.dialogueAI.accept()
        self.deleteLater()
    def verify(self,img):
        if self.isViewing:
            return False
        if(len(self.imagepath)>=10):
            return False
        try:
            totaldist=0
            totaldist=getImagedist(img,self.imagepath[len(self.imagepath)-1])
            # print('distance is ',totaldist)
            if(totaldist < self.threshold):
                self.imagepath.append(img)
                self.nameLabel.setText(self.name + ' '+ str(len(self.imagepath)))
                w = 150 #self.image.width()
                h = 150 #self.image.height()
                convertToQtFormat = QtGui.QImage(self.imagepath[len(self.imagepath)-1].data, self.imagepath[len(self.imagepath)-1].shape[1], self.imagepath[len(self.imagepath)-1].shape[0],QtGui.QImage.Format_RGB888)
                q = convertToQtFormat.scaled(w, h, Qt.KeepAspectRatio)
                self.image.setPixmap(QtGui.QPixmap.fromImage(q))
                self.image.setAlignment(Qt.AlignCenter | Qt.AlignVCenter) 
                return True
            else:
                return False
        except:
            return False
    def update(self):
        if self.isViewing:
            return
        self.nameLabel.setText(self.name + ' '+ str(len(self.imagepath)))
        self.progressBar.setValue(int(self.match))
        self.value.setText(str(self.match)+'% MATCH')
    def viewAttendance(self):
        user=databasehandler.getUser(self.name)
        n=databasehandler.getAttendance(user.id)
        def openfile():
            dirname = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            if(dirname):
                print('dirname' ,dirname)
                workbook = xlsxwriter.Workbook(dirname+'/'+str(datetime.now()).replace(':','').replace(' ','_').replace('.','')+'.xlsx')
                worksheet = workbook.add_worksheet("Attendance")
                row = 0
                worksheet.write(row, 0, 'Date')
                worksheet.write(row, 1, 'Time')
                worksheet.write(row, 2, 'Name')
                worksheet.write(row, 3, 'Camera')
                worksheet.write(row, 4, 'Type')
                row = 1 
                for t in n: 
                    worksheet.write(row, 0,str(t.datetime.strftime("%m-%d-%Y")))
                    worksheet.write(row, 1,str(t.datetime.strftime("%H:%M")))
                    worksheet.write(row, 2,str(t.name))
                    worksheet.write(row, 3,str(t.cam))
                    worksheet.write(row, 4,str(t.direction))
                    row += 1 
                workbook.close()  
                self.parent.showMessage('File Saved')
            else:
                self.parent.showMessage('Invalid Directory')
        dialogue = QDialog()
        dialogue.setWindowTitle(LANGUAGE.ATTENDANCE)
        dialogue.setMinimumHeight(100)
        dialogue.setMinimumWidth(300)
        dialogueLayout   = QGridLayout(dialogue)
        dialogueCloseBtn = QPushButton(LANGUAGE.CLOSE)
        export = QPushButton('Export')
        dialogueCloseBtn.clicked.connect(lambda : dialogue.accept())
        export.clicked.connect(openfile)
        # attendance=databasehandler.getAllAttendance()
        attendanceTable=QTableWidget(0,5)
        attendanceTable.setHorizontalHeaderLabels(['Date','Time','Name','Camera','Type'])
        dialogueLayout.addWidget(attendanceTable,1,1,10,10)
        dialogueLayout.addWidget(dialogueCloseBtn,11,10,1,1)
        dialogueLayout.addWidget(export,11,9,1,1)
        attendanceTable.setRowCount(0)
        count=0
        
        for t in n:
            attendanceTable.setRowCount(count+1)
            attendanceTable.setItem(count,0,QTableWidgetItem(str(t.datetime.strftime("%m-%d-%Y"))))
            attendanceTable.setItem(count,1,QTableWidgetItem(str(t.datetime.strftime("%H:%M"))))
            attendanceTable.setItem(count,2,QTableWidgetItem(str(t.name)))
            attendanceTable.setItem(count,3,QTableWidgetItem(str(t.cam)))
            attendanceTable.setItem(count,3,QTableWidgetItem(str(t.direction)))
            count+=1
        dialogue.exec_()
        

class FaceRecognizer(QThread):
    faceCardnotDetectedSignal = pyqtSignal(np.ndarray,str,int)
    faceCardDetectedSignal = pyqtSignal(np.ndarray,str,int)
    def __init__(self,parent,source,MainWindow):
        super(FaceRecognizer, self).__init__()
        print('real thread init started')
        # self.faceDetector    = dlib.get_frontal_face_detector()
        # self.predictor       = dlib.shape_predictor('data/shape_predictor_68_face_landmarks.dat')
        # self.faceAligner     = FaceAligner(self.predictor, desiredFaceWidth=256)
        self.mainWindow=MainWindow
        self.parent=parent
        self.isRunning=True
        self.source = source
        self.numtries=0
        self.isReady=False
        self.tempimagedir="data/temp/"
        self.facecards=[]
        self.skip=0
        self.skipFrames=5
        self.modelpath="data/model/model.pkl"
        self.model=None
        self.datapath='data/person'
        self.isloading=False
        
        self.detectionSkip=3
        self.dskip=10 #just to be sure it runs first time
        self.encodings=[]
        self.labels=[]
        self.load()
        print('real thread init completed')
    def load(self):
        print('model loaded')
        self.isloading=True
        self.isReady=False
        self.encodings=[]
        self.labels=[]
        for feature in databasehandler.getAllFeature():
            user = str(databasehandler.getUserid(feature.user).username)
            self.labels.append(user)
            self.encodings.append(feature.features)
            self.isReady=True
        self.isloading=False
    # def load(self):
    #     print('model loaded')
    #     self.isloading=True
    #     self.encodings=[]
    #     self.labels=[]
    #     for mydir in os.listdir(self.datapath):
    #         temp=os.path.join(self.datapath, mydir)
    #         user=databasehandler.insertUser(mydir)
    #         if (os.path.isfile(temp)==False):
    #             count=0
    #             for sample in os.listdir(temp):
    #                 picturepath=os.path.join(temp,sample)
    #                 if(os.path.isfile(picturepath)==True):
    #                     img = cv2.imread(picturepath)
    #                     self.isReady=True
    #                     f=getFeatures(img)
    #                     # f=face_recognition.face_encodings(img)[0]
    #                     if type(f) is not type(None):
    #                         self.encodings.append(f)
    #                         self.labels.append(user.username)
    #                         count=count+1
    #     self.isloading=False
        # print(self.message)
    # def load(self):
    #     # print('model loaded')
    #     self.isloading=True
    #     if os.path.exists("data/model/model.pkl"):
    #         self.model   = joblib.load(self.modelpath)
    #         self.isReady = True
    #         self.message = "model Loaded Predictor"
    #     else:
    #         self.isReady = False
    #         self.message = "model not trained"
    #     self.isloading=False
    #     # print(self.message)
    def stop(self):
        self.isRunning=False
    def run(self):
        print('run intiated')
        try:
            cap = cv2.VideoCapture(self.source)
            print('device capture')
            self.numtries=0
            self.nr=[]
        except:
            self.isRunning=False
        while self.isRunning:
            # print('running')
            try:
                # print('going to get frame')
                ret, frame = cap.read()
                # print('got the frame')
            except:
                print("fail to get frame")
                ret = False
                self.isRunning=False
                self.parent.error('Fail to Get Camera')
            if ret:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if(self.dskip > self.detectionSkip):
                    
                    face_locations = face_recognition.face_locations(rgb_small_frame,number_of_times_to_upsample=2)
                    # face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                    face_names=[]#['unknown' for i in face_locations ]
                    for fe in range(0,len(face_locations)):
                        # See if the face is a match for the known face(s)
                        self.dskip = 0
                        (top, right, bottom, left)=face_locations[fe]
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4
                        # self.isloading=True
                        img =  frame[top:bottom,left:right,:].copy()
                        # faceAligned = self.faceAligner.align(frame, gray, rect)
                        # start_time = time.time()
                        # encodings = face_recognition.face_encodings(rgb_small_frame, [face_locations[fe]])
                        current_encodings = getFeatures(img)
                        # end_time = time.time()
                        # print("face detection time:", end_time - start_time,rgb_small_frame.shape)
                        # face=np.array(img)
                        name = "unknown"
                        if self.isReady and not self.isloading and type(current_encodings) is not type(None):
                            # print('conditions passed',len(self.encodings),len(self.labels))
                            matches = face_recognition.compare_faces(self.encodings, current_encodings)
                            face_distances = face_recognition.face_distance(self.encodings, current_encodings)
                            best_match_index = np.argmin(face_distances)
                            if matches[best_match_index]:
                                score=1-face_distances[best_match_index]
                                # print('score is ',score)
                                if(score > 0.60):
                                    name = self.labels[best_match_index]
                                    self.faceCardDetectedSignal.emit(img,name,score * 100)
                                else:
                                    self.faceCardnotDetectedSignal.emit(img,LANGUAGE.UNRECOGNIZED,0)
                            else:
                                self.faceCardnotDetectedSignal.emit(img,LANGUAGE.UNRECOGNIZED,0)
                        else:
                            # start_time = time.time()
                            self.faceCardnotDetectedSignal.emit(img,LANGUAGE.UNRECOGNIZED,0)
                            # end_time = time.time()
                            # print("face card unrecognized time:", end_time - start_time)
                        face_names.append(name)
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                self.dskip+=1
                self.drawImage(frame)
            else:
                cap.release()
                self.numtries+=1
                if(self.numtries>=4):
                    self.isRunning=False
                    self.parent.error('Camera Source Failed')

    def detectFace(self,frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.equalizeHist( gray, gray )
        rects = self.faceDetector(gray, 1)
        nr=[]
        for rect in rects:
            (x, y, w, h) = rect_to_bb(rect)
            nr.append((x,y,w,h))
            faceAligned = self.faceAligner.align(frame, gray, rect)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
            face=np.array(faceAligned[:,26:230,:])
            if self.skip >= self.skipFrames:
                print('predicting',self.skip)
                self.predict(face)
                self.skip =0
        self.skip+=1
        return frame,nr
    def drawFace(self,frame,rects):
        for rect in rects:
            (x, y, w, h) = rect
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        return frame
    def predict(self,img):
        if self.isReady and not self.isloading:
            print('loaded')
            feat=getFeatures(img)
            if (type(feat) == type(None)):
                return
            matches = face_recognition.compare_faces(self.encodings, feat)
            print('got features len',len(matches))
            name = "unknown"
            face_distances = face_recognition.face_distance(self.encodings, feat)
            best_match_index = np.argmin(face_distances)
            print('best match ')
            score=1-face_distances[best_match_index]
            print('score is ',score)
            if matches[best_match_index]:
                name = self.labels[best_match_index]
                self.faceCardDetectedSignal.emit(img,name,score * 100)
                print('matched')
            else:
                self.faceCardnotDetectedSignal.emit(img,LANGUAGE.UNRECOGNIZED,0)
                print('not matched')
        else:
            self.mainWindow.showMessage("No User is Registered")
            self.faceCardnotDetectedSignal.emit(img,LANGUAGE.UNRECOGNIZED,0)          
    # def predict(self,img):
    #     if self.isReady and not self.isloading:
    #         feat=getFeatures(img)
    #         if (type(feat) == type(None)):
    #             return
    #         label=self.model.predict_proba(feat.reshape(1,-1))
    #         label=label[0]
    #         names=os.listdir(self.datapath)
    #         ind = np.where(label == np.amax(label))[0]
    #         name = names[ind[0]]
    #         conf = label[ind[0]]
    #         if(name == 'unknown' or conf < 0.7):
    #             self.faceCardnotDetectedSignal.emit(img,"UnRecognized",0)
    #         else:
    #             self.faceCardDetectedSignal.emit(img,name,label[ind]*100)
    #     else:
    #         self.mainWindow.showMessage("No User is Registered")
    #         self.faceCardnotDetectedSignal.emit(img,"UnRecognized",0)        
    def drawImage(self,rgbImage):
        try:
            if(self.parent.isViewing):
                self.parent.draw(rgbImage)
        except:
            self.stop()
            print('fail drawing')
    # def drawFace(self,rgbImage):
    #     w = self.parent.faceview.width()
    #     h = self.parent.faceview.height()
    #     convertToQtFormat = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],QtGui.QImage.Format_RGB888)
    #     q = convertToQtFormat.scaled(w, h, Qt.KeepAspectRatio)
    #     self.parent.faceview.setPixmap(QtGui.QPixmap.fromImage(q))
class Camera(QWidget):
    def __init__(self,parent,name,source,camType="IP",camDirection="IN",UnRecognized=True):
        super(Camera, self).__init__()
        print('cam init')
        # self.setStyleSheet("border: 2px solid gray;")
        self.UnRecognized = UnRecognized
        self.camDirection=camDirection
        self.parent = parent
        self.source = source
        self.camType= camType
        self.layout = QGridLayout(self)
        # self.view   = QLabel()
        self.namestr= name 
        self.closeBtn  = QPushButton(LANGUAGE.CLOSE)
        self.view  = QPushButton(LANGUAGE.VIEW)
        self.name   = QLabel(self.namestr)
        self.name.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        # self.view.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.layout.addWidget(QWidget(),1,1,1,1)
        self.layout.addWidget(self.name,1,2,1,1)
        self.layout.addWidget(self.view,1,3,1,1)
        self.layout.addWidget(self.closeBtn,1,4,1,1)
        self.layout.addWidget(QWidget(),1,5,1,1)
        # self.layout.addWidget(self.closeBtn,3,11,1,1)
        self.closeBtn.clicked.connect(self.close)
        self.index=None
        self.isViewing = False
        self.iserror = False
        self.view.clicked.connect(self.viewme)
        self.notDetectedCards=queue.Queue(5)
        self.DetectedCards=queue.Queue(5)
        self.cameraThread=FaceRecognizer(self,self.source,self.parent)
        self.cameraThread.faceCardDetectedSignal.connect(self.createFaceCardDetected)
        self.cameraThread.faceCardnotDetectedSignal.connect(self.createFaceCardnotDetected)
        self.cameraThread.start()
        self.setMaximumWidth(int(self.parent.width()/5))
        # self.setMaximumHeight(int(self.parent.height()/5))
    def setUnRecognized(self,value):
        self.UnRecognized = value
    def clearDetected(self):
        while(not self.DetectedCards.empty()):
            temp=self.DetectedCards.get()
    def clearUnDetected(self):
        while(not self.notDetectedCards.empty()):
            temp=self.notDetectedCards.get()
    def viewme(self):
        self.isViewing = True
        self.parent.viewme(self)
    def draw(self,rgbImage):
        if(self.isViewing and not self.iserror):
            self.parent.draw(rgbImage)
    def mouseReleaseEvent(self,event):
        print('mouse clicked')
    def notDetectedVerfiy(self,img):

        # if 
        try:
        # if True:
            for f in list(self.notDetectedCards.queue):
                found = f.verify(img)
                if(found == True):
                    return found
        except:
            print('exception in notdetected verify')
        return False
    def DetectedVerfiy(self,img,name,match):
        try:
            for f in list(self.DetectedCards.queue):
                if(f.name == name):
                    f.match=match
                    # f.imagepath.append(img)
                    fmt = '%Y-%m-%d %H:%M:%S'
                    d1 = f.startTime

                    d2 = datetime.now()
                    daysDiff = (d2-d1) / timedelta(minutes=1)
                    # print('days difference',daysDiff)
                    if(daysDiff > 5):
                        user=databasehandler.getUser(name)
                        databasehandler.insertAttendance(user.id,name,self.namestr+' '+self.camType ,datetime.now(),self.camDirection)
                    f.update()
                    return True
        except:
            print('exception in detected verify')
        return False            
    def createFaceCardnotDetected(self,image,name,match):
        if self.UnRecognized:
            if(self.notDetectedCards.empty()):
                newFaceCard=FaceCard(self.parent,imagepath=image,name=name,match=match,status=self.camDirection,Detected=False,camName=self.namestr)
                self.parent.notDetected(newFaceCard)
                self.notDetectedCards.put(newFaceCard)
            else:
                # print('verifiying the data')
                if(self.notDetectedVerfiy(image) == False):
                    # print('verify fail')
                    newFaceCard=FaceCard(self.parent,imagepath=image,name=name,match=match,status=self.camDirection,Detected=False,camName=self.namestr)
                    self.parent.notDetected(newFaceCard)
                    if(self.notDetectedCards.full()):
                        self.notDetectedCards.get()
                        self.notDetectedCards.put(newFaceCard)
                    else:
                        self.notDetectedCards.put(newFaceCard)
    def createFaceCardDetected(self,image,name,match):
        if(self.DetectedCards.empty()):
            newFaceCard=FaceCard(self.parent,imagepath=image,name=name,match=match,status=self.camDirection,Detected=True,camName=self.namestr)
            self.parent.addDetected(newFaceCard)
            self.DetectedCards.put(newFaceCard)
            user=databasehandler.getUser(name)
            databasehandler.insertAttendance(user.id,name,self.namestr+' '+self.camType ,datetime.now(),self.camDirection)
        else:
            if(self.DetectedVerfiy(image,name,match) == False):
                newFaceCard=FaceCard(self.parent,imagepath=image,name=name,match=match,status=self.camDirection,Detected=True,camName=self.namestr)
                self.parent.addDetected(newFaceCard)
                user=databasehandler.getUser(name)
                databasehandler.insertAttendance(user.id,name,self.namestr+' '+self.camType,datetime.now(),self.camDirection)
                if(self.DetectedCards.full()):
                    self.DetectedCards.get()
                    self.DetectedCards.put(newFaceCard)
                else:
                    self.DetectedCards.put(newFaceCard)
    def showMessage(self,msg):
        self.parent.showMessage(msg)
    def setTabIndex(self,index):
        self.index=index
    def error(self,message):
        self.iserror = True  
        self.name.setStyleSheet("color:red;")
    def close(self):
        self.isViewing=False
        self.cameraThread.stop()
        if self.camType=="USB":
            if self.source in self.parent.camInUse:
                self.parent.camInUse.remove(self.source)
        self.parent.cameralist.remove(self)
        self.parent.cameraclosed()
        self.deleteLater()
    
        

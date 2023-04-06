
from PyQt5.QtWidgets import QWidget, QLabel, QDialog,QGridLayout,QComboBox,QLineEdit,QPushButton
from PyQt5.QtCore import Qt, QRect, QThread, pyqtSignal, pyqtSlot
import cv2

class AddUSBCamera(QDialog):
    addcam  = pyqtSignal(str,int,str)
    def __init__(self,parent,LANGUAGE):
        super(AddUSBCamera, self).__init__()
        self.LANGUAGE=LANGUAGE
        self.parent=parent
        self.check=False
        self.setMinimumHeight(100)
        self.setMinimumWidth(300)
        self.setWindowTitle(self.LANGUAGE.ADDUSBCAMERA)
        self.setWindowModality(Qt.ApplicationModal)
        self.layout=QGridLayout(self)
        self.layout.addWidget(QLabel(self.LANGUAGE.ADDUSBCAMERA),1,3,1,1)
        self.inputCamera = QComboBox()
        for i in self.getCams():
            self.inputCamera.addItem(str(i))
        self.layout.addWidget(QLabel('Select Camera'),2,1,1,2)
        self.layout.addWidget(self.inputCamera,2,3,1,2)
        self.inputName = QLineEdit()
        self.layout.addWidget(QLabel(self.LANGUAGE.NAME),3,1,1,2)
        self.layout.addWidget(self.inputName,3,3,1,2)

        self.camDirection = QComboBox()
        self.camDirection.addItem("IN")
        self.camDirection.addItem("OUT")
        self.layout.addWidget(QLabel('Label'),4,1,1,2)
        self.layout.addWidget(self.camDirection, 4,3,1,2)

        self.addCameraBtn=QPushButton(self.LANGUAGE.ADD)
        self.cancelBtn   =QPushButton(self.LANGUAGE.CANCEL)
        self.cancelBtn.clicked.connect(lambda: self.accept())
        self.addCameraBtn.clicked.connect(self.selectCam)
        self.layout.addWidget(self.addCameraBtn,5,1,1,2)
        self.layout.addWidget(self.cancelBtn   ,5,3,1,2)
        self.newCam=(self.check,"",0,"")
        self.exec_()
    def getCams(self):
        devices=[]
        i=0
        while(True):
            if i not in self.parent.camInUse:
                cap = cv2.VideoCapture(i)
                if not cap.read()[0]:
                    break
                else:
                    devices.append(i)
                    i+=1
                cap.release()
                cv2.destroyAllWindows()
            else:
                i+=1
        return devices
    def selectCam(self):
        name = self.inputName.text()
        cam=self.inputCamera.itemText(self.inputCamera.currentIndex())
        if(cam==""):
            self.parent.showMessage("No Camera")
            self.inputCamera.setStyleSheet("border:2px solid red;")
            return
        if(name == ""):
            name = "Cam"+cam
        camdir=self.camDirection.itemText(self.camDirection.currentIndex())
        self.newCam=(True,name,int(cam),camdir)
        self.accept()


class AddIPCamera(QDialog):
    def __init__(self,parent,LANGUAGE):
        super(AddIPCamera, self).__init__()
        self.LANGUAGE=LANGUAGE
        self.setMinimumHeight(100)
        self.setMinimumWidth(300)
        self.parent=parent
        self.check = False
        self.setWindowTitle(self.LANGUAGE.ADDIPCAMERA)
        self.setWindowModality(Qt.ApplicationModal)
        self.layout=QGridLayout(self)
        self.layout.addWidget(QLabel(self.LANGUAGE.ADDIPCAMERA),1,3,1,1)

        self.inputCamera = QLineEdit()
        self.layout.addWidget(QLabel(self.LANGUAGE.ENTERIPSOURCE),2,1,1,2)
        self.layout.addWidget(self.inputCamera,2,3,1,2)
        self.inputName = QLineEdit()
        self.layout.addWidget(QLabel(self.LANGUAGE.NAME),3,1,1,2)
        self.layout.addWidget(self.inputName,3,3,1,2)


        self.camDirection = QComboBox()
        self.camDirection.addItem("IN")
        self.camDirection.addItem("OUT")
        self.layout.addWidget(QLabel('Label'),4,1,1,2)
        self.layout.addWidget(self.camDirection, 4,3,1,2)

        self.addCameraBtn=QPushButton(self.LANGUAGE.ADD)
        self.cancelBtn   =QPushButton(self.LANGUAGE.CANCEL)
        self.cancelBtn.clicked.connect(lambda: self.accept())
        self.addCameraBtn.clicked.connect(self.selectCam)
        self.layout.addWidget(self.addCameraBtn,5,1,1,2)
        self.layout.addWidget(self.cancelBtn   ,5,3,1,2)
        self.newCam=(self.check,"",0,"")
        self.exec_()
    def selectCam(self):
        name = self.inputName.text()
        cam=self.inputCamera.text()
        if(cam==""):
            self.parent.showMessage("No Camera")
            self.inputCamera.setStyleSheet("border:2px solid red;")
            return
        if(name == ""):
            name = "Cam"+cam
        camdir=self.camDirection.itemText(self.camDirection.currentIndex())
        self.newCam=(True,name,cam,camdir)
        self.accept()
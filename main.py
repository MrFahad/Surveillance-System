from pony.orm import dbproviders
from pony.orm.dbproviders import sqlite
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QGridLayout,QDialog,QPushButton,QComboBox
from PyQt5 import QtGui
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal,Qt
from PyQt5.QtGui import QIcon, QPixmap,QFont,QPalette,QColor
from mainwindow import MainWindow
import face_recognition
import sklearn.utils._cython_blas
from skimage.feature import local_binary_pattern
import sys
import os
# import requests
import astor

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Face Recognition System")
        self.mainwindow = QWidget(self)
        self.setCentralWidget(self.mainwindow)
        self.mainLayout = QGridLayout(self.mainwindow)
        self.statusBar().showMessage('Loading')
        self.selectLanguage()
        self.setIcon()
        self.show()

    def setIcon(self):
        self.setWindowTitle('FR')
        self.setWindowIcon(QIcon('Icon.png'))

        self.show()        
        
    def close_application(self):
        self.statusBar().showMessage('Closing Application')
        sys.exit()
    def selectLanguage(self):
        self.languageselector = QWidget()
        self.languageselector_layout = QGridLayout(self.languageselector)
        self.start = QPushButton('start')
        self.close = QPushButton('close')
        self.inputLanguage = QComboBox()
        self.inputLanguage.addItem('English')
        self.inputLanguage.addItem('Arabic')
        self.languageselector_layout.addWidget(self.inputLanguage,1,1,1,2)
        self.languageselector_layout.addWidget(self.start,2,1,1,1)
        self.languageselector_layout.addWidget(self.close,2,2,1,1)
        self.start.clicked.connect(self.mainGui)
        self.close.clicked.connect(self.close_application)
        self.mainLayout.addWidget(self.languageselector,1,1,1,1)
        # self.languageselector.exec_()

    def mainGui(self):
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setMinimumSize(800,600)
        self.showMaximized()
        self.languageselector.deleteLater()
        
        self.language = self.inputLanguage.currentIndex()
        print('index is ',self.language)
        self.setWindowTitle("Face Recognition System")
        self.mainwindow = QWidget(self)
        self.setCentralWidget(self.mainwindow)
        self.mainLayout = QGridLayout(self.mainwindow)
        self.statusBar().showMessage('Loading')
        self.statusBar().showMessage('Loading Main Menu')
        self.maingui = MainWindow(self,self.language)
        self.mainLayout.addWidget(self.maingui, 1, 1)


def main(argv):
    app = QApplication(argv)
    print("Number of arguments: ", len(argv))
    GUI = Window()
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    sys.excepthook = except_hook
    try:
        sys.exit(app.exec_())
    except:
        print("exception")
if __name__ == "__main__":
    main(sys.argv)

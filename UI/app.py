import sys
import shutil

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QFileDialog, QLabel, QVBoxLayout
)

from PyQt5.QtCore import(
    QDir, pyqtSignal, pyqtSlot, Qt, QThread
)

from PyQt5.uic import loadUi
from PyQt5 import QtGui
from PyQt5.QtGui import *

from main_window_ui import Ui_MainWindow
from image_large_ui import Ui_Dialog

#from processData import *
from fileDialog import *

#for webcam detection
import cv2
import torch
import sys
import mmcv
import numpy as np 

import os
import sys

...

scriptpath = "C:\cust\Studium_local\Studienprojekt\Hand_Gesture_Recognizer"
sys.path.append(os.path.abspath(scriptpath))

from hand_gesture_detection import VideoDetThread

from processData import *
from ModelHandler import ModelHandler

class Window(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):

        self.imageDet = ImageDet()
        self.modelHandler = ModelHandler()

        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()
        self.loadImages()
        self.initModelOptions()

    def connectSignalsSlots(self):
        self.Btn_ImageDet_2.clicked.connect(self.openImageDetection)
        self.Btn_VideoDet_2.clicked.connect(self.openVideoDetection)
        self.Btn_VideoDet_2.clicked.connect(self.openWebcamDetection)
        self.list_filenames.itemDoubleClicked.connect(self.displayImageOrig)
        self.btn_process.clicked.connect(self.processImage)
        self.btn_openImageDialog.clicked.connect(self.openImageDialog)
        self.combo_model.currentIndexChanged.connect(self.modelchanged)
        self.combo_api.currentIndexChanged.connect(self.apichanged)
        self.btn_addImage.clicked.connect(self.addImage)
        self.btn_startWebcam.clicked.connect(self.startWebcam)
        self.btn_startWebcamDet.clicked.connect(self.startHandGestureRecog)
    
    #check which models exist in filepath and add those to dropdown 
    def initModelOptions(self): 
        self.combo_model.clear()
        for m in self.modelHandler.models: 
            self.combo_model.addItem(m.name)
        self.combo_model.setCurrentIndex(-1)
        self.combo_model.setCurrentText("Choose a model")
        self.combo_api.setCurrentIndex(-1)
        self.combo_api.setCurrentText("Choose an API")

    def openImageDetection(self):
        self.tabWidget.setCurrentIndex(1)
        self.loadImages()

    def openVideoDetection(self):
        self.tabWidget.setCurrentIndex(2)
    
    def openWebcamDetection(self):
        self.tabWidget.setCurrentIndex(3)
    
    def loadImages(self):
        #clear list: 
        self.list_filenames.clear()
        #assume the directory exists and contains some files and you want all jpg and JPG files
        dir = QDir("./../images")
        filters = ["*.jpg", "*.JPG"]
        dir.setNameFilters(filters)
        for filename in dir.entryList(): 
            self.list_filenames.addItem(filename)
        

    def displayImageOrig(self): 
        path = "./../images/" + self.list_filenames.currentItem().text()

        im_cv = cv2.imread(path, cv2.IMREAD_ANYCOLOR)
        self.lb_image_orig.setPixmap(self.convert_cv_qt(im_cv))

    def processImage(self): 
        #Bild in Funktion reinwerfen
        path = "./../images/" + self.list_filenames.currentItem().text()
        self.list_status.addItem("processing Image...")
        ret = self.imageDet.processImage(path)
        if(ret>=0): 
            self.displayImageRes()
            self.ln_ObjectCount.setText("Objects detected: " + str(ret))
        else: self.list_status.addItem("processing Image didnt work")
        

    def displayImageRes(self): 
        path = "./../images/results/vis/" + self.list_filenames.currentItem().text()
        im_cv = cv2.imread(path, cv2.IMREAD_ANYCOLOR)
        self.lb_image_res.setPixmap(self.convert_cv_qt(im_cv))
        self.list_status.addItem("trying to display Result image")

    def openImageDialog(self): 
        Imagedialog = ImageLarge(self)
        #image = self.lb_image_res.pixmap()
        Imagedialog.setImage(self)
        Imagedialog.exec()
        
    def modelchanged(self): 
        self.imageDet.changemodelconfig(self.modelHandler.models[self.combo_model.currentIndex()])
        self.list_status.addItem("-model changed to " + self.combo_model.currentText())
    
    def apichanged(self): 
        self.imageDet.api = self.combo_api.currentText()
        self.list_status.addItem("-API changed to " + self.combo_api.currentText())

    def addImage(self): 
        app = fileDialog(self)
        #app.openFileNamesDialog()
        app.exec()
        #sys.exit(app.exec_())

#Webcam Detection
    def startWebcam(self): 
        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

    def startHandGestureRecog(self): 
        #execute TechVidvan-hand_gesture_detection.py
        return 0    

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.lb_webcam.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(600, 400, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def startHandGestureRecog(self): 
        # create the video capture thread
        self.thread = VideoDetThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_imageDet)
        # start the thread
        self.thread.start()

    @pyqtSlot(np.ndarray)
    def update_imageDet(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.lb_webcamDet.setPixmap(qt_img)
    


class ImageLarge(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("./imageLarge.ui", self)

    def setImage(self, parent): 
        path = "./../images/result.jpg"
        image= QPixmap(path)
        if(not image.isNull()): 
            image = image.scaledToWidth(1000)
            self.lb_ImageLarge.setPixmap(image)
        else: 
            self.list_status.addItem("Picture cannot be displayed")

        #Model sollte anders übergeben werden, Combo-Box könnte ja schon geändert sein 
        self.ln_heading.setText("Processed Picture with " + parent.combo_model.currentText())
        print("Set Image \n")


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0)
        while True:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)



if __name__ == "__main__":

    #QApplication.addLibraryPath(".")
    app = QApplication(sys.argv)


    win = Window()
    win.resize(1800, 1000)
    win.show()



    sys.exit(app.exec())
#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: F:\code\easyofd\gui
#CREATE_TIME: 2023-11-18 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#note:  

import sys,os,base64

lib_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0,lib_path)
from PIL import Image
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QDialog,QMessageBox
from PyQt6 import QtCore, QtGui, QtWidgets
from easyofd import OFD

class Ui_MainWindow(object):
    def __init__(self):
        self.ofd = OFD()
        
    def read_ofd(self,path):
        with open(path,"rb") as f:
            ofdb64 = str(base64.b64encode(f.read()),"utf-8")
        return ofdb64
    
    def read_pfd(self,path):
        pfd_byte =None
        with open(path,"rb") as f:
           pfd_byte = f.read()
        return pfd_byte
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        icon = QtGui.QIcon(r'gui\ico\reno.ico')
        MainWindow.setWindowIcon(icon)
        MainWindow.resize(744, 463)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 2, 2))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(20, 320, 161, 41))
        self.pushButton.setObjectName("pushButton")
        self.textEdit = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(120, 180, 461, 51))
        self.textEdit.setObjectName("textEdit")
        self.textEdit_2 = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.textEdit_2.setGeometry(QtCore.QRect(120, 250, 461, 51))
        self.textEdit_2.setObjectName("textEdit_2")
        # 单选框
        self.radioButton = QtWidgets.QRadioButton(parent=self.centralwidget)
        self.radioButton.setGeometry(QtCore.QRect(40, 50, 95, 20))
        self.radioButton.setObjectName("radioButton")
        self.radioButton_2 = QtWidgets.QRadioButton(parent=self.centralwidget)
        self.radioButton_2.setGeometry(QtCore.QRect(170, 50, 95, 20))
        self.radioButton_2.setObjectName("radioButton_2")
        self.radioButton_3 = QtWidgets.QRadioButton(parent=self.centralwidget)
        self.radioButton_3.setGeometry(QtCore.QRect(40, 90, 95, 20))
        self.radioButton_3.setObjectName("radioButton_3")
        self.radioButton_4 = QtWidgets.QRadioButton(parent=self.centralwidget)
        self.radioButton_4.setGeometry(QtCore.QRect(170, 90, 95, 20))
        self.radioButton_4.setObjectName("radioButton_4")
        self.radioButton_5 = QtWidgets.QRadioButton(parent=self.centralwidget)
        self.radioButton_5.setGeometry(QtCore.QRect(300, 50, 95, 20))
        self.radioButton_5.setObjectName("radioButton_5")
        self.radioButton_6 = QtWidgets.QRadioButton(parent=self.centralwidget)
        self.radioButton_6.setGeometry(QtCore.QRect(300, 90, 95, 20))
        self.radioButton_6.setObjectName("radioButton_6")
        
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 20, 54, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 140, 54, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(40, 200, 54, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(40, 270, 54, 16))
        self.label_4.setObjectName("label_4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 744, 22))
        self.menubar.setObjectName("menubar")
        self.mebnu_2 = QtWidgets.QMenu(parent=self.menubar)
        self.mebnu_2.setObjectName("mebnu_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        # 单选框
        self.actionpdf2ofd = QtGui.QAction(parent=MainWindow)
        self.actionpdf2ofd.setObjectName("actionpdf2ofd")
        self.actionpdf2ofd.setCheckable(True)
        self.actionpdf2ofd.triggered.connect(self.action_triggered)
        
        self.actionpfd2img = QtGui.QAction(parent=MainWindow)
        self.actionpfd2img.setObjectName("actionpfd2img")
        self.actionpfd2img.setCheckable(True)
        
        self.actionofd2pfd = QtGui.QAction(parent=MainWindow)
        self.actionofd2pfd.setObjectName("actionofd2pfd")
        self.actionofd2pfd.setCheckable(True)
        
        self.actionofd2img = QtGui.QAction(parent=MainWindow)
        self.actionofd2img.setObjectName("actionofd2img")
        self.actionofd2img.setCheckable(True)
        
        self.menubar.addAction(self.mebnu_2.menuAction())
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    
    def action_triggered(self,actionpdf2ofd):
        if self.actionpdf2ofd.isChecked():
            print("Action is checked!")
        else:
            print("Action is unchecked!")
            
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "开始"))
        
        self.radioButton.setText(_translate("MainWindow", "ofd2pdf"))
        self.radioButton_2.setText(_translate("MainWindow", "ofd2img"))
        self.radioButton_3.setText(_translate("MainWindow", "pdf2ofd"))
        self.radioButton_4.setText(_translate("MainWindow", "pdf2img"))
        self.radioButton_5.setText(_translate("MainWindow", "img2ofd"))
        self.radioButton_6.setText(_translate("MainWindow", "img2pdf"))
        
        self.label.setText(_translate("MainWindow", "选择模式"))
        self.label_2.setText(_translate("MainWindow", "文件路径"))
        self.label_3.setText(_translate("MainWindow", "输入路径"))
        self.textEdit.setText(_translate("MainWindow", ""))
        self.label_4.setText(_translate("MainWindow", "输出路径"))
        self.textEdit_2.setText(_translate("MainWindow", ""))
        self.mebnu_2.setTitle(_translate("MainWindow", "说明"))
        self.actionpdf2ofd.setText(_translate("MainWindow", "pdf2ofd"))
        self.actionpfd2img.setText(_translate("MainWindow", "pfd2img"))
        self.actionofd2pfd.setText(_translate("MainWindow", "ofd2pfd"))
        self.actionofd2img.setText(_translate("MainWindow", "ofd2img"))

        # 点击事件
        self.pushButton.clicked.connect(self.buttonClicked)
        text = f"作者:{' '*5}renoyuan\r\n版本:{' '*5}1.0.0\n"

        
        # self.mebnu_2.triggered.connect(lambda: self.showDialog(text))
        self.mebnu_2.aboutToShow.connect(lambda:self.showDialog(text))
        exit_action = QtGui.QAction(self.mebnu_2)
        exit_action.triggered.connect( self.showDialog)
        
    def showDialog(self,msg:str):  
        # QMessageBox.warning(self, 'Alert', msg, QMessageBox.Ok())  
        msgBox = QMessageBox()  
        msgBox.setText(msg)  
        msgBox.exec()
    
    def check_file(self,name,endswith:str):
        if name.lower().endswith(endswith):
            return True
    
    def save_file(self,name,_bytes):
        
        with open(name,"wb") as f:
            if isinstance(_bytes,list):
                _bytes = _bytes[0]
            f.write(_bytes)
            
    def save_img(self, name, img_np):
        for inx,img in enumerate(img_np):
            # im = Image.fromarray(img)
            img.save(name.format(inx))
            
    def run_convert(self,mode,input,output):
        inputs= os.listdir(input)

        for file in inputs:
            if mode == "ofd2pdf":
                if self.check_file(file,"ofd"):
                    
                    ofdb64 = self.read_ofd(os.path.join(input,file))
                    self.ofd.read(ofdb64)
                    pdf_bytes = self.ofd.to_pdf()
                    self.save_file(os.path.join(output,os.path.splitext(file)[0]+".pdf"), pdf_bytes)
            elif mode == "ofd2img":  
                if self.check_file(file,"ofd"):
                    ofdb64 = self.read_ofd(os.path.join(input,file))
                    self.ofd.read(ofdb64)
                    img_np = self.ofd.to_jpg()
                    self.save_img(os.path.join(output,os.path.splitext(file)[0]+"_{}"+".jpg"), img_np)
            elif mode == "pdf2ofd":
                if self.check_file(file,"pdf"):
                    pfdbyte = self.read_pfd(os.path.join(input,file))
                    ofd_byte = self.ofd.pdf2ofd(pfdbyte)
                    self.save_file(os.path.join(output,os.path.splitext(file)[0]+".ofd"), ofd_byte)
            elif mode == "pdf2img":
                if self.check_file(file, "pdf"):
                    print(os.path.join(input, file))
                    pfdbyte = self.read_pfd(os.path.join(input,file))
                    img_nps = self.ofd.pdf2img(pfdbyte)
                    print(type(img_nps))
                    if img_nps:
                        for idx, img in enumerate(img_nps):
                            img.save(os.path.join(output, os.path.splitext(file)[0]+f"_{idx}"+".jpg"))
                           
            elif mode == "img2ofd":
               pass
            elif mode == "img2pdf":
                pass
            self.ofd.del_data()
                
        self.showDialog("执行完毕")
            
                
        
                   
    def buttonClicked(self):
        """
        执行事件
        """
        # sender = self.sender()
        input_path = self.textEdit.toPlainText()
        output_path = self.textEdit_2.toPlainText()
        self.actionpdf2ofd 
        print("Input path: " + input_path)
        print("onput path: " + output_path)
        
        if not os.path.exists(input_path) or not os.path.exists(output_path):
            self.showDialog(f"输入路径{input_path} \n或 输出路径{output_path}\n 不存在，请检查。 ")
            return
            
      
        # ofd2pdf ofd2img pdf2ofd pdf2img
        mode = [self.radioButton.isChecked(),self.radioButton_2.isChecked(),self.radioButton_3.isChecked(),self.radioButton_4.isChecked(),self.radioButton_5.isChecked()]
        print(mode)
        if mode[0]:

            print("ofd2pdf")
            self.run_convert("ofd2pdf",input_path,output_path)
        elif mode[1]:
            print("ofd2img")
            self.run_convert("ofd2img",input_path,output_path)
        elif mode[2]:
            print("pdf2ofd")
            self.run_convert("pdf2ofd",input_path,output_path)
        elif mode[3]:
            print("pdf2img")
            self.run_convert("pdf2img",input_path,output_path)
        elif mode[4]:
            print("img2ofd")
            self.run_convert("img2ofd",input_path,output_path)
        elif mode[5]:
            print("img2pdf")
            self.run_convert("img2pdf",input_path,output_path)
        # msg = f'{sender.text()} was pressed'
        # self.statusBar().showMessage(msg)
        

if __name__ == "__main__":
    
    # 一、应用程序对象，只能有一个
    # 1、该类管理GUI应用程序控制流和主要设置，专门用于QWidget所需的一些功能
    # 2、不使用命令行或提示符程序（cmd），则为空列表 []
    # 3、如果使用命令行或提示符程序(cmd)，则为sys.argv

    app = QApplication(sys.argv)
    
    # 二、从窗口类型中可以创建三种窗口对象
    # 1、QWidget
    # 2、QMainWindow
    # 3、QDialog
    window = QMainWindow()
    # 三、QWidget显示窗口
    ui_ =Ui_MainWindow()
    ui_.setupUi(window)
 
    window.show()
    
    # 四、执行程序
    sys.exit(app.exec())
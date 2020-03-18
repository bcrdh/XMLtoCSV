# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xmltocsv.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!
import glob
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from logic import convert_to_csv, get_mods_files


def get_version():
    return '0.1.0'


def show_msg(msg, msg_type):
    msg_box = QMessageBox()
    msg_box.setIcon(msg_type)
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec()


class Ui_MainWindow(object):
    # Big UI stuff, ignore and scroll to bottom
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(460, 632)
        MainWindow.setMinimumSize(QtCore.QSize(460, 632))
        MainWindow.setMaximumSize(QtCore.QSize(460, 632))
        font = QtGui.QFont()
        font.setFamily("Microsoft JhengHei UI")
        MainWindow.setFont(font)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("background-color: rgb(239, 239, 239);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.lblName = QtWidgets.QLabel(self.centralwidget)
        self.lblName.setGeometry(QtCore.QRect(170, 60, 271, 51))
        self.lblName.setStyleSheet("font: 11pt \"Gadugi\";")
        self.lblName.setScaledContents(False)
        self.lblName.setObjectName("lblName")
        self.fileListWidget = QtWidgets.QListWidget(self.centralwidget)
        self.fileListWidget.setGeometry(QtCore.QRect(10, 290, 441, 231))
        self.fileListWidget.setStyleSheet("background-color: rgb(239, 239, 239);\n"
                                          "font: 11pt \"Gadugi\";\n"
                                          "color: rgb(0, 125, 92);")
        self.fileListWidget.setObjectName("fileListWidget")
        self.txtInputPath = QtWidgets.QTextEdit(self.centralwidget)
        self.txtInputPath.setGeometry(QtCore.QRect(10, 170, 351, 31))
        self.txtInputPath.setStyleSheet("background-color: rgb(239, 239, 239);\n"
                                        "font: 11pt \"Gadugi\";\n"
                                        "color: rgb(0, 125, 92);")
        self.txtInputPath.setReadOnly(True)
        self.txtInputPath.setObjectName("txtInputPath")
        self.btnBrowseInput = QtWidgets.QPushButton(self.centralwidget)
        self.btnBrowseInput.setGeometry(QtCore.QRect(370, 170, 81, 31))
        self.btnBrowseInput.clicked.connect(self.btn_input_folder_select)
        self.btnBrowseInput.setStyleSheet("background-color: rgb(0, 170, 127);\n"
                                          "color: rgb(255, 255, 255);\n"
                                          "border-radius: 5px;\n"
                                          "font: 11pt \"Gadugi\";")
        self.btnBrowseInput.setObjectName("btnBrowseInput")
        self.btnStart = QtWidgets.QPushButton(self.centralwidget)
        self.btnStart.setGeometry(QtCore.QRect(10, 530, 441, 41))
        self.btnStart.clicked.connect(self.btn_start)
        self.btnStart.setStyleSheet("background-color: rgb(0, 170, 127);\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "border-radius: 5px;\n"
                                    "font: 11pt \"Gadugi\";")
        self.btnStart.setObjectName("btnStart")
        self.btnBrowseOutput = QtWidgets.QPushButton(self.centralwidget)
        self.btnBrowseOutput.setGeometry(QtCore.QRect(370, 210, 81, 31))
        self.btnBrowseOutput.clicked.connect(self.btn_output_folder_select)
        self.btnBrowseOutput.setStyleSheet("background-color: rgb(0, 170, 127);\n"
                                           "color: rgb(255, 255, 255);\n"
                                           "border-radius: 5px;\n"
                                           "font: 11pt \"Gadugi\";")
        self.btnBrowseOutput.setObjectName("btnBrowseOutput")
        self.txtOutputPath = QtWidgets.QTextEdit(self.centralwidget)
        self.txtOutputPath.setGeometry(QtCore.QRect(10, 210, 351, 31))
        self.txtOutputPath.setStyleSheet("background-color: rgb(239, 239, 239);\n"
                                         "font: 11pt \"Gadugi\";\n"
                                         "color: rgb(0, 125, 92);")
        self.txtOutputPath.setReadOnly(True)
        self.txtOutputPath.setObjectName("txtOutputPath")
        self.txtOutputFile = QtWidgets.QTextEdit(self.centralwidget)
        self.txtOutputFile.setGeometry(QtCore.QRect(10, 250, 351, 31))
        self.txtOutputFile.setStyleSheet("background-color: rgb(239, 239, 239);\n"
                                         "font: 11pt \"Gadugi\";\n"
                                         "color: rgb(0, 125, 92);")
        self.txtOutputFile.setReadOnly(False)
        self.txtOutputFile.setObjectName("txtOutputFile")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 0, 151, 151))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("BCRDH_logo.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 460, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Arca - XMLtoCSV 0.1.0"))
        self.lblName.setText(_translate("MainWindow",
                                        "<html><head/><body><p><span style=\" font-size:20pt; color:#00aa7f;\">Arca</span><span style=\" font-size:20pt; color:#00aa7f;\"> - XMLtoCSV</span><span style=\" font-size:20pt; color:#00aa7f; vertical-align:super;\">V0.1.0</span></p></body></html>"))
        self.txtInputPath.setPlaceholderText(_translate("MainWindow", "Select an input folder..."))
        self.btnBrowseInput.setText(_translate("MainWindow", "Browse..."))
        self.btnStart.setText(_translate("MainWindow", "Convert"))
        self.btnBrowseOutput.setText(_translate("MainWindow", "Browse..."))
        self.txtOutputPath.setPlaceholderText(_translate("MainWindow", "Select an output folder..."))
        self.txtOutputFile.setPlaceholderText(_translate("MainWindow", "Enter the output file name..."))

    # Stop big UI stuff
    def select_folder(self):
        """
        Opens a file dialog and asks the user to select a folder.
        :return: the string path to the folder selected by the user
        """
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.DirectoryOnly)
        if dlg.exec():
            [result] = dlg.selectedFiles()
            return result
        else:
            return None

    def btn_input_folder_select(self):
        """
        Executed when the Browse button for input folder is clicked.
        Opens a file dialog and updates the text edit element to the selected path
        :return: None
        """
        # Select folder
        selected_folder = self.select_folder()
        if selected_folder is not None:
            # Update input path text edit / field
            self.txtInputPath.setText(selected_folder)
            # Update output file name
            output_file = selected_folder.replace("\\", os.sep).replace("/", os.sep)
            output_file = output_file.split(os.sep)[-1]
            self.txtOutputFile.setText(output_file + ".csv")
            # Clear list widget
            self.fileListWidget.clear()
            # Fill list widget
            self.fileListWidget.addItems(
                [filename.replace('/', os.sep).replace('\\', os.sep) for filename in
                 get_mods_files(selected_folder)]
            )

    def btn_output_folder_select(self):
        """
        Executed when the Browse button for output folder is clicked.
        Opens a file dialog and updates the text edit element to the selected path
        :return: None
        """
        self.txtOutputPath.setText(self.select_folder())

    def btn_start(self):
        """
        Executed when the Convert button is clicked.
        Will perform checks and then call logic (convert_to_csv function) from logic.py
        :return:
        """
        if len(self.txtInputPath.toPlainText()) == 0:
            show_msg('Select an input folder first.', QMessageBox.Critical)
        elif len(self.txtOutputPath.toPlainText()) == 0:
            show_msg('Select an output folder first.', QMessageBox.Critical)
        elif len(self.txtOutputFile.toPlainText()) == 0:
            show_msg('Enter an output file first.', QMessageBox.Critical)
        else:
            output_file = self.txtOutputFile.toPlainText()
            if not output_file.endswith('.csv'):
                output_file = output_file + '.csv'
            convert_to_csv(
                self.txtInputPath.toPlainText(),
                self.txtOutputPath.toPlainText(),
                output_file
            )
            show_msg(
                'Converted files and placed in ' + self.txtOutputPath.toPlainText() +
                "/" + self.txtOutputFile.toPlainText(),
                QMessageBox.Information
            )


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

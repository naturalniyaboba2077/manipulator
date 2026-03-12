from PyQt5.QtCore import QTimer

import ui
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QMainWindow

class Log():
    def __init__(self):
        self.logs = []
        self.errors = []


    def add_logs(self, logs):
        self.logs.append(logs)


    def add_errors(self, errors):
        self.errors.append(errors)
        self.logs.append(errors)

    def get_logs(self):
        logss = ""
        for i in self.logs:
            logss+= i
            logss+= "\n"
        return logss

    def get_errors(self):
        errorss = ""
        for i in self.errors:
            errorss+= i
            errorss+= "\n"
        return errorss

class Ui_Main(QMainWindow, ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.turnon = False
        self.pause_mot = True
        self.color = 0
        self.motors = [0, 0, 0, 0, 0, 0]
        self.setupUi(self)
        self.pushButton_10.clicked.connect(self.button_click)
        self.comboBox.currentTextChanged.connect(self.change_cords)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updates)
        self.timer.start(50)
        self.horizontalSlider.valueChanged.connect(self.mot1)
        self.horizontalSlider_2.valueChanged.connect(self.mot2)
        self.horizontalSlider_3.valueChanged.connect(self.mot3)
        self.horizontalSlider_4.valueChanged.connect(self.mot4)
        self.horizontalSlider_5.valueChanged.connect(self.mot5)
        self.horizontalSlider_6.valueChanged.connect(self.mot6)
        self.pushButton.clicked.connect(self.pause)

    def button_click(self):
        self.turnon=not self.turnon
        if self.turnon:
            self.pushButton_10.setText("Стоп")
            self.color=1
        else:
            self.pushButton_10.setText("Старт")
            self.color=0

    def pause(self):
        self.pause_mot = not self.pause_mot
        if self.pause_mot:
            self.pushButton.setText("пауза")
            self.color=2
        else:
            self.pushButton.setText("возобновить")
            self.color=3

    def change_cords (self, s):
        if s == "по градусам":
            self.label.setText("J1")
            self.label_2.setText("J2")
            self.label_3.setText("J3")
            self.label_4.setText("J4")
            self.label_5.setText("J5")
            self.label_6.setText("J6")
        elif s == "по координатам":
            self.label.setText("X")
            self.label_2.setText("Y")
            self.label_3.setText("Z")
            self.label_4.setText("Rx")
            self.label_5.setText("Ry")
            self.label_6.setText("Rz")



    def updates(self):
        if self.color == 0:
            self.label_8.setStyleSheet("background-color : white;")
            self.label_9.setStyleSheet("background-color : white;")
            self.label_10.setStyleSheet("background-color : white;")
            self.label_11.setStyleSheet("background-color : white;")
        elif self.color == 1:
            self.label_8.setStyleSheet("background-color : blue;")
            self.label_9.setStyleSheet("background-color : white;")
            self.label_10.setStyleSheet("background-color : white;")
            self.label_11.setStyleSheet("background-color : white;")
        elif self.color == 2:
            self.label_8.setStyleSheet("background-color : white;")
            self.label_9.setStyleSheet("background-color : green;")
            self.label_10.setStyleSheet("background-color : white;")
            self.label_11.setStyleSheet("background-color : white;")
        elif self.color == 3:
            self.label_8.setStyleSheet("background-color : white;")
            self.label_9.setStyleSheet("background-color : white;")
            self.label_10.setStyleSheet("background-color : yellow;")
            self.label_11.setStyleSheet("background-color : white;")
        elif self.color == 4:
            self.label_8.setStyleSheet("background-color : white;")
            self.label_9.setStyleSheet("background-color : white;")
            self.label_10.setStyleSheet("background-color : white;")
            self.label_11.setStyleSheet("background-color : red;")

        for i in range(6):
            self.tableWidget.setItem(i, 3, QTableWidgetItem(str(self.motors[i])))

    def mot1(self, p):
        self.motors[0]=p
    def mot2(self, p):
        self.motors[1]=p
    def mot3(self, p):
        self.motors[2]=p
    def mot4(self, p):
        self.motors[3]=p
    def mot5(self, p):
        self.motors[4]=p
    def mot6(self, p):
        self.motors[5]=p



app = QApplication([])

window = Ui_Main()
window.show()

app.exec()
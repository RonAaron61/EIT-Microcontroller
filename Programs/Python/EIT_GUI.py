"""https://github.com/RonAaron61/EIT-Microcontroller/"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import serial
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
from pyqtgraph.console import ConsoleWidget
from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.dockarea.DockArea import DockArea

import re
import EIT_Reconstruct as MyEIT #Place the Program on same directory/folder


"""Microcontroller - Change the COM address to your own"""
try:
    ser = serial.Serial('COM13', 115200)
    ser.close()
    ser.open()
except:
    print("Please check the com")

app = pg.mkQApp("EIT")

pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'w')

win = QtWidgets.QMainWindow()
area = DockArea()
win.setCentralWidget(area)
win.resize(500,500)
win.setWindowTitle('EIT Microcontroller')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

#Initializing dock
d1 = Dock("Main", size=(500, 270), closable=False)
d2 = Dock("Anomaly Graph", size=(500,300), closable=False)
d3 = Dock("Homogen Graph", size=(500,300), closable=False)
d4 = Dock("Status", size=(500, 100),closable=False)


area.addDock(d1)
area.addDock(d2, 'bottom', d1)
area.addDock(d3, 'bottom', d2)
area.addDock(d4, 'bottom', d3)

#Plot result
plotGraph_H = pg.GraphicsLayoutWidget(show=True, title="Graph")
plotH = plotGraph_H.addPlot(row=1, col=1, colspan=1,title="Homogen Data")
curve_H = plotH.plot(pen=pg.mkPen('r', width=2))
plotGraph_A = pg.GraphicsLayoutWidget(show=True, title="Graph")
plotA = plotGraph_A.addPlot(row=1, col=1, colspan=1,title="Anomaly Data")
curve_A = plotA.plot(pen=pg.mkPen('r', width=2))

Main_Info = pg.GraphicsLayoutWidget(show=True, title="Testing")
table = pg.TableWidget()


d1.addWidget(Main_Info)
d2.addWidget(plotGraph_A)
d3.addWidget(plotGraph_H)
d4.addWidget(table)


#Button
btn1 = QtWidgets.QPushButton("Get Homogen Data")
proxy1 = QtWidgets.QGraphicsProxyWidget()
proxy1.setWidget(btn1)
Main_Info.addItem(proxy1, row=2, col=0, colspan=2, rowspan=2)

btn2 = QtWidgets.QPushButton("Get Anomaly Data")
proxy2 = QtWidgets.QGraphicsProxyWidget()
proxy2.setWidget(btn2)
Main_Info.addItem(proxy2, row=4, col=0, colspan=2, rowspan=2)

rec_Hgn_btn = QtWidgets.QPushButton("Reconstruct With Homogen Data")
rec_proxy1 = QtWidgets.QGraphicsProxyWidget()
rec_proxy1.setWidget(rec_Hgn_btn)
Main_Info.addItem(rec_proxy1, row=6, col=0, colspan=1, rowspan=2)

rec_Ave_btn = QtWidgets.QPushButton("Reconstruct With Average Data")
rec_proxy2 = QtWidgets.QGraphicsProxyWidget()
rec_proxy2.setWidget(rec_Ave_btn)
Main_Info.addItem(rec_proxy2, row=6, col=1, colspan=1, rowspan=2)

btn3 = QtWidgets.QPushButton("Calibrate")
proxy3 = QtWidgets.QGraphicsProxyWidget()
proxy3.setWidget(btn3)
Main_Info.addItem(proxy3, row=8, col=0, colspan=2, rowspan=2)


"""Getting the Data"""
def Get_homogen(btn1):
    global reference
    string = "D"
    ser.write(string.encode('utf-8')) 
    reference = []
    while True:
        ser_data = ser.readline()
        ser_data = ser_data.decode().rstrip()
        if ser_data == "Done":
            break
        else:
            reference.append(float(ser_data))

    curve_H.setData(reference)
    print(reference)
    print(f"Data Length: {len(reference)}")


def Get_data(btn2):
    global data
    string = "D"
    ser.write(string.encode('utf-8')) 
    data = []

    while True:
        ser_data = ser.readline()
        ser_data = ser_data.decode().rstrip()
        if ser_data == "Done":
            break
        else:
            data.append(float(ser_data))

    curve_A.setData(data)
    print(data)
    print(f"Data Length: {len(data)}")

def Calibrate(btn3):
    string = "C"
    ser.write(string.encode('utf-8'))
    print("Electrode inject on 1-2 and read at 3-4")

def EIT_Reconstruct_noR(rec_Ave_btn):    
    print("Reconstruct with no homogen data (Average)")
    reconstruct = MyEIT.EIT_reconstruct(data=data, reference=[], use_ref=0, n_el=16)
    yoo = reconstruct.Reconstruct()

def EIT_Reconstruct_R(rec_Hgn_btn):  
    print("Reconstruct with homogen data")
    reconstruct = MyEIT.EIT_reconstruct(data=data, reference=reference, use_ref=1, n_el=16)
    yoo = reconstruct.Reconstruct() 

rec_Ave_btn.clicked.connect(EIT_Reconstruct_noR)
rec_Hgn_btn.clicked.connect(EIT_Reconstruct_R)
btn1.clicked.connect(Get_homogen)
btn2.clicked.connect(Get_data)
btn3.clicked.connect(Calibrate)


win.show()

if __name__ == '__main__':
    pg.exec()
import pyqtgraph as pg
from utils import valid_address, valid_path
from datetime import datetime
from PySide6.QtWidgets import (QMainWindow, QPushButton, QHBoxLayout,
                               QVBoxLayout, QWidget, QLabel, QComboBox,
                               QSlider, QGroupBox, QFormLayout, QCheckBox,
                               QFileDialog, QProgressBar, QGridLayout)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QIcon, QLinearGradient, QBrush, QGradient
from sensor import SensorScanner, SensorClient
from logger import Logger

class ViewSignals(QObject):
    """Cannot be defined on View directly since Signal needs to be defined on
    object that inherits from QObject"""
    annotation = Signal(tuple)
    start_recording = Signal(str)

class View(QMainWindow):
    def __init__(self, model): 
        super().__init__()
            
        self.setGeometry(300, 300, 750, 450)
        self.setWindowTitle('Connect the HR-ECG Sensor')

        self.model = model
        self.signals = ViewSignals()

        self.scanner = SensorScanner()
        self.scanner.sensor_update.connect(self.model.set_sensors)
        self.scanner.status_update.connect(self.show_status)

        self.sensor = SensorClient()
        self.sensor.ibi_update.connect(self.model.set_ibis_buffer)
        self.sensor.status_update.connect(self.show_status)


        self.scan_button = QPushButton("Scan")  ##scan button
        self.scan_button.clicked.connect(self.scanner.scan)

        self.address_menu = QComboBox() ##drop down box

        self.connect_button = QPushButton("Connect")    ##connect button    
        self.connect_button.clicked.connect(self.connect_sensor)

        self.disconnect_button = QPushButton("Disconnect")  ##disconnect button
        self.disconnect_button.clicked.connect(self.disconnect_sensor)

        self.model.addresses_update.connect(self.list_addresses)

        self.statusbar = self.statusBar()

        layout = QVBoxLayout()
        layout.addWidget(self.scan_button)
        layout.addWidget(self.address_menu)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.disconnect_button)

        widget = QWidget()
        widget.setLayout(layout)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)


    def connect_sensor(self):
        if not self.address_menu.currentText():
            return
        address = self.address_menu.currentText().split(",")[1].strip()    # discard device name
        if not valid_address(address):
            print(f"Invalid sensor address: {address}.")
            return
        sensor = [s for s in self.model.sensors if s.address().toString() == address]
        self.sensor.connect_client(*sensor)

    def disconnect_sensor(self):
        self.sensor.disconnect_client()

    def list_addresses(self, addresses):
        self.address_menu.clear()
        self.address_menu.addItems(addresses[1])

    def show_status(self, status, print_to_terminal=True):
        self.statusbar.showMessage(status, 0)
        if print_to_terminal:
            print(status)
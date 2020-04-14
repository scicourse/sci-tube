# Libraries
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
import os
import sys
from ase.io import read, write
import numpy as np
from ase.build import make_supercell

class MainWindow(QMainWindow):
    def __init__(self, *args, ** kwargs):
        super().__init__(*args, ** kwargs)
        self.initUI()
    
    def initUI(self):
        
        self.window = QWidget()
        self.setCentralWidget(self.window)

        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomLeftTabWidget()
        self.createBottomRightGroupBox()

        self.grid = QGridLayout()
        self.grid.addWidget(self.TopLeftGroupBox, 0, 0)
        self.grid.addWidget(self.TopRightGroupBox, 0, 1)
        self.grid.addWidget(self.BottomLeftGroupBox, 1, 0)
        self.grid.addWidget(self.BottomRightGroupBox, 1, 1)

        self.grid.setRowStretch(0, 3)
        self.grid.setRowStretch(1, 3)
        self.grid.setColumnStretch(0, 3)
        self.grid.setColumnStretch(1, 3)
        
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        file_toolbar = QToolBar("File")
        file_toolbar.setIconSize(QSize(14, 14))
        self.addToolBar(file_toolbar)
        file_menu = self.menuBar().addMenu("&File")

        
        open_file_action = QAction(QIcon(os.path.join('images', 'blue-folder-open-document.png')), "Open file...", self)
        open_file_action.setStatusTip("Open file")
        open_file_action.triggered.connect(self.file_open)

        file_menu.addAction(open_file_action)
        file_toolbar.addAction(open_file_action)

        saveas_file_action = QAction(QIcon(os.path.join('images', 'disk--pencil.png')), "Save As...", self)
        saveas_file_action.setStatusTip("Save current page to specified file")
        saveas_file_action.triggered.connect(self.file_saveas)
        file_menu.addAction(saveas_file_action)
        file_toolbar.addAction(saveas_file_action)


        self.window.setLayout(self.grid)
        
    
        self.setWindowTitle("SciTube Widget")
        self.resize(1000, 600)
    
    def createTopLeftGroupBox(self):
        self.TopLeftGroupBox = QGroupBox("Preview")
        layoutTL = QVBoxLayout()

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        layoutTL.addWidget(self.imageLabel)
        self.TopLeftGroupBox.setLayout(layoutTL)

    def createTopRightGroupBox(self):
        self.TopRightGroupBox = QGroupBox("General Options")
        self.supported_structure = QComboBox()
        self.tube_radius = QLineEdit()
        self.vac = QLineEdit()
        self.convert_button = QPushButton('Convert to NanoTube')
        self.supported_structure.addItems(['X', 'Y'])
        #self.supported_structure.currentTextChanged.connect(self._updateCombo2)
        self.convert_button.clicked.connect(self.convert_to_tube)
        
        # Grid + Navigation Bar

        layoutTR = QGridLayout()
        layoutTR.addWidget(QLabel("Cut along"), 0, 0)
        layoutTR.addWidget(self.supported_structure, 0, 1)
        layoutTR.addWidget(QLabel("Vacuum"), 1, 0)
        layoutTR.addWidget(self.vac, 1, 1)
        layoutTR.addWidget(QLabel('Enter length of the ribbon'), 2, 0)
        layoutTR.addWidget(self.tube_radius, 2, 1)
        layoutTR.addWidget(self.convert_button, 3, 0)

        self.TopRightGroupBox.setLayout(layoutTR)
    def convert_to_tube(self):
        self.tube_convert()
        tubeimage = QImage('nanotube.png')
        self.tubeLabel.setPixmap(QPixmap.fromImage(tubeimage))
    def createBottomLeftTabWidget(self):
        self.BottomLeftGroupBox = QGroupBox("Tube")
        layoutBL = QVBoxLayout()
        self.tubeLabel = QLabel()
        self.tubeLabel.setBackgroundRole(QPalette.Base)
        self.tubeLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.tubeLabel.setScaledContents(True)

        layoutBL.addWidget(self.tubeLabel)
        self.BottomLeftGroupBox.setLayout(layoutBL)

    def createBottomRightGroupBox(self):
        self.BottomRightGroupBox = QGroupBox("HowTo")
        layoutBR = QVBoxLayout()
        layoutBR.addWidget(QLabel('1- Just click on open file icon'))
        layoutBR.addWidget(QLabel("2- Choose Cif format of your structure"))
        self.BottomRightGroupBox.setLayout(layoutBR)
    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Crystallographic Information File (*.cif);All files (*.*)")
        self.primitive_cell = read(path)

        write('primitive_cell.png', self.primitive_cell, rotation='90z,-90x')

        image = QImage('primitive_cell.png')
        self.imageLabel.setPixmap(QPixmap.fromImage(image))
    def tube_convert(self):
        try:
            a = float(str(self.tube_radius.text()))
            if str(self.supported_structure.currentText()) == 'X':
                self.p = np.array([[1 ,0 ,0],
                                   [0 ,a ,0],
                                   [0 ,0 ,1]])
                super_struct = make_supercell(self.primitive_cell, self.p)
            elif str(self.supported_structure.currentText()) == 'Y':
                self.p = np.array([[0 ,1 ,0],
                                   [a ,0 ,0],
                                   [0 ,0 ,1]])
                super_struct = make_supercell(self.primitive_cell, self.p)
                write('super.cif', super_struct)
                super_struct = read('super.cif')
                os.remove('super.cif')
            super_struct.center(vacuum=15.0, axis=2)
            R = super_struct.get_cell_lengths_and_angles()[1]
            RS = R / (2 * np.pi)

            s = super_struct.copy()

            anchor_position = (np.amax(s.get_positions()[:,2], axis = 0) - np.amin(s.get_positions()[:,2], axis = 0))/2 + np.amin(s.get_positions()[:,2], axis = 0)

            delta = []

            for counter, value in enumerate(s.get_positions()[:,2]):
                delta.append(s.get_positions()[:,2][counter] - anchor_position)
            
            delta = np.array(delta)

            s.positions[:,2] = (RS + delta) * np.cos(2 * np.pi * s.positions[:,1]/R)
            s.positions[:,1] = (RS + delta) * np.sin(2 * np.pi * s.positions[:,1]/R)

            s.center(vacuum=float(str(self.vac.text())), axis=(1,2))

            write('nanotube.xsf', s)
            write('nanotube.png', s, rotation='90z,-90x')
        except Exception as e:
            self.dialog_critical(str(e))

    def file_saveas(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Data", "", "XCrySDen structure format (*.xsf);All files (*.*)")

        if not path:
            # If dialog is cancelled, will return ''
            return

        self._save_to_path(path)

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()

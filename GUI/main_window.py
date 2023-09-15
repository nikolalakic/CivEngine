from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont
from concrete_window import ConcreteWindow
from steel_window import SteelWindow
from soil_window import SoilWindow
from wood_window import WoodWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(800, 600))
        self.setWindowTitle('CivEngine')
        self.concrete_window = None
        self.steel_window = None
        self.soil_window = None
        self.wood_window = None

        layout = QVBoxLayout()

        choose_text = QLabel('Choose option based on material design:')
        font = QFont()
        font.setPointSize(16)
        choose_text.setFont(font)
        choose_text.setFixedSize(800, 30)
        choose_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(choose_text)

        buttons = ["Concrete elements", "Steel elements and joints", "Wood elements and joints", "Soil"]
        for i, button_text in enumerate(buttons):
            button = QPushButton(button_text)
            button_font = QFont()
            button_font.setPointSize(12)
            button.setFont(button_font)
            button.setFixedSize(800, 100)
            button.setStyleSheet("text-align: center")
            layout.addWidget(button)
            if button_text == 'Concrete elements':
                button.clicked.connect(self.concrete_click)
            elif button_text == 'Steel elements and joints':
                button.clicked.connect(self.steel_click)
            elif button_text == 'Wood elements and joints':
                button.clicked.connect(self.wood_click)
            elif button_text == 'Soil':
                button.clicked.connect(self.soil_click)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def concrete_click(self):
        sender = self.sender()
        if sender.text() == "Concrete elements" and self.concrete_window == None:
            self.concrete_window = ConcreteWindow()
            self.concrete_window.show()
        else:
            self.concrete_window.close()
            self.concrete_window = None

    def steel_click(self):
        sender = self.sender()
        if sender.text() == "Steel elements and joints" and self.steel_window is None:
            self.steel_window = SteelWindow()
            self.steel_window.show()
        else:
            self.steel_window.close()
            self.steel_window = None

    def wood_click(self):
        sender = self.sender()
        if sender.text() == "Wood elements and joints" and self.wood_window is None:
            self.wood_window = WoodWindow()
            self.wood_window.show()
        else:
            self.wood_window.close()
            self.wood_window = None


    def soil_click(self):
        sender = self.sender()
        if sender.text() == "Soil" and self.soil_window is None:
            self.soil_window = SoilWindow()
            self.soil_window.show()
        else:
            self.soil_window.close()
            self.soil_window = None


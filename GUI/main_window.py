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
        self.concrete_window = ConcreteWindow()
        self.steel_window = SteelWindow()
        self.soil_window = SoilWindow()
        self.wood_window = WoodWindow()

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

    def closeEvent(self, event):
        self.concrete_window.close()
        self.steel_window.close()
        self.wood_window.close()
        self.soil_window.close()
        event.accept()

    def concrete_click(self):
        if self.concrete_window is None or not self.concrete_window.isVisible():
            self.concrete_window = ConcreteWindow()
            self.concrete_window.closed.connect(self.show_main_window)
        self.hide()
        self.concrete_window.show()

    def show_main_window(self):
        self.show()  # Show the MainWindow

    def steel_click(self):
        if self.steel_window.isVisible():
            self.steel_window.hide()
        else:
            self.steel_window.show()

    def wood_click(self):
        if self.wood_window.isVisible():
            self.wood_window.hide()
        else:
            self.wood_window.show()

    def soil_click(self):
        if self.soil_window.isVisible():
            self.soil_window.hide()
        else:
            self.soil_window.show()

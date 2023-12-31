from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget


class SoilWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(800, 600))
        self.setWindowTitle('Soil')
        layout = QVBoxLayout()
        choose_text = QLabel('Choose one from options:')
        font = QFont()
        font.setPointSize(16)
        choose_text.setFont(font)
        choose_text.setFixedSize(800, 30)
        choose_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(choose_text)

        buttons = ["b1", "b2", "b3"]
        for i, button_text in enumerate(buttons):
            button = QPushButton(button_text)
            button_font = QFont()
            button_font.setPointSize(12)
            button.setFont(button_font)
            button.setFixedSize(800, 50)
            button.setStyleSheet("text-align: center")
            layout.addWidget(button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit, QHBoxLayout


class ComplexBending(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(800, 600))
        self.setWindowTitle('Complex bending')
        layout1 = QVBoxLayout()
        layout2 = QHBoxLayout()
        layout1.addLayout(layout2)

        choose_text = QLabel('Enter parameters:')
        font = QFont()
        font.setPointSize(15)
        choose_text.setFont(font)
        choose_text.setFixedSize(200, 30)
        # choose_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout1.addWidget(choose_text)
#TODO Uredi gui za slozeno savijanje
        lines_of_text = ["Bending moment MRd [kNm]:", ""]
        for i, button_text in enumerate(lines_of_text):
            button = QLineEdit(button_text)
            button_font = QFont()
            button_font.setPointSize(10)
            button.setFont(button_font)
            button.setFixedSize(200, 20)
            button.setStyleSheet("text-align: center")
            if i == 0:
                button.setReadOnly(True)
                button.setCursorPosition(0)
            layout1.addWidget(button)

        widget = QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)


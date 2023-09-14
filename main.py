from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont
import sys
from concrete_window import ConcreteWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(800, 600))
        self.setWindowTitle('CivEngine')

        layout = QVBoxLayout()

        choose_text = QLabel('Choose one from options:')
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
            button.clicked.connect(self.button_click)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def button_click(self):
        sender = self.sender()
        if sender.text() == "Concrete elements":
            self.concrete_window = ConcreteWindow()
            self.concrete_window.show()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

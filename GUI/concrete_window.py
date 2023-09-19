from PyQt6.QtCore import QSize, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget
from ConcreteElementsWindows.complexbending import ComplexBending


class ConcreteWindow(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(800, 600))
        self.complexbending_window = None
        self.setWindowTitle('Concrete elements')
        layout = QVBoxLayout()
        choose_text = QLabel('Choose one from options:')
        font = QFont()
        font.setPointSize(16)
        choose_text.setFont(font)
        choose_text.setFixedSize(800, 30)
        choose_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(choose_text)
        self.closed.connect(self.onClosed)

        buttons = ["Complex bending", "Shear and torsion", "Slab punching check", "Deflection by indirect method",
                   "Stress check", "Column bracing", "Wall bracing", "Bending moment capacity",
                   "Moment - curvature diagrams"]
        for i, button_text in enumerate(buttons):
            button = QPushButton(button_text)
            button_font = QFont()
            button_font.setPointSize(12)
            button.setFont(button_font)
            button.setFixedSize(800, 50)
            button.setStyleSheet("text-align: center")
            layout.addWidget(button)
            if button_text == "Complex bending":
                button.clicked.connect(self.complexbending_click)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def complexbending_click(self):
        sender = self.sender()
        if self.complexbending_window is None and sender.text() == "Complex bending":
            self.complexbending_window = ComplexBending()
            self.complexbending_window.show()
        else:
            self.complexbending_window.close()
            self.complexbending_window = None

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    @pyqtSlot()
    def onClosed(self):
        self.close()

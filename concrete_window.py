from PyQt6.QtWidgets import QMainWindow, QLabel

class ConcreteWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Concrete elements')
        self.setFixedSize(400, 400)
        label = QLabel("This is the Concrete elements window")
        self.setCentralWidget(label)
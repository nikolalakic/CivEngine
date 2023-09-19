from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout


class ComplexBending(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)

        layout = QGridLayout()

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
#TODO Uredi gui za slozeno savijanje koristeci QGridLayout



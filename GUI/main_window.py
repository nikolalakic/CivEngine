from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from ConcreteElementsWindows import interaction_diagram

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CivEngine")
        self.setFixedSize(900, 600)


        # Okviri za layout-ove

        self.beton_frame = QFrame()
        self.beton_frame.setStyleSheet("""
                    QFrame {
                        border: 2px solid gray;
                        border-radius: 8px;
                        background-color: palette(window);
                    }
                """)

        self.celik_frame = QFrame()
        self.celik_frame.setStyleSheet("""
                    QFrame {
                        border: 2px solid gray;
                        border-radius: 8px;
                        background-color: palette(window);
                    }
                """)

        # Definisanje layout-a

        self.glavni_layout = QHBoxLayout()
        self.beton_layout = QVBoxLayout(self.beton_frame)
        self.celik_layout = QVBoxLayout(self.celik_frame)

        # Razmaci do dugmića

        self.beton_layout.setSpacing(5)
        self.celik_layout.setSpacing(5)

        # Naslovi layout-ova

        self.beton_naslov = QLabel("Betonski elementi:")
        self.celik_naslov = QLabel("Čelični elementi:")

        # Definisanje dugmića
        self.beton_button1 = QPushButton('Dijagram interakcije')
        self.celik_button1 = QPushButton('todo')

        # Stilovi dugmića i teksta
        stil_dugmica = ("""
                        QPushButton {
                            min-width: 200px; 
                            min-height: 45px;
                            font-size: 14px;
                            text-align: center;
                                    }
                                    """)

        stil_naslova = ("""
                        QLabel {
                            min-width: 300px; 
                            min-height: 20px;
                            font-size: 25px;
                            qproperty-alignment: 'AlignCenter';
                                    }
                                    """)

        self.beton_button1.setStyleSheet(stil_dugmica)
        self.celik_button1.setStyleSheet(stil_dugmica)

        self.beton_naslov.setStyleSheet(stil_naslova)
        self.celik_naslov.setStyleSheet(stil_naslova)

        # Dodavanje layout-a
        self.beton_layout.addWidget(self.beton_naslov)
        self.beton_layout.addWidget(self.beton_button1)
        self.celik_layout.addWidget(self.celik_naslov)
        self.celik_layout.addWidget(self.celik_button1)
        self.glavni_layout.addLayout(self.beton_layout)
        self.glavni_layout.addLayout(self.celik_layout)
        self.glavni_layout.addWidget(self.beton_frame)
        self.glavni_layout.addWidget(self.celik_frame)

        self.setLayout(self.glavni_layout)

        # Konekcije za signale
        self.beton_button1.setCheckable(True)
        self.beton_button1.clicked.connect(self.interaction_diagram_button_click)

    def interaction_diagram_button_click(self):
        self.interaction_diagram_window = interaction_diagram.Window()
        self.interaction_diagram_window.show()








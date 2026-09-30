import math
import os.path

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLabel, QLineEdit, QPushButton)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class DijagramInterakcije:
    def __init__(self, fck, k, b, h, d1, d2, MEd, NEd):
        self.fck = int(fck)
        self.k = float(k) / 100.0
        self.fcd = 0.85 * self.fck / 1.5  # [MPa]
        self.b = float(b) / 100.0
        self.h = float(h) / 100.0
        self.d1 = float(d1) / 100.0  # [m]
        self.d = self.h - self.d1
        self.d2 = float(d2) / 100.0  # [m]
        self.Es = 200  # [GPa]
        self.fyk = 500  # [MPa]
        self.fyd = 500 / 1.15  # [MPa]
        self.epsilon_yd = self.fyd / self.Es / 1000
        self.epsilon_cu2 = 0.0035
        self.alfa_1 = self.d1 / self.h
        self.alfa_2 = self.d2 / self.h
        self.MEd = float(MEd)
        self.NEd = float(NEd)
        self.mi_Ed = self.MEd / (self.b * self.h ** 2 * self.fcd * 1000)
        self.ni_Ed = self.NEd / (self.b * self.h * self.fcd * 1000)

    @staticmethod
    def beta2_koeficijent(epsilon_c2):
        epsilon_c2 = epsilon_c2 * 1000  # [Formula radi za promile]
        if 2.0 <= epsilon_c2 <= 3.5:
            beta2 = (epsilon_c2 * (3 * epsilon_c2 - 4) + 2) / (2 * epsilon_c2 * (3 * epsilon_c2 - 2))
        elif 0 <= epsilon_c2 < 2.0:
            beta2 = (8 - epsilon_c2) / (4 * (6 - epsilon_c2))
        else:
            beta2 = None
        return beta2

    @staticmethod
    def gustina_omege():
        omege = np.linspace(0, 0.5, num=20)
        return omege

    def centricni_pritisak(self):
        niz_ni_Rd = np.array([])
        niz_mi_Rd = np.array([])
        omege = self.gustina_omege()
        for omega in omege:
            omega1 = 0.5 * omega
            omega2 = 0.5 * omega
            NRd = (1 + omega) * self.b * self.h * self.fcd * 1000
            MRd = (omega2 * (0.5 - self.alfa_2) - omega1 * (0.5 - self.alfa_1)) * self.b * self.h ** 2 * self.fcd * 1000
            ni_Rd = NRd / (self.fcd * 1000 * self.b * self.h)
            mi_Rd = MRd / (self.fcd * 1000 * self.b * self.h ** 2)
            niz_ni_Rd = np.append(niz_ni_Rd, ni_Rd)
            niz_mi_Rd = np.append(niz_mi_Rd, mi_Rd)
        return np.array([niz_ni_Rd, niz_mi_Rd])

    def granica_malog_ekscentriciteta(self):
        epsilon_c2 = self.epsilon_cu2
        beta2 = self.beta2_koeficijent(epsilon_c2)
        epsilon_s2 = epsilon_c2 * (1 - self.alfa_2)
        if epsilon_s2 >= self.epsilon_yd:
            epsilon_s2 = self.epsilon_yd
        epsilon_s1 = self.epsilon_cu2 * self.alfa_1
        if epsilon_s1 >= self.epsilon_yd:
            epsilon_s1 = self.epsilon_yd
        x = self.h
        niz_ni_Rd = np.array([])
        niz_mi_Rd = np.array([])
        omege = self.gustina_omege()
        for omega in omege:
            omega1 = self.k * omega
            omega2 = (1 - self.k) * omega
            As1 = omega1 * self.b * self.h * self.fcd / self.fyd
            As2 = omega2 * self.b * self.h * self.fcd / self.fyd
            Fc = 0.81 * 1 / (1 - self.alfa_1) * self.d * self.b * self.fcd * 1000  # [kN]
            Fs2 = As2 * epsilon_s2 * self.Es * math.pow(10, 6)  # [kN]
            Fs1 = As1 * epsilon_s1 * self.Es * math.pow(10, 6)  # [kN]
            NRd = Fc + Fs1 + Fs2
            MRd = Fc * (self.h / 2 - beta2 * x) + Fs2 * (self.h / 2 - self.d2) - Fs1 * (self.h / 2 - self.d1)
            ni_Rd = NRd / (self.b * self.h * self.fcd * 1000)
            mi_Rd = MRd / (self.fcd * 1000 * self.b * self.h ** 2)
            niz_ni_Rd = np.append(niz_ni_Rd, ni_Rd)
            niz_mi_Rd = np.append(niz_mi_Rd, mi_Rd)
        return np.array([niz_ni_Rd, niz_mi_Rd])

    def tri_i_po_sa_dva_jedan_sedam_cetiri(self):
        epsilon_s1 = self.epsilon_yd
        epsilon_c2 = self.epsilon_cu2
        x = (self.epsilon_cu2 * (self.h - self.d1)) / (self.epsilon_yd + self.epsilon_cu2)
        epsilon_s2 = self.epsilon_cu2 * (x - self.d2) / x
        if epsilon_s2 >= self.epsilon_yd:
            epsilon_s2 = self.epsilon_yd
        niz_ni_Rd = np.array([])
        niz_mi_Rd = np.array([])
        omege = self.gustina_omege()
        beta2 = self.beta2_koeficijent(epsilon_c2)
        for omega in omege:
            omega1 = self.k * omega
            omega2 = (1 - self.k) * omega
            As1 = omega1 * self.b * self.h * self.fcd / self.fyd
            As2 = omega2 * self.b * self.h * self.fcd / self.fyd
            Fc = 0.81 * x * self.b * self.fcd * 1000  # [kN]
            Fs2 = As2 * epsilon_s2 * self.Es * math.pow(10, 6)  # [kN]
            Fs1 = As1 * epsilon_s1 * self.Es * math.pow(10, 6)  # [kN]
            NRd = Fc - Fs1 + Fs2
            MRd = Fc * (self.h / 2 - beta2 * x) + Fs2 * (self.h / 2 - self.d2) + Fs1 * (self.h / 2 - self.d1)
            ni_Rd = NRd / (self.b * self.h * self.fcd * 1000)
            mi_Rd = MRd / (self.fcd * 1000 * self.b * self.h ** 2)
            niz_ni_Rd = np.append(niz_ni_Rd, ni_Rd)
            niz_mi_Rd = np.append(niz_mi_Rd, mi_Rd)
        return np.array([niz_ni_Rd, niz_mi_Rd])

    def tri_i_po_sa_deset(self):
        epsilon_s1 = 0.01
        epsilon_c2 = self.epsilon_cu2
        x = (self.epsilon_cu2 * (self.h - self.d1)) / (epsilon_s1 + self.epsilon_cu2)
        epsilon_s2 = self.epsilon_cu2 * (x - self.d2) / x
        if epsilon_s2 >= self.epsilon_yd:
            epsilon_s2 = self.epsilon_yd
        if epsilon_s1 >= self.epsilon_yd:
            epsilon_s1 = self.epsilon_yd
        niz_ni_Rd = np.array([])
        niz_mi_Rd = np.array([])
        omege = self.gustina_omege()
        beta2 = self.beta2_koeficijent(epsilon_c2)
        for omega in omege:
            omega1 = self.k * omega
            omega2 = (1 - self.k) * omega
            As1 = omega1 * self.b * self.h * self.fcd / self.fyd
            As2 = omega2 * self.b * self.h * self.fcd / self.fyd
            Fc = 0.81 * x * self.b * self.fcd * 1000  # [kN]
            Fs2 = As2 * epsilon_s2 * self.Es * math.pow(10, 6)  # [kN]
            Fs1 = As1 * epsilon_s1 * self.Es * math.pow(10, 6)  # [kN]
            NRd = Fc - Fs1 + Fs2
            MRd = Fc * (self.h / 2 - beta2 * x) + Fs2 * (self.h / 2 - self.d2) + Fs1 * (self.h / 2 - self.d1)
            ni_Rd = NRd / (self.b * self.h * self.fcd * 1000)
            mi_Rd = MRd / (self.fcd * 1000 * self.b * self.h ** 2)
            niz_ni_Rd = np.append(niz_ni_Rd, ni_Rd)
            niz_mi_Rd = np.append(niz_mi_Rd, mi_Rd)
        return np.array([niz_ni_Rd, niz_mi_Rd])

    def tri_i_po_sa_dvadeset(self):
        epsilon_s1 = 0.02
        epsilon_c2 = self.epsilon_cu2
        x = (self.epsilon_cu2 * (self.h - self.d1)) / (epsilon_s1 + self.epsilon_cu2)
        epsilon_s2 = self.epsilon_cu2 * (x - self.d2) / x
        if epsilon_s2 >= self.epsilon_yd:
            epsilon_s2 = self.epsilon_yd
        if epsilon_s1 >= self.epsilon_yd:
            epsilon_s1 = self.epsilon_yd
        niz_ni_Rd = np.array([])
        niz_mi_Rd = np.array([])
        omege = self.gustina_omege()
        beta2 = self.beta2_koeficijent(epsilon_c2)
        for omega in omege:
            omega1 = self.k * omega
            omega2 = (1 - self.k) * omega
            As1 = omega1 * self.b * self.h * self.fcd / self.fyd
            As2 = omega2 * self.b * self.h * self.fcd / self.fyd
            Fc = 0.81 * x * self.b * self.fcd * 1000  # [kN]
            Fs2 = As2 * epsilon_s2 * self.Es * math.pow(10, 6)  # [kN]
            Fs1 = As1 * epsilon_s1 * self.Es * math.pow(10, 6)  # [kN]
            NRd = Fc - Fs1 + Fs2
            MRd = Fc * (self.h / 2 - beta2 * x) + Fs2 * (self.h / 2 - self.d2) + Fs1 * (self.h / 2 - self.d1)
            ni_Rd = NRd / (self.b * self.h * self.fcd * 1000)
            mi_Rd = MRd / (self.fcd * 1000 * self.b * self.h ** 2)
            niz_ni_Rd = np.append(niz_ni_Rd, ni_Rd)
            niz_mi_Rd = np.append(niz_mi_Rd, mi_Rd)
        return np.array([niz_ni_Rd, niz_mi_Rd])

    def tri_i_po_sa_cetrdeset(self):
        epsilon_s1 = 0.04
        epsilon_c2 = self.epsilon_cu2
        x = (self.epsilon_cu2 * (self.h - self.d1)) / (epsilon_s1 + self.epsilon_cu2)
        epsilon_s2 = self.epsilon_cu2 * (x - self.d2) / x
        if epsilon_s2 >= self.epsilon_yd:
            epsilon_s2 = self.epsilon_yd
        if epsilon_s1 >= self.epsilon_yd:
            epsilon_s1 = self.epsilon_yd
        niz_ni_Rd = np.array([])
        niz_mi_Rd = np.array([])
        omege = self.gustina_omege()
        beta2 = self.beta2_koeficijent(epsilon_c2)
        for omega in omege:
            omega1 = self.k * omega
            omega2 = (1 - self.k) * omega
            As1 = omega1 * self.b * self.h * self.fcd / self.fyd
            As2 = omega2 * self.b * self.h * self.fcd / self.fyd
            Fc = 0.81 * x * self.b * self.fcd * 1000  # [kN]
            Fs2 = As2 * epsilon_s2 * self.Es * math.pow(10, 6)  # [kN]
            Fs1 = As1 * epsilon_s1 * self.Es * math.pow(10, 6)  # [kN]
            NRd = Fc - Fs1 + Fs2
            MRd = Fc * (self.h / 2 - beta2 * x) + Fs2 * (self.h / 2 - self.d2) + Fs1 * (self.h / 2 - self.d1)
            ni_Rd = NRd / (self.b * self.h * self.fcd * 1000)
            mi_Rd = MRd / (self.fcd * 1000 * self.b * self.h ** 2)
            niz_ni_Rd = np.append(niz_ni_Rd, ni_Rd)
            niz_mi_Rd = np.append(niz_mi_Rd, mi_Rd)
        return np.array([niz_ni_Rd, niz_mi_Rd])

    def stampa_na_osi(self, ax):
        omege = self.gustina_omege()
        centricni_pritisak = self.centricni_pritisak()
        granica_malog_ekscentriciteta = self.granica_malog_ekscentriciteta()
        tri_i_po_sa_dva_jedan_sedam_cetiri = self.tri_i_po_sa_dva_jedan_sedam_cetiri()
        tri_i_po_sa_deset = self.tri_i_po_sa_deset()
        tri_i_po_sa_dvadeset = self.tri_i_po_sa_dvadeset()
        tri_i_po_sa_cetrdeset = self.tri_i_po_sa_cetrdeset()

        ax.set_xlabel('\u03BDEd')
        ax.set_ylabel('\u03BCEd')
        ax.set_title('Dijagram interakcije')

        # Osnovne linije
        ax.plot(centricni_pritisak[0], centricni_pritisak[1], color='green',
                label='Ec2/Ec1 = 2\u2030/ 2\u2030')
        ax.plot(granica_malog_ekscentriciteta[0],
                granica_malog_ekscentriciteta[1], color='purple',
                label='Ec2/Ec1 = 3.5\u2030/ 0\u2030')
        ax.plot(tri_i_po_sa_dva_jedan_sedam_cetiri[0],
                tri_i_po_sa_dva_jedan_sedam_cetiri[1], color='black',
                linestyle='--', label='Ec2/Es1 = 3.5\u2030/ -2.174\u2030')
        ax.plot(tri_i_po_sa_deset[0], tri_i_po_sa_deset[1], color='black',
                label='Ec2/Es1 = 3.5\u2030/ -10\u2030')
        ax.plot(tri_i_po_sa_dvadeset[0], tri_i_po_sa_dvadeset[1], color='blue',
                label='Ec2/Es1 = 3.5\u2030/ -20\u2030')
        ax.plot(tri_i_po_sa_cetrdeset[0], tri_i_po_sa_cetrdeset[1], color='magenta',
                label='Ec2/Es1 = 3.5\u2030/ -40\u2030')
        ax.plot([], [],
                label=f'As1 = {self.k} * As = {self.k} * \u03C9 * b * h * fcd / fyd', linestyle='-', color='black',
                linewidth=2, marker='>', markersize=10)
        ax.plot([], [],
                label=f'As2 = {1 - self.k} * As = {1 - self.k} * \u03C9 * b * h * fcd / fyd', linestyle='-',
                color='black', linewidth=2, marker='>', markersize=10)
        ax.plot([], [],
                label=f'fck = {self.fck} MPa', linestyle='-', color='black', linewidth=2, marker='*', markersize=10)
        ax.plot([], [],
                label=f'\u03BC_Ed = {round(self.mi_Ed, 2)} ', linestyle='-', color='black', linewidth=2, marker='*',
                markersize=10)
        ax.plot([], [],
                label=f'\u03BD_Ed = {round(self.ni_Ed, 2)} ', linestyle='-', color='black', linewidth=2, marker='*',
                markersize=10)

        niz_x = np.array([centricni_pritisak[0],
                          granica_malog_ekscentriciteta[0],
                          tri_i_po_sa_dva_jedan_sedam_cetiri[0],
                          tri_i_po_sa_deset[0],
                          tri_i_po_sa_dvadeset[0],
                          tri_i_po_sa_cetrdeset[0]
                          ], dtype=object)
        niz_y = np.array([centricni_pritisak[1],
                          granica_malog_ekscentriciteta[1],
                          tri_i_po_sa_dva_jedan_sedam_cetiri[1],
                          tri_i_po_sa_deset[1],
                          tri_i_po_sa_dvadeset[1],
                          tri_i_po_sa_cetrdeset[1]
                          ], dtype=object)

        ax.plot(niz_x, niz_y, color='gray')

        niz_x = np.array([niz_x[0], niz_x[1], niz_x[2], niz_x[3], niz_x[4], niz_x[5]])
        niz_y = np.array([niz_y[0], niz_y[1], niz_y[2], niz_y[3], niz_y[4], niz_y[5]])

        tacka_ni_Ed = [self.ni_Ed]
        tacka_mi_Ed = [self.mi_Ed]
        ax.plot(tacka_ni_Ed, tacka_mi_Ed, marker="x", markersize=6, color="red")

        for i, (x, y) in enumerate(zip(niz_x, niz_y)):
            for j in range(len(x)):
                if i == 0:
                    rotation = 90
                elif i == 4:
                    rotation = 45
                elif i == 5:
                    rotation = 45
                else:
                    rotation = 0
                ax.text(x[j], y[j], f'{round(omege[j], 2)}', fontsize=6, verticalalignment="bottom", rotation=rotation)

        ax.legend(fontsize='x-small')


class PlotWindow(QWidget):
    def __init__(self, model):
        super().__init__()
        self.setWindowTitle("Dijagram interakcije - Grafički prikaz")
        self.resize(1000, 800)

        layout = QVBoxLayout()
        self.fig = Figure(figsize=(10, 8), dpi=96)
        self.canvas = FigureCanvas(self.fig)

        # Matplotlib toolbar (zumiranje, pomeranje, čuvanje)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        ax = self.fig.add_subplot(111)
        model.stampa_na_osi(ax)
        self.canvas.draw()


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dijagram interakcije")
        self.resize(900, 600)

        # Layout koji sadrži glavni kao i layout za naslov
        main_layout = QVBoxLayout()

        # Layout za naslov (ispravno kreiran i popunjen na početku)
        self.naslov_layout = QHBoxLayout()
        self.naslov_label = QLabel('Dijagram interakcije')

        self.naslov_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.naslov_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.naslov_layout.addWidget(self.naslov_label)
        main_layout.addLayout(self.naslov_layout)

        # Glavni layout je horizontalan: [Unos podataka] | [Slika]
        self.glavni_layout = QHBoxLayout()

        # Layout za ulazne podatke (leva strana)
        self.ulazni_podaci_layout = QFormLayout()

        # Unošenje imena, polja i opisa za promenljive
        self.fck_label = QLabel("fck [MPa]:")
        self.fck_input = QLineEdit()

        self.k_label = QLabel('k [%]:')
        self.k_input = QLineEdit()

        self.b_label = QLabel('b [cm]:')
        self.b_input = QLineEdit()

        self.h_label = QLabel('h [cm]:')
        self.h_input = QLineEdit()

        self.d1_label = QLabel('d1 [cm]:')
        self.d1_input = QLineEdit()

        self.d2_label = QLabel('d2 [cm]:')
        self.d2_input = QLineEdit()

        self.MEd_label = QLabel('MEd [kNm]:')
        self.MEd_input = QLineEdit()

        self.NEd_label = QLabel('NEd [kN]:')
        self.NEd_input = QLineEdit()

        # Definisanje ikonica sa tooltipovima
        self.fck_help = QLabel("❓")
        self.fck_help.setToolTip("Karakteristična čvrstoća betona na pritisak u [MPa].")

        self.k_help = QLabel("❓")
        self.k_help.setToolTip("Procenat površine zategnute armature u odnosu na ukupnu armaturu u [%].")

        self.b_help = QLabel("❓")
        self.b_help.setToolTip("Širina poprečnog preseka u [cm].")

        self.h_help = QLabel("❓")
        self.h_help.setToolTip("Visina poprečnog preseka u [cm].")

        self.d1_help = QLabel("❓")
        self.d1_help.setToolTip("Rastojanje od težišta zategnute armature do ivice zategnutog preseka [cm].")

        self.d2_help = QLabel("❓")
        self.d2_help.setToolTip("Rastojanje od težišta pritisnute armature do ivice pritisnutog preseka [cm].")

        self.MEd_help = QLabel("❓")
        self.MEd_help.setToolTip("Vrednost proračunskog momenta savijanja oko visine preseka u [kNm]")

        self.NEd_help = QLabel("❓")
        self.NEd_help.setToolTip("Vrednost proračunske aksijalne sile pritiska (za zatezanje uneti sa -) u [kN]")

        # Horizontalni redovi za unose
        fck_red_layout = QHBoxLayout()
        fck_red_layout.addWidget(self.fck_input)
        fck_red_layout.addWidget(self.fck_help)

        k_red_layout = QHBoxLayout()
        k_red_layout.addWidget(self.k_input)
        k_red_layout.addWidget(self.k_help)

        b_red_layout = QHBoxLayout()
        b_red_layout.addWidget(self.b_input)
        b_red_layout.addWidget(self.b_help)

        h_red_layout = QHBoxLayout()
        h_red_layout.addWidget(self.h_input)
        h_red_layout.addWidget(self.h_help)

        d1_red_layout = QHBoxLayout()
        d1_red_layout.addWidget(self.d1_input)
        d1_red_layout.addWidget(self.d1_help)

        d2_red_layout = QHBoxLayout()
        d2_red_layout.addWidget(self.d2_input)
        d2_red_layout.addWidget(self.d2_help)

        MEd_red_layout = QHBoxLayout()
        MEd_red_layout.addWidget(self.MEd_input)
        MEd_red_layout.addWidget(self.MEd_help)

        NEd_red_layout = QHBoxLayout()
        NEd_red_layout.addWidget(self.NEd_input)
        NEd_red_layout.addWidget(self.NEd_help)

        # Dodavanje redova u formu
        self.ulazni_podaci_layout.addRow(self.MEd_label, MEd_red_layout)
        self.ulazni_podaci_layout.addRow(self.NEd_label, NEd_red_layout)
        self.ulazni_podaci_layout.addRow(self.fck_label, fck_red_layout)
        self.ulazni_podaci_layout.addRow(self.k_label, k_red_layout)
        self.ulazni_podaci_layout.addRow(self.b_label, b_red_layout)
        self.ulazni_podaci_layout.addRow(self.h_label, h_red_layout)
        self.ulazni_podaci_layout.addRow(self.d1_label, d1_red_layout)
        self.ulazni_podaci_layout.addRow(self.d2_label, d2_red_layout)

        # Dugme za proračun
        self.calc_button = QPushButton("Izračunaj i prikaži dijagram")
        self.calc_button.clicked.connect(self.pokreni_proracun)
        self.ulazni_podaci_layout.addRow(self.calc_button)

        # Kreiranje vertikalnog layout-a za sliku (desna strana)
        self.slika_layout = QVBoxLayout()

        self.slika_label = QLabel("Ovde ide slika poprečnog preseka\n(Postavite sliku npr. preseka stubova)")
        self.slika_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slika_label.setStyleSheet(
            "border: 2px dashed #aaa; background-color: palette(window); color: #555; border-radius: 8px;")
        self.slika_label.setMinimumSize(450, 500)
        putanja_slike = os.path.join("Graphics", "interaction_diagram.png")

        if os.path.exists(putanja_slike):
            pixmap = QPixmap(putanja_slike)
            # Skaliranje slike da lepo stane u prozor uz očuvanje srazmere
            self.slika_label.setPixmap(
                pixmap.scaled(440, 490, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.slika_label.setText(f"Slika nije pronađena!\nOčekivana putanja:\n{putanja_slike}")
            self.slika_label.setStyleSheet(
                "border: 2px dashed red; color: red; background-color: palette(window); border-radius: 8px;")

        self.slika_layout.addWidget(self.slika_label)

        # Formiranje konačnih layoutova (Leva strana: unos, Desna strana: slika)
        self.glavni_layout.addLayout(self.ulazni_podaci_layout)
        self.glavni_layout.addLayout(self.slika_layout)

        main_layout.addLayout(self.glavni_layout)

        self.setLayout(main_layout)
        self.plot_window = None

    def pokreni_proracun(self):
        try:
            fck = float(self.fck_input.text())
            k = float(self.k_input.text())
            b = float(self.b_input.text())
            h = float(self.h_input.text())
            d1 = float(self.d1_input.text())
            d2 = float(self.d2_input.text())
            MEd = float(self.MEd_input.text())
            NEd = float(self.NEd_input.text())

            model = DijagramInterakcije(fck, k, b, h, d1, d2, MEd, NEd)
            self.plot_window = PlotWindow(model)
            self.plot_window.show()

        except ValueError:
            print("Greška: Proverite da li ste uneli validne brojeve u sva polja!")
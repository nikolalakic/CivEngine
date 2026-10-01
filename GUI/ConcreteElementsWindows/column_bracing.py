import math
import os.path
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QDialog, QTextEdit, QComboBox)


class UtezanjeStuba:
    def __init__(self, params, bi_niz):
        self.sniz = np.array([20, 15, 12.5, 10, 7.5], dtype=float) / 100

        # Mapiranje izabranog prečnika iz padajućeg menija na površinu (m^2)
        precnik_str = params.get('precnik_uzengije', 'φ 8')
        if '8' in precnik_str:
            self.izabrani_fi = 0.503 / 10000
        elif '10' in precnik_str:
            self.izabrani_fi = 0.785 / 10000
        elif '12' in precnik_str:
            self.izabrani_fi = 1.13 / 10000
        else:
            self.izabrani_fi = 0.503 / 10000

        self.NEd = abs(float(params.get('NEd', 0)))
        self.b = float(params.get('b', 0)) / 100
        self.h = float(params.get('h', 0)) / 100
        self.h0 = self.h - 0.08

        fck_val = int(params.get('fck', 0))
        self.fck = fck_val * 1000
        self.fcd = 0.85 * self.fck / 1.5
        self.fyd = 500 / 1.15 * 1000
        self.esyd = 0.002174
        self.nied = self.NEd / (self.b * self.h * self.fcd)
        self.b0 = self.b - 0.08

        self.q0 = float(params.get('q0', 0))
        self.Tc = 0.5
        self.ObimUzg = float(params.get('ObimUzg', 0)) / 100
        self.tip_armature = str(params.get('tip_armature', 'B500B')).upper()
        self.T = float(params.get('T', 0))
        self.MEd = float(params.get('MEd', 0))
        self.MRd = float(params.get('MRd', 0))
        self.Hs = float(params.get('Hs', 0))

        self.bi_niz = np.array(bi_niz, dtype=float) / 100

    def Armatura(self):
        if self.tip_armature == 'B500B':
            koeficijent = 1.5
        elif self.tip_armature == 'B500C':
            koeficijent = 1
        else:
            raise ValueError('Tip armature mora biti B500B ili B500C.')
        return koeficijent

    def Mfi(self):
        koeficijent = self.Armatura()
        Tc = 0.5
        if self.T > Tc:
            mfi = koeficijent * (2 * self.q0 * self.MEd / self.MRd - 1)
        else:
            mfi = koeficijent * (2 * (self.q0 * self.MEd / self.MRd) - 1) * Tc / self.T + 1
        if self.MRd >= self.MEd * self.q0:
            mfi = 1
        return mfi

    def Utezanje(self):
        rezultati_log = []
        if self.MRd >= self.MEd * self.q0:
            rezultati_log.append('Presek je predimenzionisan, usvojena je minimalna vrednost mφ = 1')

        if self.nied > 0.65:
            raise ValueError(
                f'Normalizovana sila ν,Ed je veća od 0.65! Povećaj marku betona ili dimenzije stuba!\nν,Ed = {self.nied:.3f} >= 0.65')
        elif self.nied <= 0.2 and self.q0 <= 2:
            rezultati_log.append('Primenjuju se pravila iz EC2!')
            return "\n".join(rezultati_log)
        else:
            rezultati_log.append(f'ν,Ed = {round(self.nied, 2)} <= 0.65')
            mfi = self.Mfi()

            proizvod = 0
            for i in self.bi_niz:
                proizvod = proizvod + math.pow(i, 2)
            alfan = 1 - proizvod / (6 * self.b0 * self.h0)

            x = self.izabrani_fi
            Vsw = x * self.ObimUzg
            uspeh = False

            omegawdprov: float = 0.0
            omegawdreq: float = 0.0
            alfas: float = 0.0
            alfa: float = 0.0
            alfa_omegawdreq: float = 0.0

            for p in self.sniz:
                # Izračunavamo parametre za trenutni razmak s (p) i izabrani prečnik
                current_alfas = (1 - p / (2 * self.b0)) * (1 - p / (2 * self.h0))
                current_alfa = current_alfas * alfan
                Vco = self.b0 * self.h0 * p
                current_omegawdprov = (Vsw * self.fyd) / (Vco * self.fcd)
                current_alfa_omegawdreq = 30 * mfi * self.nied * self.esyd * self.b / self.b0 - 0.035
                current_omegawdreq = current_alfa_omegawdreq / current_alfa

                precnik = math.sqrt(4 * x / math.pi) * 1000

                if current_omegawdprov >= current_omegawdreq:
                    rezultati_log.append(f'φ = {round(precnik, 0)} na s = {p * 100:.1f} cm ............OK!')
                    # Čuvamo tačne vrednosti uspešnog koraka
                    omegawdprov = current_omegawdprov
                    omegawdreq = current_omegawdreq
                    alfas = current_alfas
                    alfa = current_alfa
                    alfa_omegawdreq = current_alfa_omegawdreq
                    uspeh = True
                    break
                else:
                    rezultati_log.append(f'φ = {round(precnik, 0)} na s = {p * 100:.1f} cm ne zadovoljava!')
                    # Čuvamo vrednosti poslednjeg razmaka i za neuspešan slučaj da se prikažu
                    omegawdprov = current_omegawdprov
                    omegawdreq = current_omegawdreq
                    alfas = current_alfas
                    alfa = current_alfa
                    alfa_omegawdreq = current_alfa_omegawdreq

            if not uspeh:
                rezultati_log.append('>>> Nedovoljno utezanje stuba za izabrani prečnik!')

            rezultati_log.append(f'ω_wd_prov = {omegawdprov:.4f}')
            rezultati_log.append(f'ω_wd_req = {omegawdreq:.4f}')
            rezultati_log.append(f'α_s = {alfas:.4f}')
            rezultati_log.append(f'α_n = {alfan:.4f}')
            rezultati_log.append(f'α = {alfa:.4f}')
            rezultati_log.append(f'α_ω = {alfa_omegawdreq:.4f}')

        return "\n".join(rezultati_log)


class RezultatiWindow(QDialog):
    """ Poseban prozor za prikaz rezultata proračuna """

    def __init__(self, tekst_rezultata):
        super().__init__()
        self.setWindowTitle("Izveštaj o proračunu - Utezanje stuba")
        self.resize(600, 500)

        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(tekst_rezultata)
        self.text_edit.setStyleSheet("font-family: Consolas, monospace; font-size: 13px;")

        layout.addWidget(self.text_edit)
        self.setLayout(layout)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Utezanje stuba")
        self.resize(1300, 700)

        main_layout = QVBoxLayout()

        # Layout za naslov
        self.naslov_layout = QHBoxLayout()
        self.naslov_label = QLabel('Utezanje stuba')
        self.naslov_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.naslov_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.naslov_layout.addWidget(self.naslov_label)
        main_layout.addLayout(self.naslov_layout)

        # Glavni horizontalni raspored: [Unos] | [Tabela (bi)] | [Slika]
        self.glavni_layout = QHBoxLayout()

        # ----------------------------------------------------
        # 1. LEVA STRANA: Polja za unos parametara
        # ----------------------------------------------------
        self.ulazni_podaci_layout = QFormLayout()

        self.ime_stuba_input = QLineEdit("Stub S1")
        self.NEd_input = QLineEdit("")
        self.b_input = QLineEdit("")
        self.h_input = QLineEdit("")
        self.fck_input = QLineEdit("")
        self.q0_input = QLineEdit("")
        self.ObimUzg_input = QLineEdit("")

        # Dropdown za izbor tipa armature
        self.tip_armature_combo = QComboBox()
        self.tip_armature_combo.addItems(["B500B", "B500C"])

        # Dropdown za izbor prečnika uzengija
        self.precnik_combo = QComboBox()
        self.precnik_combo.addItems(["φ 8", "φ 10", "φ 12"])

        self.T_input = QLineEdit("")
        self.MEd_input = QLineEdit("1")
        self.MRd_input = QLineEdit("1")
        self.Hs_input = QLineEdit("3.0")


        self.ulazni_podaci_layout.addRow("Ime stuba:", self.ime_stuba_input)
        self.ulazni_podaci_layout.addRow("Normalna sila NEd [kN]:", self.NEd_input)
        self.ulazni_podaci_layout.addRow("Širina b [cm]:", self.b_input)
        self.ulazni_podaci_layout.addRow("Visina h [cm]:", self.h_input)
        self.ulazni_podaci_layout.addRow("Marka betona fck [MPa]:", self.fck_input)
        self.ulazni_podaci_layout.addRow("Faktor ponašanja q0:", self.q0_input)
        self.ulazni_podaci_layout.addRow("Obim uzengija [cm]:", self.ObimUzg_input)
        self.ulazni_podaci_layout.addRow("Tip armature:", self.tip_armature_combo)
        self.ulazni_podaci_layout.addRow("Prečnik uzengija (φ):", self.precnik_combo)
        self.ulazni_podaci_layout.addRow("Period T [s]:", self.T_input)
        self.ulazni_podaci_layout.addRow("Seizmički moment MEd [kNm]:", self.MEd_input)
        self.ulazni_podaci_layout.addRow("Moment nosivosti MRd [kNm]:", self.MRd_input)
        self.ulazni_podaci_layout.addRow("Spratna visina Hs [m]:", self.Hs_input)

        self.calc_button = QPushButton("Izračunaj utezanje")
        self.calc_button.clicked.connect(self.pokreni_proracun)
        self.ulazni_podaci_layout.addRow(self.calc_button)

        # ----------------------------------------------------
        # 2. SREDINA: Excel-like tabela za razmake bi [cm]
        # ----------------------------------------------------
        self.tabela_layout = QVBoxLayout()

        self.tabela_naslov = QLabel("Razmak pridržanih šipki bi [cm]")
        self.tabela_naslov.setStyleSheet("font-weight: bold;")
        self.tabela_layout.addWidget(self.tabela_naslov)

        self.table_widget = QTableWidget(3, 1)
        self.table_widget.setHorizontalHeaderLabels(["bi [cm]"])

        pocetni_bi = [10.0, 15.0, 10.0]
        for row, val in enumerate(pocetni_bi):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(val)))

        self.tabela_layout.addWidget(self.table_widget)

        self.dodaj_red_btn = QPushButton("Dodaj novi red (bi)")
        self.dodaj_red_btn.clicked.connect(self.dodaj_novi_red)
        self.tabela_layout.addWidget(self.dodaj_red_btn)

        self.obrisi_red_btn = QPushButton("Obriši selektovani red")
        self.obrisi_red_btn.setStyleSheet("background-color: #f2dede; color: #a94442;")
        self.obrisi_red_btn.clicked.connect(self.obrisi_red)
        self.tabela_layout.addWidget(self.obrisi_red_btn)

        # ----------------------------------------------------
        # 3. DESNA STRANA: Slika poprečnog preseka
        # ----------------------------------------------------
        self.slika_layout = QVBoxLayout()

        self.slika_label = QLabel("Slika preseka")
        self.slika_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slika_label.setStyleSheet(
            "border: 2px dashed #aaa; background-color: palette(window); color: #555; border-radius: 8px;")
        self.slika_label.setMinimumSize(400, 500)


    ## TODO odradi grafiku za utezanje
        putanja_slike = os.path.join("Graphics", "column_bracing.png")
        if os.path.exists(putanja_slike):
            pixmap = QPixmap(putanja_slike)
            self.slika_label.setPixmap(
                pixmap.scaled(390, 490, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.slika_label.setText(f"Slika nije pronađena!\nOčekivana putanja:\n{putanja_slike}")
            self.slika_label.setStyleSheet(
                "border: 2px dashed red; color: red; background-color: palette(window); border-radius: 8px;")

        self.slika_layout.addWidget(self.slika_label)

        # Spajanje sve tri kolone
        self.glavni_layout.addLayout(self.ulazni_podaci_layout)
        self.glavni_layout.addLayout(self.tabela_layout)
        self.glavni_layout.addLayout(self.slika_layout)

        main_layout.addLayout(self.glavni_layout)

        # ----------------------------------------------------
        # 4. DONJI RED: Kratak status/obaveštenje
        # ----------------------------------------------------
        self.rezultat_layout = QHBoxLayout()

        self.rezultat_tekst_label = QLabel("Status:")
        self.rezultat_tekst_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.rezultat_vrednost_label = QLabel("Unesite podatke i kliknite Izračunaj")
        self.rezultat_vrednost_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #2980b9;")

        self.rezultat_layout.addWidget(self.rezultat_tekst_label)
        self.rezultat_layout.addWidget(self.rezultat_vrednost_label)
        self.rezultat_layout.addStretch()

        main_layout.addLayout(self.rezultat_layout)
        self.setLayout(main_layout)

        self.rezultati_prozor = None

    def dodaj_novi_red(self):
        trenutni_broj_redova = self.table_widget.rowCount()
        self.table_widget.insertRow(trenutni_broj_redova)
        self.table_widget.setItem(trenutni_broj_redova, 0, QTableWidgetItem("10.0"))

    def obrisi_red(self):
        selected_rows = self.table_widget.selectionModel().selectedRows()
        if selected_rows:
            row_to_delete = selected_rows[0].row()
            self.table_widget.removeRow(row_to_delete)
        else:
            trenutni_broj_redova = self.table_widget.rowCount()
            if trenutni_broj_redova > 0:
                self.table_widget.removeRow(trenutni_broj_redova - 1)
            else:
                QMessageBox.warning(self, "Upozorenje", "Tabela je već prazna!")

    def pokreni_proracun(self):
        try:
            params = {
                'NEd': float(self.NEd_input.text()),
                'b': float(self.b_input.text()),
                'h': float(self.h_input.text()),
                'fck': float(self.fck_input.text()),
                'q0': float(self.q0_input.text()),
                'ObimUzg': float(self.ObimUzg_input.text()),
                'tip_armature': self.tip_armature_combo.currentText(),
                'precnik_uzengije': self.precnik_combo.currentText(),
                'T': float(self.T_input.text()),
                'MEd': float(self.MEd_input.text()),
                'MRd': float(self.MRd_input.text()),
                'Hs': float(self.Hs_input.text())
            }

            bi_niz = []
            for row in range(self.table_widget.rowCount()):
                item = self.table_widget.item(row, 0)
                if item and item.text().strip():
                    bi_niz.append(float(item.text()))

            if not bi_niz:
                raise ValueError("Tabela za razmake bi ne može biti prazna!")

            proracun = UtezanjeStuba(params, bi_niz)
            rezultat = proracun.Utezanje()

            self.rezultat_vrednost_label.setText(
                "Proračun uspešno završen. Pogledajte otvoreni prozor sa rezultatima.")

            self.rezultati_prozor = RezultatiWindow(rezultat)
            self.rezultati_prozor.show()

        except ValueError as e:
            QMessageBox.critical(self, "Greška u podacima", f"Došlo je do greške:\n{str(e)}")
        except Exception as ex:
            QMessageBox.critical(self, "Greška", f"Neočekivana greška:\n{str(ex)}")
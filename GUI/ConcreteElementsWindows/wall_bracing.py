import math
import os.path
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QDialog, QTextEdit, QComboBox)


class UtezanjeZida:
    def __init__(self, params, bi_niz):
        # Mapiranje izabranog prečnika iz padajućeg menija na površinu (m^2)
        precnik_str = params.get('precnik_uzengije', 'φ 8')
        if '8' in precnik_str:
            precnik_m = 0.008
        elif '10' in precnik_str:
            precnik_m = 0.010
        elif '12' in precnik_str:
            precnik_m = 0.012
        elif '14' in precnik_str:
            precnik_m = 0.014
        else:
            precnik_m = 0.008

        self.a1_uz = math.pow(precnik_m, 2) * math.pi / 4

        self.naziv_zida = str(params.get('naziv_zida', 'Z1'))
        self.NEd = abs(float(params.get('NEd', 0)))
        b_cm = float(params.get('b', 0))
        self.b = b_cm / 100
        self.b_0 = self.b - 0.05

        h_cm = float(params.get('h', 0))
        self.h = h_cm / 100

        fck_val = float(params.get('fck', 30))
        self.fck = fck_val
        self.fcd = 0.85 * fck_val * 1000 / 1.5  # KPa
        self.fyd = 500 * 1000 / 1.15  # KPa
        self.omega_v = 0.201 / 100 * self.fyd / self.fcd  # iz minimalnog procenta armiranja

        self.tip_armature = str(params.get('tip_armature', 'B500B')).upper()
        self.T = float(params.get('T', 0.1))
        self.q0 = float(params.get('q0', 1.5))

        h0_cm = float(params.get('h0', 30.0))
        self.h_0 = h0_cm / 100

        self.obim_uzengija = float(params.get('obim_uzengija', 100.0)) / 100
        self.s = float(params.get('s', 10.0)) / 100

        self.ni = self.NEd / (self.b * self.h * self.fcd)
        self.MEd = float(params.get('MEd', 1))
        self.MRd = float(params.get('MRd', 1))
        self.Hs = float(params.get('Hs', 3.0))

        self.bi_niz = np.array(bi_niz, dtype=float) / 100  # [m]

    def Armatura(self):
        if self.tip_armature == 'B500B':
            koeficijent = 1.5
        elif self.tip_armature == 'B500C':
            koeficijent = 1.0
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
            mfi = 1.0
        return mfi

    def Alfa_n(self):
        suma = 0
        for i in self.bi_niz:
            suma = suma + math.pow(i, 2)
        alfan = 1 - suma / (6 * self.b_0 * self.h_0)
        return alfan

    def Alfa_s(self):
        alfas = (1 - self.s / (2 * self.b_0)) * (1 - self.s / (2 * self.h_0))
        return alfas

    def Alfa(self):
        alfan = self.Alfa_n()
        alfas = self.Alfa_s()
        alfa = alfan * alfas
        return alfa

    def alfa_omega_dreq(self):
        mfi = self.Mfi()
        alfa_omegad_dreq = 30 * mfi * (self.ni + self.omega_v) * 0.002174 * self.b / self.b_0 - 0.035
        return alfa_omegad_dreq

    def Minimalna_Duzina_Utezanja(self):
        alfa_omegad_req = self.alfa_omega_dreq()
        xu = (self.ni + self.omega_v) * self.h * self.b / self.b_0
        epsilon_cu2_c = 0.0035 + 0.1 * alfa_omegad_req
        lc_mreq = xu * (1 - 0.0035 / epsilon_cu2_c)
        if lc_mreq < max(0.15 * self.h, 1.5 * self.b):
            lc_mreq = max(0.15 * self.h, 1.5 * self.b)
        return lc_mreq

    def Kontrola_minimalne_debljine_utegnutog_elementa(self):
        if self.h_0 >= max(self.b, 0.2 * self.h):
            a = f'Prema članu 5.4.3.4.2 (10) Evrokoda 8 minimalna debljina utegnutog elementa je: b0,min = Hs/10 = {round(self.Hs / 10, 2) * 100} [cm]'
        else:
            a = f'Prema članu 5.4.3.4.2 (10) Evrokoda 8 minimalna debljina utegnutog elementa je: b0,min = Hs/15 = {round(self.Hs / 15, 2) * 100} [cm]'
        return a

    def Utezanje(self):
        rezultati_log = []

        # Kontrola normalizovane sile
        if self.ni <= 0.15:
            rezultati_log.append(f'Nije potrebno utezanje krajeva zida {self.naziv_zida}')
            return "\n".join(rezultati_log)
        elif self.ni > 0.4:
            ni_rnd = round(self.ni, 2)
            raise ValueError(
                f'Prekoračena maksimalna normalizovana sila za seizmički zid {self.naziv_zida}!!!\nν = {ni_rnd} , ν_max = 0.4')
        else:
            rezultati_log.append(f'Potrebno je utezanje krajeva zida za zid {self.naziv_zida}\n')

        if self.MRd >= self.MEd * self.q0:
            rezultati_log.append('Presek je predimenzionisan, usvojena je minimalna vrednost mφ = 1\n')

        xu = (self.ni + self.omega_v) * self.h * self.b / self.b_0
        alfa_omegad_req = self.alfa_omega_dreq()
        lc_mreq = self.Minimalna_Duzina_Utezanja()
        alfa = self.Alfa()
        alfa_s = self.Alfa_s()
        alfa_n = self.Alfa_n()
        Vco = self.b_0 * self.h_0 * self.s
        Vsw = self.a1_uz * self.obim_uzengija
        omega_d_prov = Vsw * self.fyd / (Vco * self.fcd)
        epsilon_cu2c_prov = 0.0035 + 0.1 * alfa * omega_d_prov
        lc_req = xu * (1 - 0.0035 / epsilon_cu2c_prov)

        limit_omega = min(0.08, alfa_omegad_req / alfa)
        if omega_d_prov <= limit_omega:
            rezultati_log.append('Nije obezbeđeno dovoljno utezanje ivičnog elementa!')
            rezultati_log.append(f'ω_wd,prov = {omega_d_prov:.4f} < ω_wd,req = {limit_omega:.4f}')

        bo_min = self.Kontrola_minimalne_debljine_utegnutog_elementa()
        rezultati_log.append(bo_min)



        rezultati_log.append(f'ν,Ed = {self.ni:.2f}')
        rezultati_log.append(f'Potrebna dužina utezanja kraja zida: lc_req = {lc_req * 100:.1f} [cm]')
        rezultati_log.append(f'Trenutna dužina utezanja zida: h0 = {self.h_0 * 100:.1f} [cm]')
        rezultati_log.append(f'Minimalna potrebna dužina utezanja zida: lc_mreq = {lc_mreq * 100:.1f} [cm]')
        rezultati_log.append(f'α_s = {alfa_s:.4f}')
        rezultati_log.append(f'α_n = {alfa_n:.4f}')
        rezultati_log.append(f'α = {alfa:.4f}')
        rezultati_log.append(f'ω_d_prov = {omega_d_prov:.4f}')
        rezultati_log.append(f'α_ω_d_req = {alfa_omegad_req:.4f}')
        rezultati_log.append(f'ω_d_req = {alfa_omegad_req / alfa:.4f}')

        if lc_req >= self.h_0:
            rezultati_log.append("\n>>> Potrebno je smanjiti stepen utezanja kraja zida ili produžiti ivični element!")
        else:
            rezultati_log.append('\n>>> Dovoljno utegnut kraj zida!')

        return "\n".join(rezultati_log)


class RezultatiWindow(QDialog):
    """ Poseban prozor za prikaz rezultata proračuna """

    def __init__(self, tekst_rezultata):
        super().__init__()
        self.setWindowTitle("Izveštaj o proračunu - Utezanje zida")
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
        self.setWindowTitle("Utezanje zida")
        self.resize(1300, 700)

        main_layout = QVBoxLayout()

        # Layout za naslov
        self.naslov_layout = QHBoxLayout()
        self.naslov_label = QLabel('Utezanje zida')
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

        self.naziv_zida_input = QLineEdit("Z1")
        self.NEd_input = QLineEdit("")
        self.b_input = QLineEdit("")
        self.h_input = QLineEdit("")
        self.fck_input = QLineEdit("")
        self.q0_input = QLineEdit("")
        self.h0_input = QLineEdit("")
        self.obim_uzengija_input = QLineEdit("")
        self.s_input = QLineEdit("10.0")

        # Dropdown za izbor tipa armature
        self.tip_armature_combo = QComboBox()
        self.tip_armature_combo.addItems(["B500B", "B500C"])

        # Dropdown za izbor prečnika uzengija
        self.precnik_combo = QComboBox()
        self.precnik_combo.addItems(["φ 8", "φ 10", "φ 12", "φ 14"])

        self.T_input = QLineEdit("")
        self.MEd_input = QLineEdit("1")
        self.MRd_input = QLineEdit("1")
        self.Hs_input = QLineEdit("3.0")

        self.ulazni_podaci_layout.addRow("Naziv platna/zida:", self.naziv_zida_input)
        self.ulazni_podaci_layout.addRow("Normalna sila NEd [kN]:", self.NEd_input)
        self.ulazni_podaci_layout.addRow("Debljina zida b [cm]:", self.b_input)
        self.ulazni_podaci_layout.addRow("Dužina preseka zida h [cm]:", self.h_input)
        self.ulazni_podaci_layout.addRow("Marka betona fck [MPa]:", self.fck_input)
        self.ulazni_podaci_layout.addRow("Faktor ponašanja q0:", self.q0_input)
        self.ulazni_podaci_layout.addRow("Dužina utegnutog elementa h0 [cm]:", self.h0_input)
        self.ulazni_podaci_layout.addRow("Obim uzengija za pridržavanje [cm]:", self.obim_uzengija_input)
        self.ulazni_podaci_layout.addRow("Vertikalni razmak uzengija s [cm]:", self.s_input)
        self.ulazni_podaci_layout.addRow("Tip armature:", self.tip_armature_combo)
        self.ulazni_podaci_layout.addRow("Prečnik uzengije (φ):", self.precnik_combo)
        self.ulazni_podaci_layout.addRow("Period T [s]:", self.T_input)
        self.ulazni_podaci_layout.addRow("Seizmički moment MEd [kNm]:", self.MEd_input)
        self.ulazni_podaci_layout.addRow("Moment nosivosti MRd [kNm]:", self.MRd_input)
        self.ulazni_podaci_layout.addRow("Čista spratna visina Hs [m]:", self.Hs_input)

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

        putanja_slike = os.path.join("Graphics", "wall_bracing.png")
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
                'naziv_zida': self.naziv_zida_input.text(),
                'NEd': float(self.NEd_input.text()),
                'b': float(self.b_input.text()),
                'h': float(self.h_input.text()),
                'fck': float(self.fck_input.text()),
                'q0': float(self.q0_input.text()),
                'h0': float(self.h0_input.text()),
                'obim_uzengija': float(self.obim_uzengija_input.text()),
                's': float(self.s_input.text()),
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

            proracun = UtezanjeZida(params, bi_niz)
            rezultat = proracun.Utezanje()

            self.rezultat_vrednost_label.setText(
                "Proračun uspešno završen. Pogledajte otvoreni prozor sa rezultatima.")

            self.rezultati_prozor = RezultatiWindow(rezultat)
            self.rezultati_prozor.show()

        except ValueError as e:
            QMessageBox.critical(self, "Greška u podacima", f"Došlo je do greške:\n{str(e)}")
        except Exception as ex:
            QMessageBox.critical(self, "Greška", f"Neočekivana greška:\n{str(ex)}")
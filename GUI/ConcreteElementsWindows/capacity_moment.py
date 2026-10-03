import math
import os.path
import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLabel, QLineEdit, QPushButton,
                             QComboBox, QMessageBox)


class NosivostModel:
    def __init__(self, hfl_str, beff_val, bw_val, b_val, As1_val, As2_val, fck_val, d_val, d1_val, Ned_val, d2_val=0.0):
        self.hfl_str = hfl_str.strip().lower()
        self.beff = float(beff_val) / 100.0 if beff_val else 0.0
        self.bw = float(bw_val) / 100.0 if bw_val else 0.0
        self.b = float(b_val) / 100.0 if b_val else 0.0
        self.As1 = float(As1_val) * math.pow(10, -4)
        self.As2 = float(As2_val) * math.pow(10, -4) if As2_val else 0.0
        self.fck_MPA = int(fck_val)
        self.d = float(d_val) / 100.0
        self.d1 = float(d1_val) / 100.0
        self.h = self.d + self.d1
        self.Ned = float(Ned_val)
        self.d2 = float(d2_val) / 100.0 if d2_val else 0.0

        # Učitavanje materijalnih karakteristika iz CSV fajla
        beton_csv_fajl = "BetonPodaci.csv"

        if beton_csv_fajl not in os.listdir('MaterialData'):
            raise FileNotFoundError(f'{beton_csv_fajl} se ne nalazi u folderu MaterialData!')

        df = pd.read_csv(os.path.join("MaterialData", "BetonPodaci.csv"), encoding='UTF-8', delimiter=';',
                         skipinitialspace=True)
        fck_lista = df['fck [Mpa]'].to_list()

        if self.fck_MPA in fck_lista:
            self.fcd = 0.85 * self.fck_MPA / 1.5
            self.fyd = 500 / 1.15
            self.Es = 200
            self.eslim = self.fyd / self.Es
        else:
            raise ValueError(f'{self.fck_MPA} nije standardna karakteristična čvrstoća betona na pritisak!')

        if self.hfl_str != 'pravougaoni':
            self.hfl = float(hfl_str) / 100.0
            self.b = self.bw
        else:
            self.hfl = math.pow(10, 10)
            self.bw = self.b

    @staticmethod
    def beta2_koeficijent(epsilon_c2):
        epsilon_c2 = epsilon_c2 * 1000
        if 2.0 <= epsilon_c2 <= 3.5:
            beta2 = (epsilon_c2 * (3 * epsilon_c2 - 4) + 2) / (2 * epsilon_c2 * (3 * epsilon_c2 - 2))
        elif 0 <= epsilon_c2 < 2.0:
            beta2 = (8 - epsilon_c2) / (4 * (6 - epsilon_c2))
        else:
            beta2 = None
        return beta2

    def tpresek(self):
        iks = 0.001
        ec = 3.5
        ecf = ec * (iks - self.hfl) / iks
        beta11 = (3 * 3.5 - 2) / (3 * ec)
        es1 = ec / iks * self.d - ec
        sigmas1 = self.fyd if es1 > 2.5 else self.Es * es1

        if ecf <= 2:
            beta12 = (ec * (6 - ec)) / 12
        elif 2 < ecf <= 3.5:
            beta12 = (3 * ecf - 2) / (3 * ecf)
        else:
            beta12 = 0

        Fs1 = self.As1 * sigmas1 * math.pow(10, 3)
        Fc1 = beta11 * iks * self.fcd * self.beff * math.pow(10, 3)
        Fc2 = beta12 * (iks - self.hfl) * self.fcd * math.pow(10, 3) * (self.beff - self.bw)
        deltaN = Fc1 - Fc2 - Fs1 - self.Ned

        while abs(deltaN) > 1:
            ec = 3.5
            ecf = ec * (iks - self.hfl) / iks
            beta11 = (3 * 3.5 - 2) / (3 * ec)
            es1 = ec / iks * self.d - ec
            sigmas1 = self.fyd if es1 > 2.5 else self.Es * es1

            if ecf <= 2:
                beta12 = (ec * (6 - ec)) / 12
            elif 2 < ecf <= 3.5:
                beta12 = (3 * ecf - 2) / (3 * ecf)

            Fs1 = self.As1 * sigmas1 * math.pow(10, 3)
            Fc1 = beta11 * iks * self.fcd * self.beff * math.pow(10, 3)
            Fc2 = beta12 * (iks - self.hfl) * self.fcd * math.pow(10, 3) * (self.beff - self.bw)
            deltaN = Fc1 - Fc2 - Fs1 - self.Ned
            iks = iks + 0.0005

        beta21 = 0.416
        if ecf < 2:
            beta22 = (8 - ecf) / (4 * (6 - ecf))
        elif 2 <= ecf <= 3.5:
            beta22 = (ecf * (3 * ecf - 4) + 2) / (2 * ecf * (3 * ecf - 2))
        else:
            raise ValueError('Dilatacija u betonu u nivou donje ivice flanše nije između 0 i 3.5‰!')

        MRds = Fc1 * (self.d - beta21 * iks) - Fc2 * (self.d - self.hfl - beta22 * (iks - self.hfl))
        MEd = MRds - self.Ned * (self.h / 2 - self.d1)
        return MEd, abs(deltaN), "T-presek"

    def nosivost(self):
        if self.As2 == 0:
            d2 = 0
            Fs2 = 0
            ksi = (self.As1 * self.fyd * math.pow(10, 3) + self.Ned) / (
                    self.b * self.d * self.fcd * math.pow(10, 3)) / 0.81
            iks = ksi * self.d
            es1 = (1 - ksi) / ksi * 3.5

            if iks > self.hfl:
                return self.tpresek()

            delta = 0
            if es1 < 2.5:
                ksi = 3.5 / (3.5 + es1)
                if ksi > 0.583:
                    ksi = 2
                    Fs1 = self.As1 * self.fyd * math.pow(10, 3)
                    Fc = 0.81 * ksi * self.b * self.d * self.fcd * math.pow(10, 3)
                    delta = abs(Fc + Fs2 - Fs1 - self.Ned)
                    ksi2 = 0.0001
                    while abs(delta) > 0.5:
                        x = ksi * self.d
                        es1 = (1 - ksi) / ksi * 3.5
                        if es1 > 2.5:
                            es1 = 2.5
                        Fc = 0.81 * x * self.b * self.fcd * math.pow(10, 3)
                        Fs1 = self.As1 * es1 / 2.5 * self.fyd * math.pow(10, 3)
                        epsilons2 = ((ksi - d2 / self.d) / ksi) * 3.5
                        Fs2 = self.As2 * epsilons2 * self.Es * math.pow(10, 3)
                        ksi = ksi - ksi2
                        delta = abs(Fc + Fs2 - Fs1 - self.Ned)

            MRds = 0.81 * ksi * (1 - 0.416 * ksi) * self.b * math.pow(self.d, 2) * self.fcd * math.pow(10, 3)
            MRd = MRds - self.Ned * (self.h / 2 - self.d1)
            return MRd, delta, "Pravougaoni presek (As2 = 0)"

        else:
            d2 = self.d2
            d1 = self.d1

            # Početna procena ksi na osnovu opterećenja i armature
            ksi = (self.As1 * self.fyd * math.pow(10, 3) + self.Ned - self.As2 * self.fyd * math.pow(10, 3)) / (
                    self.b * self.d * self.fcd * math.pow(10, 3)) / 0.81
            if ksi < 0.1:
                ksi = 0.3
            elif ksi > 2.0:
                ksi = 1.2

            ksi2 = 0.0005
            max_iter = 10000
            iteracija = 0

            def izracunaj_sile_i_razliku(k_val):
                x = k_val * self.d
                Fc = 0.81 * x * self.b * self.fcd * math.pow(10, 3)

                # Gornja armatura (As2) - uvek u pritisku
                epsilons2 = ((k_val - d2 / self.d) / k_val) * 3.5
                if epsilons2 > 2.175:
                    epsilons2 = 2.175
                Fs2 = self.As2 * epsilons2 * self.Es * math.pow(10, 3)

                # Donja armatura (As1) - proveravamo da li je u zatezanju ili pritisku
                if x >= self.d:  # Neutralna linija ispod ili na nivou donje armature -> pritisak
                    eps_s1_pritisak = ((k_val - 1.0) / k_val) * 3.5
                    if eps_s1_pritisak > 2.175:
                        eps_s1_pritisak = 2.175
                    Fs1_eff = self.As1 * eps_s1_pritisak * self.Es * math.pow(10, 3)  # Doprinosi pritisku (+)
                    nacin = "pritisak"
                else:  # Zatezanje (-)
                    es1 = ((1.0 - k_val) / k_val) * 3.5
                    sigmas1 = self.fyd if es1 > 2.5 else self.Es * es1
                    Fs1_eff = - self.As1 * sigmas1 * math.pow(10, 3)  # Oduzima se (-)
                    nacin = "zatezanje"

                # Ravnoteža: Fc + Fs2 + Fs1_eff - Ned = 0
                delta_N = Fc + Fs2 + Fs1_eff - self.Ned
                return delta_N, Fc, Fs2, Fs1_eff, nacin

            delta_N, Fc, Fs2, Fs1_eff, nacin = izracunaj_sile_i_razliku(ksi)
            delta = abs(delta_N)

            while delta >= 0.5 and iteracija < max_iter:
                if delta_N > 0:
                    # Previše sile pritiska u preseku -> smanjujemo ksi
                    ksi -= ksi2
                else:
                    # Premalo sile pritiska -> povećavamo ksi
                    ksi += ksi2

                if ksi <= 0.01:
                    ksi = 0.01
                    break
                if ksi > 3.0:
                    ksi = 3.0
                    break

                delta_N, Fc, Fs2, Fs1_eff, nacin = izracunaj_sile_i_razliku(ksi)
                delta = abs(delta_N)
                iteracija += 1

            ceta = 1 - 0.416 * ksi
            moment_as1 = Fs1_eff * (self.d - d1) if nacin == "pritisak" else 0
            MRds = Fc * ceta * self.d + Fs2 * (self.d - d2) + moment_as1
            MEd = MRds - self.Ned * (self.h / 2 - self.d1)
            return MEd, delta, "Pravougaoni presek sa obostranom armaturom"


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proračun momenta nosivosti preseka")
        self.resize(700, 650)

        main_layout = QVBoxLayout()

        # Naslov
        self.naslov_layout = QHBoxLayout()
        self.naslov_label = QLabel('Proračun momenta nosivosti')
        self.naslov_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.naslov_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.naslov_layout.addWidget(self.naslov_label)
        main_layout.addLayout(self.naslov_layout)

        # Forma za unos
        self.form_layout = QFormLayout()

        # Izbor tipa preseka
        self.tip_presek_combo = QComboBox()
        self.tip_presek_combo.addItems(["Pravougaoni presek", "T-presek"])
        self.tip_presek_combo.currentIndexChanged.connect(self.promeni_tip_preseka)

        # Polja za unos
        self.fck_input = QLineEdit()
        self.Ned_input = QLineEdit()
        self.b_input = QLineEdit()
        self.d_input = QLineEdit()
        self.d1_input = QLineEdit()
        self.As1_input = QLineEdit()
        self.As2_input = QLineEdit()
        self.d2_input = QLineEdit()

        # Specifična polja za T-presek
        self.hfl_input = QLineEdit()
        self.beff_input = QLineEdit()
        self.bw_input = QLineEdit()

        # Tooltipovi
        self.fck_help = QLabel("❓")
        self.fck_help.setToolTip("Karakteristična čvrstoća betona na pritisak u [MPa].")

        self.Ned_help = QLabel("❓")
        self.Ned_help.setToolTip("Aksijalna sila (pritisak je +) u [kN].")

        def wrap_field(widget, help_widget):
            lay = QHBoxLayout()
            lay.addWidget(widget)
            lay.addWidget(help_widget)
            return lay

        self.form_layout.addRow(QLabel("Tip preseka:"), self.tip_presek_combo)
        self.form_layout.addRow(QLabel("fck [MPa]:"), wrap_field(self.fck_input, self.fck_help))
        self.form_layout.addRow(QLabel("Ned [kN]:"), wrap_field(self.Ned_input, self.Ned_help))

        self.row_b = QLabel("Širina preseka b [cm]:")
        self.row_As2 = QLabel("Pritisnuta armatura As2 [cm²]:")
        self.row_d2 = QLabel("Rastojanje d2 [cm]:")

        self.form_layout.addRow(self.row_b, self.b_input)
        self.form_layout.addRow(QLabel("Statička visina d [cm]:"), self.d_input)
        self.form_layout.addRow(QLabel("Rastojanje d1 [cm]:"), self.d1_input)
        self.form_layout.addRow(QLabel("Zategnuta armatura As1 [cm²]:"), self.As1_input)
        self.form_layout.addRow(self.row_As2, self.As2_input)
        self.form_layout.addRow(self.row_d2, self.d2_input)

        self.row_hfl = QLabel("Visina flanse hf [cm]:")
        self.row_beff = QLabel("Efektivna širina beff [cm]:")
        self.row_bw = QLabel("Širina rebra bw [cm]:")

        self.form_layout.addRow(self.row_hfl, self.hfl_input)
        self.form_layout.addRow(self.row_beff, self.beff_input)
        self.form_layout.addRow(self.row_bw, self.bw_input)

        self.prikazi_t_presek_polja(False)

        self.calc_button = QPushButton("Izračunaj moment nosivosti")
        self.calc_button.clicked.connect(self.pokreni_proracun_nosivosti)
        self.form_layout.addRow(self.calc_button)

        main_layout.addLayout(self.form_layout)
        self.setLayout(main_layout)

    def prikazi_t_presek_polja(self, prikaz):
        self.row_hfl.setVisible(prikaz)
        self.hfl_input.setVisible(prikaz)
        self.row_beff.setVisible(prikaz)
        self.beff_input.setVisible(prikaz)
        self.row_bw.setVisible(prikaz)
        self.bw_input.setVisible(prikaz)

        self.row_As2.setVisible(not prikaz)
        self.As2_input.setVisible(not prikaz)
        self.row_d2.setVisible(not prikaz)
        self.d2_input.setVisible(not prikaz)

        if prikaz:
            self.row_b.setText("Širina rebra bw / b [cm]:")
        else:
            self.row_b.setText("Širina preseka b [cm]:")

    def promeni_tip_preseka(self, index):
        if index == 0:
            self.prikazi_t_presek_polja(False)
        else:
            self.prikazi_t_presek_polja(True)

    def pokreni_proracun_nosivosti(self):
        try:
            fck = self.fck_input.text()
            Ned = self.Ned_input.text()
            d = self.d_input.text()
            d1 = self.d1_input.text()
            As1 = self.As1_input.text()

            if self.tip_presek_combo.currentIndex() == 0:
                hfl_str = "pravougaoni"
                b = self.b_input.text()
                beff = "0"
                bw = "0"
                As2 = self.As2_input.text() if self.As2_input.text() else "0"
                d2 = self.d2_input.text() if self.d2_input.text() else "0"
            else:
                hfl_str = self.hfl_input.text()
                b = self.bw_input.text()
                beff = self.beff_input.text()
                bw = self.bw_input.text()
                As2 = "0"
                d2 = "0"

            model = NosivostModel(hfl_str, beff, bw, b, As1, As2, fck, d, d1, Ned, float(d2))
            mrd, greska, tip = model.nosivost()

            rezultat_tekst = (
                f"<b>Tip proračuna:</b> {tip}<br>"
                f"<b>Moment nosivosti (MRd):</b> {mrd:.2f} kNm<br>"
                f"<b>Greška ravnoteže sila:</b> {greska:.4f} kN"
            )

            QMessageBox.information(self, "Rezultat proračuna", rezultat_tekst)

        except Exception as e:
            QMessageBox.critical(self, "Greška", f"Došlo je do greške tokom proračuna:\n{str(e)}")
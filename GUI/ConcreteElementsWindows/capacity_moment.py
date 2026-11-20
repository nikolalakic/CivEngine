import math
import os.path
import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLabel, QLineEdit, QPushButton,
                             QComboBox, QMessageBox)
from GUI.ConcreteElementsWindows.report_buttons import ReportButtons


class NosivostModel:
    def __init__(self, hfl_str, beff_val, bw_val, b_val, As1_val, As2_val, fck_val, h_val, d1_val, Ned_val, d2_val=0.0):
        self.hfl_str = hfl_str.strip().lower()
        self.beff = float(beff_val) / 100.0 if beff_val else 0.0
        self.bw = float(bw_val) / 100.0 if bw_val else 0.0
        self.b = float(b_val) / 100.0 if b_val else 0.0
        self.As1 = float(As1_val) * math.pow(10, -4)
        self.As2 = float(As2_val) * math.pow(10, -4) if As2_val else 0.0
        self.fck_MPA = int(fck_val)
        self.h = float(h_val) / 100.0
        self.d1 = float(d1_val) / 100.0
        self.d = self.h - self.d1
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

    def napon_armature(self, es):
        """Bilinearni dijagram čelika: sigma = Es * eps, ograničeno na +/- fyd [MPa] (eps u promilima)."""
        return max(-self.fyd, min(self.fyd, self.Es * es))

    def stanje_t_preseka(self, iks):
        """Sile u T-preseku za položaj neutralne linije iks [m] u rebru (iks >= hfl)."""
        ec = 3.5
        ecf = ec * (iks - self.hfl) / iks
        beta11 = (3 * ec - 2) / (3 * ec)
        es1 = ec / iks * self.d - ec
        sigmas1 = self.napon_armature(es1)

        # Koeficijent punoće dela pritisnute zone ispod flanše (širine beff - bw),
        # zavisi od dilatacije u nivou donje ivice flanše ecf
        if ecf <= 2:
            beta12 = ecf * (6 - ecf) / 12
        else:
            beta12 = (3 * ecf - 2) / (3 * ecf)

        Fs1 = self.As1 * sigmas1 * math.pow(10, 3)
        Fc1 = beta11 * iks * self.fcd * self.beff * math.pow(10, 3)
        Fc2 = beta12 * (iks - self.hfl) * self.fcd * math.pow(10, 3) * (self.beff - self.bw)
        deltaN = Fc1 - Fc2 - Fs1 - self.Ned
        return dict(iks=iks, ec=ec, ecf=ecf, beta11=beta11, beta12=beta12, es1=es1,
                    sigmas1=sigmas1, Fs1=Fs1, Fc1=Fc1, Fc2=Fc2, deltaN=deltaN)

    def tpresek(self):
        """T-presek sa neutralnom linijom u rebru: ravnoteža se traži polovljenjem intervala
        hfl <= x <= h (deltaN raste sa x), do tačnosti |deltaN| <= 1 kN."""
        tolerancija = 1.0
        x_min, x_max = self.hfl, self.h
        st_max = self.stanje_t_preseka(x_max)
        if st_max['deltaN'] < 0:
            raise ValueError('T-presek ne može da prihvati zadatu aksijalnu silu '
                             '(ravnoteža nije moguća ni za x = h)!')
        st = self.stanje_t_preseka(x_min)
        iteracija = 0
        while abs(st['deltaN']) > tolerancija and iteracija < 200:
            x_sr = (x_min + x_max) / 2
            st = self.stanje_t_preseka(x_sr)
            if st['deltaN'] > 0:
                x_max = x_sr
            else:
                x_min = x_sr
            iteracija += 1

        iks, ecf = st['iks'], st['ecf']
        beta21 = 0.416
        if ecf < 2:
            beta22 = (8 - ecf) / (4 * (6 - ecf))
        elif 2 <= ecf <= 3.5:
            beta22 = (ecf * (3 * ecf - 4) + 2) / (2 * ecf * (3 * ecf - 2))
        else:
            raise ValueError('Dilatacija u betonu u nivou donje ivice flanše nije između 0 i 3.5‰!')

        MRds = st['Fc1'] * (self.d - beta21 * iks) - st['Fc2'] * (self.d - self.hfl - beta22 * (iks - self.hfl))
        MEd = MRds - self.Ned * (self.h / 2 - self.d1)
        self.detalji.update(putanja='T', beta21=beta21, beta22=beta22, MRds=MRds, MRd=MEd,
                            iteracija=iteracija, **st)
        return MEd, abs(st['deltaN']), "T-presek"

    def nosivost(self):
        # Međurezultati proračuna (koristi ih generator izveštaja)
        self.detalji = {}
        if self.As2 == 0:
            d2 = 0
            Fs2 = 0
            b = self.b
            if self.hfl_str != 'pravougaoni':
                # Neutralna linija je u flanši ako je pri x = hfl pritisak u flanši
                # (širine beff) dovoljan za ravnotežu, tj. deltaN(x = hfl) >= 0.
                st_hf = self.stanje_t_preseka(self.hfl)
                u_flansi = st_hf['deltaN'] >= 0
                self.detalji.update(st_hf=st_hf, u_flansi=u_flansi)
                if not u_flansi:
                    return self.tpresek()
                b = self.beff  # pravougaoni presek širine beff
            self.detalji.update(b_proracun=b)

            ksi = (self.As1 * self.fyd * math.pow(10, 3) + self.Ned) / (
                    b * self.d * self.fcd * math.pow(10, 3)) / 0.81
            iks = ksi * self.d
            es1 = (1 - ksi) / ksi * 3.5
            self.detalji.update(ksi0=ksi, iks0=iks, es1_0=es1)

            delta = 0
            if es1 < 2.5:
                ksi = 3.5 / (3.5 + es1)
                if ksi > 0.583:
                    ksi = 2
                    Fs1 = self.As1 * self.fyd * math.pow(10, 3)
                    Fc = 0.81 * ksi * b * self.d * self.fcd * math.pow(10, 3)
                    delta = abs(Fc + Fs2 - Fs1 - self.Ned)
                    ksi2 = 0.0001
                    while abs(delta) > 0.5 and ksi > 2 * ksi2:
                        x = ksi * self.d
                        es1 = (1 - ksi) / ksi * 3.5
                        if es1 > 2.5:
                            es1 = 2.5
                        Fc = 0.81 * x * b * self.fcd * math.pow(10, 3)
                        Fs1 = self.As1 * es1 / 2.5 * self.fyd * math.pow(10, 3)
                        epsilons2 = ((ksi - d2 / self.d) / ksi) * 3.5
                        Fs2 = self.As2 * epsilons2 * self.Es * math.pow(10, 3)
                        ksi = ksi - ksi2
                        delta = abs(Fc + Fs2 - Fs1 - self.Ned)

            MRds = 0.81 * ksi * (1 - 0.416 * ksi) * b * math.pow(self.d, 2) * self.fcd * math.pow(10, 3)
            MRd = MRds - self.Ned * (self.h / 2 - self.d1)
            self.detalji.update(putanja='As1', ksi=ksi, es1=es1, delta=delta, MRds=MRds, MRd=MRd)
            if self.hfl_str != 'pravougaoni':
                return MRd, delta, "T-presek (neutralna linija u flanši)"
            return MRd, delta, "Pravougaoni presek (As2 = 0)"

        else:
            d2 = self.d2
            tolerancija = 0.5

            def izracunaj_sile_i_razliku(k_val):
                x = k_val * self.d
                Fc = 0.81 * x * self.b * self.fcd * math.pow(10, 3)

                # Gornja armatura (As2): pritisnuta za x > d2, zategnuta za x < d2;
                # dilatacija se ograničava na granicu tečenja u oba smera
                epsilons2 = ((k_val - d2 / self.d) / k_val) * 3.5
                epsilons2 = max(-2.175, min(2.175, epsilons2))
                Fs2 = self.As2 * epsilons2 * self.Es * math.pow(10, 3)

                # Donja armatura (As1) - proveravamo da li je u zatezanju ili pritisku
                if x >= self.d:  # Neutralna linija ispod ili na nivou donje armature -> pritisak
                    es1 = ((k_val - 1.0) / k_val) * 3.5
                    if es1 > 2.175:
                        es1 = 2.175
                    Fs1_eff = self.As1 * es1 * self.Es * math.pow(10, 3)  # Doprinosi pritisku (+)
                    nacin = "pritisak"
                else:  # Zatezanje (-)
                    es1 = ((1.0 - k_val) / k_val) * 3.5
                    sigmas1 = self.napon_armature(es1)
                    Fs1_eff = - self.As1 * sigmas1 * math.pow(10, 3)  # Oduzima se (-)
                    nacin = "zatezanje"

                # Ravnoteža: Fc + Fs2 + Fs1_eff - Ned = 0 (deltaN raste sa ksi)
                delta_N = Fc + Fs2 + Fs1_eff - self.Ned
                return dict(delta_N=delta_N, Fc=Fc, Fs2=Fs2, Fs1_eff=Fs1_eff, nacin=nacin,
                            epsilons2=epsilons2, es1=es1, x=x)

            # Polovljenje intervala 0.01 <= ksi <= 3.0
            ksi_min, ksi_max = 0.01, 3.0
            st_min = izracunaj_sile_i_razliku(ksi_min)
            st_max = izracunaj_sile_i_razliku(ksi_max)
            iteracija = 0
            if st_min['delta_N'] >= 0:
                ksi, st, granica = ksi_min, st_min, 'donja'
            elif st_max['delta_N'] <= 0:
                ksi, st, granica = ksi_max, st_max, 'gornja'
            else:
                granica = None
                ksi = (ksi_min + ksi_max) / 2
                st = izracunaj_sile_i_razliku(ksi)
                while abs(st['delta_N']) >= tolerancija and iteracija < 200:
                    if st['delta_N'] > 0:
                        ksi_max = ksi
                    else:
                        ksi_min = ksi
                    ksi = (ksi_min + ksi_max) / 2
                    st = izracunaj_sile_i_razliku(ksi)
                    iteracija += 1

            Fc, Fs2, Fs1_eff, nacin = st['Fc'], st['Fs2'], st['Fs1_eff'], st['nacin']
            delta = abs(st['delta_N'])
            ceta = 1 - 0.416 * ksi
            # Momenti se računaju oko težišta armature As1, pa ona ne daje doprinos
            MRds = Fc * ceta * self.d + Fs2 * (self.d - d2)
            MEd = MRds - self.Ned * (self.h / 2 - self.d1)
            self.detalji.update(putanja='As1As2', ksi=ksi, iteracija=iteracija, Fc=Fc, Fs2=Fs2,
                                Fs1_eff=Fs1_eff, nacin=nacin, ceta=ceta, granica=granica,
                                epsilons2=st['epsilons2'], es1=st['es1'], x=st['x'],
                                delta=delta, MRds=MRds, MRd=MEd)
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
        self.h_input = QLineEdit()
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
        self.form_layout.addRow(QLabel("Visina poprečnog preseka h [cm]:"), self.h_input)
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

        self.izvestaj_dugmici = ReportButtons(self.napravi_izvestaj, 'Moment_nosivosti')
        self.form_layout.addRow(self.izvestaj_dugmici)

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

    def procitaj_ulaz(self):
        """Argumenti za NosivostModel iz polja za unos."""
        fck = self.fck_input.text()
        Ned = self.Ned_input.text()
        h = self.h_input.text()
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
        return hfl_str, beff, bw, b, As1, As2, fck, h, d1, Ned, float(d2)

    def napravi_izvestaj(self):
        from LatexScripts.CapacityMoment_tex import CapacityMomentTex
        return CapacityMomentTex(*self.procitaj_ulaz())

    def pokreni_proracun_nosivosti(self):
        try:
            model = NosivostModel(*self.procitaj_ulaz())
            mrd, greska, tip = model.nosivost()

            rezultat_tekst = (
                f"<b>Tip proračuna:</b> {tip}<br>"
                f"<b>Moment nosivosti (MRd):</b> {mrd:.2f} kNm<br>"
                f"<b>Greška ravnoteže sila:</b> {greska:.4f} kN"
            )

            QMessageBox.information(self, "Rezultat proračuna", rezultat_tekst)

        except Exception as e:
            QMessageBox.critical(self, "Greška", f"Došlo je do greške tokom proračuna:\n{str(e)}")
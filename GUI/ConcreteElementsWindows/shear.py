"""Dimenzionisanje poprečne armature (uzengija) za smicanje, EN 1992-1-1, 6.2.

Proračun je prenet iz skripte Scripts/Smicanje.py: θ = 45°, vertikalne uzengije
(α = 90°), prečnici uzengija φ8, φ10 i φ12.
"""
import math
import os

import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QDialog, QTextEdit)

from GUI.ConcreteElementsWindows.section_drawings import ShearDrawing
from GUI.ConcreteElementsWindows.report_buttons import ReportButtons


class Smicanje:
    """Ulaz: VEd [kN], b, h, d1 [cm], fck [MPa], Asl [cm²], m (sečnost uzengija)."""

    PRECNICI = (8, 10, 12)

    def __init__(self, VEd, b, h, d1, fck, Asl, m):
        self.VEd = abs(float(VEd))
        self.b = float(b) / 100
        self.h = float(h) / 100
        self.d1 = float(d1) / 100
        self.d = self.h - self.d1
        self.fck = int(fck)
        self.Asl = float(Asl) / 1e4          # [m²]
        self.m = float(m)

        df = pd.read_csv(os.path.join('MaterialData', 'BetonPodaci.csv'), delimiter=';',
                         encoding='UTF-8', skipinitialspace=True)
        if self.fck not in df['fck [Mpa]'].to_list():
            raise ValueError(f'{self.fck} nije standardna karakteristična čvrstoća betona!')
        fi = df['fi [mm]'].dropna().to_list()
        A = df['A [cm2]'].dropna().to_list()
        # Površine jedne šipke iz tabele (kao u skripti) [m²]
        self.Asw1 = {f: A[fi.index(f)] / 1e4 for f in self.PRECNICI}

        self.gama_c = 1.5
        self.fcd = 0.85 * self.fck / self.gama_c   # [MPa]
        self.fyk = 500
        self.fyd = self.fyk / 1.15                 # [MPa] (= fywd)
        self.cot_teta = 1.0                        # θ = 45°
        self.cot_alfa = 0.0                        # α = 90°
        self.z = 0.9 * self.d

    # --- nosivosti -------------------------------------------------------
    def VRd_c(self):
        """Nosivost elementa bez računske armature za smicanje, 6.2.2(1)."""
        d_mm = self.d * 1000
        self.k = min(1 + math.sqrt(200 / d_mm), 2.0)
        self.rho_l = min(self.Asl / (self.b * self.d), 0.02)
        self.CRd_c = 0.18 / self.gama_c
        self.VRd_c1 = self.CRd_c * self.k * (100 * self.rho_l * self.fck) ** (1 / 3) * self.b * self.d * 1000
        self.v_min = 0.035 * self.k ** 1.5 * self.fck ** 0.5
        self.VRd_c_min = self.v_min * self.b * self.d * 1000
        return max(self.VRd_c1, self.VRd_c_min)

    def VRd_max(self):
        """Nosivost pritisnutih betonskih dijagonala, izraz (6.9), αcw = 1, ν1 = ν."""
        self.ni_1 = 0.6 * (1 - self.fck / 250)
        return self.b * self.z * self.ni_1 * self.fcd * self.cot_teta / (1 + self.cot_teta ** 2) * 1000

    # --- rastojanja --------------------------------------------------------
    def s_rac(self, Asw1):
        """Rastojanje računske armature, izraz (6.8) [m]."""
        return self.m * Asw1 / self.VEd * self.z * self.fyd * 1000 * self.cot_teta if self.VEd > 0 else math.inf

    def s_min_armatura(self, Asw1):
        """Najveće rastojanje za minimalni procenat ρw,min = 0.08 √fck / fyk, (9.4) i (9.5N) [m]."""
        self.rho_w_min = 0.08 * math.sqrt(self.fck) / self.fyk
        return self.m * Asw1 / (self.rho_w_min * self.b)

    def sl_max(self, VRd_max):
        """Najveće podužno rastojanje uzengija [m] (kao u skripti)."""
        gornja = 0.3 if self.fck <= 50 else 0.2
        if self.VEd <= 0.3 * VRd_max:
            return min(0.75 * self.d, gornja)
        if self.VEd <= 0.6 * VRd_max:
            return min(0.55 * self.d, gornja)
        return min(0.3 * self.d, 0.2)

    def st_max(self, VRd_max):
        """Najveće poprečno rastojanje krakova uzengija [m] (kao u skripti)."""
        gornja = 0.6 if self.fck <= 50 else 0.4
        if self.VEd <= 0.6 * VRd_max:
            return min(0.75 * self.d, gornja)
        return min(0.3 * self.d, 0.3)

    def proracun(self):
        VRd_c = self.VRd_c()
        VRd_max = self.VRd_max()
        r = dict(VRd_c=VRd_c, VRd_max=VRd_max)
        poruke = []
        p = poruke.append

        if self.VEd > VRd_max:
            r['slucaj'] = 'prekoracenje'
            p('Prekoračena maksimalna nosivost pritisnute betonske dijagonale na smicanje!')
            p(f'VEd = {self.VEd:.2f} kN > VRd,max = {VRd_max:.2f} kN')
            p('Potrebno je povećati presek ili marku betona.')
            r['poruke'] = poruke
            return r

        r['slucaj'] = 'racunska' if self.VEd > VRd_c else 'minimalna'
        sl_max = self.sl_max(VRd_max)
        st_max = self.st_max(VRd_max)
        delta_Ftd = 0.5 * self.VEd * (self.cot_teta - self.cot_alfa)    # (6.18)
        delta_As1 = delta_Ftd / (self.fyd * 1000)                        # [m²]
        r.update(sl_max=sl_max, st_max=st_max, delta_Ftd=delta_Ftd, delta_As1=delta_As1)

        p(f'VRd,c = {VRd_c:.2f} kN,  VRd,max = {VRd_max:.2f} kN,  VEd = {self.VEd:.2f} kN')
        if r['slucaj'] == 'minimalna':
            p('VEd ≤ VRd,c: računska armatura nije potrebna, usvaja se minimalni procenat armiranja.')
        else:
            p('VRd,c < VEd ≤ VRd,max: potrebna je računska armatura za smicanje.')
        p('')
        p(f'Sečnost uzengija m = {self.m:g}')
        r['uzengije'] = []
        for fi in self.PRECNICI:
            Asw1 = self.Asw1[fi]
            s_rac = self.s_rac(Asw1)
            s_min = self.s_min_armatura(Asw1)
            s = min(s_rac, s_min, sl_max)
            r['uzengije'].append(dict(fi=fi, Asw1=Asw1, s_rac=s_rac, s_min=s_min, s=s))
            p(f'  φ{fi}: s = min({s_rac * 100:.2f}; {s_min * 100:.2f}; {sl_max * 100:.2f}) = {s * 100:.2f} cm')
        p('')
        p(f'Maksimalno podužno rastojanje uzengija: sl,max = {sl_max * 100:.2f} cm')
        p(f'Maksimalno poprečno rastojanje krakova: st,max = {st_max * 100:.2f} cm')
        p(f'Dodatna zategnuta armatura: ΔAs1 = {delta_As1 * 1e4:.2f} cm²  (ΔFtd = {delta_Ftd:.2f} kN)')
        r['poruke'] = poruke
        return r


class RezultatiWindow(QDialog):
    """Poseban prozor za prikaz rezultata proračuna."""

    def __init__(self, tekst, naziv=''):
        super().__init__()
        self.setWindowTitle(f'Rezultati - Smicanje - {naziv}' if naziv else 'Rezultati - Smicanje')
        self.resize(620, 380)
        lay = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(tekst)
        self.text_edit.setStyleSheet('font-family: Consolas, monospace; font-size: 13px;')
        lay.addWidget(self.text_edit)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Smicanje')
        self.resize(900, 600)

        main_layout = QVBoxLayout()
        naslov = QLabel('Dimenzionisanje armature za smicanje')
        naslov.setStyleSheet('font-size: 20px; font-weight: bold;')
        naslov.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(naslov)

        glavni = QHBoxLayout()
        self.forma = QFormLayout()

        self.ime_grede_input = QLineEdit('G1')
        self.VEd_input = QLineEdit()
        self.b_input = QLineEdit()
        self.h_input = QLineEdit()
        self.d1_input = QLineEdit()
        self.fck_input = QLineEdit()
        self.Asl_input = QLineEdit()
        self.m_input = QLineEdit('2')

        polja = [
            ('Ime grede:', self.ime_grede_input, 'Oznaka grede; koristi se u izveštaju i u imenu fajla.'),
            ('VEd [kN]:', self.VEd_input, 'Proračunska sila smicanja (uzima se apsolutna vrednost).'),
            ('b [cm]:', self.b_input, 'Najmanja širina preseka u zategnutoj zoni (bw).'),
            ('h [cm]:', self.h_input, 'Visina preseka.'),
            ('d1 [cm]:', self.d1_input, 'Rastojanje težišta zategnute armature od zategnute ivice.'),
            ('fck [MPa]:', self.fck_input, 'Karakteristična čvrstoća betona (standardna klasa).'),
            ('Asl [cm²]:', self.Asl_input, 'Površina zategnute podužne armature, sidrene iza preseka '
                                           '(za VRd,c, ρl ≤ 2%).'),
            ('m:', self.m_input, 'Sečnost uzengija (broj krakova).'),
        ]
        for tekst, polje, pomoc in polja:
            red = QHBoxLayout()
            red.addWidget(polje)
            upitnik = QLabel('❓')
            upitnik.setToolTip(pomoc)
            red.addWidget(upitnik)
            self.forma.addRow(QLabel(tekst), red)

        self.calc_button = QPushButton('Izračunaj armaturu')
        self.calc_button.clicked.connect(self.pokreni_proracun)
        self.forma.addRow(self.calc_button)

        self.izvestaj_dugmici = ReportButtons(
            self.napravi_izvestaj, lambda: 'Smicanje_' + self.ime_grede())
        self.forma.addRow(self.izvestaj_dugmici)

        self.slika = ShearDrawing(320, 480)
        glavni.addLayout(self.forma)
        glavni.addWidget(self.slika)
        main_layout.addLayout(glavni)
        self.setLayout(main_layout)
        self.rezultati_prozor = None

    def ime_grede(self):
        return self.ime_grede_input.text().strip() or 'G1'

    def procitaj_ulaz(self):
        """Argumenti za Smicanje redom (VEd, b, h, d1, fck, Asl, m)."""
        vrednosti = [float(p.text().replace(',', '.')) for p in (
            self.VEd_input, self.b_input, self.h_input, self.d1_input,
            self.fck_input, self.Asl_input, self.m_input)]
        VEd, b, h, d1, fck, Asl, m = vrednosti
        if min(b, h) <= 0:
            raise ValueError('Dimenzije preseka b i h moraju biti veće od nule.')
        if not 0 < d1 < h:
            raise ValueError('Rastojanje d1 mora biti unutar visine preseka.')
        if Asl < 0:
            raise ValueError('Površina podužne armature Asl ne može biti negativna.')
        if m < 1:
            raise ValueError('Sečnost uzengija m mora biti najmanje 1.')
        return vrednosti

    def napravi_izvestaj(self):
        from LatexScripts.Shear_tex import ShearTex
        return ShearTex(*self.procitaj_ulaz(), naziv=self.ime_grede())

    def pokreni_proracun(self):
        try:
            rezultat = Smicanje(*self.procitaj_ulaz()).proracun()
        except ValueError as e:
            QMessageBox.critical(self, 'Greška u podacima', f'Došlo je do greške:\n{e}')
            return
        except Exception as e:
            QMessageBox.critical(self, 'Greška', f'Neočekivana greška:\n{e}')
            return
        self.rezultati_prozor = RezultatiWindow('\n'.join(rezultat['poruke']), self.ime_grede())
        self.rezultati_prozor.show()

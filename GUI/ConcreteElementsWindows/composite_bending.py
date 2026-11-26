"""Dimenzionisanje preseka za složeno savijanje (moment + aksijalna sila).

Proračun je prenet iz skripte Scripts/SlozenoSavijanje.py, sa istim granama:
centrični pritisak, (eks)centrično zatezanje, veliki ekscentricitet (jednostruko
ili dvojno armiranje) i mali ekscentricitet (simetrična armatura).
"""
import math
import os

import numpy as np
import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QDialog, QTextEdit)

from GUI.ConcreteElementsWindows.section_drawings import CompositeBendingDrawing
from GUI.ConcreteElementsWindows.report_buttons import ReportButtons


class SlozenoSavijanje:
    """Ulaz: MEd [kNm], NEd [kN] (pritisak +), b, b_rebra, h, d1, d2 [cm], fck [MPa]."""

    def __init__(self, MEd, NEd, b, brebra, h, fck, d1, d2):
        self.MEd = abs(float(MEd))
        self.NEd = float(NEd)
        self.b = float(b) / 100
        self.brebra = float(brebra) / 100
        self.h = float(h) / 100
        self.d1 = float(d1) / 100
        self.d2 = float(d2) / 100
        self.d = self.h - self.d1
        self.fck = int(fck)

        df = pd.read_csv(os.path.join('MaterialData', 'BetonPodaci.csv'), delimiter=';',
                         encoding='UTF-8', skipinitialspace=True)
        fck_lista = df['fck [Mpa]'].to_list()
        if self.fck not in fck_lista:
            raise ValueError(f'{self.fck} nije standardna karakteristična čvrstoća betona!')
        self.fctm = float(df['fctm [Mpa]'].to_numpy()[fck_lista.index(self.fck)])

        self.fcd = 0.85 * self.fck / 1.5   # [MPa]
        self.fyk = 500
        self.fyd = 500 / 1.15              # [MPa]
        self.Es = 200                      # [GPa]
        self.eslim = self.fyd / (self.Es * 1000)

        # Naponi na ivicama preseka (za izbor slučaja), sa širinom b
        self.sigma1 = self.NEd / (self.b * self.h) - self.MEd * 6 / (self.b * self.h ** 2)
        self.sigma2 = self.NEd / (self.b * self.h) + self.MEd * 6 / (self.b * self.h ** 2)
        self.MEdu = self.MEd + self.NEd * (self.h / 2 - self.d1)

    # ------------------------------------------------------------------
    def minimalni_i_maksimalni_procenat(self):
        """As,min i As,max [cm^2], kao u skripti."""
        AsMin = max(0.26 * self.fctm / self.fyk * self.brebra * self.d * 1e4,
                    0.0013 * self.brebra * self.d * 1e4)
        AsMax = 0.473 * self.b * self.d * self.fcd / self.fyd * 1e4
        return AsMin, AsMax

    def proracun(self):
        """Sprovodi proračun; vraća rečnik sa slučajem, armaturom i porukama."""
        self.poruke = []
        self.rezultat = {}
        # Redosled grana kroz koje je proračun prošao, sa međurezultatima (za izveštaj)
        self.koraci = []
        p = self.poruke.append

        # Centrični pritisak
        if self.MEd == 0 and self.sigma1 > 0:
            return self._centricni_pritisak()

        # (Eks)centrično zatezanje: mali ekscentricitet (sigma2 < 0) ili sila
        # zatezanja između armatura ili u težištu As1 (MEdu <= 0)
        if self.sigma2 < 0 or (self.NEd < 0 and self.MEd != 0 and self.MEdu <= 0):
            return self._zatezanje()

        if self.MEd == 0:
            p('Nema momenta ni pritiska - nema proračuna.')
            return self._kraj('nema')

        # Mali ekscentricitet - ceo presek pritisnut
        if self.sigma1 >= 0:
            return self._mali_ekscentricitet()

        # Veliki ekscentricitet - kvadratna jednačina po ksi
        K = self.b * self.d ** 2 * self.fcd * 1e3
        a = -0.33696 * K
        be = 0.81 * K
        c = -self.MEdu
        disk = be ** 2 - 4 * a * c
        self.rezultat.update(K=K, diskriminanta=disk)
        korak = dict(K=K, a=a, be=be, c=c, disk=disk)
        self.koraci.append(('veliki', korak))
        if disk < 0:
            # Nema realnog rešenja: jednostruko armiran presek ne može da primi MEdu
            return self._dvojno_armiranje()
        ksi = (-be + math.sqrt(disk)) / (2 * a)
        es1 = (1 - ksi) / ksi * 3.5
        As1 = 0.81 * ksi * self.fcd / self.fyd * self.b * self.d * 1e4 - self.NEd / (self.fyd * 1000) * 1e4
        self.rezultat.update(ksi=ksi, es1=es1, ec2=3.5, As1=As1, x=ksi * self.d)
        korak.update(ksi=ksi, es1=es1, As1=As1)
        if As1 < 0:
            return self._mali_ekscentricitet()
        if abs(es1) <= 2.5:
            return self._dvojno_armiranje()

        AsMin, AsMax = self.minimalni_i_maksimalni_procenat()
        self.rezultat.update(AsMin=AsMin, AsMax=AsMax)
        korak.update(AsMin=AsMin, AsMax=AsMax)
        if As1 < AsMin:
            p('Minimalni procenat armiranja! Za veliku silu pritiska a mali moment je možda '
              'potrebno dimenzionisanje uz pomoć dijagrama interakcije!')
            p(f'Minimalna površina armature je As,min = {AsMin:.2f} [cm²]')
            return self._kraj('minimalna')
        if As1 > AsMax:
            p(f'Procenat armiranja je veći od maksimalnog! As,max = {AsMax:.2f} [cm²]')
            return self._kraj('maksimalna')
        self._stampa(es1, 3.5, ksi, As1)
        return self._kraj('jednostruko')

    # ------------------------------------------------------------------
    def _kraj(self, slucaj):
        self.rezultat['slucaj'] = slucaj
        self.rezultat['poruke'] = list(self.poruke)
        return self.rezultat

    def _stampa(self, es1, ec2, ksi, As1):
        p = self.poruke.append
        p(f'Dilatacija u armaturi ε,s1 = {es1:.2f} [‰]')
        p(f'Dilatacija u betonu ε,c2 = {ec2:.2f} [‰]')
        p(f'ξ = {ksi:.4f}')
        p(f'Površina zategnute armature je: As1 = {As1:.2f} [cm²]')
        p(f'Visina pritisnute zone je: x = {100 * self.d * ksi:.2f} [cm]')

    def _centricni_pritisak(self):
        p = self.poruke.append
        p('Centrični pritisak!')
        Ac = self.b * self.h
        napon_beton = self.NEd / (Ac * 1e3)
        self.rezultat.update(napon_beton=napon_beton)
        korak = dict(Ac=Ac, napon_beton=napon_beton)
        self.koraci.append(('centricni', korak))
        if napon_beton <= self.fcd:
            As = max(0.15 * self.NEd / self.fyd * 10, 0.003 * Ac * 1e4, 4 * 1.13)
            self.rezultat.update(As=As)
            korak.update(As=As)
            p(f'Potrebna površina armature je: As = {As:.2f} [cm²]')
            return self._kraj('centricni')
        p('Napon u betonu je veći od proračunskog napona nosivosti betona!')
        p(f'fcd = {self.fcd:.2f} [MPa]')
        p(f'Napon u betonu = {napon_beton:.2f} [MPa]')
        return self._kraj('centricni_prekoracen')

    def _zatezanje(self):
        p = self.poruke.append
        p('(Eks)centrično zatezanje!')
        N = abs(self.NEd)
        e = self.MEd / N
        As = N / self.fyd * 10
        self.rezultat.update(e=e)
        korak = dict(N=N, e=e, As=As)
        self.koraci.append(('zatezanje', korak))
        if e != 0:
            c1 = self.h / 2 - self.d1
            c2 = self.h / 2 - self.d2
            As1 = N / self.fyd * (c2 + e) / (c1 + c2) * 10
            As2 = N / self.fyd * (c2 - e) / (c1 + c2) * 10
            self.rezultat.update(As1=As1, As2=As2, As=As1 + As2)
            korak.update(c1=c1, c2=c2, As1=As1, As2=As2, As=As1 + As2)
            p(f'Površina armature na zategnutoj ivici od momenta je As1 = {As1:.2f} [cm²]')
            p(f'Površina armature na pritisnutoj ivici od momenta je As2 = {As2:.2f} [cm²]')
        else:
            self.rezultat.update(As=As)
            p(f'Ukupna površina potrebne armature je As = {As:.2f} [cm²]')
        return self._kraj('zatezanje')

    def _dvojno_armiranje(self):
        p = self.poruke.append
        p('Dilatacija u armaturi je ispod 2.5 ‰ >>>> Dvojno armiranje!')
        ksi = 0.583
        dM = self.MEdu - (self.d / 1.672) ** 2 * self.b * self.fcd * 1000
        As2 = dM / ((self.d - self.d2) * self.fyd * 1000) * 1e4
        As1 = 0.81 * ksi * self.fcd / self.fyd * self.b * self.d * 1e4 - self.NEd / (self.fyd * 1000) * 1e4 + As2
        self.rezultat.update(ksi=ksi, es1=2.5, ec2=3.5, As1=As1, As2=As2, dM=dM, x=ksi * self.d)
        self.koraci.append(('dvojno', dict(ksi=ksi, Mlim=self.MEdu - dM, dM=dM, As1=As1, As2=As2)))
        if As2 > As1:
            return self._mali_ekscentricitet()
        p(f'Površina pritisnute armature je: As2 = {As2:.2f} [cm²]')
        self._stampa(2.5, 3.5, ksi, As1)
        return self._kraj('dvojno')

    def _mali_ekscentricitet(self):
        """Ceo presek pritisnut, simetrična armatura (As1 = As2), d2 = d1.

        Isto kao u skripti, za εc2 od 2 do 3.5 ‰ (obrtanje oko tačke na 3/7 h) traži se
        prvo stanje u kome je ravnoteža moguća sa 0 <= As1, As2 <= 0.04 b h. Za zadato εc2
        su obe jednačine ravnoteže linearne po As1 i As2, pa se rešavaju direktno
        (skripta je isto tražila grubom pretragom po mreži vrednosti).
        """
        p = self.poruke.append
        p('Mali ekscentricitet!')
        # Vrednosti iz prethodne grane (npr. dvojnog armiranja) ne važe za ovaj slučaj
        for kljuc in ('ksi', 'es1', 'ec2', 'As1', 'As2', 'dM', 'x'):
            self.rezultat.pop(kljuc, None)
        b, h, d1, d, fcd = self.b, self.h, self.d1, self.d, self.fcd
        d2 = d1
        alfas1, alfas2 = d1 / h, d2 / h
        MEdu = self.MEd + self.NEd * (h / 2 - d1)
        nu = self.NEd / (b * h * fcd * 1e3)
        mu = self.MEd / (b * h ** 2 * fcd * 1e3)
        self.rezultat.update(nu_Ed=nu, mu_Ed=mu)
        korak = dict(nu=nu, mu=mu, MEdu=MEdu, resenje=False)
        self.koraci.append(('mali', korak))
        p(f'ν,Ed = {nu:.3f}')
        p(f'μ,Ed = {mu:.3f}')

        As_max = 0.04 * b * h
        eslim = self.eslim * 1e3
        for ec2 in np.linspace(2, 3.5, num=1000):
            beta3 = (1 / 189) * (125 + 64 * ec2 - 16 * ec2 ** 2)
            beta4 = (3 / 14) * ((8 * ec2 + 5) * (37 - 8 * ec2)) / (125 + 64 * ec2 - 16 * ec2 ** 2)
            Fc = beta3 * b * h * fcd * 1e3
            es1 = min((2 * (1 - alfas1) - ec2 * (4 / 7 - alfas1)) / (3 / 7), eslim)
            es2 = min((2 * alfas2 + ec2 * (3 / 7 - alfas2)) / (3 / 7), eslim)
            sigmas1 = self.Es * 1e3 * es1
            sigmas2 = self.Es * 1e3 * es2
            # Ravnoteža momenata oko As1 i aksijalnih sila
            As2 = (MEdu - Fc * (d - beta4 * h)) / (sigmas2 * (d - d1))
            As1 = (self.NEd - Fc - sigmas2 * As2) / sigmas1
            if 0 <= As1 <= As_max and 0 <= As2 <= As_max:
                As = max(As1, As2) * 1e4
                self.rezultat.update(ec2=ec2, es1=es1, es2=es2, As1=As, As2=As, As=2 * As,
                                     beta3=beta3, beta4=beta4)
                korak.update(resenje=True, ec2=ec2, beta3=beta3, beta4=beta4, es1=es1, es2=es2,
                             sigmas1=sigmas1 / 1e3, sigmas2=sigmas2 / 1e3, Fc=Fc,
                             As1_r=As1 * 1e4, As2_r=As2 * 1e4, As=As)
                p(f'Dilatacija u betonu ε,c2 = {ec2:.3f} [‰]')
                p(f'Za simetrično armirane preseke ukupna površina armature je As = {2 * As:.2f} [cm²]')
                p(f'Površina armature u jednom delu preseka je As1 = As2 = {As:.2f} [cm²]')
                return self._kraj('mali_ekscentricitet')
        p('Postoji i zategnuta armatura u preseku, ili je potrebno više od 4% armature! '
          'Pogledaj dijagrame interakcije!')
        return self._kraj('mali_bez_resenja')


class RezultatiWindow(QDialog):
    """Poseban prozor za prikaz rezultata proračuna."""

    def __init__(self, tekst, naziv=''):
        super().__init__()
        self.setWindowTitle(f'Rezultati - Složeno savijanje - {naziv}' if naziv else 'Rezultati - Složeno savijanje')
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
        self.setWindowTitle('Složeno savijanje')
        self.resize(900, 600)

        main_layout = QVBoxLayout()
        naslov = QLabel('Dimenzionisanje preseka za složeno savijanje')
        naslov.setStyleSheet('font-size: 20px; font-weight: bold;')
        naslov.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(naslov)

        glavni = QHBoxLayout()
        self.forma = QFormLayout()

        self.ime_grede_input = QLineEdit('G1')

        self.MEd_input = QLineEdit()
        self.NEd_input = QLineEdit()
        self.b_input = QLineEdit()
        self.brebra_input = QLineEdit()
        self.h_input = QLineEdit()
        self.fck_input = QLineEdit()
        self.d1_input = QLineEdit()
        self.d2_input = QLineEdit()

        polja = [
            ('Ime grede:', self.ime_grede_input, 'Oznaka grede; koristi se u izveštaju i u imenu fajla.'),
            ('MEd [kNm]:', self.MEd_input, 'Proračunski moment savijanja (uzima se apsolutna vrednost).'),
            ('NEd [kN]:', self.NEd_input, 'Proračunska aksijalna sila; pritisak je +, zatezanje −.'),
            ('beff [cm]:', self.b_input, 'Efektivna širina pritisnute flanše kod T-preseka; '
                                      'kod pravougaonog preseka uneti širinu preseka b.'),
            ('b rebra [cm]:', self.brebra_input, 'Širina rebra (za minimalnu armaturu). Kod pravougaonog preseka = b.'),
            ('h [cm]:', self.h_input, 'Visina preseka.'),
            ('fck [MPa]:', self.fck_input, 'Karakteristična čvrstoća betona (standardna klasa).'),
            ('d1 [cm]:', self.d1_input, 'Rastojanje težišta zategnute armature od zategnute ivice.'),
            ('d2 [cm]:', self.d2_input, 'Rastojanje težišta pritisnute armature od pritisnute ivice '
                                        '(dvojno armiranje i zatezanje).'),
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
            self.napravi_izvestaj, lambda: 'Slozeno_savijanje_' + self.ime_grede())
        self.forma.addRow(self.izvestaj_dugmici)

        self.slika = CompositeBendingDrawing(300, 560)
        glavni.addLayout(self.forma)
        glavni.addWidget(self.slika)
        main_layout.addLayout(glavni)
        self.setLayout(main_layout)
        self.rezultati_prozor = None

    def ime_grede(self):
        return self.ime_grede_input.text().strip() or 'G1'

    def procitaj_ulaz(self):
        """Argumenti za SlozenoSavijanje redom (MEd, NEd, b, b_rebra, h, fck, d1, d2)."""
        vrednosti = [float(p.text().replace(',', '.')) for p in (
            self.MEd_input, self.NEd_input, self.b_input, self.brebra_input,
            self.h_input, self.fck_input, self.d1_input, self.d2_input)]
        if min(vrednosti[2], vrednosti[3], vrednosti[4]) <= 0:
            raise ValueError('Dimenzije preseka beff, b rebra i h moraju biti veće od nule.')
        if not 0 < vrednosti[6] < vrednosti[4] or not 0 <= vrednosti[7] < vrednosti[4]:
            raise ValueError('Rastojanja d1 i d2 moraju biti unutar visine preseka.')
        return vrednosti

    def napravi_izvestaj(self):
        from LatexScripts.CompositeBending_tex import CompositeBendingTex
        return CompositeBendingTex(*self.procitaj_ulaz(), naziv=self.ime_grede())

    def pokreni_proracun(self):
        try:
            model = SlozenoSavijanje(*self.procitaj_ulaz())
            rezultat = model.proracun()
        except ValueError as e:
            QMessageBox.critical(self, 'Greška u podacima', f'Došlo je do greške:\n{e}')
            return
        except Exception as e:
            QMessageBox.critical(self, 'Greška', f'Neočekivana greška:\n{e}')
            return
        self.rezultati_prozor = RezultatiWindow('\n'.join(rezultat['poruke']), self.ime_grede())
        self.rezultati_prozor.show()

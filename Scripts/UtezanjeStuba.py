import math
import numpy as np
import pandas as pd
import os


class UtezanjeStuba:

    def __init__(self):
        df = pd.read_excel('SeizmikaPodaci.xlsx')
        self.df = df
        self.finiz = np.array([0.503, 0.785, 1.13], dtype=float)/10000
        self.sniz = np.array([20, 15, 12.5, 10, 7.5], dtype=float)/100
        NEd = df['Normalna sila [kN]'].to_numpy(dtype=float)
        self.NEd = abs(NEd[0])
        b = df['b [cm]'].to_numpy(dtype=float)
        self.b = b[0]/100
        h = df['h [cm]'].to_numpy(dtype=float)
        self.h = h[0]/100
        self.h0 = self.h - 0.08
        fckMPA = df['Marka betona fck [Mpa]'].to_numpy(dtype=int)
        self.fck = fckMPA[0]*1000
        self.fcd = 0.85*self.fck/1.5
        self.fyd = 500/1.15*1000
        self.esyd = 0.002174
        self.nied = self.NEd/(self.b * self.h * self.fcd)
        self.b0 = self.b - 0.08
        # h0 = df['Duzina utegnutog elementa h0 [cm]'].to_numpy(dtype=float)
        # self.h0 = h0[0]/100
        q0 = df['Faktor ponasanja q0'].to_numpy(dtype=float)
        self.q0 = q0[0]
        self.Tc = 0.5
        obim_uzengija = df['Obim uzengija za pridrzavanje [cm]'].to_numpy(dtype=float)
        self.ObimUzg = obim_uzengija[0]/100
        tip_armature = df['Tip armature'].to_numpy(dtype=str)
        tip_armature = tip_armature[0]
        self.tip_armature = tip_armature.upper()
        T = df['Period oscilovanja T [s]'].to_numpy(dtype=float)
        self.T = T[0]
        MEd = self.df['Seizmicki moment Med [kNm]'].to_numpy(dtype=float)
        self.MEd = MEd[0]
        MRd = self.df['Moment nosivosti preseka MRd [kNm]'].to_numpy(dtype=float)
        self.MRd = MRd[0]
        Hs = self.df['Cista spratna visina Hs [m]'].to_numpy(dtype=float)
        self.Hs = Hs[0]
        
    def Armatura(self):
        if self.tip_armature == 'B500B':
            koeficijent = 1.5
        elif self.tip_armature == 'B500C':
            koeficijent = 1
        else:
            print('\nTip armature mora biti B500B ili B500C, '
                  'unesi jednu od dve vrednosti u odgovarajucu kolonu tabele.')
            exit()
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
        if self.MRd >= self.MEd * self.q0:
            print('Presek je predimenzionisan, usvojena je minimalna vrednost m\u03D5 = 1\n')
        else:
            pass
        if self.nied > 0.65:
            print('Normalizovana sila \u03BD,Ed je veca od 0.65! Povecaj marku betona ili dimenzije stuba!')
            print(f'\u03BD,Ed = {self.nied} >= 0.65 = \u03BD,Ed,max!')
            exit()
        elif self.nied <= 0.2 and self.q0 <= 2:
            print('\nPrimenjuju se pravila iz EC2!')
            exit()
        else:
            print(f'\u03BD,Ed = {round(self.nied,2)} <= 0.65')
            mfi = self.Mfi()
            bi_niz = self.df['Razmak pridrzanih sipki bi [cm]'].to_numpy(dtype=float)
            bi_niz = bi_niz/100
            proizvod = 0
            for i in bi_niz:
                proizvod = proizvod + math.pow(i, 2)
            alfan = 1 - proizvod/(6*self.b0*self.h0)
            for x in self.finiz:
                Vsw = x*self.ObimUzg
                for p in self.sniz:
                    alfas = (1 - p / (2 * self.b0)) * (1 - p / (2 * self.h0))
                    alfa = alfas * alfan
                    Vco = self.b0 * self.h0 * p
                    omegawdprov = (Vsw*self.fyd)/(Vco*self.fcd)
                    alfa_omegawdreq = 30 * mfi * self.nied * self.esyd * self.b / self.b0 - 0.035
                    omegawdreq = alfa_omegawdreq/alfa
                    precnik = math.sqrt(4*x/math.pi)*1000
                    if omegawdprov >= omegawdreq:
                        print('\n\u03C6 = ', round(precnik, 0), 'na s =', p*100, '[cm]' + '............OK!')
                        break
                    else:
                        print("\n\u03C6 =", round(precnik, 0), 'na s =', p*100, '[cm]' + ' ne zadovoljava!')
                        if x == 1.13*math.pow(10, -4) and p == 7.5/100:
                            print('\n>>>>>Nedovoljno utezanje stuba!')
            print('\u03C9_wd_prov = ', omegawdprov)
            print('\u03C9_wd_req = ', omegawdreq)
            print('\u03B1_s = ', alfas)
            print('\u03B1_n = ', alfan)
            print('\u03B1 = ', alfa)
            print('\u03B1_\u03C9 = ', alfa_omegawdreq)


def seizmikapodaci():
    # os.chdir('BetonskeKonstrukcije')
    fajlovi = os.listdir()
    try:
        if 'SeizmikaPodaci.xlsx' not in fajlovi:
            print("Fajl SeizmikaPodaci.xlsx se ne nalazi u folderu")
            exit()
        else:
            print('Fajl SeizmikaPodaci.xlsx se nalazi u folderu. \n -------------------------')
            klasa = UtezanjeStuba()
    except IndexError:
        print('Svaka kolona mora biti popunjena sa odgovarajucim podacima da bi skripta radila.')
        exit()
    return klasa


def main():
    klasa = seizmikapodaci()
    klasa.Utezanje()

    
if __name__ == "__main__":
    main()

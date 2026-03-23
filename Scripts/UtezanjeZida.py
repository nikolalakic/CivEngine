import math
import os
import pandas as pd

class UtezanjeZida:
    def __init__(self):
        df = pd.read_excel('SeizmikaPodaci.xlsx')
        self.df = df
        naziv_zida = df['Naziv platna'].to_numpy(dtype=str)
        self.naziv_zida = naziv_zida[0]
        NEd = df['Normalna sila [kN]'].to_numpy(dtype=float)
        self.NEd = abs(NEd[0])
        b = df['b [cm]'].to_numpy(dtype=float)
        b = b[0]
        self.b = b/100
        self.b_0 = b/100 - 0.05
        h = df['h [cm]'].to_numpy(dtype=float)
        h = h[0]
        self.h = h/100
        fck = df['Marka betona fck [Mpa]'].to_numpy(dtype=int)
        self.fck =  fck[0]
        self.fcd = 0.85*fck[0]*1000/1.5 # KPa
        self.fyd = 500*1000/1.15 # KPa
        self.omega_v = 0.201/100 * self.fyd/self.fcd # iz minimalnog procenta armiranja
        tip_armature = df['Tip armature'].to_numpy(dtype=str)
        tip_armature = tip_armature[0]
        self.tip_armature = tip_armature.upper()
        T = df['Period oscilovanja T [s]'].to_numpy(dtype=float)
        self.T = T[0]
        q0 = df['Faktor ponasanja q0'].to_numpy(dtype=float)
        self.q0 = q0[0]
        h0 = df['Duzina utegnutog elementa h0 [cm]'].to_numpy(dtype=float)
        self.h_0 = h0[0]/100
        precnik_uzengije = df['Precnik uzengije [mm]'].to_numpy(dtype=int)
        precnik_uzengije = precnik_uzengije/1000 # m
        precnik_uzengije = precnik_uzengije[0]
        povrsina_preseka_uzengije = math.pow(precnik_uzengije ,2) * math.pi /4
        self.a1_uz = povrsina_preseka_uzengije
        obim_uznegija = df['Obim uzengija za pridrzavanje [cm]'].to_numpy(dtype=float)
        obim_uznegija = obim_uznegija/100
        self.obim_uzengija = obim_uznegija[0]
        s = self.df['Vertikalni razmak uzengija s [cm]'].to_numpy(dtype=float)
        s = s[0]
        self.s = s/100
        self.ni = self.NEd/(self.b * self.h * self.fcd)
        MEd = self.df['Seizmicki moment Med [kNm]'].to_numpy(dtype=float)
        self.MEd = MEd[0]
        MRd = self.df['Moment nosivosti preseka MRd [kNm]'].to_numpy(dtype=float)
        self.MRd = MRd[0]
        Hs = self.df['Cista spratna visina Hs [m]'].to_numpy(dtype=float)
        self.Hs = Hs[0]


    def kontrola_normalizovane_sile(self):
        if self.ni <= 0.15:
            print(f'Nije potrebno utezanje krajeva zida {self.naziv_zida}')
            exit()
        elif self.ni > 0.4:
            ni = round(self.ni, 2)
            print(f'Prekoracena maksimalna normalizovana sila za seizmicki zid {self.naziv_zida}!!! \n \u03BD = {ni} , \u03BD_max = 0.4')
            exit()
        else:
            print(f'Potrebno je utezanje krajeva zida za zid {self.naziv_zida} \n')

    def Armatura(self):
        if self.tip_armature == 'B500B':
            koeficijent = 1.5
        elif self.tip_armature == 'B500C':
            koeficijent = 1
        else:
            print('Tip armature mora biti B500B ili B500C')
            koeficijent = None
            exit()
        return koeficijent

    def Mfi(self):
        koeficijent = self.Armatura()
        Tc = 0.5
        if self.T > Tc:
            mfi = koeficijent * (2 * self.q0 * self.MEd / self.MRd - 1)
        else:
            mfi = koeficijent * (2 * (self.q0 * self.MEd/ self.MRd) - 1) * Tc / self.T + 1
        if self.MRd >= self.MEd * self.q0:
            mfi = 1
        return mfi

    def Alfa_n(self):
        niz_bi = self.df['Razmak pridrzanih sipki bi [cm]'].to_numpy(dtype=float)
        niz_bi = niz_bi / 100  # [m]
        suma = 0
        for i in niz_bi:
            suma = suma + math.pow(i, 2)
        alfan = 1 - suma/(6 * self.b_0 * self.h_0)
        return alfan

    def Alfa_s(self):
        alfas = (1 - self.s/(2*self.b_0)) * (1 - self.s/(2*self.h_0))
        return alfas

    def Alfa(self):
        alfan = self.Alfa_n()
        alfas = self.Alfa_s()
        alfa = alfan * alfas
        return alfa

    def alfa_omega_dreq(self):
        mfi = self.Mfi()
        alfa_omegad_dreq = 30 * mfi * (self.ni + self.omega_v) * 0.002174 * self.b/self.b_0 - 0.035
        return alfa_omegad_dreq

    def Minimalna_Duzina_Utezanja(self):
        alfa_omegad_req = self.alfa_omega_dreq()
        xu = (self.ni + self.omega_v) * self.h * self.b/self.b_0
        epsilon_cu2_c = 0.0035 + 0.1 * alfa_omegad_req
        lc_mreq = xu * (1 - 0.0035/epsilon_cu2_c)
        if lc_mreq < max(0.15 * self.h, 1.5 * self.b):
            lc_mreq = max(0.15 * self.h, 1.5 * self.b)
        else:
            pass
        return lc_mreq

    def Kontrola_minimalne_debljine_utegnutog_elementa(self):
        if self.h_0 >= max(self.b, 0.2 * self.h):
            a = f'\nPrema članu 5.4.3.4.2 (10) Evrokoda 8 minimalna debljina utegnutog elementa je: b0,min = Hs/10 = {round(self.Hs/10, 2) * 100} [cm] \n'
        else:
            a = f'\nPrema članu 5.4.3.4.2 (10) Evrokoda 8 minimalna debljina utegnutog elementa je: b0,min = Hs/15 = {round(self.Hs/15, 2) * 100} [cm] \n'
        return a

    def Kontrola_postojeceg_utezanja(self):
        if self.MRd >= self.MEd * self.q0:
            print('Presek je predimenzionisan, usvojena je minimalna vrednost m\u03D5 = 1\n')
        else:
            pass
        xu = (self.ni + self.omega_v) * self.h * self.b/self.b_0
        alfa_omegad_req = self.alfa_omega_dreq()
        lc_mreq = self.Minimalna_Duzina_Utezanja()
        alfa = self.Alfa()
        alfa_s = self.Alfa_s()
        alfa_n = self.Alfa_n()
        Vco = self.b_0 * self.h_0 * self.s
        Vsw = self.a1_uz * self.obim_uzengija
        omega_d_prov = Vsw * self.fyd/(Vco * self.fcd)
        epsilon_cu2c_prov = 0.0035 + 0.1 * alfa * omega_d_prov
        lc_req = xu * (1 - 0.0035/epsilon_cu2c_prov)
        if omega_d_prov <= max(0.08, alfa_omegad_req/alfa):
            print('Nije obezbeđeno dovoljno utezanje ivičnog elementa! \n \n \u03C9wd,prov = ', round(omega_d_prov, 2), '< \u03C9wd,req = ', round(max(0.08, alfa_omegad_req/alfa), 2) )
            exit()
        if lc_req >= self.h_0:
            bo_min = self.Kontrola_minimalne_debljine_utegnutog_elementa()
            print("Potrebno je smanjiti stepen utezanja kraja zida ili produžiti ivični element!")
            print(bo_min)
            print('Potrebna dužina utezanja kraja zida: lc_req = ', round(lc_req*100, 1), '[cm]')
            print('Trenutna dužina utezanja zida: h0 = ', round(self.h_0*100, 1), '[cm]')
            print('Minimalna potrebna dužina utezanja zida: lc_mreq = ', round(lc_mreq*100,1), '[cm]')
            print('\u03B1_s = ', round(alfa_s,2))
            print('\u03B1_n = ', round(alfa_n,2))
            print('\u03B1 = ', round(alfa,2))
            print('\u03C9_d_prov = ', round(omega_d_prov,2))
            print('\u03B1_\u03C9_d_req = ', round(alfa_omegad_req,2))
            print('\u03C9_d_req = ', round(alfa_omegad_req/alfa,2))
        else:
            bo_min = self.Kontrola_minimalne_debljine_utegnutog_elementa()
            print('Dovoljno utegnut kraj zida!')
            print(bo_min)
            print('\u03BD,Ed = ', round(self.ni,2))
            print('Potrebna dužina utezanja kraja zida: lc_req = ', round(lc_req*100, 1), '[cm]')
            print('Trenutna dužina utezanja zida: h0 = ', round(self.h_0*100, 1), '[cm]')
            print('Minimalna potrebna dužina utezanja zida: lc_mreq = ', round(lc_mreq * 100, 1), '[cm]')
            print('\u03B1_s = ', round(alfa_s,2))
            print('\u03B1_n = ', round(alfa_n,2))
            print('\u03B1 = ', round(alfa,2))
            print('\u03C9_d_prov = ', round(omega_d_prov,2))
            print('\u03B1_\u03C9_d_req = ', round(alfa_omegad_req,2))
            print('\u03C9_d_req = ', round(alfa_omegad_req/alfa,2))


def SeizmikaPodaci():
    # os.chdir('BetonskeKonstrukcije')
    fajlovi = os.listdir()
    try:
        if 'SeizmikaPodaci.xlsx' not in fajlovi:
            print("Fajl SeizmikaPodaci.xlsx se ne nalazi u folderu")
            exit()
        else:
            print('Fajl SeizmikaPodaci.xlsx se nalazi u folderu. \n -------------------------')
            klasa = UtezanjeZida()
    except IndexError:
        print('Svaka kolona mora biti popunjena sa odgovarajućim podacima da bi skripta radila.')
        exit()
    return klasa


def main():
    klasa = SeizmikaPodaci()
    klasa.kontrola_normalizovane_sile()
    klasa.Kontrola_postojeceg_utezanja()
    
if __name__=="__main__":
    main()


import os
import pandas as pd
import math


class BetonIArmatura:
    def __init__(self):
        #self.fck = int(input('Unesi karakterističnu čvrstoću betona fck [MPa]: '))
        self.fck = 25
        #b = float(input('Unesi sirinu preseka b [cm]: '))
        b = 70
        self.b = b / 100  # [m]
        #h = float(input('Unesi visinu preseka h [cm]: '))
        h = 60
        self.h = h / 100  # [m]
        #d1 = float(input('Unesi rastojanje zategnute armature od zategnute ivice betona d1 [cm]: '))
        d1 = 5.5
        self.d1 = d1 / 100  # [m]
        self.A = self.b * self.h  # Površina preseka [m^2]
        self.u = 2 * (self.b + self.h)  # Obim preseka za pravougaone preseke
        self.d = self.h - self.d1
        self.alfa_cc = 0.85
        self.Es = 200  # [GPa]
        self.fyk = 500  # [MPa]
        self.fyd = self.fyk/1.15
        self.fywd = self.fyd
        self.eslim = self.fyd/(self.Es*math.pow(10, 3))
        self.gama_c = 1.5
        self.ni_1 = 0.6 * (1 - self.fck/250)
        self.cot_teta = 1  # kotangens ugla pritisnutih betonskih dijagonala prema osi nosača kod smicanja
        # , usvojeno teta = 45 stepena
        self.sin_alfa_cw = 1  # sinus ugla uzengija prema osi nosača kod smicanja, usvojeno alfa = 90 stepena
        self.cot_alfa = 0

    @staticmethod
    def dataframe():
        if 'BetonPodaci.csv' not in os.listdir():
            print('BetonPodaci.csv se ne nalazi u radnom folderu!')
            exit()
        else:
            df = pd.read_csv('BetonPodaci.csv', delimiter=';', encoding='UTF-8', skipinitialspace=True)
            return df

    def fcd(self):
        df = self.dataframe()
        fck_lista = df['fck [Mpa]'].to_list()
        if self.fck in fck_lista:
            fcd = self.alfa_cc * self.fck/self.gama_c
        else:
            print(f'fck = {self.fck} [MPa] nije standardna klasa betona prema Evrokodu 2.')
            exit()
        return fcd

    def fctm(self):
        df = self.dataframe()
        fck_lista = df['fck [Mpa]'].to_list()
        if self.fck in fck_lista:
            fctm_lista = df['fctm [Mpa]'].to_numpy()
            indeks = fck_lista.index(self.fck)
            fctm = fctm_lista[indeks]
        else:
            print(f'{self.fck} nije standardna klasa betona prema Evrokodu 2.')
            exit()
        return fctm

    def fctk_005(self):
        df = self.dataframe()
        fck_lista = df['fck [Mpa]'].to_list()
        if self.fck in fck_lista:
            fctk_005_lista = df['fctk005 [Mpa]'].to_numpy()
            indeks = fck_lista.index(self.fck)
            fctk_005 = fctk_005_lista[indeks]
        else:
            print(f'{self.fck} nije standardna klasa betona prema Evrokodu 2.')
            exit()
        return fctk_005

    def Ecm(self):
        df = self.dataframe()
        fck_lista = df['fck [Mpa]'].to_list()
        if self.fck in fck_lista:
            Ecm_lista = df['Ecm [Gpa]'].to_numpy()
            indeks = fck_lista.index(self.fck)
            Ecm = Ecm_lista[indeks]
        else:
            print(f'{self.fck} nije standardna klasa betona prema Evrokodu 2.')
            exit()
        return Ecm

    def fi_lista(self):
        df = self.dataframe()
        lista = df['fi [mm]'].to_numpy()
        return lista

    def fi_lista_povrsina(self):
        df = self.dataframe()
        lista = df['A [cm2]'].to_numpy()
        return lista

    def klasa_izlozenosti(self):
        df = self.dataframe()
        lista = df['KlaseIzlozenosti'].to_numpy()
        return lista

    def poduzna_armatura(self):
        #Asl = float(input('Unesi povrsinu poduzne armature od savijanja u preseku ili rebru Asl [cm^2]: '))
        Asl = 18.84
        Asl = Asl / math.pow(10, 4)
        return Asl

    def secnost(self):
        #m = int(input('Unesi sečnost za smicanje posmatranog preseka m [m=2 ili m=4]: '))
        m = 4
        return m

    def t_eff(self):
        t_eff = max(self.A/self.u, 2 * self.d1)
        return t_eff

    def bk(self):
        t_eff = self.t_eff()
        bk = self.b - 2 * t_eff/2
        return bk

    def hk(self):
        t_eff = self.t_eff()
        hk = self.h - 2 * t_eff/2
        return hk

    def Ak(self):
        bk = self.bk()
        hk = self.hk()
        Ak = bk * hk
        return Ak

    def uk(self):
        bk = self.bk()
        hk = self.hk()
        uk = 2 * (bk + hk)
        return uk

    def minimalna_nosivost_betona_na_torziju(self):
        Ak = self.Ak()
        t_eff = self.t_eff()
        alfa_ct = 1  # Nacionalni prilog
        fctk_005 = self.fctk_005()
        fctd = alfa_ct * fctk_005 / self.gama_c
        TRd_c = 2 * fctd * Ak * t_eff * 1000  # [kN]
        return TRd_c

    def maksimalna_nosivost_betona_na_torziju(self):
        alfa_cw = 1  # Nacionalni prilog? Geometrija preseka?
        Ak = self.Ak()
        ni_1 = self.ni_1
        fcd = self.fcd()
        t_eff = self.t_eff()
        sinus_teta = math.sqrt(2) / 2  # teta = 45 stepeni
        cosinus_teta = math.sqrt(2) / 2
        TRd_max = 2 * Ak * alfa_cw * ni_1 * fcd * t_eff * sinus_teta * cosinus_teta * 1000  # [kNm]
        return TRd_max

    def minimalna_nosivost_betona_na_smicanje(self):
        Asl = self.poduzna_armatura()
        k1 = 0.15  # nacionalni prilog
        ro_1 = Asl/(self.b * self.d)
        sigma_cp = 0  # proracun vazi za nepritisnut betonski presek
        CRd_c = 0.18/self.gama_c
        k = 1 + math.sqrt(200/(self.d*1000))
        VRd_c_1 = ((CRd_c * k * math.pow((100 * ro_1 * self.fck), 1/3) + k1 * sigma_cp) * self.b * self.d *
                   1000)  # [kN]
        Vmin = 0.035 * math.pow(k, 3/2) * math.pow(self.fck, 1/2) * self.b * self.d * 1000  # [kN]
        VRd_c = max(VRd_c_1, Vmin)
        return VRd_c

    def maksimalna_nosivost_betona_na_smicanje(self):
        fcd = self.fcd()
        VRd_max = (self.sin_alfa_cw * self.ni_1 * fcd * self.b * 0.9 * self.d *
                   (self.cot_teta/(1 + math.pow(self.cot_teta, 2)))) * 1000
        return VRd_max

import os
import pandas as pd
import math


class BetonIArmatura:
    def __init__(self):
        self.fck = int(input('Unesi karakterističnu čvrstoću betona fck [MPa]: '))
        self.alfa_cc = 0.85
        self.Es = 200  # [GPa]
        self.fyk = 500  # [MPa]
        self.fyd = self.fyk/1.15
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

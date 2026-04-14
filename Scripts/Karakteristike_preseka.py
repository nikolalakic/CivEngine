import pandas as pd
import math
import os


class KarakteristikeBetonaIArmature:
    def __init__(self):
        # Internal storage initialized as None to track if user has been asked
        self._fck = None
        self._b = None
        self._h = None
        self._d1 = None
        self._df = None
        self.alfa_cc = 0.85
        self.Es = 200  # [GPa]
        self.fyk = 500  # [MPa]
        self.fyd = self.fyk / 1.15
        self.fywd = self.fyd
        self.gama_c = 1.5
        self.cot_teta = 1  # teta = 45 deg
        self.sin_alfa_cw = 1  # alfa = 90 deg
        self.cot_alfa = 0

    def _get_df(self):
        if self._df is None:
            if 'BetonPodaci.csv' not in os.listdir():
                print('Greška: BetonPodaci.csv se ne nalazi u radnom folderu!')
                exit()
            self._df = pd.read_csv('BetonPodaci.csv', delimiter=';', encoding='UTF-8', skipinitialspace=True)
        return self._df

    def _get_row_index(self):
        """Finds the row index for the current fck."""
        df = self._get_df()
        fck_lista = df['fck [Mpa]'].to_list()
        if self.fck in fck_lista:
            return fck_lista.index(self.fck)
        else:
            print(f'Greška: fck = {self.fck} [MPa] nije standardna klasa u bazi.')
            exit()

    @property
    def fck(self):
        if self._fck is None:
            self._fck = int(input('Unesi karakterističnu čvrstoću betona fck [MPa]: '))
        return self._fck

    @fck.setter
    def fck(self, value):
        self._fck = value

    @property
    def b(self):
        if self._b is None:
            self._b = float(input('Unesi širinu preseka b [cm]: ')) / 100
        return self._b

    @property
    def h(self):
        if self._h is None:
            self._h = float(input('Unesi visinu preseka h [cm]: ')) / 100
        return self._h

    @property
    def d1(self):
        if self._d1 is None:
            self._d1 = float(input('Unesi rastojanje d1 [cm]: ')) / 100
        return self._d1

    @property
    def d(self):
        return self.h - self.d1

    @property
    def A(self):
        return self.b * self.h

    @property
    def u(self):
        return 2 * (self.b + self.h)

    @property
    def ni_1(self):
        return 0.6 * (1 - self.fck / 250)

    def fcd(self):
        return self.alfa_cc * self.fck / self.gama_c

    def _lookup(self, column):
        idx = self._get_row_index()
        return self._get_df()[column].iloc[idx]

    def fctm(self):
        return self._lookup('fctm [Mpa]')

    def fctk_005(self):
        return self._lookup('fctk005 [Mpa]')

    def Ecm(self):
        return self._lookup('Ecm [Gpa]')

    def fi_lista(self):
        return self._get_df()['fi [mm]'].dropna().to_numpy()

    def fi_lista_povrsina(self):
        return self._get_df()['A [cm2]'].dropna().to_numpy()

    def klasa_izlozenosti(self):
        return self._get_df()['KlaseIzlozenosti'].dropna().to_numpy()

    def t_eff(self):
        return max(self.A / self.u, 2 * self.d1)

    def Ak(self):
        t = self.t_eff()
        return (self.b - t) * (self.h - t)

    def minimalna_nosivost_betona_na_torziju(self):
        fctd = self.fctk_005() / self.gama_c
        return 2 * fctd * self.Ak() * self.t_eff() * 1000  # [kN]

    def maksimalna_nosivost_betona_na_torziju(self):
        # teta = 45 -> sin*cos = 0.5
        return 2 * self.Ak() * 1.0 * self.ni_1 * self.fcd() * self.t_eff() * 0.5 * 1000

    def minimalna_nosivost_betona_na_smicanje(self, Asl_cm2):
        Asl = Asl_cm2 / 10000
        k = min(1 + math.sqrt(200 / (self.d * 1000)), 2.0)
        ro_1 = min(Asl / (self.b * self.d), 0.02)

        VRd_c1 = (0.18 / self.gama_c * k * (100 * ro_1 * self.fck) ** (1 / 3)) * self.b * self.d * 1000
        Vmin = 0.035 * k ** 1.5 * self.fck ** 0.5 * self.b * self.d * 1000
        return max(VRd_c1, Vmin)

    def maksimalna_nosivost_betona_na_smicanje(self):
        z = 0.9 * self.d
        den = 1 + self.cot_teta ** 2
        return (self.sin_alfa_cw * self.ni_1 * self.fcd() * self.b * z * (self.cot_teta / den)) * 1000

class KarakteristikeCelicnogPreseka:
    def __init__(self, profil=None):
        self._profil = profil
        self._bf1 = None
        self._bf2 = None
        self._tw = None
        self._tf1 = None
        self._tf2 = None
        self._fya = None
        self._beff = None
        self._povrsina_preseka = None
        self._hfl = None
        self._ha = None
        self._povrsina_smicanja = None


    @staticmethod
    def dataframe():
        if 'VruceValjaniProfili.csv' not in os.listdir():
            print('VruceValjaniProfili.csv se ne nalazi u radnom folderu!')
            exit()
        else:
            df = pd.read_csv('VruceValjaniProfili.csv', delimiter=',', encoding='UTF-8', skipinitialspace=True)
            return df

    @property
    def profil(self):
        if self._profil is None:
            unos_profil = input(
                'Unesi traženi profil (IPE,HEA,HEB,UPN) ili stisni enter za ručni unos: '
            ).strip().upper()
            if unos_profil == "":
                return None
            df = self.dataframe()
            if unos_profil in df['Section'].values:
                self._profil = unos_profil
            else:
                print(f'Profil "{unos_profil}" ne postoji u tabeli.')
                self._profil = None
        return self._profil

    def get_value(self, column):
        df = self.dataframe()
        profil = self.profil
        row = df[df['Section'] == profil]
        if not row.empty:
            return row.iloc[0][column]
        return None

    @property
    def bf1(self):
        profil = self.profil
        if self._bf1 is None and profil is None:
            unos_bf1 = float(input('Unesi širinu donje nožice bf1 [mm]: '))
            self._bf1 = unos_bf1 / 1000  # [m]
        else:
            self._bf1 = self.get_value('b') / 1000 # [m]
        return self._bf1

    @property
    def bf2(self):
        profil = self.profil
        if self._bf2 is None and profil is None:
            unos_bf2 = float(input('Unesi širinu gornje nožice bf2 [mm]: '))
            self._bf2 = unos_bf2 / 1000  # [m]
        else:
            self._bf2 = self.get_value('b') / 1000 # [m]
        return self._bf2

    @property
    def tw(self):
        profil = self.profil
        if self._tw is None and profil is None:
            unos_tw = float(input('Unesi debljinu rebra tw [mm]: '))
            self._tw = unos_tw / 1000  # [m]
        else:
            self._tw = self.get_value('tw') / 1000 # [m]
        return self._tw

    @property
    def ha(self):
        profil = self.profil
        if self._ha is None and profil is None:
            unos_ha = float(input('Unesi ukupnu visinu profila ha [mm]: '))
            self._ha = unos_ha / 1000  # [m]
        else:
            self._ha = self.get_value('h') / 1000 # [m]
        return self._ha

    @property
    def tf1(self):
        profil = self.profil
        if self._tf1 is None and profil is None:
            unos_tf1 = float(input('Unesi debljinu donje nozice tf1 [mm]: '))
            self._tf1 = unos_tf1 / 1000  # [m]
        else:
            self._tf1 = self.get_value('tf') / 1000 # [m]
        return self._tf1

    @property
    def tf2(self):
        profil = self.profil
        if self._tf2 is None and profil is None:
            unos_tf2 = float(input('Unesi debljinu gornje nozice tf2 [mm]: '))
            self._tf2 = unos_tf2 / 1000  # [m]
        else:
            self._tf2 = self.get_value('tf') / 1000 # [m]
        return self._tf2

    @property
    def fya(self):
        if self._fya is None:
            unos_fya = float(input('Unesi kvalitet čelika fya [MPa]: '))
            self._fya = unos_fya * 1000  # [KPa]
        return self._fya

    @property
    def beff(self):
        if self._beff is None:
            unos_beff = float(input('Unesi efektivnu širinu flanše beff (za bilo koji pritisnut presek) [cm]: '))
            self._beff = unos_beff / 100 # [m]
        return self._beff

    @property
    def povrsina_preseka(self):
        profil = self.profil
        if self._povrsina_preseka is None:
            value = None
            if profil is not None:
                value = self.get_value('A_mm2')
            if value is not None:
                self._povrsina_preseka = value / 1e6  # [m^2]
            else:
                unos = float(input('Unesi površinu čeličnog dela preseka A [mm^2]: '))
                self._povrsina_preseka = unos / 1e6  # [m^2]
        return self._povrsina_preseka

    @property
    def povrsina_smicanja(self):
        profil = self.profil
        if self._povrsina_smicanja is None and profil is None:
            unos_Avz = float(input('Unesi površinu smicanja Avz [mm^2]: '))
            self._povrsina_smicanja = unos_Avz / 1e6  # [m^2]
        else:
            self._povrsina_smicanja = self.get_value('Av_z_mm2') / 1e6 # [m^2]
        return self._povrsina_smicanja

    @property
    def hfl(self):
        if self._hfl is None:
            unos_hfl = float(input('Unesi visinu ploče/flanše hfl [cm]: '))
            self._hfl = unos_hfl / 100 # [m]
        return self._hfl
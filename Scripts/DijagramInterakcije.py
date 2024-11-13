import math
import numpy as np
import matplotlib.pyplot as plt


class DijagramInterakcije:
    def __init__(self):
        self.fck = int(input('Unesi karakteristicnu cvrstocu betona na pritisak fck [MPa]: '))
        self.k = float(input('Unesi % zategnute armature As1 u odnosu na ukupnu armaturu As [%]: '))
        self.k = self.k/100
        self.fcd = 0.85 * self.fck / 1.5  # [MPa]
        self.b = float(input('Unesi sirinu preseka b [cm]: '))
        self.b = 30
        self.b = self.b / 100
        self.h = float(input('Unesi visinu preseka h [cm]: '))
        self.h = self.h / 100
        self.d1 = float(input('Unesi rastojanje od tezista zategnute armature do zategnute ivice d1 [cm]: '))
        self.d1 = self.d1 / 100  # [m]
        self.d = self.h - self.d1
        self.d2 = float(input('Unesi rastojanje od tezista pritisnute armature do pritisnute ivice d2 [cm]: '))
        self.d2 = self.d2 / 100  # [m]
        self.Es = 200  # [GPa]
        self.fyk = 500  # [MPa]
        self.fyd = 500 / 1.15  # [MPa]
        self.epsilon_yd = self.fyd / self.Es / 1000
        self.epsilon_cu2 = 0.0035
        self.alfa_1 = self.d1 / self.h
        self.alfa_2 = self.d2 / self.h
        self.MEd = float(input('Unesi vrednost momenta MEd [kN]: '))
        self.NEd = float(input('Unesi vrednost aksijalne sile NEd [kN](+ je pritisak): '))
        self.mi_Ed = self.MEd / (self.b * self.h ** 2 * self.fcd * 1000)
        self.ni_Ed = self.NEd / (self.b * self.h * self.fcd * 1000)

    @staticmethod
    def beta2_koeficijent(epsilon_c2):
        epsilon_c2 = epsilon_c2 * 1000  # [Formula radi za promile]
        if 3.5 <= epsilon_c2 <= 3.5:
            beta2 = (epsilon_c2 * (3 * epsilon_c2 - 4) + 2) / (2 * epsilon_c2 * (3 * epsilon_c2 - 2))
        elif 0 <= epsilon_c2 < 2:
            beta2 = (8 - epsilon_c2) / (4 * (6 - epsilon_c2))
        else:
            beta2 = None
        return beta2

    @staticmethod
    def gustina_omege():
        omege = np.linspace(0, 0.5, num=20)
        return omege

    def centricni_pritisak(self):
        niz_ni_Rd = np.array([])
        niz_mi_Rd = np.array([])
        omege = self.gustina_omege()
        for omega in omege:
            omega1 = 0.5 * omega
            omega2 = 0.5 * omega
            NRd = (1 + omega) * self.b * self.h * self.fcd * 1000
            MRd = (omega2 * (0.5 - self.alfa_2) - omega1 * (0.5 - self.alfa_1)) * self.b * self.h ** 2 * self.fcd * 1000
            ni_Rd = NRd / (self.fcd * 1000 * self.b * self.h)
            mi_Rd = MRd / (self.fcd * 1000 * self.b * self.h ** 2)
            niz_ni_Rd = np.append(niz_ni_Rd, ni_Rd)
            niz_mi_Rd = np.append(niz_mi_Rd, mi_Rd)
        return np.array([niz_ni_Rd, niz_mi_Rd])

    def granica_malog_ekscentriciteta(self):
        epsilon_c2 = self.epsilon_cu2
        beta2 = self.beta2_koeficijent(epsilon_c2)
        epsilon_s2 = epsilon_c2 * (1 - self.alfa_2)
        if epsilon_s2 >= self.epsilon_yd:
            epsilon_s2 = self.epsilon_yd
        epsilon_s1 = self.epsilon_cu2 * self.alfa_1
        if epsilon_s1 >= self.epsilon_yd:
            epsilon_s1 = self.epsilon_yd
        x = self.h
        niz_ni_Rd = np.array([])
        niz_mi_Rd = np.array([])
        omege = self.gustina_omege()
        for omega in omege:
            omega1 = self.k * omega
            omega2 = (1 - self.k) * omega
            As1 = omega1 * self.b * self.h * self.fcd / self.fyd
            As2 = omega2 * self.b * self.h * self.fcd / self.fyd
            Fc = 0.81 * 1 / (1 - self.alfa_1) * self.d * self.b * self.fcd * 1000  # [kN]
            Fs2 = As2 * epsilon_s2 * self.Es * math.pow(10, 6)  # [kN]
            Fs1 = As1 * epsilon_s1 * self.Es * math.pow(10, 6)  # [kN]
            NRd = Fc + Fs1 + Fs2
            MRd = Fc * (self.h / 2 - beta2 * x) + Fs2 * (self.h / 2 - self.d2) - Fs1 * (self.h / 2 - self.d1)
            ni_Rd = NRd / (self.b * self.h * self.fcd * 1000)
            mi_Rd = MRd / (self.fcd * 1000 * self.b * self.h ** 2)
            niz_ni_Rd = np.append(niz_ni_Rd, ni_Rd)
            niz_mi_Rd = np.append(niz_mi_Rd, mi_Rd)
        return np.array([niz_ni_Rd, niz_mi_Rd])

    def tri_i_po_sa_dva_jedan_sedam_cetiri(self):
        epsilon_s1 = self.epsilon_yd
        epsilon_c2 = self.epsilon_cu2
        x = (self.epsilon_cu2 * (self.h - self.d1)) / (self.epsilon_yd + self.epsilon_cu2)
        epsilon_s2 = self.epsilon_cu2 * (x - self.d2) / x
        if epsilon_s2 >= self.epsilon_yd:
            epsilon_s2 = self.epsilon_yd
        niz_ni_Rd = np.array([])
        niz_mi_Rd = np.array([])
        omege = self.gustina_omege()
        beta2 = self.beta2_koeficijent(epsilon_c2)
        for omega in omege:
            omega1 = self.k * omega
            omega2 = (1 - self.k) * omega
            As1 = omega1 * self.b * self.h * self.fcd / self.fyd
            As2 = omega2 * self.b * self.h * self.fcd / self.fyd
            Fc = 0.81 * x * self.b * self.fcd * 1000  # [kN]
            Fs2 = As2 * epsilon_s2 * self.Es * math.pow(10, 6)  # [kN]
            Fs1 = As1 * epsilon_s1 * self.Es * math.pow(10, 6)  # [kN]
            NRd = Fc - Fs1 + Fs2
            MRd = Fc * (self.h / 2 - beta2 * x) + Fs2 * (self.h / 2 - self.d2) + Fs1 * (self.h / 2 - self.d1)
            ni_Rd = NRd / (self.b * self.h * self.fcd * 1000)
            mi_Rd = MRd / (self.fcd * 1000 * self.b * self.h ** 2)
            niz_ni_Rd = np.append(niz_ni_Rd, ni_Rd)
            niz_mi_Rd = np.append(niz_mi_Rd, mi_Rd)
        return np.array([niz_ni_Rd, niz_mi_Rd])

    def tri_i_po_sa_deset(self):
        epsilon_s1 = 0.01
        epsilon_c2 = self.epsilon_cu2
        x = (self.epsilon_cu2 * (self.h - self.d1)) / (epsilon_s1 + self.epsilon_cu2)
        epsilon_s2 = self.epsilon_cu2 * (x - self.d2) / x
        if epsilon_s2 >= self.epsilon_yd:
            epsilon_s2 = self.epsilon_yd
        if epsilon_s1 >= self.epsilon_yd:
            epsilon_s1 = self.epsilon_yd
        niz_ni_Rd = np.array([])
        niz_mi_Rd = np.array([])
        omege = self.gustina_omege()
        beta2 = self.beta2_koeficijent(epsilon_c2)
        for omega in omege:
            omega1 = self.k * omega
            omega2 = (1 - self.k) * omega
            As1 = omega1 * self.b * self.h * self.fcd / self.fyd
            As2 = omega2 * self.b * self.h * self.fcd / self.fyd
            Fc = 0.81 * x * self.b * self.fcd * 1000  # [kN]
            Fs2 = As2 * epsilon_s2 * self.Es * math.pow(10, 6)  # [kN]
            Fs1 = As1 * epsilon_s1 * self.Es * math.pow(10, 6)  # [kN]
            NRd = Fc - Fs1 + Fs2
            MRd = Fc * (self.h / 2 - beta2 * x) + Fs2 * (self.h / 2 - self.d2) + Fs1 * (self.h / 2 - self.d1)
            ni_Rd = NRd / (self.b * self.h * self.fcd * 1000)
            mi_Rd = MRd / (self.fcd * 1000 * self.b * self.h ** 2)
            niz_ni_Rd = np.append(niz_ni_Rd, ni_Rd)
            niz_mi_Rd = np.append(niz_mi_Rd, mi_Rd)
        return np.array([niz_ni_Rd, niz_mi_Rd])

    def tri_i_po_sa_dvadeset(self):
        epsilon_s1 = 0.02
        epsilon_c2 = self.epsilon_cu2
        x = (self.epsilon_cu2 * (self.h - self.d1)) / (epsilon_s1 + self.epsilon_cu2)
        epsilon_s2 = self.epsilon_cu2 * (x - self.d2) / x
        if epsilon_s2 >= self.epsilon_yd:
            epsilon_s2 = self.epsilon_yd
        if epsilon_s1 >= self.epsilon_yd:
            epsilon_s1 = self.epsilon_yd
        niz_ni_Rd = np.array([])
        niz_mi_Rd = np.array([])
        omege = self.gustina_omege()
        beta2 = self.beta2_koeficijent(epsilon_c2)
        for omega in omege:
            omega1 = self.k * omega
            omega2 = (1 - self.k) * omega
            As1 = omega1 * self.b * self.h * self.fcd / self.fyd
            As2 = omega2 * self.b * self.h * self.fcd / self.fyd
            Fc = 0.81 * x * self.b * self.fcd * 1000  # [kN]
            Fs2 = As2 * epsilon_s2 * self.Es * math.pow(10, 6)  # [kN]
            Fs1 = As1 * epsilon_s1 * self.Es * math.pow(10, 6)  # [kN]
            NRd = Fc - Fs1 + Fs2
            MRd = Fc * (self.h / 2 - beta2 * x) + Fs2 * (self.h / 2 - self.d2) + Fs1 * (self.h / 2 - self.d1)
            ni_Rd = NRd / (self.b * self.h * self.fcd * 1000)
            mi_Rd = MRd / (self.fcd * 1000 * self.b * self.h ** 2)
            niz_ni_Rd = np.append(niz_ni_Rd, ni_Rd)
            niz_mi_Rd = np.append(niz_mi_Rd, mi_Rd)
        return np.array([niz_ni_Rd, niz_mi_Rd])

    def tri_i_po_sa_cetrdeset(self):
        epsilon_s1 = 0.04
        epsilon_c2 = self.epsilon_cu2
        x = (self.epsilon_cu2 * (self.h - self.d1)) / (epsilon_s1 + self.epsilon_cu2)
        epsilon_s2 = self.epsilon_cu2 * (x - self.d2) / x
        if epsilon_s2 >= self.epsilon_yd:
            epsilon_s2 = self.epsilon_yd
        if epsilon_s1 >= self.epsilon_yd:
            epsilon_s1 = self.epsilon_yd
        niz_ni_Rd = np.array([])
        niz_mi_Rd = np.array([])
        omege = self.gustina_omege()
        beta2 = self.beta2_koeficijent(epsilon_c2)
        for omega in omege:
            omega1 = self.k * omega
            omega2 = (1 - self.k) * omega
            As1 = omega1 * self.b * self.h * self.fcd / self.fyd
            As2 = omega2 * self.b * self.h * self.fcd / self.fyd
            Fc = 0.81 * x * self.b * self.fcd * 1000  # [kN]
            Fs2 = As2 * epsilon_s2 * self.Es * math.pow(10, 6)  # [kN]
            Fs1 = As1 * epsilon_s1 * self.Es * math.pow(10, 6)  # [kN]
            NRd = Fc - Fs1 + Fs2
            MRd = Fc * (self.h / 2 - beta2 * x) + Fs2 * (self.h / 2 - self.d2) + Fs1 * (self.h / 2 - self.d1)
            ni_Rd = NRd / (self.b * self.h * self.fcd * 1000)
            mi_Rd = MRd / (self.fcd * 1000 * self.b * self.h ** 2)
            niz_ni_Rd = np.append(niz_ni_Rd, ni_Rd)
            niz_mi_Rd = np.append(niz_mi_Rd, mi_Rd)
        return np.array([niz_ni_Rd, niz_mi_Rd])

    def stampa(self):
        omege = self.gustina_omege()
        centricni_pritisak = self.centricni_pritisak()
        granica_malog_ekscentriciteta = self.granica_malog_ekscentriciteta()
        tri_i_po_sa_dva_jedan_sedam_cetiri = self.tri_i_po_sa_dva_jedan_sedam_cetiri()
        tri_i_po_sa_deset = self.tri_i_po_sa_deset()
        tri_i_po_sa_dvadeset = self.tri_i_po_sa_dvadeset()
        tri_i_po_sa_cetrdeset = self.tri_i_po_sa_cetrdeset()

        dpi = 96
        width_px = 1000
        height_px = 800
        figsize = (width_px / dpi, height_px / dpi)
        plt.figure(figsize=figsize)
        plt.xlabel('\u03BDRd')
        plt.ylabel('\u03BCRd')
        plt.title('Dijagram interakcije')

        # Osnovne linije
        plt.plot(centricni_pritisak[0], centricni_pritisak[1], color='green',
                 label='Ec2/Ec1 = 2\u2030/ 2\u2030')
        plt.plot(granica_malog_ekscentriciteta[0],
                 granica_malog_ekscentriciteta[1], color='purple',
                 label='Ec2/Ec1 = 3.5\u2030/ 0\u2030')
        plt.plot(tri_i_po_sa_dva_jedan_sedam_cetiri[0],
                 tri_i_po_sa_dva_jedan_sedam_cetiri[1], color='black',
                 linestyle='--', label='Ec2/Es1 = 3.5\u2030/ -2.174\u2030')
        plt.plot(tri_i_po_sa_deset[0], tri_i_po_sa_deset[1], color='black',
                 label='Ec2/Es1 = 3.5\u2030/ -10\u2030')
        plt.plot(tri_i_po_sa_dvadeset[0], tri_i_po_sa_dvadeset[1], color='blue',
                 label='Ec2/Es1 = 3.5\u2030/ -20\u2030')
        plt.plot(tri_i_po_sa_cetrdeset[0], tri_i_po_sa_cetrdeset[1], color='magenta',
                 label='Ec2/Es1 = 3.5\u2030/ -40\u2030')
        plt.plot([], [],
                 label=f'As1 = {self.k} * As', linestyle='-', color='black', linewidth=2, marker='>', markersize=10)
        plt.plot([], [],
                 label=f'As2 = {1 - self.k} * As', linestyle='-', color='black', linewidth=2, marker='>', markersize=10)
        plt.plot([], [],
                 label=f'fck = {self.fck} MPa', linestyle='-', color='black', linewidth=2, marker='*', markersize=10)

        niz_x = np.array([centricni_pritisak[0],
                          granica_malog_ekscentriciteta[0],
                          tri_i_po_sa_dva_jedan_sedam_cetiri[0],
                          tri_i_po_sa_deset[0],
                          tri_i_po_sa_dvadeset[0],
                          tri_i_po_sa_cetrdeset[0]
                          ])
        niz_y = np.array([centricni_pritisak[1],
                          granica_malog_ekscentriciteta[1],
                          tri_i_po_sa_dva_jedan_sedam_cetiri[1],
                          tri_i_po_sa_deset[1],
                          tri_i_po_sa_dvadeset[1],
                          tri_i_po_sa_cetrdeset[1]
                          ])

        plt.plot(niz_x, niz_y, color='gray')
        # cursor = mplcursors.cursor(hover=True)
        niz_x = np.array([niz_x[0], niz_x[1], niz_x[2], niz_x[3], niz_x[4], niz_x[5]])
        niz_y = np.array([niz_y[0], niz_y[1], niz_y[2], niz_y[3], niz_y[4], niz_y[5]])

        tacka_ni_Ed = [self.ni_Ed]
        tacka_mi_Ed = [self.mi_Ed]
        plt.plot(tacka_ni_Ed, tacka_mi_Ed, marker="x", markersize=6, color="red")

        for i, (x, y) in enumerate(zip(niz_x, niz_y)):
            for j in range(len(x)):
                if i == 0:
                    rotation = 90
                elif i == 4:
                    rotation = 45
                elif i == 5:
                    rotation = 45
                else:
                    rotation = 0
                plt.text(x[j], y[j], f'{round(omege[j], 2)}', fontsize=6, verticalalignment="bottom", rotation=rotation)

        plt.legend()

        plt.show()


def main():
    dijagram_interakcije = DijagramInterakcije()
    dijagram_interakcije.stampa()


if __name__ == "__main__":
    main()

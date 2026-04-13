from Karakteristike_preseka import *
import math


# važi samo za pritisnutu ili zategnutu flanšu bez doprinosa čeličnog preseka
class SpregnutiPresek:
    def __init__(self):
        self.kb = KarakteristikeBetonaIArmature()
        profil = input(
            'Unesi traženi profil (IPE,HEA,HEB,UPN) ili stisni enter za ručni unos: '
        ).strip().upper()
        fya_input = float(input('Unesi kvalitet čelika [MPa]: '))
        self.kc = KarakteristikeCelicnogPreseka(profil)
        self.Aa = self.kc.povrsina_preseka
        self.ha = self.kc.ha
        self.bf1 = self.kc.bf1
        self.bf2 = self.kc.bf2
        self.tw = self.kc.tw
        self.tf1 = self.kc.tf1
        self.tf2 = self.kc.tf2
        self.fya = fya_input * 1000  # [KPa]
        self.fck = self.kb.fck * 1000 # [KPa]
        self.beff = self.kc.beff
        self.hfl = self.kc.hfl
        self.MEd = float(input('Unesi dejstujući moment savijanja MEd [KNm]: '))
        self.VEd = float(input('Unesi dejstvujuću smičuću silu VEd [KN]: '))
        self.polozaj = self.polozaj_momenta()
        self.gamma_v = 1.25

    @staticmethod
    def polozaj_momenta():
        while True:
            upit = input(
                'Unesi slovo b ili c ako moment savijanja pritiska beton ili čelik [b ili c]: ').lower().strip()
            if upit in ['b', 'c']:
                return upit
            print(f'Nije uneto slovo b ili c, već "{upit}"')

    def Mpl_Rd(self):
        Na = self.Aa * self.fya  # kN
        if self.polozaj == 'b':
            zp = 0.0
            delta_N = 1  # [kN]
            Nc = self.beff * zp * 0.85 * self.fck / 1.5

            while abs(Na - Nc) > delta_N:
                if zp > self.hfl:
                    print(f'\nNeutralna osa je van ploče!\nzp={round(zp * 100, 4)} [cm] > hfl = {self.hfl * 100} [cm]')
                    exit()
                else:
                    zp += 0.0001
                    Nc = self.beff * zp * 0.85 * self.fck / 1.5
        else:
            # TODO: odradi za pritisnut celik
            zp = 0.0

        Mpl = Na * (self.ha / 2 + self.hfl - zp / 2)  # [kNm]
        return Mpl

    def Vpl_Rd(self):
        Avz = self.kc.povrsina_smicanja
        return Avz * self.fya / math.sqrt(3)  # [kN]
    def interakcija_smicanja_i_savijanja(self):
        current_Mpl = self.Mpl_Rd()
        Vpl_Rd = self.Vpl_Rd()

        if self.MEd > current_Mpl:
            print(f'\nPrekoračena plastična nosivost! {self.MEd} > {round(current_Mpl, 2)} [kNm]')
            exit()

        if self.VEd <= 0.5 * Vpl_Rd:
            print(f'\nNije potrebna interakcija. VEd/Vpl = {round(self.VEd / Vpl_Rd, 2)} < 0.5')
            return current_Mpl

        print('\nPotrebna je redukcija usled interakcije smicanja i savijanja:')
        print(f'VEd/Vpl_Rd = {round(self.VEd / Vpl_Rd, 2)} > 0.5')

        Na_flanges = self.fya * (self.tf1 * self.bf1 + self.tf2 * self.bf2)
        zp = 0.0
        delta_N = 1
        Mf_Rd = 0

        while abs(Na_flanges - (self.beff * zp * 0.85 * self.fck / 1.5)) > delta_N:
            if zp > self.hfl:
                print(f'\nNeutralna osa za Mf_Rd je van ploče!')
                exit()
            zp += 0.0001
            Mf_Rd = (self.fya * self.bf1 * self.tf1 * (self.ha - self.tf1 / 2 + self.hfl) +
                     self.fya * self.bf2 * self.tf2 * (self.tf2 / 2 + self.hfl) - Na_flanges * (zp / 2))
        rho = math.pow(2 * self.VEd / Vpl_Rd - 1, 2)
        Mpl_Rd_red = Mf_Rd + (current_Mpl - Mf_Rd) * (1 - rho)
        return Mpl_Rd_red

    def proracun_mozdanika(self):
        Na = self.Aa * self.fya
        Nc = self.beff * 0.85 / 1.5 * self.fck * self.hfl
        Ecm = self.kb.Ecm() * 1e6
        Vl = min(Na, Nc)
        fu_stud = 450000  # [KPa]
        hsc = float(input('Unesi visinu moždanika hsc [mm]: ')) / 1000
        d = float(input('Unesi prečnik moždanika d [mm]: ')) / 1000
        if hsc / d < 4:
            print(f'hsc/d = {round(hsc / d, 3)} < 4, koeficijent \u03B1 je nedefinisan')
            exit()
        alfa = 1.0
        PRd_1 = 0.8 * fu_stud * (math.pi * d ** 2 / 4) / self.gamma_v
        PRd_2 = 0.29 * alfa * d ** 2 * math.sqrt(self.fck * Ecm) / self.gamma_v
        PRd = min(PRd_1, PRd_2)
        return Vl / PRd

obj = SpregnutiPresek()
final_M = obj.interakcija_smicanja_i_savijanja()
print(f'\nPlastični moment nosivosti (redukovan): {round(final_M, 2)} [kNm]')
print(f'\nPotreban broj moždanika: n = {round(obj.proracun_mozdanika(), 2)}')
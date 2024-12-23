import math
from Karakteristike_preseka import BetonIArmatura


class Smicanje(BetonIArmatura):
    def __init__(self):
        super().__init__()
        self.VEd = abs(float(input('Unesi silu smicanja VEd [kN]: ')))
        self.mv = self.secnost()
        self.VRd_c = self.minimalna_nosivost_betona_na_smicanje()

    def izabrana_povrsina_armature_za_smicanje(self):  # uzeti su samo fi 8, 10, i 12 u obzir
        fi_lista_povrsina = self.fi_lista_povrsina() / math.pow(10, 4)  # m^2
        lista = fi_lista_povrsina[1:4]
        return lista

    def izabrani_precnici_armature_za_smicanje(self):
        fi_lista = self.fi_lista()
        lista = fi_lista[1:4]
        return lista

    def minimalna_povrsina_armature_za_smicanje(self):
        fi_lista_povrsina = self.izabrana_povrsina_armature_za_smicanje()
        ro_w_min = 0.08 * math.sqrt(self.fck) / self.fyk
        sr_min_lista = []
        for fi_povrsina in fi_lista_povrsina:
            sr_min = self.mv * fi_povrsina / (ro_w_min * self.b)  # [m]
            sr_min_lista.append(sr_min)
        return sr_min_lista

    def potrebno_rastojanje_racunske_armature_za_smicanje(self):  # dimenzionisanje
        fi_lista_povrsina = self.izabrana_povrsina_armature_za_smicanje()
        s_rac_lista = []
        for fi_povrsina in fi_lista_povrsina:
            s_rac = self.mv * fi_povrsina / self.VEd * 0.9 * self.d * self.fyd * 1000 * self.cot_teta  # [m]
            s_rac_lista.append(s_rac)
        return s_rac_lista

    def maksimalno_poduzno_rastojanje_armature(self):
        VRd_max = self.maksimalna_nosivost_betona_na_smicanje()
        if self.fck <= 50:  # poredjenja su za [m]
            if self.VEd <= 0.3 * VRd_max:
                sr_max = min(0.75 * self.d, 0.3)
            elif 0.3 * VRd_max < self.VEd <= 0.6 * VRd_max:
                sr_max = min(0.55 * self.d, 0.3)
            else:
                sr_max = min(0.3 * self.d, 0.2)
        else:
            if self.VEd <= 0.3 * VRd_max:
                sr_max = min(0.75 * self.d, 0.2)
            elif 0.3 * VRd_max < self.VEd <= 0.6 * VRd_max:
                sr_max = min(0.55 * self.d, 0.2)
            else:
                sr_max = min(0.3 * self.d, 0.2)
        return sr_max

    def maksimalno_poprecno_rastojanje_nozica_armature(self):
        VRd_max = self.maksimalna_nosivost_betona_na_smicanje()
        if self.fck <= 50:  # poredjenja su za [m]
            if self.VEd <= 0.3 * VRd_max:
                st_max = min(0.75 * self.d, 0.6)
            elif 0.3 * VRd_max < self.VEd <= 0.6 * VRd_max:
                st_max = min(0.75 * self.d, 0.6)
            else:
                st_max = min(0.3 * self.d, 0.3)
        else:
            if self.VEd <= 0.3 * VRd_max:
                st_max = min(0.75 * self.d, 0.4)
            elif 0.3 * VRd_max < self.VEd <= 0.6 * VRd_max:
                st_max = min(0.75 * self.d, 0.4)
            else:
                st_max = min(0.3 * self.d, 0.3)
        return st_max

    def dodatna_zategnuta_armatura(self):
        delta_Ftd = self.VEd/2 * (self.cot_teta - self.cot_alfa)
        delta_As1 = delta_Ftd/(self.fyd * 1000)  # [m^2]
        return delta_As1

    def rezultat(self):
        delta_As1 = self.dodatna_zategnuta_armatura()
        st_max = self.maksimalno_poprecno_rastojanje_nozica_armature()
        sr_max = self.maksimalno_poduzno_rastojanje_armature()
        s_rac_lista = self.potrebno_rastojanje_racunske_armature_za_smicanje()
        fi_lista = self.izabrani_precnici_armature_za_smicanje()
        VRd_max = self.maksimalna_nosivost_betona_na_smicanje()
        sr_min_lista = self.minimalna_povrsina_armature_za_smicanje()
        rezultat = ''
        if self.VRd_c < self.VEd <= VRd_max:
            print('--------------------')
            for s, fi, sr_min in zip(s_rac_lista, fi_lista, sr_min_lista):
                odgovor = (f'Potrebno rastojanje armature: s = {round(min(s, sr_min, sr_max), 4)*100}'
                           f' [cm] za prečnik uzengije \u03C6 = {fi}')
                rezultat += odgovor + '\n'
            print(f'Sečnost m = {self.mv}')
            print(f'Dodatna zategnuta armatura: \u0394As1 =  {round(delta_As1, 4) * math.pow(10,4)} [cm^2]')
            print(f'Maksimalno podužno rastojanje armature: sr_max = {round(sr_max, 4) * 100} [cm]')
            print(f'Maksimalno poprečno rastojanje armature: st_max = {round(st_max, 4) * 100} [cm]\n')
            print(f'Maksimalna nosivost pritisnute betonske dijagonale: VRd,max = {round(VRd_max, 2)} kN')
        elif self.VEd <= self.VRd_c:
            print('--------------------')
            print('Minimalni procenat armiranja!\n')
            for s, fi, sr_min in zip(s_rac_lista, fi_lista, sr_min_lista):
                odgovor = (f'Potrebno rastojanje armature: s = {round(min(s, sr_min, sr_max), 4)*100} [cm] '
                           f'za prečnik uzengije: \u03C6 = {fi}')
                rezultat += odgovor + '\n'
            print(f'Sečnost: m = {self.mv}')
            print(f'Minimalna nosivost betonskog preseka na smicanje VRd,c = {round(self.VRd_c, 2)} kN')
            print(f'Dodatna zategnuta armatura: \u0394As1 =  {round(delta_As1, 4) * math.pow(10, 4)} [cm^2]')
            print(f'Maksimalno podužno rastojanje armature: sr_max = {round(sr_max, 4) * 100} [cm]')
            print(f'Maksimalno poprečno rastojanje armature: st_max = {round(st_max, 4) * 100} [cm]\n')
            print(f'Maksimalna nosivost pritisnute betonske dijagonale: VRd,max = {round(VRd_max, 2)} kN')

        else:
            print('--------------------')
            rezultat = 'Prekoračena maksimalna nosivost pritisnute betonske dijagonale na smicanje!\n'
            print(f'VEd = {self.VEd} [kN] > {round(VRd_max, 2)} [kN] = VRd_max')
        return print(rezultat)


if __name__ == "__main__":
    obj = Smicanje()
    obj.rezultat()

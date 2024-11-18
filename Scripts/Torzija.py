import math
from Karakteristike_preseka import BetonIArmatura


class Torzija(BetonIArmatura):
    def __init__(self):
        super().__init__()
        self.TEd = abs(float(input('Unesi silu torzije TEd [kNm]: ')))
        self.Asl = self.poduzna_armatura()
        self.mt = 1

    def izabrani_precnici_armature_za_torziju(self):
        fi_lista = self.fi_lista()
        lista = fi_lista[1:4]
        return lista

    def izabrana_povrsina_armature_za_torziju(self):  # uzeti su samo fi 8, 10, i 12 u obzir
        fi_lista_povrsina = self.fi_lista_povrsina() / math.pow(10, 4)  # m^2
        lista = fi_lista_povrsina[1:4]
        return lista

    def minimalna_povrsina_armature_za_torziju(self):
        fi_lista_povrsina = self.izabrana_povrsina_armature_za_torziju()
        ro_w_min = 0.08 * math.sqrt(self.fck) / self.fyk
        sr_min_lista = []
        for fi_povrsina in fi_lista_povrsina:
            sr_min = self.mt * fi_povrsina / (ro_w_min * self.b)  # [m]
            sr_min_lista.append(sr_min)
        return sr_min_lista

    def maksimalno_poprecno_rastojanje_nozica_armature_za_torziju(self):
        TRd_max = self.maksimalna_nosivost_betona_na_torziju()
        if self.fck <= 50:  # poredjenja su za [m]
            if self.TEd <= 0.3 * TRd_max:
                st_max = min(0.75 * self.d, 0.6)
            elif 0.3 * TRd_max < self.TEd <= 0.6 * TRd_max:
                st_max = min(0.75 * self.d, 0.6)
            else:
                st_max = min(0.3 * self.d, 0.3)
        else:
            if self.TEd <= 0.3 * TRd_max:
                st_max = min(0.75 * self.d, 0.4)
            elif 0.3 * TRd_max < self.TEd <= 0.6 * TRd_max:
                st_max = min(0.75 * self.d, 0.4)
            else:
                st_max = min(0.3 * self.d, 0.3)
        return st_max

    def maksimalno_poduzno_rastojanje_armature_za_torziju(self):
        TRd_max = self.maksimalna_nosivost_betona_na_torziju()
        if self.fck <= 50:  # poredjenja su za [m]
            if self.TEd <= 0.3 * TRd_max:
                sr_max = min(0.75 * self.d, 0.3)
            elif 0.3 * TRd_max < self.TEd <= 0.6 * TRd_max:
                sr_max = min(0.55 * self.d, 0.3)
            else:
                sr_max = min(0.3 * self.d, 0.2)
        else:
            if self.TEd <= 0.3 * TRd_max:
                sr_max = min(0.75 * self.d, 0.2)
            elif 0.3 * TRd_max < self.TEd <= 0.6 * TRd_max:
                sr_max = min(0.55 * self.d, 0.2)
            else:
                sr_max = min(0.3 * self.d, 0.2)
        return sr_max

    def dodatna_poduzna_armatura_za_torziju(self):
        Ak = self.Ak()
        uk = self.uk()
        Asl = self.TEd / (2 * Ak * self.fywd * 1000) * uk * self.cot_teta
        return Asl

    def potrebno_rastojanje_racunske_armature_za_torziju(self):  # dimenzionisanje
        fi_lista_povrsina = self.izabrana_povrsina_armature_za_torziju()
        s_rac_lista = []
        Ak = self.Ak()
        fywd = self.fywd
        cot_teta = self.cot_teta
        for fi_povrsina in fi_lista_povrsina:
            s_rac = 2 * Ak * fywd * cot_teta * fi_povrsina / self.TEd * 1000  # [m]
            s_rac_lista.append(s_rac)
        return s_rac_lista

    def rezultat(self):
        Asl_torzija = self.dodatna_poduzna_armatura_za_torziju()
        st_max = self.maksimalno_poprecno_rastojanje_nozica_armature_za_torziju()
        sr_max = self.maksimalno_poduzno_rastojanje_armature_za_torziju()
        s_rac_lista = self.potrebno_rastojanje_racunske_armature_za_torziju()
        fi_lista = self.izabrani_precnici_armature_za_torziju()
        TRd_c = self.minimalna_nosivost_betona_na_torziju()
        TRd_max = self.maksimalna_nosivost_betona_na_torziju()
        sr_min_lista = self.minimalna_povrsina_armature_za_torziju()
        rezultat = ''
        if TRd_c < self.TEd <= TRd_max:
            print('--------------------')
            for s, fi, sr_min in zip(s_rac_lista, fi_lista, sr_min_lista):
                odgovor = (f'Potrebno rastojanje armature: s = {round(min(s, sr_min, sr_max), 4) * 100}'
                           f' [cm] za prečnik uzengije \u03C6 = {fi}')
                rezultat += odgovor + '\n'
            print(f'Sečnost m = {self.mt}')
            print(f'Dodatna podužna armatura za osiguranje od torzije'
                  f': Asl =  {round(Asl_torzija, 4) * math.pow(10, 4)} [cm^2]')
            print(f'Maksimalno podužno rastojanje armature: sr_max = {round(sr_max, 4) * 100} [cm]')
            print(f'Maksimalno poprečno rastojanje armature: st_max = {round(st_max, 4) * 100} [cm]\n')
            print(f'Maksimalna nosivost pritisnute betonske dijagonale: TRd,max = {round(TRd_max, 2)} kN')
        elif self.TEd <= TRd_c:
            print('--------------------')
            print('Minimalni procenat armiranja!\n')
            for s, fi, sr_min in zip(s_rac_lista, fi_lista, sr_min_lista):
                odgovor = (f'Potrebno rastojanje poprečne armature: s = {round(min(s, sr_min, sr_max), 4) * 100} [cm] '
                           f'za prečnik uzengije: \u03C6 = {fi}')
                rezultat += odgovor + '\n'
            print(f'Sečnost: m = {self.mt}')
            print(f'Dodatna podužna armatura za osiguranje od torzije'
                  f': \u0394As1 =  {round(Asl_torzija, 4) * math.pow(10, 4)} [cm^2]')
            print(f'Maksimalno podužno rastojanje armature: sr_max = {round(sr_max, 4) * 100} [cm]')
            print(f'Maksimalno poprečno rastojanje armature: st_max = {round(st_max, 4) * 100} [cm]\n')
            print(f'Maksimalna nosivost pritisnute betonske dijagonale: TRd,max = {round(TRd_max, 2)} kN')

        else:
            print('--------------------')
            rezultat = 'Prekoračena maksimalna nosivost pritisnute betonske dijagonale na torziju!\n'
            print(f'TEd = {self.TEd} [kN] > {round(TRd_max, 2)} [kN] = VRd_max')
        return print(rezultat)


if __name__ == "__main__":
    obj = Torzija()
    obj.rezultat()

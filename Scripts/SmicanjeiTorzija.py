from Smicanje import Smicanje
from Torzija import Torzija


class SmicanjeITorzija(Smicanje, Torzija):
    def __init__(self):
        super().__init__()

    def kontorla_interakcije_smicanja_i_torzije(self):
        VEd = self.VEd
        TEd = self.TEd
        TRd_c = self.minimalna_nosivost_betona_na_torziju()
        TRd_max = self.maksimalna_nosivost_betona_na_torziju()
        VRd_c = self.minimalna_nosivost_betona_na_smicanje()
        VRd_max = self.maksimalna_nosivost_betona_na_smicanje()
        sr_max = self.maksimalno_poduzno_rastojanje_armature()
        st_max = self.maksimalno_poprecno_rastojanje_nozica_armature()
        Asl_torzija = self.dodatna_poduzna_armatura_za_torziju()
        sr_rac_lista_smicanje = self.potrebno_rastojanje_racunske_armature_za_smicanje()
        # TODO nastavi sa uslovima
        if VEd/VRd_c + TEd/TRd_c <= 1:
            print('--------------------')


if __name__ == "__main__":
    obj = SmicanjeITorzija()
    obj.kontorla_interakcije_smicanja_i_torzije()

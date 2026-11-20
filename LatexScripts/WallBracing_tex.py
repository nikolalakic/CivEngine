"""Izveštaj za utezanje krajeva zida (po uzoru na RetainingWall2_tex.py)."""
import os

from GUI.ConcreteElementsWindows.wall_bracing import UtezanjeZida
from LatexScripts.report_engine import LatexReport


class WallBracingTex(UtezanjeZida, LatexReport):
    template_name = 'WallBracing.tex'

    def __init__(self, params, bi_niz):
        super().__init__(params, bi_niz)
        self.params = params
        self.naziv = self.naziv_zida
        self.naslov = f'Utezanje krajeva zida {self.naziv_zida}'
        # Proračun se izvršava isto kao u GUI-ju; greška (npr. prekoračena sila)
        # je takođe rezultat koji ide u izveštaj.
        try:
            self.log = self.Utezanje()
            self.greska = None
        except ValueError as e:
            self.log = None
            self.greska = str(e)

    def context(self):
        return dict(m=self, d=self.detalji,
                    bi=[float(b) * 100 for b in self.bi_niz],
                    precnik=self.params.get('precnik_uzengije', 'φ 8').replace('φ', '').strip(),
                    k_arm=self.Armatura(), Tc=0.5, esyd=0.002174)

    def figures(self, out_dir, ext):
        from GUI.ConcreteElementsWindows.section_drawings import WallBracingDrawing
        ime = f'presek.{ext}'
        WallBracingDrawing().save_image(os.path.join(out_dir, ime), width_mm=45)
        return {'presek': ime}

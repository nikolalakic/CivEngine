"""Izveštaj za utezanje stuba (po uzoru na RetainingWall2_tex.py)."""
import os

from GUI.ConcreteElementsWindows.column_bracing import UtezanjeStuba
from LatexScripts.report_engine import LatexReport


class ColumnBracingTex(UtezanjeStuba, LatexReport):
    template_name = 'ColumnBracing.tex'

    def __init__(self, params, bi_niz, naziv='S1'):
        super().__init__(params, bi_niz)
        self.params = params
        self.naziv = naziv
        self.naslov = f'Utezanje stuba {naziv}'
        # Proračun se izvršava isto kao u GUI-ju; greška (npr. prekoračena sila)
        # je takođe rezultat koji ide u izveštaj.
        try:
            self.log = self.Utezanje()
            self.greska = None
        except ValueError as e:
            self.log = None
            self.greska = str(e)

    def context(self):
        return dict(m=self, d=self.detalji, iteracije=self.iteracije,
                    bi=[float(b) * 100 for b in self.bi_niz],
                    precnik=self.params.get('precnik_uzengije', 'φ 8').replace('φ', '').strip(),
                    k_arm=self.Armatura())

    def figures(self, out_dir, ext):
        from GUI.ConcreteElementsWindows.section_drawings import ColumnBracingDrawing
        ime = f'presek.{ext}'
        ColumnBracingDrawing().save_image(os.path.join(out_dir, ime), width_mm=90)
        return {'presek': ime}

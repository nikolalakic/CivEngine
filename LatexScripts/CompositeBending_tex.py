"""Izveštaj za dimenzionisanje preseka na složeno savijanje (po uzoru na RetainingWall2_tex.py)."""
import os

from GUI.ConcreteElementsWindows.composite_bending import SlozenoSavijanje
from LatexScripts.report_engine import LatexReport


class CompositeBendingTex(SlozenoSavijanje, LatexReport):
    template_name = 'CompositeBending.tex'
    naslov = 'Dimenzionisanje preseka za složeno savijanje'

    def __init__(self, *args, naziv='G1'):
        super().__init__(*args)
        self.naziv = naziv
        self.naslov = f'Složeno savijanje grede {naziv}'
        # Isti proračun kao u GUI-ju; model beleži korake u self.koraci
        self.rezultat = self.proracun()

    def context(self):
        return dict(m=self, r=self.rezultat, koraci=self.koraci)

    def figures(self, out_dir, ext):
        from GUI.ConcreteElementsWindows.section_drawings import CompositeBendingDrawing
        ime = f'presek.{ext}'
        CompositeBendingDrawing().save_image(os.path.join(out_dir, ime), width_mm=40)
        return {'presek': ime}

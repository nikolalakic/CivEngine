"""Izveštaj za dimenzionisanje armature za smicanje (po uzoru na RetainingWall2_tex.py)."""
import os

from GUI.ConcreteElementsWindows.shear import Smicanje
from LatexScripts.report_engine import LatexReport


class ShearTex(Smicanje, LatexReport):
    template_name = 'Shear.tex'
    naslov = 'Dimenzionisanje armature za smicanje'

    def __init__(self, *args, naziv='G1'):
        super().__init__(*args)
        self.naziv = naziv
        self.naslov = f'Smicanje grede {naziv}'
        # Isti proračun kao u GUI-ju; međurezultati su atributi modela
        self.rezultat = self.proracun()

    def context(self):
        return dict(m=self, r=self.rezultat)

    def figures(self, out_dir, ext):
        from GUI.ConcreteElementsWindows.section_drawings import ShearDrawing
        ime = f'presek.{ext}'
        ShearDrawing().save_image(os.path.join(out_dir, ime), width_mm=40)
        return {'presek': ime}

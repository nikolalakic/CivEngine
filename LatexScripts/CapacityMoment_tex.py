"""Izveštaj za moment nosivosti preseka (po uzoru na RetainingWall2_tex.py)."""
import math

from GUI.ConcreteElementsWindows.capacity_moment import NosivostModel
from LatexScripts.report_engine import LatexReport


class CapacityMomentTex(NosivostModel, LatexReport):
    template_name = 'CapacityMoment.tex'
    naslov = 'Moment nosivosti preseka'
    ima_slike = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.t_presek = self.hfl_str != 'pravougaoni'
        # Proračun identičan onom u GUI-ju; NosivostModel puni self.detalji
        self.MRd, self.greska_ravnoteze, self.tip = self.nosivost()

    def context(self):
        d = self.detalji
        ctx = dict(m=self, d=d, t_presek=self.t_presek, MRd=self.MRd, tip=self.tip,
                   delta=self.greska_ravnoteze)
        if d['putanja'] == 'As1As2':
            ctx['tolerancija'] = 0.5
        elif d['putanja'] == 'As1':
            ctx['ksi_teci'] = 3.5 / (3.5 + d['es1_0']) if d['es1_0'] < 2.5 else None
            ctx['tolerancija'] = 0.5
        else:
            ctx['tolerancija'] = 1.0
        ctx['ravnoteza_ok'] = self.greska_ravnoteze <= ctx['tolerancija'] and not math.isnan(self.greska_ravnoteze)
        return ctx

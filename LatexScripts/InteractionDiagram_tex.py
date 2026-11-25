"""Izveštaj za dijagram interakcije (po uzoru na RetainingWall2_tex.py)."""
import os

from GUI.ConcreteElementsWindows.interaction_diagram import DijagramInterakcije
from LatexScripts.report_engine import LatexReport

# Redosled i opis stanja dilatacija (isti kao legenda dijagrama u GUI-ju)
STANJA = [
    ('centricni_pritisak', 'centricni', r'Centrični pritisak: $\varepsilon_{c2}/\varepsilon_{c1} = 2\text{‰}/2\text{‰}$'),
    ('granica_malog_ekscentriciteta', 'mali',
     r'Granica malog ekscentriciteta: $\varepsilon_{c2}/\varepsilon_{c1} = 3.5\text{‰}/0\text{‰}$'),
    ('tri_i_po_sa_dva_jedan_sedam_cetiri', 'veliki',
     r'Stanje $\varepsilon_{c2}/\varepsilon_{s1} = 3.5\text{‰}/-2.174\text{‰}$ (granica tečenja armature)'),
    ('tri_i_po_sa_deset', 'veliki', r'Stanje $\varepsilon_{c2}/\varepsilon_{s1} = 3.5\text{‰}/-10\text{‰}$'),
    ('tri_i_po_sa_dvadeset', 'veliki', r'Stanje $\varepsilon_{c2}/\varepsilon_{s1} = 3.5\text{‰}/-20\text{‰}$'),
    ('tri_i_po_sa_cetrdeset', 'veliki', r'Stanje $\varepsilon_{c2}/\varepsilon_{s1} = 3.5\text{‰}/-40\text{‰}$'),
]


class InteractionDiagramTex(DijagramInterakcije, LatexReport):
    template_name = 'InteractionDiagram.tex'
    naslov = 'Dijagram interakcije'

    def __init__(self, fck, k, b, h, d1, d2, MEd, NEd):
        super().__init__(fck, k, b, h, d1, d2, MEd, NEd)
        # Iste funkcije kao za crtanje dijagrama -- popunjavaju i self.stanja
        self.krive = {ime: getattr(self, ime)() for ime, _, _ in STANJA}

    def context(self):
        stanja = []
        for i, (ime, tip, opis) in enumerate(STANJA, start=1):
            st = dict(self.stanja[ime])
            st.update(ime=ime, tip=tip, opis=opis, broj=i)
            stanja.append(st)
        omege = self.gustina_omege()
        tabela = []
        for j, omega in enumerate(omege):
            red = [float(omega)]
            for ime, _, _ in STANJA:
                red += [float(self.krive[ime][0][j]), float(self.krive[ime][1][j])]
            tabela.append(red)
        return dict(m=self, stanja=stanja, tabela=tabela)

    def figures(self, out_dir, ext):
        from matplotlib.figure import Figure
        from GUI.ConcreteElementsWindows.section_drawings import InteractionDiagramDrawing

        presek = f'presek.{ext}'
        InteractionDiagramDrawing().save_image(os.path.join(out_dir, presek), width_mm=40)

        dijagram = f'dijagram.{ext}'
        fig = Figure(figsize=(9, 7))
        ax = fig.add_subplot(111)
        self.stampa_na_osi(ax)
        if ext == 'pdf':
            # PDF bez providnosti: pojedini čitači (npr. Master PDF Editor) pogrešno
            # primenjuju stanja providnosti (/CA, /ca), pa se linije grafika ne vide.
            fig.patch.set_visible(False)
            ax.patch.set_visible(False)
            ax.get_legend().get_frame().set_alpha(1)
        fig.savefig(os.path.join(out_dir, dijagram), bbox_inches='tight', dpi=200)
        return {'presek': presek, 'dijagram': dijagram}

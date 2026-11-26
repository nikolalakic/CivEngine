"""Glavni prozor: bočni meni sa kategorijama i kartice proračuna.

Novi proračun se dodaje jednim unosom u listu PRORACUNI (kategorija, grupa,
naziv, opis, modul sa klasom Window i, po želji, crtež za sličicu kartice).
Nova kategorija se dodaje u KATEGORIJE.
"""
import importlib

from PyQt6.QtCore import Qt, QRectF, QSize
from PyQt6.QtGui import QPainter, QPixmap, QPalette
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel,
                             QListWidget, QListWidgetItem, QStackedWidget, QScrollArea, QLineEdit,
                             QFrame, QSizePolicy)

from GUI.ConcreteElementsWindows import section_drawings as crtezi


KATEGORIJE = ['Beton', 'Čelik']

PRORACUNI = [
    dict(kategorija='Beton', grupa='Dimenzionisanje preseka (EN 1992-1-1)',
         naziv='Moment nosivosti preseka',
         opis='Nosivost pravougaonog ili T-preseka sa zadatom armaturom.',
         modul='GUI.ConcreteElementsWindows.capacity_moment', slika=crtezi.InteractionDiagramDrawing),
    dict(kategorija='Beton', grupa='Dimenzionisanje preseka (EN 1992-1-1)',
         naziv='Složeno savijanje',
         opis='Potrebna armatura za moment i aksijalnu silu.',
         modul='GUI.ConcreteElementsWindows.composite_bending', slika=crtezi.CompositeBendingDrawing),
    dict(kategorija='Beton', grupa='Dimenzionisanje preseka (EN 1992-1-1)',
         naziv='Smicanje',
         opis='Potrebne uzengije za silu smicanja VEd.',
         modul='GUI.ConcreteElementsWindows.shear', slika=crtezi.ShearDrawing),
    dict(kategorija='Beton', grupa='Dimenzionisanje preseka (EN 1992-1-1)',
         naziv='Dijagram interakcije',
         opis='M–N dijagram interakcije pravougaonog preseka.',
         modul='GUI.ConcreteElementsWindows.interaction_diagram', slika=crtezi.InteractionCurveDrawing),
    dict(kategorija='Beton', grupa='Seizmičko utezanje (EN 1998-1)',
         naziv='Utezanje stuba',
         opis='Kontrola utezanja kritične oblasti stuba uzengijama.',
         modul='GUI.ConcreteElementsWindows.column_bracing', slika=crtezi.ColumnBracingDrawing),
    dict(kategorija='Beton', grupa='Seizmičko utezanje (EN 1998-1)',
         naziv='Utezanje zida',
         opis='Kontrola utezanja krajeva duktilnog zida.',
         modul='GUI.ConcreteElementsWindows.wall_bracing', slika=crtezi.WallBracingDrawing),
]


def slicica(klasa, sirina, visina, boja):
    """Crtež preseka iscrtan u pixmap (bez okvira), za karticu."""
    pix = QPixmap(sirina, visina)
    pix.fill(Qt.GlobalColor.transparent)
    crtez = klasa(1, 1)
    crtez.fg = boja
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    crtez._paint_logical(p, QRectF(0, 0, sirina, visina))
    p.end()
    crtez.deleteLater()
    return pix


class Kartica(QPushButton):
    """Kartica proračuna: sličica, naziv i kratak opis."""

    SIRINA, VISINA = 220, 250

    def __init__(self, proracun, parent=None):
        super().__init__(parent)
        self.proracun = proracun
        self.setFixedSize(self.SIRINA, self.VISINA)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(proracun['opis'])
        self.setObjectName('kartica')
        self.setStyleSheet("""
            QPushButton#kartica {
                border: 1px solid palette(mid);
                border-radius: 10px;
                background-color: palette(base);
            }
            QPushButton#kartica:hover, QPushButton#kartica:focus {
                border: 2px solid palette(highlight);
            }
            QPushButton#kartica:pressed {
                background-color: palette(alternate-base);
            }
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(6)

        slika = QLabel()
        slika.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if proracun.get('slika'):
            boja = self.palette().color(QPalette.ColorRole.Text)
            dpr = self.devicePixelRatioF()
            pix = slicica(proracun['slika'], round(190 * dpr), round(108 * dpr), boja)
            pix.setDevicePixelRatio(dpr)
            slika.setPixmap(pix)
        slika.setFixedHeight(112)

        naziv = QLabel(proracun['naziv'])
        naziv.setAlignment(Qt.AlignmentFlag.AlignCenter)
        naziv.setWordWrap(True)
        naziv.setFixedHeight(44)   # mesta za naziv u dva reda
        naziv.setStyleSheet('font-size: 15px; font-weight: bold; background: transparent;')

        opis = QLabel(proracun['opis'])
        opis.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        opis.setWordWrap(True)
        opis.setStyleSheet('font-size: 12px; color: palette(placeholder-text); background: transparent;')

        for w in (slika, naziv, opis):
            w.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            lay.addWidget(w)
        lay.addStretch()

    def odgovara(self, tekst):
        tekst = tekst.lower()
        p = self.proracun
        return not tekst or any(tekst in p[k].lower() for k in ('naziv', 'opis', 'grupa'))


class StranaKategorije(QScrollArea):
    """Kartice jedne kategorije, grupisane; broj kolona prati širinu prozora."""

    RAZMAK = 14

    def __init__(self, proracuni, otvori, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)

        sadrzaj = QWidget()
        self.lay = QVBoxLayout(sadrzaj)
        self.lay.setContentsMargins(4, 4, 4, 4)
        self.lay.setSpacing(10)
        self.setWidget(sadrzaj)

        self.grupe = []   # (naslov, grid, [kartice])
        for grupa in dict.fromkeys(p['grupa'] for p in proracuni):
            naslov = QLabel(grupa)
            naslov.setStyleSheet('font-size: 16px; font-weight: bold; padding-top: 6px;')
            grid = QGridLayout()
            grid.setSpacing(self.RAZMAK)
            grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            kartice = []
            for p in proracuni:
                if p['grupa'] == grupa:
                    k = Kartica(p)
                    k.clicked.connect(lambda _, p=p: otvori(p))
                    kartice.append(k)
            self.lay.addWidget(naslov)
            self.lay.addLayout(grid)
            self.grupe.append((naslov, grid, kartice))

        self.prazno = QLabel('Nema proračuna u ovoj kategoriji.' if not proracuni
                             else 'Nijedan proračun ne odgovara pretrazi.')
        self.prazno.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prazno.setStyleSheet('font-size: 14px; color: palette(placeholder-text); padding: 40px;')
        self.lay.addWidget(self.prazno)
        self.lay.addStretch()

        self._kolone = 0
        self._filter = ''
        self.rasporedi()

    def _broj_kolona(self):
        sirina = self.viewport().width() - 8
        return max(1, (sirina + self.RAZMAK) // (Kartica.SIRINA + self.RAZMAK))

    def rasporedi(self, sila=True):
        kolone = self._broj_kolona()
        if not sila and kolone == self._kolone:
            return
        self._kolone = kolone
        ukupno = 0
        for naslov, grid, kartice in self.grupe:
            for k in kartice:
                grid.removeWidget(k)
            vidljive = [k for k in kartice if k.odgovara(self._filter)]
            for k in kartice:
                k.setVisible(k in vidljive)
            for i, k in enumerate(vidljive):
                grid.addWidget(k, i // kolone, i % kolone)
            naslov.setVisible(bool(vidljive))
            ukupno += len(vidljive)
        self.prazno.setVisible(ukupno == 0)
        return ukupno

    def filtriraj(self, tekst):
        self._filter = tekst.strip()
        return self.rasporedi()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.rasporedi(sila=False)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('CivEngine')
        self.setMinimumSize(720, 520)
        self.resize(1000, 720)
        self.prozori = {}

        glavni = QHBoxLayout(self)
        glavni.setContentsMargins(0, 0, 0, 0)
        glavni.setSpacing(0)

        # --- Bočni meni ---------------------------------------------------
        bocni = QFrame()
        bocni.setObjectName('bocni')
        bocni.setFixedWidth(190)
        bocni.setStyleSheet('QFrame#bocni { background-color: palette(alternate-base); '
                            'border-right: 1px solid palette(mid); }')
        bl = QVBoxLayout(bocni)
        bl.setContentsMargins(10, 16, 10, 12)

        logo = QLabel('CivEngine')
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet('font-size: 22px; font-weight: bold; padding-bottom: 12px;')
        bl.addWidget(logo)

        self.meni = QListWidget()
        self.meni.setFrameShape(QFrame.Shape.NoFrame)
        self.meni.setStyleSheet("""
            QListWidget { background: transparent; font-size: 15px; outline: none; }
            QListWidget::item { padding: 10px 12px; border-radius: 6px; margin: 1px 0; }
            QListWidget::item:selected { background-color: palette(highlight);
                                         color: palette(highlighted-text); }
            QListWidget::item:hover:!selected { background-color: palette(midlight); }
        """)
        bl.addWidget(self.meni)
        glavni.addWidget(bocni)

        # --- Desni deo: pretraga i kartice --------------------------------
        desno = QVBoxLayout()
        desno.setContentsMargins(20, 16, 12, 12)
        desno.setSpacing(10)

        gore = QHBoxLayout()
        self.naslov = QLabel()
        self.naslov.setStyleSheet('font-size: 24px; font-weight: bold;')
        self.pretraga = QLineEdit()
        self.pretraga.setPlaceholderText('Pretraga proračuna…')
        self.pretraga.setClearButtonEnabled(True)
        self.pretraga.setFixedWidth(260)
        self.pretraga.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        gore.addWidget(self.naslov)
        gore.addStretch()
        gore.addWidget(self.pretraga)
        desno.addLayout(gore)

        self.strane = QStackedWidget()
        desno.addWidget(self.strane)
        glavni.addLayout(desno)

        for kat in KATEGORIJE:
            proracuni = [p for p in PRORACUNI if p['kategorija'] == kat]
            item = QListWidgetItem(kat)
            item.setData(Qt.ItemDataRole.UserRole, kat)
            item.setSizeHint(QSize(0, 42))
            self.meni.addItem(item)
            self.strane.addWidget(StranaKategorije(proracuni, self.otvori))

        self.meni.currentRowChanged.connect(self.promeni_kategoriju)
        self.pretraga.textChanged.connect(self.pretrazi)
        self.meni.setCurrentRow(0)

    def promeni_kategoriju(self, red):
        if red < 0:
            return
        self.strane.setCurrentIndex(red)
        self.naslov.setText(KATEGORIJE[red])
        self.strane.currentWidget().rasporedi()

    def pretrazi(self, tekst):
        """Filtrira sve kategorije; u meniju prikazuje broj pogodaka."""
        pogoci = [self.strane.widget(i).filtriraj(tekst) for i in range(self.strane.count())]
        for i, kat in enumerate(KATEGORIJE):
            self.meni.item(i).setText(f'{kat}  ({pogoci[i]})' if tekst.strip() else kat)
        red = self.meni.currentRow()
        if tekst.strip() and pogoci[red] == 0 and any(pogoci):
            self.meni.setCurrentRow(next(i for i, n in enumerate(pogoci) if n))

    def otvori(self, proracun):
        """Otvara prozor proračuna; ako je već otvoren, vraća ga u prvi plan."""
        prozor = self.prozori.get(proracun['naziv'])
        if prozor is None or not prozor.isVisible():
            prozor = importlib.import_module(proracun['modul']).Window()
            self.prozori[proracun['naziv']] = prozor
        prozor.show()
        prozor.showNormal()
        prozor.raise_()
        prozor.activateWindow()

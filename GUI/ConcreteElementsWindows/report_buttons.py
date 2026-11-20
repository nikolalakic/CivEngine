"""Dugmići za generisanje izveštaja (PDF preko LaTeX-a, Word, LibreOffice)."""
import os

from PyQt6.QtCore import Qt, QStandardPaths, QUrl
from PyQt6.QtGui import QDesktopServices, QGuiApplication
from PyQt6.QtWidgets import (QGroupBox, QHBoxLayout, QPushButton, QFileDialog, QMessageBox)


class ReportButtons(QGroupBox):
    """Dugmići: PDF (LaTeX), Word (.docx), LibreOffice (.odt) i kopiranje LaTeX koda proračuna.

    napravi_izvestaj: funkcija bez argumenata koja čita ulazne podatke iz
    prozora i vraća objekat izveštaja (LatexReport); može da baci ValueError.
    podrazumevano_ime: predlog imena fajla (bez ekstenzije).
    """

    poslednji_folder = None  # pamti se između prozora

    def __init__(self, napravi_izvestaj, podrazumevano_ime, parent=None):
        super().__init__('Izveštaj', parent)
        self._napravi = napravi_izvestaj
        self._ime = podrazumevano_ime

        lay = QHBoxLayout(self)
        for fmt, tekst, opis in (('pdf', 'PDF (LaTeX)', 'Izveštaj u PDF formatu, preveden pdflatex-om'),
                                 ('docx', 'Word (.docx)', 'Izveštaj za Microsoft Word'),
                                 ('odt', 'LibreOffice (.odt)', 'Izveštaj za LibreOffice Writer')):
            btn = QPushButton(tekst)
            btn.setToolTip(opis)
            btn.clicked.connect(lambda _=False, f=fmt: self.generisi(f))
            lay.addWidget(btn)

        kopiraj = QPushButton('Kopiraj LaTeX')
        kopiraj.setToolTip('Kopira proračun (podpoglavlja, bez preambule) u clipboard,\n'
                           'za umetanje u drugi LaTeX izveštaj. Slike se snimaju u izabrani folder.')
        kopiraj.clicked.connect(self.kopiraj_latex)
        lay.addWidget(kopiraj)

    folder_slika = None  # pamti se između prozora

    def _izvestaj(self):
        try:
            return self._napravi()
        except ValueError as e:
            QMessageBox.critical(self, 'Greška u podacima',
                                 f'Proverite da li su sva polja ispravno popunjena.\n{e}')
        except Exception as e:
            QMessageBox.critical(self, 'Greška', f'Greška tokom proračuna:\n{e}')
        return None

    def kopiraj_latex(self):
        from LatexScripts.report_engine import ReportError

        izvestaj = self._izvestaj()
        if izvestaj is None:
            return
        ime = (self._ime() if callable(self._ime) else self._ime).replace(' ', '_')

        folder = None
        if izvestaj.ima_slike:
            if ReportButtons.folder_slika is None:
                pocetni = ReportButtons.poslednji_folder or QStandardPaths.writableLocation(
                    QStandardPaths.StandardLocation.DocumentsLocation)
                izabran = QFileDialog.getExistingDirectory(
                    self, 'Folder za slike iz proračuna (pamti se do zatvaranja programa)', pocetni)
                if not izabran:
                    return
                ReportButtons.folder_slika = izabran
            folder = ReportButtons.folder_slika

        QGuiApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            tekst = izvestaj.latex_sadrzaj(folder, prefiks=ime)
        except (ReportError, OSError) as e:
            QGuiApplication.restoreOverrideCursor()
            QMessageBox.critical(self, 'Greška pri kopiranju', str(e))
            return
        QGuiApplication.restoreOverrideCursor()

        QGuiApplication.clipboard().setText(tekst)
        poruka = 'LaTeX kod proračuna je kopiran u clipboard.'
        if folder:
            poruka += f'\n\nSlike su snimljene u:\n{folder}'
        QMessageBox.information(self, 'Kopirano', poruka)

    def generisi(self, fmt):
        from LatexScripts.report_engine import FORMATI, ReportError

        izvestaj = self._izvestaj()
        if izvestaj is None:
            return

        folder = ReportButtons.poslednji_folder or QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation)
        ime = (self._ime() if callable(self._ime) else self._ime).replace(' ', '_')
        putanja, _ = QFileDialog.getSaveFileName(
            self, 'Sačuvaj izveštaj', os.path.join(folder, f'{ime}.{fmt}'), FORMATI[fmt][1])
        if not putanja:
            return
        if not putanja.lower().endswith(f'.{fmt}'):
            putanja += f'.{fmt}'
        ReportButtons.poslednji_folder = os.path.dirname(putanja)

        QGuiApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            izvestaj.generate(fmt, putanja)
        except ReportError as e:
            QGuiApplication.restoreOverrideCursor()
            QMessageBox.critical(self, 'Greška pri generisanju izveštaja', str(e))
            return
        except Exception as e:
            QGuiApplication.restoreOverrideCursor()
            QMessageBox.critical(self, 'Greška pri generisanju izveštaja', f'Neočekivana greška:\n{e}')
            return
        QGuiApplication.restoreOverrideCursor()

        odgovor = QMessageBox.question(
            self, 'Izveštaj je sačuvan', f'Izveštaj je sačuvan u:\n{putanja}\n\nOtvoriti izveštaj?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if odgovor == QMessageBox.StandardButton.Yes:
            QDesktopServices.openUrl(QUrl.fromLocalFile(putanja))

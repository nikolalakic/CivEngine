"""Zajednički mehanizam za generisanje izveštaja (LaTeX -> PDF, Word, LibreOffice).

Princip je isti kao u RetainingWall2_tex.py: LaTeX šablon iz foldera
LatexTemplates se popunjava vrednostima iz proračuna. Razlika je u tome što
se koristi Jinja2, pa šablon može da sadrži i uslove (\\BLOCK{if ...}) -- tako
se u izveštaju prikazuju samo jednačine one grane proračuna koja je zaista
izvršena, i rezultati kontrola (zadovoljava / ne zadovoljava).

Isti popunjeni .tex fajl se:
  * prevodi pdflatex-om u PDF,
  * konvertuje pandoc-om (pypandoc-binary) u .docx (Word) i .odt (LibreOffice),
    sa jednačinama kao pravim (editabilnim) formulama.
"""
import datetime
import math
import re
import os
import shutil
import subprocess
import tempfile

import jinja2

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(ROOT_DIR, 'LatexTemplates')

FORMATI = {
    'pdf': ('PDF (LaTeX)', 'PDF dokument (*.pdf)'),
    'docx': ('Word', 'Word dokument (*.docx)'),
    'odt': ('LibreOffice', 'LibreOffice dokument (*.odt)'),
}


class ReportError(Exception):
    pass


# Oznake u šablonima između kojih je sam proračun (kopira se u drugi izveštaj)
POCETAK_SADRZAJA = '%% ---- POCETAK PRORACUNA ----'
KRAJ_SADRZAJA = '%% ---- KRAJ PRORACUNA ----'
ZAGLAVLJE_SADRZAJA = r"""% ======================================================================
% CivEngine: {naslov}
% Potrebno u preambuli izveštaja:
%   \usepackage{{amsmath, amssymb, graphicx, float, xcolor}}
%   \definecolor{{ok}}{{RGB}}{{0, 120, 0}}
%   \definecolor{{nok}}{{RGB}}{{190, 0, 0}}
% ======================================================================
"""


# ----------------------------------------------------------------------
# Filteri za šablone
# ----------------------------------------------------------------------
def broj(value, dec=2, zagrada=True):
    """Broj za ispis u jednačini; negativni brojevi idu u zagradu (osim u tabelama)."""
    if value is None:
        return '-'
    value = float(value)
    if math.isinf(value) or math.isnan(value):
        return r'\infty' if value > 0 else '-'
    if abs(value) < 0.5 * 10 ** (-dec):
        value = 0.0
    txt = f'{value:.{dec}f}'
    return f'({txt})' if value < 0 and zagrada else txt


def tex_escape(text):
    zamene = {
        '\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
        '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
    }
    return ''.join(zamene.get(c, c) for c in str(text))


_ALIGN_RE = re.compile(r'\\begin\{align\*\}(.*?)\\end\{align\*\}', re.S)


def razbij_align(tex):
    """align* -> niz pojedinačnih jednačina bez znakova poravnanja (&).

    Word/LibreOffice ne prikazuju pouzdano poravnate višelinijske formule
    (u LibreOffice-u se & pojavljuje kao '¿' ili kao doslovan znak), pa se za
    .docx/.odt svaki red prikazuje kao zasebna centrirana jednačina.
    """
    def zameni(m):
        izlaz = []
        leva = ''
        for red in re.split(r'\\\\', m.group(1)):
            red = red.strip()
            if not red:
                continue
            if '&' in red:
                lev, desn = red.split('&', 1)
                lev = lev.strip()
                if lev:
                    leva = lev
                else:
                    # Nastavak prethodnog reda ("&= ..."): ponavlja se leva strana,
                    # jer LibreOffice ne prihvata formulu koja počinje znakom "=".
                    lev = leva
                red = f'{lev} {desn.replace("&", " ").strip()}'
            izlaz.append(f'\\[ {red} \\]')
        return '\n'.join(izlaz)
    return _ALIGN_RE.sub(zameni, tex)


def _environment(fmt):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
        block_start_string=r'\BLOCK{', block_end_string='}',
        variable_start_string=r'\VAR{', variable_end_string='}',
        comment_start_string=r'\#{', comment_end_string='}',
        line_comment_prefix='%#',
        trim_blocks=True, lstrip_blocks=True,
        autoescape=False, undefined=jinja2.StrictUndefined,
    )
    env.filters['n'] = broj
    env.filters['tex'] = tex_escape

    def kontrola(uslov):
        """Oznaka rezultata kontrole (u math okruženju)."""
        if fmt == 'pdf':
            if uslov:
                return r'\rightarrow\ \textcolor{ok}{\checkmark\ \text{zadovoljava}}'
            return r'\rightarrow\ \textcolor{nok}{\times\ \text{ne zadovoljava}}'
        return r'\rightarrow\ \checkmark\ \text{zadovoljava}' if uslov else \
            r'\rightarrow\ \times\ \text{ne zadovoljava}'

    def uslov(ispunjen):
        """Neutralna oznaka uslova koji samo bira granu proračuna (nije kontrola)."""
        return r'\rightarrow\ \text{uslov je ispunjen}' if ispunjen else \
            r'\rightarrow\ \text{uslov nije ispunjen}'

    env.globals.update(kontrola=kontrola, uslov=uslov, fmt=fmt)
    return env


# ----------------------------------------------------------------------
# Osnovna klasa izveštaja
# ----------------------------------------------------------------------
class LatexReport:
    """Podklasa definiše šablon, kontekst (vrednosti) i slike."""

    template_name = None
    naslov = 'Izveštaj'
    ima_slike = True  # da li sadržaj proračuna uključuje slike (za kopiranje LaTeX-a)

    def context(self):
        raise NotImplementedError

    def figures(self, out_dir, ext):
        """Snima slike u out_dir, vraća {ime: naziv_fajla}."""
        return {}

    def render(self, fmt, out_dir):
        ext = 'pdf' if fmt == 'pdf' else 'png'
        slike = self.figures(out_dir, ext)
        ctx = dict(self.context())
        ctx.update(slike=slike, naslov=self.naslov, naziv=getattr(self, 'naziv', ''),
                   datum=datetime.date.today().strftime('%d.%m.%Y.'))
        tex = _environment(fmt).get_template(self.template_name).render(**ctx)
        tex_path = os.path.join(out_dir, 'izvestaj.tex')
        with open(tex_path, 'w', encoding='UTF-8') as f:
            f.write(tex)
        self._slike = slike
        return tex_path

    def latex_sadrzaj(self, folder_slika=None, prefiks='slika'):
        """LaTeX kod samog proračuna (podpoglavlja, bez preambule) za umetanje u drugi izveštaj.

        Slike se snimaju u folder_slika (pod imenom '<prefiks>_<ime>') i u kodu se
        navode apsolutnom putanjom, pa kod radi iz bilo kog foldera.
        """
        work = tempfile.mkdtemp(prefix='civengine_')
        try:
            with open(self.render('pdf', work), encoding='UTF-8') as f:
                tex = f.read()
            try:
                sadrzaj = tex.split(POCETAK_SADRZAJA, 1)[1].split(KRAJ_SADRZAJA, 1)[0].strip('\n')
            except IndexError as e:
                raise ReportError(f'Šablon {self.template_name} nema oznake početka/kraja proračuna.') from e
            if self._slike:
                if folder_slika is None:
                    raise ReportError('Nije izabran folder za slike.')
                os.makedirs(folder_slika, exist_ok=True)
                for fajl in self._slike.values():
                    cilj = os.path.abspath(os.path.join(folder_slika, f'{prefiks}_{fajl}'))
                    shutil.copyfile(os.path.join(work, fajl), cilj)
                    sadrzaj = sadrzaj.replace('{' + fajl + '}', '{' + cilj.replace(os.sep, '/') + '}')
        finally:
            shutil.rmtree(work, ignore_errors=True)
        return ZAGLAVLJE_SADRZAJA.format(naslov=self.naslov) + sadrzaj + '\n'

    def generate(self, fmt, output_path):
        if fmt not in FORMATI:
            raise ReportError(f'Nepoznat format izveštaja: {fmt}')
        work = tempfile.mkdtemp(prefix='civengine_')
        try:
            tex_path = self.render(fmt, work)
            if fmt == 'pdf':
                self._pdflatex(tex_path)
                shutil.copyfile(os.path.join(work, 'izvestaj.pdf'), output_path)
            else:
                self._pandoc(tex_path, fmt, output_path, work)
        finally:
            shutil.rmtree(work, ignore_errors=True)
        return output_path

    @staticmethod
    def _pdflatex(tex_path):
        exe = shutil.which('pdflatex')
        if exe is None:
            raise ReportError('pdflatex nije pronađen. Instalirajte TeX distribuciju '
                              '(TeX Live / MiKTeX) za izveštaj u PDF formatu.')
        work = os.path.dirname(tex_path)
        r = subprocess.run([exe, '-interaction=nonstopmode', '-halt-on-error', os.path.basename(tex_path)],
                           cwd=work, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if r.returncode != 0 or not os.path.exists(os.path.join(work, 'izvestaj.pdf')):
            log = r.stdout.splitlines()
            greske = [i for i, l in enumerate(log) if l.startswith('!')]
            od = greske[0] if greske else max(0, len(log) - 15)
            raise ReportError('Greška pri prevođenju LaTeX dokumenta:\n' + '\n'.join(log[od:od + 15]))

    @staticmethod
    def _pandoc(tex_path, fmt, output_path, work):
        try:
            import pypandoc
        except ImportError as e:
            raise ReportError('Paket pypandoc-binary nije instaliran (uv sync).') from e
        with open(tex_path, encoding='UTF-8') as f:
            tex = f.read()
        with open(tex_path, 'w', encoding='UTF-8') as f:
            f.write(razbij_align(tex))
        try:
            pypandoc.convert_file(tex_path, fmt, format='latex', outputfile=output_path,
                                  extra_args=['--resource-path', work], cworkdir=work)
        except (RuntimeError, OSError) as e:
            raise ReportError(f'Greška pri konverziji u {fmt}:\n{e}') from e

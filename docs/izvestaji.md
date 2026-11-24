# Izveštaji

[← Sadržaj](README.md) · Kod: [`report_engine.py`](../LatexScripts/report_engine.py), [`report_buttons.py`](../GUI/ConcreteElementsWindows/report_buttons.py) · Šabloni: [`LatexTemplates/`](../LatexTemplates)

Svaki prozor proračuna ima grupu dugmića **Izveštaj**:

| Dugme | Rezultat | Potrebno |
|---|---|---|
| PDF (LaTeX) | PDF dokument | `pdflatex` (TeX Live / MiKTeX) |
| Word (.docx) | Word dokument sa editabilnim formulama | paket `pypandoc-binary` (sadrži pandoc) |
| LibreOffice (.odt) | Writer dokument sa editabilnim formulama | paket `pypandoc-binary` |
| Kopiraj LaTeX | LaTeX kod proračuna u clipboard-u, za umetanje u drugi izveštaj | – |

## Sadržaj izveštaja

Izveštaj prati korake opisane na stranicama pojedinačnih funkcija. Svaka jednačina se prikazuje u tri koraka:
opšti oblik, oblik sa zamenjenim brojevima i rezultat. Prikazuju se samo grane proračuna koje je program zaista
izvršio (npr. samo izraz za $\mu_\phi$ koji odgovara odnosu $T_1$ i $T_C$). Kontrole su označene sa
„zadovoljava“ / „ne zadovoljava“, a uslovi koji samo biraju granu proračuna sa „uslov je (nije) ispunjen“.

## Kako radi

1. Klasa izveštaja (npr. `ColumnBracingTex` u [`LatexScripts/ColumnBracing_tex.py`](../LatexScripts/ColumnBracing_tex.py))
   nasleđuje klasu proračuna, izvršava isti proračun kao GUI i iz `self.detalji` uzima međurezultate.
2. Šablon iz [`LatexTemplates/`](../LatexTemplates) popunjava se pomoću Jinja2 (`\VAR{...}` za vrednosti,
   `\BLOCK{if ...}` za uslove). Zajednička preambula je u [`_preamble.tex`](../LatexTemplates/_preamble.tex).
3. Popunjeni `.tex` se prevodi `pdflatex`-om u PDF, ili pandoc-om u `.docx` / `.odt`. Za Word i LibreOffice se
   višelinijske poravnate jednačine (`align*`) razbijaju na pojedinačne jednačine, jer ih ti programi ne prikazuju pouzdano.
4. Crteži preseka se snimaju kao vektorski PDF (za LaTeX) ili PNG 300 dpi (za Word/ODT).

## Kopiranje LaTeX koda u drugi izveštaj

Dugme **Kopiraj LaTeX** kopira samo proračun (bez preambule i naslova), podeljen na `\subsection`, pa se može
nalepiti ispod nekog `\section` u vašem izveštaju. Pri prvom kopiranju bira se folder u koji se snimaju slike;
kod ih navodi apsolutnom putanjom. Na početku kopiranog koda je komentar sa paketima potrebnim u preambuli:

```latex
\usepackage{amsmath, amssymb, graphicx, float, xcolor}
\definecolor{ok}{RGB}{0, 120, 0}
\definecolor{nok}{RGB}{190, 0, 0}
```

## Dodavanje izveštaja za novu funkciju

1. U klasi proračuna sačuvati međurezultate u `self.detalji` (bez menjanja samog proračuna).
2. Napraviti klasu `NazivTex(KlasaProracuna, LatexReport)` sa `template_name`, `context()` i `figures()`.
3. Napraviti šablon `LatexTemplates/Naziv.tex` koji počinje sa `\BLOCK{include '_preamble.tex'}` i ima oznake
   `%% ---- POCETAK PRORACUNA ----` i `%% ---- KRAJ PRORACUNA ----` oko sadržaja.
4. U prozoru dodati `ReportButtons(self.napravi_izvestaj, 'Ime_fajla')`.

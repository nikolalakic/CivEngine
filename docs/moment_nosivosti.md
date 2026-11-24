# Moment nosivosti preseka

[← Sadržaj](README.md) · Kod: [`capacity_moment.py`](../GUI/ConcreteElementsWindows/capacity_moment.py) · Izveštaj: [`CapacityMoment_tex.py`](../LatexScripts/CapacityMoment_tex.py), [`CapacityMoment.tex`](../LatexTemplates/CapacityMoment.tex)

## 1. Namena

Proračun momenta nosivosti $M_{Rd}$ armiranobetonskog preseka pri zadatoj aksijalnoj sili $N_{Ed}$, za:

- pravougaoni presek sa jednostrukom armaturom ($A_{s2} = 0$),
- pravougaoni presek sa dvostrukom armaturom ($A_{s2} > 0$),
- T-presek (flanša širine $b_{eff}$, rebro širine $b_w$), sa jednostrukom armaturom.

Položaj neutralne linije se određuje iz uslova ravnoteže sila, a moment nosivosti se svodi na težište preseka.

## 2. Ulazni podaci

| Oznaka | Polje u GUI | Jedinica | Napomena |
|---|---|---|---|
| – | Tip preseka | – | Pravougaoni presek / T-presek |
| $f_{ck}$ | fck | MPa | mora biti standardna klasa iz [`MaterialData/BetonPodaci.csv`](../MaterialData/BetonPodaci.csv) |
| $N_{Ed}$ | Ned | kN | pritisak + |
| $b$ | Širina preseka b | cm | za T-presek: širina rebra $b_w$ |
| $h$ | Visina poprečnog preseka h | cm | |
| $d_1$ | Rastojanje d1 | cm | težište zategnute armature od donje ivice |
| $A_{s1}$ | Zategnuta armatura As1 | cm² | |
| $A_{s2}$, $d_2$ | Pritisnuta armatura As2, Rastojanje d2 | cm², cm | samo za pravougaoni presek |
| $h_f$, $b_{eff}$, $b_w$ | Visina flanše, Efektivna širina, Širina rebra | cm | samo za T-presek |

## 3. Teorijska osnova i formule

### 3.1 Materijal i pretpostavke

```math
f_{cd} = 0.85 \cdot \frac{f_{ck}}{1.5}, \qquad f_{yd} = \frac{500}{1.15}, \qquad E_s = 200 \ \mathrm{GPa}, \qquad d = h - d_1
```

Važe pretpostavke iz **EN 1992-1-1, 6.1(2)P** (ravni preseci, ista dilatacija armature i betona, beton ne prima
zatezanje, dijagram parabola–pravougaonik iz **3.1.7** i bilinearni dijagram armature iz **3.2.7**, Slika 3.8).
Dilatacija na pritisnutoj ivici je $\varepsilon_c = \varepsilon_{cu2} = 3.5$‰ (**6.1(3)P**, Tabela 3.1).

Napon u armaturi (bilinearni dijagram sa horizontalnom gornjom granom, **3.2.7(2)b**):

```math
\sigma_s = \max\left(-f_{yd};\ \min\left(E_s \, \varepsilon_s;\ f_{yd}\right)\right)
```

### 3.2 Ravnoteža sila i moment

Koeficijenti pritisnute zone za $\varepsilon_c = 3.5$‰ su $\alpha_v = 0.81$ i $k_a = 0.416$
([zajedničke osnove](README.md#koeficijenti-pritisnute-zone-betona)). Sa $\xi = x/d$:

```math
F_c = 0.81 \cdot \xi \, d \cdot b \cdot f_{cd}, \qquad z = d - 0.416 \, x = \zeta \, d, \quad \zeta = 1 - 0.416 \, \xi
```

Moment nosivosti u odnosu na težište zategnute armature $M_{Rd,s}$ svodi se na težište preseka:

```math
M_{Rd} = M_{Rd,s} - N_{Ed} \left(\frac{h}{2} - d_1\right)
```

### 3.3 Pravougaoni presek sa jednostrukom armaturom ($A_{s2} = 0$)

Početna procena uz pretpostavku da armatura teče:

```math
\xi = \frac{A_{s1} f_{yd} + N_{Ed}}{0.81 \, b \, d \, f_{cd}}, \qquad
\varepsilon_{s1} = \frac{1 - \xi}{\xi} \cdot 3.5 ‰
```

Ako je $\varepsilon_{s1} \geq 2.5$‰, procena se usvaja. U suprotnom se $\xi$ određuje iterativno (korak 0.0001, polazeći
od $\xi = 2$) iz uslova

```math
0.81 \, \xi \, d \, b \, f_{cd} - A_{s1} \, \frac{\varepsilon_{s1}}{2.5} \, f_{yd} - N_{Ed} = 0, \qquad \varepsilon_{s1} \leq 2.5 ‰
```

do tačnosti $|\Delta N| \leq 0.5$ kN. Zatim je

```math
M_{Rd,s} = 0.81 \, \xi \, (1 - 0.416 \, \xi) \, b \, d^2 \, f_{cd}
```

### 3.4 Pravougaoni presek sa dvostrukom armaturom ($A_{s2} > 0$)

```math
\varepsilon_{s2} = 3.5 \, \frac{\xi - d_2/d}{\xi}, \quad |\varepsilon_{s2}| \leq 2.175 ‰, \qquad F_{s2} = A_{s2} \, \varepsilon_{s2} \, E_s
```

Za $x < d$ armatura $A_{s1}$ je zategnuta, a za $x \geq d$ pritisnuta:

```math
x < d: \ \ \varepsilon_{s1} = 3.5 \, \frac{1 - \xi}{\xi}, \ \ F_{s1} = -A_{s1} \, \sigma_s(\varepsilon_{s1}); \qquad
x \geq d: \ \ \varepsilon_{s1} = 3.5 \, \frac{\xi - 1}{\xi} \leq 2.175 ‰, \ \ F_{s1} = +A_{s1} \, \varepsilon_{s1} \, E_s
```

Uslov ravnoteže, rešava se polovljenjem intervala $0.01 \leq \xi \leq 3.0$ do $|\Delta N| < 0.5$ kN ($\Delta N$ monotono raste sa $\xi$):

```math
\Delta N = F_c + F_{s2} + F_{s1} - N_{Ed} = 0
```

Moment oko težišta armature $A_{s1}$ (sila $A_{s1}$ nema krak):

```math
M_{Rd,s} = F_c \, \zeta \, d + F_{s2} \, (d - d_2)
```

### 3.5 T-presek

**Položaj neutralne linije.** Proverava se ravnoteža za $x = h_f$ (pritisnuta je cela flanša):

```math
\Delta N(h_f) = 0.8095 \, h_f \, b_{eff} \, f_{cd} - A_{s1} \, \sigma_s\!\left(\frac{3.5 \, d}{h_f} - 3.5\right) - N_{Ed}
```

- $\Delta N(h_f) \geq 0$: neutralna linija je u flanši, presek se računa kao pravougaoni širine $b = b_{eff}$ (poglavlje 3.3).
- $\Delta N(h_f) < 0$: neutralna linija je u rebru.

**Neutralna linija u rebru.** Pritisnuta zona se deli na pravougaonik širine $b_{eff}$ i visine $x$, umanjen za deo širine
$b_{eff} - b_w$ ispod flanše (od $h_f$ do $x$), u kome je najveća dilatacija $\varepsilon_{cf}$:

```math
\varepsilon_{cf} = \varepsilon_c \, \frac{x - h_f}{x}, \qquad
\varepsilon_{s1} = \frac{\varepsilon_c}{x} \, d - \varepsilon_c
```

```math
F_{c1} = \alpha_v(\varepsilon_c) \, x \, b_{eff} \, f_{cd}, \qquad
F_{c2} = \alpha_v(\varepsilon_{cf}) \, (x - h_f) \, (b_{eff} - b_w) \, f_{cd}, \qquad
F_{s1} = A_{s1} \, \sigma_s(\varepsilon_{s1})
```

Ravnoteža $\Delta N = F_{c1} - F_{c2} - F_{s1} - N_{Ed} = 0$ rešava se polovljenjem intervala $h_f \leq x \leq h$, do $|\Delta N| \leq 1$ kN:

```math
M_{Rd,s} = F_{c1} \, (d - 0.416 \, x) - F_{c2} \left(d - h_f - k_a(\varepsilon_{cf}) \, (x - h_f)\right)
```

$\alpha_v(\varepsilon)$ i $k_a(\varepsilon)$ su koeficijenti iz [zajedničkih osnova](README.md#koeficijenti-pritisnute-zone-betona)
(u kodu `beta11`, `beta12`, `beta21`, `beta22`).

## 4. Tok proračuna u programu

Klasa `NosivostModel`:

| Korak | Metoda | Šta radi |
|---|---|---|
| 1 | `__init__` | Jedinice (cm → m, cm² → m²); proverava da li je $f_{ck}$ standardna klasa (CSV); $f_{cd}$, $f_{yd}$, $E_s$. Za pravougaoni presek $h_f = 10^{10}$ (flanša ne postoji). |
| 2 | `napon_armature(eps)` | $\sigma_s$ po bilinearnom dijagramu, ograničeno na $\pm f_{yd}$. |
| 3 | `nosivost()` | Bira putanju: $A_{s2} = 0$ (pravougaoni ili T) ili $A_{s2} > 0$. Za T-presek poziva `stanje_t_preseka(hf)` i odlučuje da li je neutralna linija u flanši. |
| 4 | `stanje_t_preseka(x)` | Sile $F_{c1}$, $F_{c2}$, $F_{s1}$ i $\Delta N$ u T-preseku za zadato $x$. |
| 5 | `tpresek()` | Polovljenje intervala $h_f \leq x \leq h$; $M_{Rd}$ za neutralnu liniju u rebru. |
| 6 | povratna vrednost | `(MRd, greška ravnoteže, tip proračuna)`; međurezultati se čuvaju u `self.detalji` (za izveštaj). |

## 5. Rezultati i kontrole

Prikazuju se tip proračuna, moment nosivosti $M_{Rd}$ [kNm] i greška ravnoteže sila $|\Delta N|$ [kN].
Kontrola ravnoteže: $|\Delta N| \leq 0.5$ kN (pravougaoni preseci), odnosno $\leq 1.0$ kN (T-presek).
Ako ravnoteža nije postignuta, izveštaj to označava kao „ne zadovoljava“ i daje upozorenje.

Ako T-presek ne može da primi zadatu silu ni za $x = h$, javlja se greška.

## 6. Pretpostavke i odstupanja od Evrokoda

- Koristi se $\alpha_{cc} = 0.85$ (preporuka EN 1992-1-1 je 1.0, vrednost propisuje nacionalni aneks).
- Uvek se pretpostavlja $\varepsilon_c = 3.5$‰ na pritisnutoj ivici. Za preseke koji su ceo pritisnuti ($x > h$) EN 1992-1-1,
  6.1(5) i Slika 6.1 ograničavaju dilataciju (obrtanje oko tačke C), a program to ne radi; takođe $F_c = 0.81\,x\,b\,f_{cd}$ tada
  uzima pritisnutu zonu veću od preseka.
- U putanji $A_{s2} = 0$ tečenje armature se računa od 2.5‰ (napon $\frac{\varepsilon_{s1}}{2.5} f_{yd}$), a ne od $\varepsilon_{yd} = 2.174$‰.
  Uslov $\xi > 0.583$ je u toj grani uvek ispunjen ($\varepsilon_{s1} < 2.5$‰ $\Leftrightarrow \xi > 3.5/6 = 0.583$).
- Granica tečenja u putanji $A_{s2} > 0$ je 2.175‰.
- Pritisnuta armatura kod T-preseka nije obuhvaćena.

# CivEngine — dokumentacija proračuna

Ova dokumentacija opisuje teorijsku osnovu i tok proračuna za svaku funkciju programa.
Svaka stranica je organizovana na isti način:

1. **Namena** — šta se proračunava.
2. **Ulazni podaci** — veličine iz GUI-ja, sa jedinicama.
3. **Teorijska osnova i formule** — izrazi po Evrokodu, sa navedenim članovima.
4. **Tok proračuna u programu** — koje klase/funkcije sprovode koje korake.
5. **Rezultati i kontrole** — šta program prikazuje i kada kontrola (ne) zadovoljava.
6. **Pretpostavke i odstupanja** — šta je u programu pojednostavljeno ili drugačije od Evrokoda.

## Funkcije programa

| Funkcija (GUI) | Stranica | Kod |
|---|---|---|
| Dijagram interakcije | [dijagram_interakcije.md](dijagram_interakcije.md) | [`interaction_diagram.py`](../GUI/ConcreteElementsWindows/interaction_diagram.py) |
| Moment nosivosti preseka | [moment_nosivosti.md](moment_nosivosti.md) | [`capacity_moment.py`](../GUI/ConcreteElementsWindows/capacity_moment.py) |
| Složeno savijanje | [slozeno_savijanje.md](slozeno_savijanje.md) | [`composite_bending.py`](../GUI/ConcreteElementsWindows/composite_bending.py) |
| Smicanje | [smicanje.md](smicanje.md) | [`shear.py`](../GUI/ConcreteElementsWindows/shear.py) |
| Utezanje stuba | [utezanje_stuba.md](utezanje_stuba.md) | [`column_bracing.py`](../GUI/ConcreteElementsWindows/column_bracing.py) |
| Utezanje zida | [utezanje_zida.md](utezanje_zida.md) | [`wall_bracing.py`](../GUI/ConcreteElementsWindows/wall_bracing.py) |
| Izveštaji (PDF / Word / LibreOffice / LaTeX) | [izvestaji.md](izvestaji.md) | [`LatexScripts/`](../LatexScripts) |

## Zajedničke osnove

### Materijali — SRPS EN 1992-1-1

Proračunska čvrstoća betona na pritisak, **EN 1992-1-1, 3.1.6(1)P, izraz (3.15)**:

```math
f_{cd} = \alpha_{cc} \cdot \frac{f_{ck}}{\gamma_c}
```

Parcijalni koeficijenti za stalne i prolazne proračunske situacije, **EN 1992-1-1, 2.4.2.4(1), Tabela 2.1N**:
$\gamma_c = 1.5$ (beton), $\gamma_s = 1.15$ (armatura).

> Program koristi $\alpha_{cc} = 0.85$. Preporučena vrednost u EN 1992-1-1 je $\alpha_{cc} = 1.0$,
> a konačnu vrednost (između 0.8 i 1.0) propisuje nacionalni aneks.

Proračunska granica razvlačenja armature (B500, $f_{yk} = 500$ MPa) i modul elastičnosti,
**EN 1992-1-1, 3.2.7 (Slika 3.8) i 3.2.7(4)**:

```math
f_{yd} = \frac{f_{yk}}{\gamma_s} = \frac{500}{1.15} = 434.78 \ \mathrm{MPa}, \qquad
E_s = 200 \ \mathrm{GPa}, \qquad
\varepsilon_{yd} = \frac{f_{yd}}{E_s} = 2.174 ‰
```

Za proračun preseka koristi se dijagram parabola–pravougaonik, **EN 1992-1-1, 3.1.7(1), izrazi (3.17) i (3.18), Tabela 3.1**
(za $f_{ck} \leq 50$ MPa: $\varepsilon_{c2} = 2.0$‰, $\varepsilon_{cu2} = 3.5$‰, $n = 2$):

```math
\sigma_c = f_{cd}\left[1 - \left(1 - \frac{\varepsilon_c}{\varepsilon_{c2}}\right)^{n}\right] \quad \text{za } 0 \leq \varepsilon_c \leq \varepsilon_{c2},
\qquad
\sigma_c = f_{cd} \quad \text{za } \varepsilon_{c2} \leq \varepsilon_c \leq \varepsilon_{cu2}
```

### Koeficijenti pritisnute zone betona

Integracijom dijagrama parabola–pravougaonik po visini pritisnute zone $x$ dobija se rezultanta
$F_c = \alpha_v \cdot x \cdot b \cdot f_{cd}$, koja deluje na rastojanju $k_a \cdot x$ od pritisnute ivice.
Koeficijenti zavise od dilatacije na pritisnutoj ivici $\varepsilon_c$ (u ‰):

| Dilatacija | Koeficijent punoće $\alpha_v$ | Položaj rezultante $k_a$ |
|---|---|---|
| $0 \leq \varepsilon_c \leq 2$‰ | $\dfrac{\varepsilon_c (6 - \varepsilon_c)}{12}$ | $\dfrac{8 - \varepsilon_c}{4 (6 - \varepsilon_c)}$ |
| $2 \leq \varepsilon_c \leq 3.5$‰ | $\dfrac{3 \varepsilon_c - 2}{3 \varepsilon_c}$ | $\dfrac{\varepsilon_c (3 \varepsilon_c - 4) + 2}{2 \varepsilon_c (3 \varepsilon_c - 2)}$ |

Za $\varepsilon_c = \varepsilon_{cu2} = 3.5$‰: $\alpha_v = 0.8095 \approx 0.81$ i $k_a = 0.416$.
To su vrednosti koje se u programu pojavljuju kao `0.81` i `0.416`.
U kodu se $\alpha_v$ zove `beta1…` (npr. `beta11`, `beta12`), a $k_a$ zove `beta2…` (`beta2_koeficijent`, `beta21`, `beta22`).

### Pretpostavke proračuna preseka — EN 1992-1-1, 6.1

**6.1(2)P:** ravni preseci ostaju ravni; dilatacija armature jednaka je dilataciji okolnog betona;
čvrstoća betona na zatezanje se zanemaruje; naponi u betonu slede iz 3.1.7, a u armaturi iz 3.2.7 (Slika 3.8).
**6.1(3)P:** dilatacija pritiska u betonu ograničena je na $\varepsilon_{cu2}$.
**6.1(5):** kod približno centrično pritisnutih delova preseka srednja dilatacija se ograničava na $\varepsilon_{c2}$.
**6.1(6), Slika 6.1:** mogući oblici raspodele dilatacija u graničnom stanju nosivosti.

### Seizmička pravila — SRPS EN 1998-1

Utezanje stubova i zidova sprovodi se po pravilima za klasu duktilnosti DCM
(**EN 1998-1, 5.4.3.2.2** za stubove i **5.4.3.4.2** za zidove).
Faktor duktilnosti krivine $\mu_\phi$ određuje se po **EN 1998-1, 5.2.3.4(3), izrazi (5.4) i (5.5)**:

```math
\mu_\phi = 2 q_0 - 1 \quad \text{za } T_1 \geq T_C, \qquad
\mu_\phi = 1 + 2 (q_0 - 1) \frac{T_C}{T_1} \quad \text{za } T_1 < T_C
```

Za armaturu klase B $\mu_\phi$ se povećava 1.5 puta (**EN 1998-1, 5.2.3.4(4)**).
Kod zidova se $q_0$ zamenjuje sa $q_0 \cdot M_{Ed}/M_{Rd}$ (**5.4.3.4.2(2)**); detalji su na stranicama o utezanju.

## Jedinice i oznake

- Dimenzije preseka se u GUI unose u **cm**, armatura u **cm²**, sile u **kN**, momenti u **kNm**, $f_{ck}$ u **MPa**.
- Aksijalna sila je **pozitivna za pritisak**.
- Dilatacije se prikazuju u **‰**.

## Literatura

- SRPS EN 1992-1-1 (EN 1992-1-1:2004), Evrokod 2: Projektovanje betonskih konstrukcija — Deo 1-1: Opšta pravila i pravila za zgrade.
- SRPS EN 1998-1 (EN 1998-1:2004), Evrokod 8: Projektovanje seizmički otpornih konstrukcija — Deo 1: Opšta pravila, seizmička dejstva i pravila za zgrade.
- Brojevi članova i izraza u ovoj dokumentaciji odnose se na EN 1992-1-1:2004 i EN 1998-1:2004.
- Važeći nacionalni aneksi (vrednosti $\alpha_{cc}$, $\gamma_c$, $\gamma_s$, $q_0$, $T_C$).

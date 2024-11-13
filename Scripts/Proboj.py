import math, os
import pandas as pd

if 'BetonPodaci.csv' not in os.listdir():
    print('BetonPodaci.csv se ne nalazi u radnom folderu!')
    exit()
else:
    df = pd.read_csv('BetonPodaci.csv', delimiter = ';', encoding = 'UTF-8', skipinitialspace = True)
    fck_lista = df['fck [Mpa]'].to_list()
    fckMPA = int(input('Unesi karakteristicnu cvrstocu betona na pritisal fck [MPa]: '))
if fckMPA in fck_lista:
    indeks = fck_lista.index(fckMPA)
else:
    print(f'{fckMPA} nije standardna karakteristicna cvrstoca betona, pogledaj u tabeli za standardne cvrstoce!')
    exit()
d = float(input('Prosecna staticka visina [cm]: '))
d = d/100
ro = float(input('Koeficijent armiranja [%], maksimalan je 2%: '))
print('\nZa ivicni stub h je strana paralelna ivici ploce\n')
b = int(input('Unesi sirinu pravougaonog stuba b [cm]: '))
b = b/100
h = int(input('Unesi visinu pravougaonog stuba h [cm]: '))
h=h/100

if d > 0.2:
    k = float(1+math.sqrt(200/(d*math.pow(10, 3))))
elif d <= 0.2:
    k = 2

NiMin = float(0.035*math.sqrt(fckMPA)*math.pow(k, 1.5)*1000)
NiRDC = float(0.12*k*math.pow(ro*fckMPA, 1/3))*1000
if NiMin >= NiRDC:
   NiRDC = NiMin

NiRdcMAX = float(0.5*0.6*(1-fckMPA/250)*0.85*fckMPA/1.5*1000)
VEd = float(input('Unesi transverzalnu silu proboja V,Ed [kN]: '))
beta = float(input('Unesi koeficijent \u03B2; \u03B2=1.15 (sredisnji stub); \u03B2=1.4 (ivicni stub); \u03B2=1.5 (ugaoni stub) '))
if beta == 1.15:
    u0 = 2*b + 2*h
    u1 = 2*b + 2*h + 2*2*d*math.pi
elif beta == 1.5:
    u0 = b + h
    u1 = b + h + 0.25*2*2*d*math.pi
elif beta == 1.4:
    u0 = 2*b + h
    u1 = 2*b + h + 0.5*2*2*d*math.pi
else:
    print('\nSkripta radi samo za uobicajene slucajeve \u03B2!')
    exit()

NiEd_0 = (beta*VEd)/(d*u0)
NiEd_1 = (beta*VEd)/(d*u1)
if NiEd_1 > NiRDC and NiEd_1 > 1.5*NiRDC and NiEd_0 < NiRdcMAX:
    print('\n>>>>> Potrebno je osiguranje kapitelom.')
elif NiEd_1 < NiRDC and NiEd_0 < NiRdcMAX:
    print("\n>>>> Nije potrebno osiguranje armaturom")
elif NiEd_1 > NiRDC and NiEd_1 < NiRDC*1.5 and NiEd_0 < NiRdcMAX:
    print('\n>>>>> Potrebno je osiguranje armaturom.')
elif NiEd_0 > NiRdcMAX:
    print('\n>>>>> Napon na ivici stuba NE prolazi!')

print('\nMinimalni napon nosivosti: \u03BD,min= ', round(NiMin, 3), '[KPa]')
print("Napon na ivici stuba: \u03BD,Ed,0= ", round(NiEd_0, 3), '[KPa]')
print('Napon pri pojavi prsline: \u03BD,Rd,c= ',round(NiRDC, 3), '[KPa]')
print('1.5*\u03BD,Rd,c= ',round(NiRDC*1.5, 3), '[KPa]')
print('Napon na osnovnom kontrolnom obimu: \u03BD,Ed,1= ', round(NiEd_1, 3), '[KPa]')
print('Maksimalni dozvoljeni napon: \u03BD,Rd,max= ',round(NiRdcMAX, 3) , '[KPa]')


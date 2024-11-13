import math, os
import numpy as np
import pandas as pd
if 'BetonPodaci.csv' not in os.listdir():
    print('BetonPodaci.csv se ne nalazi u radnom folderu!')
    exit()
else:
    df = pd.read_csv('BetonPodaci.csv', delimiter = ';', skipinitialspace = True, encoding = 'UTF-8')
    fck_lista = df['fck [Mpa]'].to_list()
    Ecm_lista = df['Ecm [Gpa]'].to_numpy()
    fctm_lista = df['fctm [Mpa]'].to_numpy()
    klaseizlozenosti_lista = df['KlaseIzlozenosti'].to_list()
print('>>>Skripta daje rezultat za savijanje i zatezanje za preseke sa rebrastom armaturom bez prednaprezanja!<<<')

fckMPA = int(input('\nUnesi marku betona [MPa]: '))

for i in fck_lista:
    if fckMPA == i:
        indeks = fck_lista.index(fckMPA)
        break
    if fckMPA not in fck_lista:
        print(f'Cvrstoca {fckMPA} nije u listi cvrstoca!')
        exit()

Ecm = Ecm_lista[indeks]
Ecm = 1.05*Ecm
Es = 200
alfa = Es/(Ecm)
fctm = fctm_lista[indeks]
klasaizlozenosti = str(input('Unesi klasu izlozenosti (x0,xc1, xc2, itd): '))
klasaizlozenosti = klasaizlozenosti.lower()

if klasaizlozenosti == 'x0' or klasaizlozenosti == 'xc1': 
    dozprslina = 0.4
elif klasaizlozenosti != 'x0' and klasaizlozenosti != 'xc1':
    dozprslina = 0.3
if klasaizlozenosti not in klaseizlozenosti_lista:
    print('Nepostojeca klasa izlozenosti ' + klasaizlozenosti, '!')
    exit()

SigmaS1 = float(input('Unesi napon u armaturi \u03C3s1 [MPa]: '))
kt = str(input('Kratkotrajno ili dugotrajno opterecenje? '))
kt = kt.lower()
kt = kt.replace(' ', '')
if kt == 'kratkotrajno':
    kt = 0.6
    alfa = Es/Ecm
elif kt == 'dugotrajno':
    kt = 0.4
    fieff = float(input('Unesi koeficijent tecenja \u03C6,eff: '))
    Eceff = Ecm/(1+fieff)
    alfa = Es/Eceff
else:
    print('Unesi lepo "kratkotrajno" ili "dugotrajno"')
    exit()

k2 = str(input('Savijanje ili zatezanje? '))
k2 = k2.lower()
if k2 == 'savijanje':
    k2 = 0.5
    d = float(input('Unesi staticku visinu d [cm]: '))
    beff = float(input('Unesi efektivnu sirinu [pritisnutu] sirinu preseka beff [cm]: '))
    b = float(input('Unesi zategnutu sirinu preseka b [cm]: '))
    d1 = float(input('Unesi rastojanje od zategnute ivice to tezista zategnute armature d1 [cm]: '))
    d2 = 0
    h = d+d1
    n1 = float(input('Unesi broj sipki u prvom redu zategnute zone [kom]: '))
    fi1 = float(input('Unesi \u03A6 sipki u prvom redu zategnute zone [mm]: '))
    n2 = float(input('Unesi broj sipki u drugom redu zategnute zone [kom]: '))
    fi2 = float(input('Unesi \u03A6 sipki u drugom redu zategnute zone [mm]: '))
    c = d1*10 -fi1/2
    fi = ((n1*math.pow(fi1, 2)+n2*math.pow(fi2, 2))/(n1*fi1+n2*fi2))
    As1 = (n1*math.pow(fi1, 2)*math.pi/4+ n2*math.pow(fi2, 2)*math.pi/4)/100

    ro1 = As1/(beff*d)
    ro2 = 0
    KSI = alfa*(ro1 + ro2)*(-1 + math.sqrt(1 + (2 * (ro1 + ro2 * d2/d))/(alfa*math.pow(ro1 + ro2, 2))))
    iks = KSI*d
    hcef = min(2.5*(h-d), (h-iks)/3, h/2)
elif k2 == 'zatezanje':
    k2 = 1
    d1 = float(input('Unesi rastojanje do tezista zategnute armature d1: '))
    b = float(input('Unesi sirinu preseka b [cm]: '))
    h = float(input('Unesi visinu preseka h [cm]: '))
    d = h - d1
    n1 = float(input('Unesi broj sipki u prvom redu zategnute zone [kom]: '))
    fi1 = float(input('Unesi \u03A6 sipki u prvom redu zategnute zone [mm]: '))
    n2 = float(input('Unesi broj sipki u drugom redu zategnute zone [kom]: '))
    fi2 = float(input('Unesi \u03A6 sipki u drugom redu zategnute zone [mm]: '))
    c = d1*10 -fi1/2
    fi = ((n1*math.pow(fi1, 2)+n2*math.pow(fi2, 2))/(n1*fi1+n2*fi2))
    As1 = (n1*math.pow(fi1, 2)*math.pi/4+ n2*math.pow(fi2, 2)*math.pi/4)/100
    hcef = min(2.5*(h-d), h/2)
else: 
    print('Unesi lepo "zatezanje" ili "savijanje" (bez navodnika)')
    exit()

ropeeff = As1/(b*hcef)
srmax = c*3.4+0.8*k2*0.425*fi/ropeeff
deltaepsilon = max((SigmaS1-(kt*fctm/ropeeff*(1+alfa*ropeeff)))/200000, 0.6*SigmaS1/200000)
wk = deltaepsilon*srmax

print('\nKarakteristicna sirina prsline je: wk = ',wk, '[mm]')
print('Dozvoljena sirina prsline je wk, doz = ', dozprslina, '[mm]')

if wk <= dozprslina:
    print('\nKontrola prslina: OK!')
if wk > dozprslina:
    print('\n>>>>>Kontrola prslina NE prolazi!<<<<<')
print('\nKarakteristicni razmak prslina Sr,max = ', srmax,'[mm]')


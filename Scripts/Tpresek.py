import numpy as np
import math, os
import pandas as pd

MEd = float(input('Unesi proracunski momenat savijanja MEd [kNm]: '))
NEd = float(input('Unesi proracunsku aksijalnu silu (pritisak je +) NEd [kN]: '))
hfl = float(input('Unesi visinu flanse hfl [cm]: '))
hfl = hfl/100
h = float(input('Unesi ukupnu visinu preseka h [cm]: '))
h = h/100
bw = float(input('Unesi sirinu rebra bw [cm]: '))
bw = bw/100
beff = float(input('Unesi efektivnu sirinu flanse beff [cm]: '))
beff = beff/100
d1 = float(input('Unesi rastojanje od zategnute ivice do tezista pritisnute armature d1 [cm]: '))
d1 = d1/100
d = h - d1
MEds = MEd + NEd*(h/2 - d1)
fckMPa = int(input('Unesi karakteristicnu cvrstocu betona na pritisak fck [MPa]: '))

if 'BetonPodaci.csv' not in os.listdir():
    print('BetonPodaci.csv se ne nalazi u radnom folderu!')
    exit()
else:
    df = pd.read_csv('BetonPodaci.csv', delimiter=';', skipinitialspace=True, encoding='UTF-8')
    fck_niz = df['fck [Mpa]'].to_list()

def ravnoteza():
    es1 = 0
    y = 0.8*d*(0.0035/(0.0035 + es1))
    Fc = fcd*(bw*y + (beff - bw)*hfl)*math.pow(10, 3)
    MRds = fcd*(bw*y*(d - y/2) + (beff - bw)*hfl*(d - hfl/2))*math.pow(10, 3)
    deltaM = MRds - MEds
    while abs(deltaM) > 5:
        y = 0.8*d*(0.0035/(0.0035 + es1))
        Fc = fcd*math.pow(10, 3)*(bw*y + (beff - bw)*hfl)
        MRds = fcd*(bw*y*(d - y/2) + (beff - bw)*hfl*(d - hfl/2))*math.pow(10, 3)
        deltaM = MRds - MEds
        es1 = es1 + 0.0001
    if es1 >= epsilons_lim:
        As1 = 0
        Fs1 = As1*fyd*math.pow(10, 3)
        deltaN = Fc - Fs1 - NEd
        while abs(deltaN) > 5:
            Fs1 = As1*fyd*math.pow(10, 3)
            deltaN = Fc - Fs1 - NEd
            As1 = As1 + 0.000001
        print('\nPotrebna povrsina zategnute armature je As1 = ', As1*math.pow(10, 4), '[cm^2]')
        print('Ravnoteza unutrasnjih sila momenata je postignuta sa greskom od ', abs(deltaM), '[kNm]')
        print('Ravnoteza unutrasnjih aksijalnih sila je postignuta sa greskom od ', abs(deltaN), '[kN]')
    else:
        print('\nDilatacija u armaturi je manja od ', epsilons_lim*math.pow(10, 3), 'promila iz cega sledi da je potrebna pritisnuta armatura za T presek')
        print('Presek nije racionalnih dimenzija za dato opterecenje!')

if fckMPa in fck_niz:
    lmbda = 0.8
    eta = 1
    fcd = 0.85*fckMPa/1.5
    indeks = fck_niz.index(fckMPa)
    fyk = 500 #MPa
    fyd = fyk/1.15
    Es = 200 #GPa
    epsilons_lim = fyd/(Es*math.pow(10, 3))
    if fckMPa >= 50:
        print('Proracun vazi kada je karakteristicna cvrstoca betona na pritisak < 50 [MPa]!')
        exit()
else:
    print(f'{fckMPa} nije standardna karakteristicna cvrstoca betona na pritisak!')
    exit()

ravnoteza()
    


import math, os
import pandas as pd
import numpy as np

def minimalniprocenatarmiranja(As1, d):
    AsMin = float(max(0.26*fctm/fyk*brebra*d*10000, 0.0013*brebra*d*10000))
    AsMax = 0.473*(b*(d))*fcd/fyd*10000 
    a = np.array([AsMin, AsMax])
    return a

def stampa(es1, ec2, ksi, As1, d):
    print('\nDilatacija u armaturi \u03B5,s1 = ', round(es1, 2),'[promila]')
    print('Dilatacija u betonu \u03B5,c2 = ', round(ec2, 2), '[promila]')
    print('\u03BE = ', ksi)
    print('Povrsina zategnute armature je: As1 = ', As1, '[cm^2]\n')
    print('Visina pritisnute zone je: x =', 100*d*ksi, '[cm]')

def maliekscentricitet (d1):
    print('\nMali ekscentricitet! Ukoliko skripta ne izbaci brzo resenje znaci da postoji zategnuta armatura, pogledaj dijagrame interakcije!')
    print('\Prekidas skriptu tako sto drzis "Ctrl" i stisnes "c"')
    print('\u03BD,Ed = ', NEd/(b*h*fcd*math.pow(10, 3)))
    print('\u03BC,Ed = ', MEd/(b*math.pow(h, 2)*fcd*math.pow(10, 3)))
    # Zahvalnica sestri Mariji za breakovanje iz svake petlje
    d2 = d1
    d = h - d1
    alfas1 = d1/h
    alfas2 = d2/h
    MEdu = MEd + NEd*(h/2 - d1)
    indikator = 0
    niz_ec2 = np.linspace(2, 3.5, num = 1000)
    for ec2 in niz_ec2:
        if indikator == 1:
            break
        beta3 = (1/189)*(125 + 64*ec2 - 16*math.pow(ec2, 2))
        beta4 = (3/14)*((8*ec2 + 5)*(37 - 8*ec2))/(125 + 64*ec2 - 16*math.pow(ec2, 2))
        Fc = beta3*b*h*fcd*math.pow(10, 3)
        es1 = (2*(1 - alfas1) - ec2*(4/7 - alfas1))/(3/7)
        es2 = (2*alfas2 + ec2*(3/7 - alfas2))/(3/7)
        if es1 > eslim*math.pow(10, 3):
            es1 = eslim*math.pow(10, 3)
        if es2 > eslim*math.pow(10, 3):
            es2 = eslim*math.pow(10, 3)
        sigmas1 = Es*math.pow(10, 3)*es1
        sigmas2 = Es*math.pow(10, 3)*es2
        for As1 in np.linspace(0, 0.04*b*h, num = 500):
            if indikator == 1:
                break
            Fs1 = sigmas1*As1
            for As2 in np.linspace(0, 0.04*b*h, num = 500):
                Fs2 = sigmas2*As2 
                deltaN = Fs1 + Fs2 + Fc - NEd
                deltaM = Fc*(d - beta4*h) + Fs2*(d - d1) - MEdu 
                if abs(deltaM) < 5 and abs(deltaN) < 5:
                    indikator = 1
                    break
    if ec2 == 3.5 and abs(deltaM)> 50 and abs(deltaN) > 50:
        print('\nPostoji i zategnuta armatura u preseku! Pogledaj dijagrame interakcije!')
    else:
        As = max(As1, As2)
        print('\nZa simetricno armirane preseke ukupna povrsina armature je As = ', 2*As*math.pow(10, 4), '[cm^2]')
        print('Povrsina armature u jednom delu preseka je As1 = As2 = ', As*math.pow(10, 4), '[cm^2]')
        print('Ravnoteza momenta oko "zategnutije" armature je postignuta sa greskom od: \u0394M = ', abs(deltaM), '[kNm]')
        print('Ravnoteza aksijalnih sila je postignuta sa greskom od: \u0394N = ', abs(deltaN), '[kN]')

def dvojnoarmiranje(es1, MEdu, d, d1):
    print(f'\n>Dilatacija u armaturi je ispod 2.5 promila >>>> Dvojno armiranje!')
    d2 = float(input('\nUnesi rastojanje tezista pritisnute armature od pritisnute ivice d2 [cm]: '))
    ksi = 0.583
    es1 = 2.5
    d2 = d2/100
    dM = float(MEdu - math.pow(d/1.672, 2)*b*fcd*1000)
    As2 = (dM/((d-d2)*fyd*1000)*10000)
    As1 = 0.81*ksi*fcd/fyd*b*d*math.pow(10, 4) - (NEd/(fyd*1000))*10000 + As2
    if As2 > As1:
        maliekscentricitet(d1)
        exit()
    print('\n>>>>>Povrsina pritisnute armature je: As2 = ', As2, '[cm^2]')
    stampa(es1, 3.5, ksi, As1, d)

def ekscentricnoopterecenje(NEd, h):
    if MEd == 0 and sigma1 > 0:
        print('\n>>>>>Centricni pritisak!')
        Ac = b*h
        napon_beton = NEd/(Ac*math.pow(10, 3))
        if napon_beton <= fcd:
            As = max(0.15*NEd/fyd*math.pow(10, 1), 0.003*Ac*math.pow(10, 4) , 4*1.13)
            print('\nPotrebna povrsina armature je: ', As, '[cm^2]')
        else:
            print('\n>>>>>Napon u betonu je veci od proracunskog napona nosivosti betona!')
            print('fcd = ', fcd, '[MPa]')
            print('Napon u betonu', napon_beton, '[MPa]')
    if sigma2 < 0:
        print('\n>>>>>(Eks)centricno zatezanje!')
        NEd = abs(NEd)
        e = MEd/NEd
        As = NEd/fyd*10
        if e != 0:
            d1 = float(input('Unesi rastojanje od zategnute ivice betona do tezista zategnute armature d1 [cm]: '))
            d1 = d1/100
            d2 = float(input('Unesi rastojanje od pritisnute ivice  betona do tezista pritisnute armature d2 [cm]: '))
            d2 = d2/100
            c1 = h/2 - d1
            c2 = h/2 - d2
            As1 = (NEd/fyd*(c2+e)/(c1+c2))*math.pow(10, 1)
            As2 = (NEd/fyd*(c2-e)/(c1+c2))*math.pow(10, 1)
            As = As1+As2
            print('\nPovrsina armature na zategnutoj ivici od momenta je As1 = ', As1, '[cm^2]')
            print('Povrsina armature na pritinsutoj ivici od momenta je As2 = ', As2, '[cm^2]')
        else:
            print('\nUkupna povrsina potrebne armature je As = ', As, '[cm^2]')
        exit()

def uticajiarmatura(MEd, NEd):
    ekscentricnoopterecenje(NEd, h)
    ecu2 = 3.5
    ec2 = ecu2
    if MEd != 0:
        ecu2 = 3.5
        ec2 = ecu2
        d1 = float(input('Unesi rastojanje od zategnute ivice betona do tezista zategnute armature d1 [cm]: '))
        d1 = d1/100
        d = h-d1
        MEdu = MEd+NEd*((h)/2-d1)
        if sigma1 >= 0:
            maliekscentricitet(d1)
            exit()
        a = -0.33696*b*math.pow(d, 2)*fcd*math.pow(10, 3) 
        be = 0.81*b*math.pow(d, 2)*fcd*math.pow(10, 3)
        c = -MEdu
        disk = abs(math.pow(be, 2)-4*a*c)
        ksi = ((-be+math.pow(disk, 0.5))/(2*a))
        es1 = (1-ksi)/(ksi)*ec2
        As1 = 0.81*ksi*fcd/fyd*b*d*math.pow(10, 4) - (NEd/(fyd*1000))*10000 
        if As1 < 0:
            maliekscentricitet(d1)
            exit()
        if abs(es1) <= 2.5:
            dvojnoarmiranje(es1, MEdu, d, d1)
        else:
            niz = minimalniprocenatarmiranja(As1, d)
            AsMin = niz[0]
            AsMax = niz[1]
            if As1 < AsMin:
                print('\n>>>>>Minimalni procenat armiranja! Za veliku silu pritiska a mali moment je mozda potrebno dimenzionisanje uz pomoc dijagrama interakcije!')
                print('Minimalna povrsina armature je As,min = ', AsMin, '[cm^2]')
            elif As1 > AsMax:
                print('\n>>>>>Procenat armiranja je veci od maksimalnog! As,max = ', AsMax, '[cm^2]')
            else:
                stampa(es1, ec2, ksi, As1, d)
        if sigma1 >= 0:
            maliekscentricitet(d1)
            exit()
if 'BetonPodaci.csv' not in os.listdir():
    print('BetonPodaci.csv se ne nalazi u radnom folderu!')
    exit()
else:
    df = pd.read_csv('BetonPodaci.csv', delimiter = ';', encoding = 'UTF-8', skipinitialspace = True)
    fck_lista = df['fck [Mpa]'].to_list()
    fctm_lista = df['fctm [Mpa]'].to_numpy()
    Ecm_lista = df['Ecm [Gpa]'].to_numpy()

MEd = float(input('Unesi proracunski moment savijanja MEd [KNm]: '))
MEd = abs(MEd)
NEd = float(input('Unesi proracunsku aksijalnu silu NEd [KN] (pritisak je +): '))
b = float(input('Unesi sirinu pritisnute zone b [cm] (sirina rebra ili beff kod pritisnute flanse): '))
brebra = float(input('Unesi sirinu rebra [cm]: '))
b = b/100
brebra = brebra/100
if b == brebra:
    b =  brebra
h = float(input('Unesi visinu preseka h [cm]: '))
h = h/100
fckMPA = int(input('Unesi karakteristicnu cvrstocu betona fck [MPa]: '))
sigma1 = (NEd/(b*(h)))-MEd*6/(b*math.pow((h),2))
sigma2 = (NEd/(b*(h)))+MEd*6/(b*math.pow((h),2))
if fckMPA in fck_lista:
    indeks = fck_lista.index(fckMPA) 
    fctm = fctm_lista[indeks]
    Ecm = Ecm_lista[indeks]
    fcd = 0.85*fckMPA/1.5
    fyk = 500
    fyd = 500/1.15
    Es = 200
    eslim = fyd/(Es*math.pow(10, 3))
else:
    print(f'{fckMPA} nije standardna karakteristicna cvrstoca betona, pogledaj u tabeli za standardne cvrstoce!')
    exit()

uticajiarmatura(MEd, NEd)

import pandas as pd
import math
import os


def tpresek():
    iks = 0.001
    ec = 3.5
    ecf = ec*(iks - hfl)/iks
    beta11 = (3*3.5 - 2)/(3*ec)
    es1 = ec/iks*d - ec
    if es1 > 2.5:
        sigmas1 = fyd
    else:
        sigmas1 = Es*es1  # MPa
    if ecf <= 2:
        beta12 = (ec*(6 - ec))/12
    elif 2 < ecf <= 3.5:
        beta12 = (3*ecf - 2)/(3*ecf)
    Fs1 = As1*sigmas1*math.pow(10, 3)
    Fc1 = beta11*iks*fcd*beff*math.pow(10, 3)
    Fc2 = beta12*(iks - hfl)*fcd*math.pow(10, 3)*(beff - bw)
    deltaN = Fc1 - Fc2 - Fs1 - Ned
    while abs(deltaN) > 5:
        ec = 3.5
        ecf = ec*(iks - hfl)/iks
        beta11 = (3*3.5 - 2)/(3*ec)
        es1 = ec/iks*d - ec
        if es1 > 2.5:
            sigmas1 = fyd
        else:
            sigmas1 = Es*es1  # MPa
        if ecf <= 2:
            beta12 = (ec*(6 - ec))/12
        elif 2 < ecf <= 3.5:
            beta12 = (3*ecf - 2)/(3*ecf)
        Fs1 = As1*sigmas1*math.pow(10, 3)
        Fc1 = beta11*iks*fcd*beff*math.pow(10, 3)
        Fc2 = beta12*(iks - hfl)*fcd*math.pow(10, 3)*(beff - bw)
        deltaN = Fc1 - Fc2 - Fs1 - Ned
        iks = iks + 0.0005
    beta21 = 0.416
    if ecf < 2:
        beta22 = (8 - ecf)/(4*(6 - ecf))
    if 2 <= ecf <= 3.5:
        beta22 = (ecf*(3*ecf-4)+2)/(2*ecf*(3*ecf - 2))
    elif 0 > ecf > 3.5:
        print('\nSkripta pravi gresku, dilatacija u betonu u nivou donje ivice flanse nije izmedju 0 i 3.5 promila!')
        exit()
    MRds = Fc1*(d - beta21*iks) - Fc2*(d - hfl - beta22*(iks - hfl))
    MEd = MRds - Ned*(h/2 - d1)
    print('\nMomenat nosivosti T preseka je MEd = ', MEd, '[kNm]')
    print('Greska ravnoteze unutrasnjih aksijalnih sila je \u0394N = ', abs(deltaN), '[kN]')


def nosivost():
    if As2 == 0:
        d2 = 0
        Fs2 = 0
        ksi = (As1*fyd*math.pow(10, 3) + Ned)/(b*d*fcd*math.pow(10, 3))/0.81
        iks = ksi*d
        es1 = (1-ksi)/ksi*3.5
        if iks > hfl:
            tpresek()
            exit()
        if es1 < 2.5:
            # Fs1 = As1*es1/2.5*fyd*math.pow(10, 3)
            ksi = 3.5/(3.5 + es1)
            if ksi > 0.583:
                print('\nProracun se vrsi iterativno uz zadovoljenje uslova ravnoteze N sila!')
                ksi = 2
                # es1 = 2.5
                Fs1 = As1*fyd*math.pow(10, 3)
                Fc = 0.81*ksi*b*d*fcd*math.pow(10, 3)
                delta = abs(Fc+Fs2-Fs1 - Ned)
                ksi2 = 0.0001
                while abs(delta) > 0.5:
                    x = ksi*d
                    es1 = (1-ksi)/ksi*3.5
                    if es1 > 2.5:
                        es1 = 2.5
                    Fc = 0.81*x*b*fcd*math.pow(10, 3)
                    Fs1 = As1*es1/2.5*fyd*math.pow(10, 3)
                    epsilons2 = ((ksi-d2/d)/ksi)*3.5
                    Fs2 = As2*epsilons2*Es*math.pow(10, 3)
                    ksi = ksi-ksi2
                    delta = abs(Fc+Fs2-Fs1 - Ned)
            print('Ravnoteza je postignuta sa greskom od', delta, '[kN]')
        else:
            pass
        MRds = 0.81*ksi*(1-0.416*ksi)*b*math.pow(d, 2)*fcd*math.pow(10, 3)
        MRd = MRds - Ned*(h/2 - d1)
        print('\nMoment nosivosti preseka: MRd = ', MRd, '[KNm]')

    elif As2 != 0:
        d2 = float(input('Unesi rastojanje od pritisnute ivice do tezista pritisnute armature d2 [cm]: '))
        d2 = d2/100
        ksi = 0.583
        # x = ksi*d
        Fc = 0.81*ksi*b*math.pow(10, 2)*fcd*math.pow(10, 3)
        Fs1 = As1*fyd*math.pow(10, 3)
        epsilons2 = ((ksi-d2/d)/ksi)*3.5
        if epsilons2 > 2.175:
            epsilons2 = 2.175
        Fs2 = As2*epsilons2*Es*math.pow(10, 3)
        delta = abs(Fc+Fs2-Fs1 - Ned)
        ksi2 = 0.0001
        while abs(delta) >= 0.5:
            x = ksi*d
            Fc = 0.81*x*b*fcd*math.pow(10, 3)
            Fs1 = As1*fyd*math.pow(10, 3)
            epsilons2 = ((ksi-d2/d)/ksi)*3.5
            if epsilons2 > 2.175:
                epsilons2 = 2.175
            Fs2 = As2*epsilons2*Es*math.pow(10, 3)
            ksi = ksi-ksi2
            delta = abs(Fc+Fs2-Fs1 - Ned)
        ceta = 1-0.416*ksi
        MRds = Fc*ceta*d + Fs2*(d-d2) 
        delta = abs(Fc+Fs2-Fs1 - Ned)
        MEd = MRds - Ned*(h/2 - d1)
        print('\n>>>>>Ravnoteza je uspostavljena za \u03BE = ', ksi, 'sa greskom uslova ravnoteze sila od \u0394N',
              delta, '[KN]')
        print('\nMoment nosivosti preseka: MRd = ', MEd, '[KNm]')


hfl = str(input('Unesi visinu flanse hf [cm], ukoliko flanse nema (pravougaoni presek) unesi "pravougaoni" '
                '(bez navodnika): '))
hfl = hfl.lower()
if hfl != 'pravougaoni':
    As2 = 0
    hfl = float(hfl)
    hfl = hfl/100
    beff = float(input('Unesi efektivnu sirinu flanse beff [cm]: '))
    beff = beff/100
    bw = float(input('Unesi sirinu rebra bw [cm]: '))
    bw = bw/100
    b = bw
    As1 = float(input('Unesi povrsinu zategnute armature As1 [cm^2]: '))
    As1 = As1*math.pow(10, -4)
elif hfl == 'pravougaoni':
    hfl = math.pow(10, 10)
    b = int(input('Unesi sirinu preseka b [cm]: '))
    b = b/100
    bw = b
    As1 = float(input('Unesi povrsinu zategnute armature As1 [cm^2]: '))
    As1 = As1*math.pow(10, -4)
    As2 = float(input('Unesi povrsinu pritisnute armature As2 [cm^2]: '))
    As2 = As2*math.pow(10, -4)
fck_MPA = int(input('Unesi karakteristicnu cvrstocu betona fck [MPa]: '))
d = float(input('Unesi staticku visinu d [cm]: '))
d = d/100
d1 = float(input('Unesi rastojanje od tezista zategnute armature do zategnute ivice preseka d1 [cm]: '))
d1 = d1/100
h = d + d1
Ned = float(input('Unesi aksijalnu silu (pritisak je +): '))

if 'BetonPodaci.csv' not in os.listdir():
    print('BetonPodaci.csv se ne nalazi u radnom folderu!')
    exit()
else:
    df = pd.read_csv('BetonPodaci.csv', encoding='UTF-8', delimiter=';', skipinitialspace=True)
    fck_lista = df['fck [Mpa]'].to_list()

if fck_MPA in fck_lista:
    indeks = fck_lista.index(fck_MPA)
    fcd = 0.85*fck_MPA/1.5
    fyd = 500/1.15
    Es = 200
    eslim = fyd/Es  # promila
else:
    print(f'{fck_MPA} nije standardna karakteristicna cvrstoca betona na pritisak!')
    exit()

nosivost()

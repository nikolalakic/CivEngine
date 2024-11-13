import math, os
import matplotlib as mp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def KrivinaPrslina():
    Mcr = b*math.pow(h, 2)/6*fctm*math.pow(10, 3)
    ecr = fctm/((Ecd)*math.pow(10, 3))
    krivinacr = ecr/h
    a = np.array([Mcr, krivinacr])
    print('\n>Pojava prsline')
    print('\nMoment pri pojavi prsline: Mcr =', Mcr, '[KNm]')
    print('Krivna pri pojavi prsline: \u03BA,cr =', krivinacr,'[1/m]')
    return a

def KrivinaLomBetona():
    ec = 3.5
    beta1 = 0.81
    beta2 = 0.416
    ksi = 0.00001
    es1 = (1-ksi)/ksi*ec
    Fs1 = As1*es1/2.5*fyd*math.pow(10, 3)
    Fc = beta1*ksi*b*d*fcd*math.pow(10, 3)
    delta = Fc - Fs1
    ksi2 = 0.00001
    while abs(delta) > 0.5:
        es1 = (1-ksi)/ksi*ec
        Fs1 = As1*es1*Es*math.pow(10, 3)
        if es1 > 2.175:
            Fs1 = As1*2.175*Es*math.pow(10, 3)
        Fc = beta1*ksi*b*d*fcd*math.pow(10, 3)
        ksi = ksi + ksi2
        delta = abs(Fc - Fs1)
    x = ksi*d
    M = beta1*ksi*d*b*fcd*d*(1-beta2*ksi)*math.pow(10, 3)
    krivinabeton = ec*math.pow(10, -3)/x
    print('\n>Lom po betonu')
    print('\nDilatacija u armaturi pri lomu betona: \u03B5,s1 =', es1)
    print('Moment nosivosti pri lomu betona: M =', M, '[KNm]')
    print('Krivina pri lomu betona: \u03BA,cr =', krivinabeton, '1/m')
    a =  np.array([M, krivinabeton])
    return a

def KrivinaTecenjeArmature():
    es1 = 2.175
    ec = 0.0000001
    beta1 = ec*(6-ec)/12
    ksi = ec/(ec+es1)
    Fc = beta1*ksi*d*b*fcd*math.pow(10, 3)
    Fs1 = As1*fyd*math.pow(10, 3)
    delta = Fc - Fs1
    umanjivac = 0.0001
    while abs(delta) > 0.5:
        if ec < 2:
            beta1 = ec*(6-ec)/12
        elif ec >=2 and ec <=3.5:
            beta1 = (3*ec-2)/(3*ec)
        else:
            print('\nLom po betonu pre tecenja armature! \u03B5,c > 3.5 promila!')
            ec = 3.5
            break
        ksi = ec/(ec+es1)
        Fc = beta1*ksi*d*b*fcd*math.pow(10, 3)
        Fs1 = As1*fyd*math.pow(10, 3)
        ec = ec + umanjivac
        delta = abs(Fc - Fs1)
    if ec <= 2:
        beta2 = (8-ec)/(4*(6-ec))
    elif ec > 2:
        beta2 = (ec*(3*ec-4)+2)/(2*ec*(3*ec-2))
    x = ksi*d
    krivinaarmatura = ec*math.pow(10, -3)/x
    M = beta1*ksi*d*b*fcd*d*(1-beta2*ksi)*math.pow(10, 3)
    if ec < 3.5:
        print('\n>Tecenje armature')
        print('\nDilatacija u betonu pri tecenju armature: \u03B5,c =', ec, 'promila')
        print('Moment pri lomu armature: M =', M)
        print('Krivna pri lomu armature: \u03BA,cr =', krivinaarmatura,'[1/m]')
        a = np.array([M, krivinaarmatura])
        return a
    else:
        a = KrivinaLomBetona()
        return a

def stampa():
    prslina = KrivinaPrslina()
    armatura = KrivinaTecenjeArmature()
    beton = KrivinaLomBetona()
    Momenti = np.array([0, prslina[0], armatura[0], beton[0]])
    Krivine = np.array([0, prslina[1], armatura[1], beton[1]])
    Krivine = Krivine*math.pow(10, 3)
    plt.style.use('seaborn-whitegrid')
    plt.xlim(-10, 50)
    plt.title('Dijagram moment-krivina')
    plt.xlabel('\u03BA 10^-3 [1/m]')
    plt.ylabel('M [kNm]')
    a = np.array([Krivine, Momenti])
    return a

b = int(input('Unesi sirinu preseka b [cm]: '))
b = b/100
d = float(input('Unesi staticku visinu preseka d [cm]: '))
d = d/100
d1 = float(input('Unesi rastojanje od zategnute ivice do tezista armature zategnute d1 [cm]: '))
d1 = d1/100
h = d + d1
fckMPA = int(input('Unesi karakteristicnu cvrstocu betona [MPa]: '))

if 'BetonPodaci.csv' not in os.listdir():
    print('BetonPodaci.csv se ne nalazi u radnom folderu!')
    exit()
else:
    df = pd.read_csv('BetonPodaci.csv', delimiter = ';', skipinitialspace = True, encoding = 'UTF-8')
    fck_lista = df['fck [Mpa]'].to_list()
    fctm_lista = df['fctm [Mpa]'].to_list()
    Ecm_lista = df['Ecm [Gpa]'].to_list()

if fckMPA in fck_lista:
    indeks = fck_lista.index(fckMPA) 
    fctm = fctm_lista[indeks]
    Ecm = Ecm_lista[indeks]
    fcd = 0.85*fckMPA/1.5
    fyd = 500/1.15
    Ecd = 1.05*Ecm
    Es = 200
else:
    print(f'{fckMPA} nije standardna karakteristicna cvrstoca betona!')
    exit()

#As1 = float(input('Unesi povrsinu zategnute armature As1 [cm^2]: '))
#Minimalni procenat armature
As1 = max(0.26*fctm/500*b*d, 0.0013*b*d)
print('\n>>>>>Minimalni procenat armiranja!<<<<<')
minarm = stampa()
#Maksimalni procenat armature
As1 = 0.473*b*d*fcd/fyd
print('\n>>>>>Maksimalni procenat armiranja!<<<<<')
maxarm = stampa()
#Uneta od strane korisnika
As1 = float(input('\nUnesi povrsinu zategnute armature As1 [cm^2]: '))
As1 = As1*math.pow(10, -4)
print('\n>>>>>Uneto od stane korisnika!<<<<<')
korarm = stampa()


plt.plot(minarm[0], minarm[1], '-.', label='As1,min' )
plt.plot(maxarm[0], maxarm[1], '--', label='As1,max')
plt.plot(korarm[0], korarm[1], '-', label='As1')
plt.legend()

fig = plt.gcf()
plt.draw()
#fig.savefig('Stampa.png', dpi=100)
plt.show()



import math, os
import pandas as pd
import numpy as np

if 'BetonPodaci.csv' not in os.listdir():
    print('BetonPodaci.csv se ne nalazi u radnom folderu!')
    exit()
else:
    df = pd.read_csv('BetonPodaci.csv', encoding = 'UTF-8', skipinitialspace = True, delimiter = ';')
    fck_lista = df['fck [Mpa]'].to_list()
    fctm_lista = df['fctm [Mpa]'].to_numpy()
    Ecm_lista = df['Ecm [Gpa]'].to_numpy()

MEd =  float(input('Unesi M (iz kvazi-stalne ili karakteristicne kombinacije) [KNm]: '))
d = float(input('Unesi staticku visinu d [cm]: '))
As1 = float(input('Unesi povrsinu zategnute armature As1 [cm^2]: '))
As2 = float(input('Unesi povrsinu pritisnute armature As2 [cm^2]: '))
if As2 != 0:
    d2 = float(input('Unesi rastojanje to tezista pritisnute armature d2 [cm]: '))
else: 
    d2 = 0

d2 = d2/100
d = (d/100)
b = float(input('Unesi sirinu pritisnutog betona b (ili beff kod pritisnute flanse) [cm]: '))
b = (b/100)
fckMPA = int(input('Unesi marku betona [MPa]: '))
for x in fck_lista:
    if fckMPA == x:
       index = fck_lista.index(fckMPA)
       break

fctm = fctm_lista[index]
Ecm = Ecm_lista[index]
Es = 200
alfa = float(Es/Ecm)
fcd = float(0.85*fckMPA/1.5)
fyd = 500/1.15
ro1 = (As1/(b*100*d*100))
ro2 = (As2/(b*100*d*100))
KSI = alfa*(ro1 + ro2)*(-1 + math.sqrt(1 + (2 * (ro1 + ro2 * d2/d))/(alfa*math.pow(ro1 + ro2, 2))))
SigmaC = MEd/(b*math.pow(d, 2))/(KSI/2*(1-KSI/3)+alfa*ro2*(1-d2/(KSI*d))*(1-d2/d))/1000
SigmaS1 = alfa*SigmaC*(1-KSI)/KSI
SigmaS2 = alfa*SigmaC*(KSI - d2/d)/KSI
print('\n\u03BE = ' , KSI)
print('\u03C3c = ', SigmaC, '[MPa]')
print('\u03c3s1 = ', SigmaS1, '[MPa]')
print('\u03c3s2 = ', SigmaS2, '[MPa]')
if SigmaC > 0.45*fckMPA:
    print('\n>>>>>Napon u betonu NE zadovoljava kontrolu za M iz kvazi stalne kombinacije!<<<<<')
if SigmaC > 0.6*fckMPA:
    print('\n>>>>>Napon u betonu NE zadovoljava kontrlolu za M iz karakteristicne kombinacije!<<<<<')
if SigmaS1 > 0.8*500:
    print('\n>>>>>Napon u armaturi NE zadovoljava kontrolu za M iz karakteristicne kombinacije!<<<<<')
if SigmaC <= 0.45*fckMPA:
    print('\nKvazi stalna kombinacija..... OK!')
if SigmaC <= (0.6*fckMPA) and (SigmaS1<=0.8*500):
    print('\nKarakteristicna kombinacija..... OK!')


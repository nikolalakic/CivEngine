import math, os
import pandas as pd

l = float(input('Unesi raspon grede l [m]: '))
d = float(input('Unesi staticku visinu grede d [cm]: '))
d = d/100
b = float(input('Unesi sirinu preseka b [cm]: '))
b = b/100
fckMPA = int(input('Unesi karakteristicnu cvrstocu betona na pritisak fck [MPa]: ')) 
K = float(input('Unesi koeficijent statickog sistema K: '))
Asreq = float(input('Unesi proracunski potrebnu armaturu od savijanja As,req [cm^2]: '))
Asreq = Asreq*math.pow(10, -4)
Asprov = float(input('Unesi usvojenu armaturu od savijanja As,prov [cm^2]: '))
Asprov = Asprov*math.pow(10, -4)


ro0 = math.sqrt(fckMPA)*math.pow(10, -3)
ro = Asreq/(b*d)

if ro <= ro0:
    granica = K*(11 + 1.5*math.sqrt(fckMPA)*ro0/ro + 3.2*math.sqrt(fckMPA)*math.pow(ro0/ro - 1, 3/2))
else:
    roprim = float(input('Unesi procenat armiranja pritisnute armature \u03C1` [%]: '))
    roprim = roprim/100
    granica = K*(11 + 1.5*math.sqrt(fckMPA)*ro0/(ro - roprim) + 1/12*math.sqrt(fckMPA)*math.sqrt(roprim/ro0))

korekcija = Asprov/Asreq
granica = granica*korekcija

if l/d <= granica:
    print('\nKontrola ugiba ..... OK')
elif l/d > granica:
    print('\nKontrola ugiba indirektnom metodom ne zadovoljava!')

print('l/d, stvarno = ', l/d)
print('l/d, lim = ', granica)

if 'BetonPodaci.csv' not in os.listdir():
    print('BetonPodaci.csv se ne nalazi u radnom folderu!')
    exit()
else:
    df = pd.read_csv('BetonPodaci.csv', delimiter = ';', encoding = 'UTF-8', skipinitialspace = True)
    fck_lista = df['fck [Mpa]'].to_list()
if fckMPA in fck_lista:
    indeks = fck_lista.index(fckMPA)
else:
    print(f'{fckMPA} nije standardna karakteristicna cvrstoca betona!')
    exit()


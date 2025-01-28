# I.1. Détermination de Csol

## Contexte

Toute première étape de mon alternance, c'est ici que tout commence et que le sujet m'est introduit.

## Objectif

A partir d'un modèle physique établi par M. Patrick Boyer, je dois faire un code python permetttant de faire tourner le code. 
Sachant qu'un code sur excel existe déjà, il permet à partir de données de rejets liquides, de la carotte de sédiments et d'autres paramètres de déterminer la concentration dans les sol (Csol) du nucléotide le césium 137 (Cs137). Cependant ce code excel prenait trop de temps à s'exécuter.

Mon objectif a donc été de reprendre le modèle et ce code excel pour en faire un nouveau sur python et ainsi améliorer le temps d'exécution du code.

## Ma version de code pour Csol

```python
from math import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import Font
import time

deb_chrono = time.time()

################################################################################################################

# Donnees de la feuille paramètre

Fichier = 'TRAJECTOIRE_LOIRE.xlsm' # A modifier avec le nom du fichier excel correspondant
Parametres = pd.read_excel(Fichier, sheet_name='Parametres') # Donnees de la feuille Parametres
DataDepots = pd.read_excel(Fichier, sheet_name='DataDepots') # Donnees de la feuille DataDepots
DataRejet = pd.read_excel(Fichier, sheet_name='DataRejet') # Donnees de la feuille DataRejet
DataCore = pd.read_excel(Fichier, sheet_name='DataCore') # Donnees de la feuille DataCore

################################################################################################################

# Parametres de calcul

def ReadParam():
    # Lecture des paramètres
    n0 = Parametres.loc[0, 'n0'] # Porosite de la couche de surface
    nsol = Parametres.loc[0, 'nsol'] # Porosite du sol
    z0 = Parametres.loc[0, 'z0 (cm)'] # Epaisseur de depot (cm)
    zmax = Parametres.loc[0, 'zmax (cm)'] # Epaisseur max de migration verticale (cm)
    ro = Parametres.loc[0, 'ro (kg/cm3)'] # Masse volumique (kg/cm3)
    Tmig = Parametres.loc[0, 'Tmig(j)']
    lmig = log(2)/Tmig # Cinetique de decroissance de la vitesse sol (cm/s)
    lrn = Parametres.loc[0, 'Lrn (/j)'] # Cinetique de decroissance radioactive (/j)
    lero = Parametres.loc[0, '%ero/an'] / 100 / 365 # Cinetique de perte par erosion/an (/j)
    dt = Parametres.loc[0, 'Dt (j)'] # Pas de temps (j)
    Kd = Parametres.loc[0, 'Kdd (l/kg)'] # Kd couche d'echange (l/kg)
    d = Parametres.loc[0, 'd (µm)'] # Epaisseur de la couche d'echange (µm)
    Q = Parametres.loc[0, 'Q (m3/s)'] # Debit (m3/s)
    SS = Parametres.loc[0, 'SS (mg/L)'] # Charge en suspension (mg/l)
    d50 = Parametres.loc[0, 'd50 (µm)'] # Diametre moyen (µm)
    nsed = Parametres.loc[0, 'nsed'] # Porosite des sédiments
    # Calcul des constantes
    lrnero = lero + lrn # Cinetique cumulee decroissance - erosion (/j)
    nrosed = nsed / ro / (1 - nsed) # masse seche des sediments
    A = (nsol - n0) * z0 / (1 - nsol)
    B = (A + zmax) / (zmax - z0)
    E = (B - 1) * dt / ro / (1 - n0) / z0
    return n0, nsol, z0, zmax, ro, lmig, lrn, lero, dt, Kd, d, Q, SS, d50, nsed, lrnero, nrosed, A, B, E

n0, nsol, z0, zmax, ro, lmig, lrn, lero, dt, Kd, d, Q, SS, d50, nsed, lrnero, nrosed, A, B, E = ReadParam()
    
################################################################################################################

# Parametres de depot

def ReadDepot():
    ND = len(DataDepots['Année']) # Nombre de depots
    # Détermination du nombre de jour de calcul pour les depots (NjD)
    jd = []
    jf = []
    Jdeb = 0 # Jour de début
    Jfin = 0 # Jour de fin
    for i in range(ND):
        Jdeb = Jfin + 1
        Jfin = Jdeb + 365
        jd.append(Jdeb)
        jf.append(Jfin)
        NjD = Jfin #Pourquoi pas de -365 ?
    FD = DataDepots["Depôts (Bq/cm2/j)"].to_numpy() # Flux de depot (Bq/cm2/j)
    return ND, jd, jf, NjD, FD

ND, Depot_jd, Depot_jf, NjD, Depot_FD = ReadDepot()

################################################################################################################

# Paramètres des rejets liquides

def ReadRejet():
    NR = len(DataRejet['Année']) # Nombre de rejets liquides
    jd = DataRejet["Jour/1945"].to_numpy() # Jours de début de rejet (j)
    jf = jd + 365
    NjR = jf[-1]
    FR = DataRejet['Total (Bq/s)'].to_numpy() #Flux de rejet (Bq/cm2/s)
    return NR, jd, jf, NjR, FR

NR, Rejet_jd, Rejet_jf, NjR, FR = ReadRejet()

################################################################################################################

# Procédure d'implémentation des pulses de dépôt

def CreatePulse() :
        jd = np.array([i for i in range(NjD)])
        FD = np.array([e for x in zip(*[Depot_FD]*366) for e in x])
        return jd, FD

Pulse_jd, Pulse_FD = CreatePulse()

################################################################################################################

# Procédure de calcul analytique de la concentration des sols superficiels après les dépôts

def funct_decrease(x):
    res = np.exp(-lrnero * x) / (B - np.exp(-lmig * x))
    return res

def RunCSOLANL():
    J0 = DataDepots.loc[0,'Date']
    Nj = NjD
    if NjD < NjR:
        Nj = (2020 - 1945) * 365
    CSOL = pd.DataFrame([],index=range(0,Nj),columns = ['Date', 'CSOL'])
    CSOL['CSOL'] = 0
    CSOL['Date'] = [J0.date() + timedelta(days=x) for x in range(Nj)]
    CSOL.loc[range(0,NjD),'CSOL'] = [E * np.dot(funct_decrease(ij - Pulse_jd[0:ij] * dt), Pulse_FD[0:ij]) for ij in range(0, NjD)]
    CSOL.loc[range(NjD, Nj),'CSOL'] = [E * np.dot(funct_decrease(ij - Pulse_jd[0:NjD-1] * dt), Pulse_FD[0:NjD-1]) for ij in range(NjD, Nj)]
    return CSOL['Date'], CSOL['CSOL']

Date, CSOL= RunCSOLANL()

################################################################################################################

# Procédure de calcul du flux des rejets liquides

def RunFREJ():
    Nj = NjD
    if NjD < NjR:
        Nj = (2020 - 1945) * 365
    ij0 = Rejet_jd[0]
    ir = 0
    FREJ = pd.DataFrame([],index=range(0,Nj),columns = ['FRJT'])
    FREJ.loc[range(0,ij0)] = 0
    for ij in range(ij0, NjR):
        if Rejet_jf[ir]<ij:
            ir+=1
        FREJ.loc[ij,'FRJT'] = FR[ir]
    FREJ.loc[range(NjR,Nj)] = 0
    return FREJ['FRJT']

FRJT = RunFREJ()

################################################################################################################

# Procédure de calcul des concentrations de la rivière

def Création_tab_constants():
    n = len(Date)
    tab_Q = [Q for i in range(n)]
    tab_d50 = [d50 for i in range(n)]
    tab_SS = [SS for i in range(n)]
    return tab_Q, tab_SS, tab_d50

tab_Q, tab_SS, tab_d50 = Création_tab_constants()

def RunCRIV():
    J0 = DataDepots.loc[0,'Date']
    Nj = NjD
    if NjD < NjR:
        Nj = (2020 - 1945) * 365
    CRIV = pd.DataFrame([],index=range(0,Nj),columns = ['Q', 'd50','SS','SSR','SSNR','CRIV,SOL','CRIV,RJT','CRIV','CRIV,E','CRIV,NE','CRIV,DIS','CRIV,SSR','CRIV,SS','CSED'])
    CRIV['Q'] = Q
    CRIV['d50'] = d50
    CRIV['SS'] = SS
    if d < d50/2:
        CRIV['SSR'] = SS * (1 - (1 - 2 * d / d50)**3)
    else:
        CRIV['SSR'] = SS
    CRIV['SSNR'] = SS - CRIV['SSR']
    CRIV['CRIV,SOL'] = 1e-6 * CSOL * SS
    CRIV['CRIV,RJT'] = FRJT / Q / 1000
    CRIV['CRIV'] = CRIV['CRIV,SOL'] + CRIV['CRIV,RJT']
    CRIV['CRIV,E'] = CRIV['CRIV,RJT'] + 1e-6 * CSOL * CRIV['SSR'][0]
    CRIV['CRIV,NE'] = 1e-6 * CSOL * CRIV['SSNR'][0]
    CRIV['CRIV,DIS'] = CRIV['CRIV,E'] / (1 + 1e-6 * Kd * CRIV['SSR'][0])
    CRIV['CRIV,SSR'] = Kd * CRIV['CRIV,DIS']
    CRIV['CRIV,SS'] = (CRIV['CRIV,SSR'] * CRIV['SSR'][0] + CSOL * CRIV['SSNR'][0]) / SS
    CRIV['CSED'] = CRIV['CRIV,DIS'] * nrosed / 1000 + CRIV['CRIV,SS']
    return CRIV['SSR'], CRIV['SSNR'], CRIV['CRIV,SOL'], CRIV['CRIV,RJT'], CRIV['CRIV'], CRIV['CRIV,E'], CRIV['CRIV,NE'], CRIV['CRIV,DIS'], CRIV['CRIV,SSR'], CRIV['CRIV,SS'], CRIV['CSED']

SSR, SSNR, CRIV_SOL, CRIV_RJT, CRIV, CRIV_E, CRIV_NE, CRIV_DIS, CRIV_SSR, CRIV_SS, CSED = RunCRIV()

################################################################################################################

# Procédure d'association modèle/mesure pour le calcul des corrélations

# La procedure calcul la valeur moyenne du modèle entre deux mesures

def ModeleMeanvsMesure():
    Jour_Deb = []
    Jour_Fin = []
    Archive = []
    Averaged_Model = []
    A = DataCore['Année'].to_numpy()
    Jours_Core = (A - 1945) * 365
    Jours_Res = [165 + i for i in range(len(Date))]
    Ce_dep = DataCore['Cesium137_Bq.kg (déposé)'].to_numpy()
    ildata = 0
    ilrun = 0
    Jdeb = Jours_Core[0]
    Jfin = Jours_Core[1]
    Jrun = Jours_Res[0]
    while Jrun > Jdeb:
        ildata += 1
        Jdeb = Jours_Core[ildata]
        Jfin = Jours_Core[ildata + 1]
    while Jrun < Jdeb:
        ilrun += 1
        Jrun = Jours_Res[ilrun]
    while ilrun < len(Jours_Res)-1 and ildata < len(Jours_Core)-2:
        Nrun = 0
        C = 0
        while Jrun < Jfin and ilrun < len(Jours_Res)-1:
            Jrun = Jours_Res[ilrun]
            C += CSED[ilrun]
            Nrun += 1
            ilrun += 1
        if not np.isnan(Ce_dep[ildata]):
            Jour_Deb.append(Jdeb / 365 + 1945)
            Jour_Fin.append(Jfin / 365 + 1945)
            Archive.append(Ce_dep[ildata])
            if Nrun > 0:
                Averaged_Model.append(C / Nrun)
        ildata += 1
        Jdeb = Jfin
        Jfin = Jours_Core[ildata + 1]
    return Jour_Deb, Jour_Fin, Archive, Averaged_Model

Jour_Deb, Jour_Fin, Archive, Averaged_Model = ModeleMeanvsMesure()

################################################################################################################

# Résultats sous excel

def Excel_res():
    wb = Workbook()

    # Feuille des résultats

    RESULTS = wb.active
    RESULTS.title = "RESULTS"
    RESULTS['A1'] = 'Date'
    RESULTS['B1'] ='Q (m3/s)'
    RESULTS['C1'] = 'd50 (µm)'
    RESULTS['D1'] = 'SS (mg/l)'
    RESULTS['E1'] = 'SSR (mg/l)'
    RESULTS['F1'] = 'SSNR (mg/l)'
    RESULTS['G1'] = 'CSOL (Bq/kg)'
    RESULTS['H1'] = 'FRJT (Bq/s)'
    RESULTS['I1'] = 'CRIV,SOL (Bq/l)'
    RESULTS['J1'] = 'CRIV,RJT (Bq/l)'
    RESULTS['K1'] = 'CRIV (Bq/l)'
    RESULTS['L1'] = 'CRIV,E (Bq/l)'
    RESULTS['M1'] = 'CRIV,NE (Bq/l)'
    RESULTS['N1'] = 'CRIV,DIS (Bq/l)'
    RESULTS['O1'] = 'CRIV,SSR (Bq/kg)'
    RESULTS['P1'] = 'CRIV,SS (Bq/kg)'
    RESULTS['Q1'] = 'CSED (Bq/kg)'

    for cellule in RESULTS[RESULTS.max_row]:
        cellule.font = Font(bold=True)

    for col, valeurs in enumerate([Date, tab_Q, tab_d50, tab_SS, SSR, SSNR, CSOL, FRJT, CRIV_SOL, CRIV_RJT, CRIV, CRIV_E, CRIV_NE, CRIV_DIS, CRIV_SSR, CRIV_SS, CSED], start=1):
        for row, valeur in enumerate(valeurs, start=2):
            RESULTS.cell(row=row, column=col, value=valeur)
            
    # Feuille de comparaison des résultats aux mesures

    vsMesures = wb.create_sheet(title="VsMesures")
    vsMesures['A1'] = 'Start (Year)'
    vsMesures['B1'] = 'End (Year)'
    vsMesures['C1'] = 'Archive (Bq/kg)'
    vsMesures['D1'] = 'Averaged Model (Bq/kg)'

    for cellule in vsMesures[vsMesures.max_row]:
        cellule.font = Font(bold=True)

    for col, valeurs in enumerate([Jour_Deb, Jour_Fin, Archive, Averaged_Model], start=1):
        for row, valeur in enumerate(valeurs, start=2):
            vsMesures.cell(row=row, column=col, value=valeur)

    return wb.save('Résultats python.xlsx')

Excel_res()

################################################################################################################

fin_chrono = time.time()
temps_execution = fin_chrono - deb_chrono
print("Temps d'exécution =", temps_execution, 's')
```

## Version finale améliorée par Mme Valérie Nicoulaud Gouin


# I.1. Détermination de Csol

## 1. Contexte

Toute première étape de mon alternance, c'est ici que tout commence et que le sujet m'est introduit.

## 2. Objectif

A partir d'un modèle semi-empirique établi par M. Patrick Boyer, je dois faire un script python qui suivra ce modèle. 
Sachant qu'un code sur excel existe déjà, il permet à partir de données de rejets liquides, de la carotte sédimentaire et d'autres paramètres de déterminer la concentration dans les sol (Csol) du nucléotide le césium 137 (Cs137). 

Cependant ce code excel prenait trop de temps à s'exécuter. Mon objectif a donc été de reprendre le modèle et ce code excel pour en faire un nouveau sur python et ainsi améliorer le temps d'exécution du code.

## 3. Signification de Csol

Csol représente la concentration moyenne de Césium 137 dans les sols des bassins versants. En voici une description détaillée issue de [*Tomczak_2021_Modelling of solid _ liquid fractionation of trace metals for suspended sediments.pdf*](https://github.com/user-attachments/files/18585992/Tomczak_2021_Modelling.of.solid._.liquid.fractionation.of.trace.metals.for.suspended.sediments.pdf) : 

>**3.4 Statistical distribution of the mean 434 137Cs concentrations in the soils of the catchment**

>The background of the <sup>137</sup>Cs concentrations in the soils of the Rhône watershed is related to the atmospheric fallout from past nuclear tests and the Chernobyl accident (Perkins and Thomas, 1980; Duffa, 2001; Zebracki et al., 2013a,b). This background was estimated between 11 and 19 Bq.kg <sup>-1</sup> 439 for the year 2003 (Antonelli et al., 2008; Eyrolle et al., 2012) and between 3 and 11 Bq.kg<sup>-1</sup> for the year 2018 (Thollet et al., 2018). Consequently, the variations of the minimal and maximal values of C<sub>soil</sub> for the period 2003 to 2018 can be described by two exponential relations with an effective decay period of 7 years for the minimal values (C<sub>soil,MIN</sub> = 11 ∙ e<sup>-0.1∙(y-2003)</sup>) and of 16 years for the maximal values (C<sub>soil,MAX</sub> = 19 ∙ e<sup>-0.042∙(y-2003)</sup>) with y the considered year. These values are within the range of the values published in the scientific literature (Garcia-Sanchez, 2008). They are faster than the radioactive decay period of <sup>137</sup>Cs (30.2 years) because they aggregate the radioactive decay with several transfer processes such as wash-off, erosion, vertical migration in soils, etc...

>The statistical distribution of C<sub>soil</sub> between 2015 and 2018 was determined by discretizing these two curves with a yearly time step. For each year, the interval between the minimal and maximal values was discretized into 20 intervals with the assumption of uniform distribution. These steps provided a dataset of 260 soil activities which was statistically described by a log-normal distribution with GM(C<sub>soil</sub>) = 9.8 Bq.kg<sup>-1</sup> and GSD(C<sub>soil</sub>) = 1.46 (R2 = 0.99).

>For each water flow rate, the distribution of Csoil was scanned between its 2th and 98th percentiles which were 4.5 and 21.3 Bq.kg<sup>-1</sup>. 

## 4. Ma version de code pour Csol

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

## 4. Version finale améliorée par Mme Valérie Nicoulaud Gouin

```python
import numpy as np
import pandas as pd
from datetime import timedelta, datetime
import os

PATH = 'Data'  # directory where are gathered the dataset


# class Concentration:
#     """
#     compute the total concentratio
#         
#     """
#     def __init__(self, df_Parameter:pd.DataFrame, df_Depot:pd.DataFrame) -> None:
#
#     implémentation des pulses de dépôt : 
#       -------------------------------    
#     def compute_pulse(self) :
# 
#     def _funct_decrease(self,x):
#
#     calcul analytique de la concentration des sols superficiels après les dépôts : 
#       --------------------------------------------------------------------------
#     def compute_analytic_SolConcentration(self):
#       # ' Calcul de la concentration du pulse
#       # ' Ajout de la concentration du pulse à la concentration totale
#     calcul du flux des rejets liquides :
#       --------------------------------
#     def compute_liquid_release_flux(self):
#       # 'Ecriture du flux (Bq/s)
#
#     calcul des concentrations de la rivière : 
#       -------------------------------------
#     def compute_river_concentration(self):
    
#       # ' Ecriture de : temps (j), Q (m3/s), d50 (µm) et SS (mg/l)
        # ' Ecriture de SSR (mg/l): si d < d50 -> SSR = SS*(1-(1-2*d/d50)^3) sinon SSR = SS     
        # ' Ecriture de SSNR (mg/l) : SSNR = SS - SSR       
        # ' Ecriture de la concentration dans les sols ramenée à la masse sèche, CRIV,SOL (Bq/l): CRIV,SOL = CSOL*SS       
        # ' Ecriture de la concentration des induite par les rejets, CRIV,RJT (Bq/l): CRIV,RJT = FRJT/Q        
        # ' Ecriture de la concentration total, CRIV (Bq/l): CRIV = CRIV,SOL + CRIV,RJT       
        # ' Ecriture de la concentration échangeable totale, CRIV,E (Bq/l) : CRIV,E = CRIV,RJT + CSOL*SSR       
        # ' Ecriture de la concentration non échangeable totale, CRIV,NE (Bq/l) : CRIV,NE = CSOL*SSNR       
        # ' Ecriture de la concentration disssoute, CRIV,DIS (Bq/l) : CRIV,DIS = CRIV,E/(1+SSR*Kd)        
        # ' Ecriture de la concentration dans la fraction réactive des SS, CRIV,SSR (Bq/kg) : CRIV,SSR = Kd*CRIV,DIS       
        # ' Ecriture de la concentration dans les SS, CRIV,SS (Bq/kg) : CRIV,SS = (CRIV,SSR*SSR + CSOL*SSNR)/SS       
        # ' Ecriture de la concentration dans les sédiments ramenée à la masse sèche, CSED (Bq/kg) : CSED = CRIV,DIS*nsed/ro/(1-nsed) + CRIV,SS

 
class Concentration:
    """
    compute the total concentration
        
             
    """
    def __init__(self, df_Parameter:pd.DataFrame, df_Depot:pd.DataFrame,df_Release:pd.DataFrame, df_Carot:pd.DataFrame, Nj) -> None:
        self.df_Parameter = df_Parameter
        self.df_Depot = df_Depot
        self.df_Release = df_Release
        self.debRelease = self.df_Release.loc[0,'Jours/1945']
        self.df_Carot = df_Carot
        self.InitDepot = self.df_Depot.loc[0,'Date']
        self.Pulse = self.compute_pulse()
        self.SCT = self.compute_analytic_SolConcentration(Nj)
        self.Release = self.compute_liquid_release_flux()
        self.RCT = self.compute_river_concentration(Nj)
        self.AveragedModel = self.ModeleMeanvsMesure()

    def compute_pulse(self) :
        Pulse = pd.DataFrame([],columns = ['jd',  'FD'])
        Pulse.jd = range(0,self.df_Parameter.NjD[0])
        elementFD = [e for x in zip(*[self.df_Depot.FD.values]*365) for e in x]
        Pulse.FD = elementFD
        return(Pulse)
    
    def _funct_decrease(self,x):
        result = np.exp(-self.df_Parameter.lrnero[0] * x) / (self.df_Parameter.B[0] - np.exp(-self.df_Parameter.lmig[0] * x))            
        return(result)
    
    
    def compute_analytic_SolConcentration(self,Nj):
        
        SCT = pd.DataFrame([],index = range(0,Nj),columns = ['pdt',  'CT'])
        SCT['CT'] = 0
        SCT['pdt'] = pd.date_range(self.InitDepot.date() , self.InitDepot.date() + timedelta(days=Nj-1),freq='D') 
        
        SCT.loc[range(1,self.df_Parameter.NjD[0]),'CT'] = [self.df_Parameter.E[0] * np.dot(self._funct_decrease((ij- self.Pulse.loc[0:(ij-1),'jd'])*self.df_Parameter.dt[0]).values,self.Pulse.loc[0:(ij-1),'FD'].values) for ij in range(1,self.df_Parameter.NjD[0])]
        SCT.loc[range(self.df_Parameter.NjD[0],Nj),'CT'] = [self.df_Parameter.E[0] * np.dot(self._funct_decrease((ij- self.Pulse.loc[0:(self.df_Parameter.NjD[0]-1),'jd'])*self.df_Parameter.dt[0]).values,self.Pulse.loc[0:(self.df_Parameter.NjD[0]-1),'FD'].values) for ij in range(self.df_Parameter.NjD[0],Nj)]     
        return(SCT)
    
    def compute_liquid_release_flux(self):
        Release = pd.DataFrame([],columns = ['pdt',  'FR'])
        Release['FR'] = 0
        Release['pdt'] = pd.date_range(self.InitDepot.date() , self.InitDepot.date() + timedelta(days=int(self.df_Parameter.NjR[0])-1),freq='D') 

        elementFR = [e for x in zip(*[self.df_Release.FR.values]*365) for e in x]
        Release.loc[range(self.debRelease,self.df_Parameter.NjR[0]),'FR']  = elementFR
        return(Release)
    
    def compute_river_concentration(self, Nj):
        RCT = pd.DataFrame([],index = range(0,Nj),columns = ['pdt',  'Q', 'd50', 'SS', 'SSR', 'SSNR','CSOL', 'FRJT', 'CRIV_SOL', 'CRIV_RJT', 'CRIV', 'CRIV_E', 'CRIV_NE', 'CRIV_DIS', 'CRIV_SSR', 'CRIV_SS','CSED'])
        RCT['pdt'] = pd.date_range(self.InitDepot.date() , self.InitDepot.date() + timedelta(days=Nj-1),freq='D') 
        RCT['pdt'] = pd.to_datetime(RCT['pdt'])
        RCT['Q'] = [self.df_Parameter.Q[0]]*Nj
        RCT['d50'] = [self.df_Parameter.d50[0]]*Nj
        RCT['SS'] = [self.df_Parameter.SS[0]]*Nj
        RCT['SSR'] = [self.df_Parameter.SS[0]]*Nj
        RCT.loc[RCT.d50 > self.df_Parameter.d[0] * 2,'SSR'] = self.df_Parameter.SS[0] * (1 - pow(1 - 2 * self.df_Parameter.d[0] / self.df_Parameter.d50[0],3))
        RCT['SSNR'] = RCT['SS'] -RCT['SSR']
        RCT['CSOL'] = self.SCT['CT']
        RCT.loc[self.debRelease:self.df_Parameter.NjR[0],'FRJT'] = self.Release['FR']
        RCT['CRIV_SOL'] = 1e-6 * self.SCT['CT'] * RCT['SS']       
        RCT['CRIV_RJT'] = 0
        RCT.loc[self.debRelease:self.df_Parameter.NjR[0],'CRIV_RJT'] = self.Release['FR']/RCT.loc[self.debRelease:self.df_Parameter.NjR[0]]['Q'] / 1000
        RCT['CRIV'] = RCT['CRIV_SOL'] +RCT['CRIV_RJT']
        RCT['CRIV_E'] = RCT['CRIV_RJT'] + 1e-6 * self.SCT['CT'] * RCT['SSR']
        RCT['CRIV_NE'] =  1e-6 * self.SCT['CT'] * RCT['SSNR']
        RCT['CRIV_DIS'] = RCT['CRIV_E'] /(1 + 1e-6 * self.df_Parameter.Kdd[0] * RCT['SSR'])
        RCT['CRIV_SSR'] = RCT['CRIV_DIS'] * self.df_Parameter.Kdd[0]
        RCT['CRIV_SS'] = (RCT['CRIV_SSR'] * RCT['SSR'] + self.SCT['CT'] * RCT['SSNR'])/RCT['SS'] 
        RCT['CSED'] = RCT['CRIV_DIS'] * self.df_Parameter.nrosed[0] / 1000 + RCT['CRIV_SS']
        return(RCT)

    def ModeleMeanvsMesure(self):
        # Nj = (2020 - 1945) * 365
        # MMM = pd.DataFrame([],index = range(0,Nj),columns = ['Time',  'Archive', 'Averaged_Model'])
        # jdeb = self.df_Carot.Date[0]
        # jfin = self.df_Carot.Date[1]
        # jrun = self.InitDepot.date()
        # if (jrun > jdeb) :
        #     # cherche la date dans les données df_Carot.Date telle qu'elle soit >= jrun
        #     index_date_carot = self.Carot.index[self.df_Carot.Date >= jrun].tolist()
        #     jdeb = self.df_Carot.loc[index_date_carot[0],'Date']
        #     jfin = self.df_Carot.loc[index_date_carot[1],'Date']
        # if (jrun <jdeb):
        #     # cherche la date dans le modèle self.df_Depot.Date telle qu'elle soit >= jdeb
        #     index_date_depot = self.df_Depot.index[self.df_Depot.Date >= jdeb].tolist()
        #     jrun = self.df_Depot.loc[index_date_depot[0],'Date']
        # #moyenne de RCT['CSED'] modèle jusqu'à la mesure suivante
        # index_deb = index_date_depot[0]
        # index_fin = self.df_Depot.index[self.df_Depot.Date >= jfin].tolist()[0]
        # meanloc= np.mean(self.RCT.loc[index_deb:index_fin,'CSED'])
        AveragedModel = pd.DataFrame([],columns = ['Time',  'Archive', 'AveragedModel'])
        format = '%Y-%m-%d'
        Date_mean = [(datetime(int(x), 1, 1) + timedelta(days = (x % 1) * 365)).strftime(format) for x in self.df_Carot.Age_mean]
        Date_min = [(datetime(int(x), 1, 1) + timedelta(days = (x % 1) * 365)).strftime(format) for x in self.df_Carot.Age_min]
        Date_min[0] =  self.RCT.pdt[0]
        Date_max = [(datetime(int(x), 1, 1) + timedelta(days = (x % 1) * 365)).strftime(format) for x in self.df_Carot.Age_max]
        Date_max[len(self.df_Carot.Age_mean)-1]= self.RCT.pdt[len(self.RCT.pdt)-1].strftime(format)
        averagedModel = [np.mean(self.RCT.loc[np.where(self.RCT.pdt == Date_min[i])[0][0]:np.where(self.RCT.pdt == Date_max[i])[0][0],"CSED"]) for i in range(len(Date_min))]
        AveragedModel.Time = Date_mean
        AveragedModel.Archive = self.df_Carot["Cesium137_Bq.kg\n(depose)"]
        AveragedModel.AveragedModel = averagedModel
        return(AveragedModel)
```


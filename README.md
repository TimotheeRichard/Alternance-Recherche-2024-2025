# I.2.d. Comparaison prédictions/mesures

## 1. Injection des valeurs calibrées des paramètres dans le modèle

**On utilise différents scritps python afin de déterminer la concentration d'après le modèle grâce aux valeurs calibrées des paramètres.**

**Les valeurs calibrées sont les médianes de Tmig et de pero déterminées grâce à leurs distribution a posteriori**

**Pour le calcul de la concentration dans le cas du modèle des moyennes, on utilise ces deux scripts python :**

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

```python
import numpy as np
import pandas as pd
import os

PATH = 'Data'  # directory where are gathered the dataset


# class Read_data:
#     """
#     read the dataset
#         name_river : name of studied river
#             
#         
#     """
#     def __init__(self, names_fleuve:str) -> None:
#         self.filenames = find_csv_filenames()
#          for i in range(0,len(filenames)):
#            if (filenames[i].find('Meuse') != -1):
#                print(" Meuse file : ", filenames[i])
#       
#     def find_csv_filenames():
#         filenames = os.listdir(path_to_dir)
#         return [ filename for filename in filenames if filename.endswith( suffix ) ]
    
 
class Read_data:
    """
    read the dataset
        name_river : nom de la rivière étudiée (1ere lettre en majuscule)
             
    """
    def __init__(self, name_river:str, start_depot, start_release, start_carot) -> None:
        print("path = ", PATH)
    #    filenames = os.listdir(PATH)
    #    suffix=".csv"
    #    self.filenames = [ filename for filename in filenames if filename.endswith( suffix ) ]
        self.filenames = self.find_csv_filenames()
        self.filenames_river = []
        for i in range(0,len(self.filenames)):
            if (self.filenames[i].find(name_river) != -1):
                print(" files of river ", name_river, " : ", self.filenames[i])
                self.filenames_river.append(self.filenames[i])
        ### introduire un test sur la présence des bons fichiers 
        self.df_Parameter = self.read_parameter(name_river)        
        self.df_Depot = self.read_depot(start_depot,name_river)
        self.df_Parameter['ND'] = self.df_Depot.shape[0]
        self.df_Parameter['NjD'] = self.df_Depot.shape[0]*365
        self.df_Release = self.read_Release(start_release,name_river)
        self.df_Parameter['NR'] = self.df_Release.shape[0]
        self.df_Parameter['NjR'] = self.df_Release.loc[0,'Jours/1945']+self.df_Release.shape[0]*365
        #self.df_Parameter['NjR'] = self.df_Release.shape[0]*365
        self.df_Carot = self.read_carot(start_carot,name_river)
#
    def read_parameter(self,name_river) :
        
        df_Parameter = pd.read_csv(os.path.join(PATH, 'Parametres'+name_river+'.csv'),sep=";",decimal=",")
        #print(df_Parameter.columns)
        df_Parameter.rename(columns={'z0 (cm)': 'z0', 'zmax (cm)':'zmax', 'ro (kg/cm3)': 'ro',
                             'Tmig(j)':'Tmig', 'Lrn (/j)': 'lrn', '%ero/an': 'pero', 
                             'Dt (j)':'dt','Kdd (l/kg)':'Kdd', 'd (microm)': 'd',
                             'Q (m3/s)': 'Q','SS (mg/L)' : 'SS', 'd50 (microm)' : 'd50'}, inplace=True)

        df_Parameter['lmig'] = np.log(2)/df_Parameter.Tmig
        df_Parameter['lero'] = df_Parameter.pero / 100 / 365
        df_Parameter['lrnero'] = df_Parameter.lrn + df_Parameter.lero
        df_Parameter['nrosed'] = df_Parameter.nsed / df_Parameter.ro / (1-df_Parameter.nsed)
        df_Parameter['A'] = (df_Parameter.nsol-df_Parameter.n0)*df_Parameter.z0/ (1-df_Parameter.nsol)
        df_Parameter['B'] = (df_Parameter.A + df_Parameter.zmax) / (df_Parameter.zmax -df_Parameter.z0) 
        df_Parameter['E'] = (df_Parameter.B - 1) * df_Parameter.dt / df_Parameter.ro / (1-df_Parameter.n0)/df_Parameter.z0

        return(df_Parameter)  
    
    def update_parameter(self,list_parameter) :
        self.df_Parameter['pero'] = list_parameter["pero"]
        self.df_Parameter['Tmig'] = list_parameter["Tmig"]
        self.df_Parameter['lmig'] = np.log(2)/self.df_Parameter.Tmig
        self.df_Parameter['lero'] = self.df_Parameter.pero / 100 / 365
        self.df_Parameter['lrnero'] = self.df_Parameter.lrn + self.df_Parameter.lero

        return(self.df_Parameter)
    
    def update_depot(self,type) :
        if (type == "ReleaseOnly"):
            self.df_Depot.FD = 0
        if (type == "Tchernobyl"):
            self.df_Depot.loc[self.df_Depot.Annee<=1985,"FD"] = 0
            self.df_Release.FR = 0
        if (type == "TestOnly"):
            self.df_Depot.loc[self.df_Depot.Annee>1985,"FD"] = 0
            self.df_Release.FR = 0
        return(self.df_Depot)

    def read_depot(self, start,name_river):
        df_Depot = pd.read_csv(os.path.join(PATH, 'Depot'+name_river+'.csv'),sep=";",decimal=",")
        df_Depot = df_Depot.loc[start:]
        df_Depot = df_Depot.reset_index()
        df_Depot.Date=pd.to_datetime(df_Depot.Date,format="%d/%m/%Y")
        df_Depot.rename(columns={'Depots\n(Bq/m2/an)': 'FY', 'Depots\n(Bq/cm2/j)':'FD'}, inplace=True)
        #df_Depot.FD = df_Depot.FY/100/100/365
        #Détermination du nombre de dépôt
        #df_Depot['jd'] = range(0,df_Depot.shape[0]*365,365)
        #df_Depot['jf'] = range(364,df_Depot.shape[0]*365+364,365)
        # Jdeb = 0
        # Jfin = 364
        # for i in range(0,df_Depot.shape[0]) :

        #     df_Depot.loc[i,'jd'] = Jdeb
        #     df_Depot.loc[i,'jf'] = Jfin
        #     Jdeb = Jfin + 1
        #     Jfin = Jfin + 365
        #     #print('Jdeb = ', Jdeb, ' Jfin = ', Jfin)
       
        return(df_Depot)
    
    def read_Release(self,start,name_river):
        df_Release = pd.read_csv(os.path.join(PATH, 'Rejet'+name_river+'.csv'),sep=";",decimal=",")
        df_Release = df_Release.loc[start:]
        df_Release = df_Release.reset_index()
        df_Release.Date=pd.to_datetime(df_Release.Date,format="%d/%m/%Y")
        df_Release.rename(columns={'Total\n(Bq/s)': 'FR'}, inplace=True)
        #deb = df_Release.loc[0,'Jours/1945']
        #df_Release['jd'] = range(deb,deb+df_Release.shape[0]*365,365)
        #df_Release['jf'] = range(deb+365,deb+365+df_Release.shape[0]*365,365)
        # Jdeb = df_Release.loc[0,'Jours/1945']
        # Jfin = Jdeb + 365
        # for i in range(0,df_Release.shape[0]) :
        #     df_Release.loc[i,'jd'] = Jdeb
        #     df_Release.loc[i,'jf'] = Jfin
        #     Jdeb = Jfin
        #     Jfin = Jdeb + 365
            #print('Jdeb = ', Jdeb, ' Jfin = ', Jfin)
        
        return(df_Release)
    
    def read_carot(self,start,name_river):
        df_Carot = pd.read_csv(os.path.join(PATH, 'Carot'+name_river+'.csv'),sep=";",decimal=",")
        df_Carot = df_Carot.loc[start:]
        df_Carot = df_Carot.reset_index()
        df_Carot.Date=pd.to_datetime(df_Carot.Date,format="%d/%m/%Y")
        return(df_Carot)
                    
    def find_csv_filenames(self):
        print("path", PATH, " type = ", type(PATH))
        filenames = os.listdir(PATH)
        suffix=".csv"
        return [ filename for filename in filenames if filename.endswith( suffix ) ]
```


**Ensuite, pour chaque fleuve on utilise les scripts python ci-dessous pour déterminer le modèle des moyennes et le modèle journalier. 
Exemple pour la Moselle :**

```python
import numpy as np
import pandas as pd
from datetime import timedelta

from Read_Path import Read_data
from Concentration import Concentration

ReadMoselle = Read_data("Moselle",start_depot=0,start_release=0, start_carot=0) # On lit les données
Nj =  (2020 - 1945) * 365 # Nbr de jours

ReadMoselle.df_Carot.head()

ReadMoselle.df_Parameter

ReadMoselle.df_Parameter.values

ReadMoselle.df_Parameter.lrnero.values

Newparameter = pd.DataFrame([[1319.0800,5.0692]],columns = ['Tmig',  'pero'])
Newparameter # On prend les médianes de Tmig et de pero

ReadMoselle.update_parameter(Newparameter) # On met ces valeurs dans les paramètres

ReadMoselle.df_Parameter.lmig # On recalcule lmig avec la nouvelle valeur de Tmig

ReadMoselle.df_Depot

ReadMoselle.df_Release.head()

ReadMoselle.df_Carot

ReadMoselle.df_Carot["Cesium137_Bq.kg\n(depose)"]

Mycompute = Concentration(ReadMoselle.df_Parameter, ReadMoselle.df_Depot,ReadMoselle.df_Release, ReadMoselle.df_Carot,Nj) # On fait le calcul complet de csed

print(Mycompute.RCT.shape)
Mycompute.RCT.head()

Mycompute.AveragedModel

Mycompute.RCT['pdt'] = pd.to_datetime(Mycompute.RCT['pdt'])

Mycompute.RCT.dtypes

from datetime import timedelta, datetime
format = '%Y-%m-%d'
Date_mean = [(datetime(int(x), 1, 1) + timedelta(days = (x % 1) * 365)).strftime(format) for x in ReadMoselle.df_Carot.Age_mean]
Date_min = [(datetime(int(x), 1, 1) + timedelta(days = (x % 1) * 365)).strftime(format) for x in ReadMoselle.df_Carot.Age_min]
Date_min[0] =  Mycompute.RCT.pdt[0]
Date_max = [(datetime(int(x), 1, 1) + timedelta(days = (x % 1) * 365)).strftime(format) for x in ReadMoselle.df_Carot.Age_max]
Date_max[len(Mycompute.df_Carot.Age_mean)-1]= Mycompute.RCT.pdt[len(Mycompute.RCT.pdt)-1].strftime(format)
Date_mean
Result= pd.DataFrame([],columns = ['Date_mean',  'Date_min', 'Date_max','Time','Archive','AveragedModel'])
Result.Date_mean = Date_mean
Result.Date_min = Date_min
Result.Date_max = Date_max
Result.Time = Mycompute.AveragedModel.Time
Result.Archive = Mycompute.AveragedModel.Archive
Result.AveragedModel = Mycompute.AveragedModel.AveragedModel
Result # Les résultats réels à partir des archives

Mycompute.RCT[["pdt","CSED"]].to_csv("DailyModel_Moselle.csv") # Crée le fichier DailyModel_Moselle

Result.to_csv("AveragedModel_Moselle.csv",sep=";",index=False) # Crée les fichiers AveragedModel_Moselle
```

**Cela nous donne des fichiers .csv donnant le modèle moyen et le modèle journaliers.**

# I.2.f. Contributions

## 1. Différentes contributions dans le modèle

Une fois le modèle avec les paramètres calibrés établi, on souhaite voir les contributions des différents phénomènes : **la catastrophe de Tchernobyl, les essais nucléaires et les rejets liquides des Centrales**.

Pour ça, Mme. Valérie Nicoulaud Gouin a établi des scripts python permettant de déterminer les contributions de chacun de ces phénomènes dans la concentration en Césium 137.
Ce  script utilise le dernier script python donné en I.1. Il lit aussi les données des carottes grâce à ce script python et aussi les fichiers .csv qui contiennent les données d'entrées du modèle :  

```python
import numpy as np
import pandas as pd
import os

PATH = 'Data'  # directory where are gathered the dataset
 
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

## 2. Tchernobyl

Par exemple, dans le cas de la **Moselle** voici le code qui donne la contribution de **Tchernobyl** dans le modèle :

```python
import numpy as np
import pandas as pd
from datetime import timedelta

from Read_Path import Read_data
from Concentration import Concentration

ReadMoselle = Read_data("Moselle",start_depot=0,start_release=0, start_carot=0)
Nj =  (2020 - 1945) * 365
ReadMoselle.df_Parameter
ReadMoselle.df_Parameter.values
ReadMoselle.df_Parameter.lrnero.values
Newparameter = pd.DataFrame([[1319.0800,5.0692]],columns = ['Tmig',  'pero'])
ReadMoselle.update_parameter(Newparameter)
ReadMoselle.df_Parameter.lmig
ReadMoselle.df_Depot
ReadMoselle.update_depot("Tchernobyl")
ReadMoselle.df_Carot
ReadMoselle.df_Carot["Cesium137_Bq.kg\n(depose)"]
Mycompute = Concentration(ReadMoselle.df_Parameter, ReadMoselle.df_Depot,ReadMoselle.df_Release, ReadMoselle.df_Carot,Nj)
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
Mycompute.RCT[["pdt","CSED"]].to_csv("DailyModel_TchernobylOnly_Moselle.csv")
Result.to_csv("AveragedModel_TchernobylOnly_Moselle.csv",sep=";",index=False)
```

**On obtient alors deux fichiers csv, l'un donnant la contribution journalière et l'autre celle moyenne.**

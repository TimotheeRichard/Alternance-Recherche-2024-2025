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


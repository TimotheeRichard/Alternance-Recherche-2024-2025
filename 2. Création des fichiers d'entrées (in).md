## Création des fichiers .in

**On utilise le script R ci_dessous pour créer les fichiers .in permettant de simuler trois chaînes de Markov à 200 itérations avec chacune un différent seed.**

```r
###############
###
### Ecriture des fichiers in
###
##########################################################
rm(list = ls()) #supprime tous les objets dans l'environnement de travail
setwd("C:/Users/richa/OneDrive/Desktop/Alternance recherche/Bayesien Informatique/mcsim_under_R/MCSim under R/Trajectory")
library(lubridate)
i = 3 # Numéro de la chaine
seed = 0
if(i == 1){
  seed = 1835128
}
if(i == 2){
  seed = 634128
}
if(i == 3){
  seed = 3412895
}
nb_iter = 200;

List_Catchment = c("Meuse","Loire","Moselle", "Rhin", "Rhone")#Catchment = bassin versant

Name_catchment = List_Catchment[3]

RepData = paste("C:/Users/richa/OneDrive/Desktop/Alternance recherche/Bayesien Informatique/mcsim_under_R/MCSim under R/Trajectory/",Name_catchment,"/Data",sep="")

RepIn = paste(Name_catchment,"/In/",sep="") #sep="" dit qu'on va coller les deux chaînes de caractères juste avant sans rien entre les deux

df_Parameters = read.table(file =paste(RepData,"/Parametres",Name_catchment,".csv",sep=""),sep=";",dec=",",header=TRUE) #lecture des paramètres
head(df_Parameters) #juste afficher pour voir si c'est bon je pense
names(df_Parameters) = c("n0","nsol","z0","zmax","ro","Tmig","lrn","pero","Dt","Kdd","d","Q","SS","d50","nsed") #Redéfinit les noms des colonnes pour éviter les unités et tout dans les noms

df_Depot = read.table(file =paste(RepData,"/Depots",Name_catchment,".csv",sep=""),sep=";",dec=",",header=TRUE) #Tout pareil avec les dépots
head(df_Depot)
names(df_Depot) = c("Annee","Date","Depot_y","Depot_d")

df_Release = read.table(file =paste(RepData,"/Rejets",Name_catchment,".csv",sep=""),sep=";",dec=",",header=TRUE)
head(df_Release)
names(df_Release)[3] = "DateRelease" #troisième colonne renommée
names(df_Release)[ncol(df_Release)] = "TotalRelease" #dernière colonne renommée

df_Carot = read.table(file =paste(RepData,"/Cores",Name_catchment,".csv",sep=""),sep=";",dec=",",header=TRUE)
head(df_Carot)
names(df_Carot)[1] = "Age_mean"
names(df_Carot)[4] = "Cesium137_Bq.kg..mesure."
names(df_Carot)[5] = "Cesium137_Bq.kg..depose." 

name_file_in = paste("model_Trajectory_MCMC_chain",i,".in",sep="")
#name_file_out = "trajectory.out"
name_MCMC_out = paste("trajectory.MCMC_",i,".out",sep="")

file.create(paste(RepIn,name_file_in,sep="")) #Création d'un fichier vide

############ On passe à la MCMC ici je pense ##############################

Tmig_min = 100.;
Tmig_max = 5000.;
pero_min = 0.5;
pero_max = 10.;
sigmasq_AM_par1 = 3.;
sigmasq_AM_par2 = 0.5;

Nj = 27667.;
NjD = nrow(df_Depot)*365;
NjR = df_Release$DateRelease[nrow(df_Release)] + 365

param<-paste("\t\t\t\t\t\t n0 = ", df_Parameters$n0 ,";
             nsol = ", df_Parameters$nsol,";
             z0 = ",df_Parameters$z0,";
             zmax = ",df_Parameters$zmax,";
             ro = ", df_Parameters$ro,";
             lrn =", format(df_Parameters$lrn,digits =17 ),";
             Dt =", df_Parameters$Dt,";
             Kdd =", df_Parameters$Kdd,";	
             d =", df_Parameters$d,";	
             Q =", df_Parameters$Q,";	
             SS =", df_Parameters$SS,";
             d50 =",df_Parameters$d50,";
             nsed =", df_Parameters$nsed,";
             nDepot =", nrow(df_Depot),";
             nRelease =", nrow(df_Release)+1,";
             nOutput =", nrow(df_Carot),";
             Nj =", Nj,";
             NjD =", NjD,";
             NjR =", NjR,";")

Depot =  format(df_Depot$Depot_d,digit=9)

Date_Depot = seq(0,(nrow(df_Depot)*365-365),365);

Release = c(format(df_Release$TotalRelease,digit=9),0.);

Date_Release = c(df_Release$DateRelease,NjR);

Date_min_values =floor(date_decimal(df_Carot$Age_min)-date_decimal(decimal_date(ymd("1945-06-15"))))
Date_min_values[1] = 0.

Date_min_dates = floor(date_decimal(df_Carot$Age_min)-date_decimal(decimal_date(ymd("1945-06-15"))))
Date_min_dates[1] = 0

Date_max_values = floor(date_decimal(df_Carot$Age_max)-date_decimal(decimal_date(ymd("1945-06-15"))))
Date_max_values[nrow(df_Carot)] =75*365-1

Date_max_dates = floor(date_decimal(df_Carot$Age_max)-date_decimal(decimal_date(ymd("1945-06-15"))))
Date_max_dates[nrow(df_Carot)] =75*365-1


init_averaged = rep(1,nrow(df_Carot));
time_averaged = floor(date_decimal(df_Carot$Age_mean)-date_decimal(decimal_date(ymd("1945-06-15"))))
time_averaged[length(time_averaged)] = Nj


############Ecriture dans fichier ################################

sink(file = paste(RepIn,name_file_in,sep=""))


cat("#------------------------------------------------------------------------------
# trajectory.MCMC.in
#
# Input file for MCMC simulations of a trajectory model. 
# The output of this file is a Monte Carlo sample from the joint posterior
# distribution of the parameters Tmig and pero.
#
# Copyright (c) 1993-2008 Free Software Foundation, Inc.
#------------------------------------------------------------------------------
\n")

cat("Integrate(Euler, 1);\n
MCMC (\"",Name_catchment,"/Out/Chain",i,"/",name_MCMC_out,"\",
\t\"\",                     # name of restart file
\t\"\",                     # name of data file\n\t",
nb_iter,", 0,                 # iterations, print predictions flag,
\t 1,", nb_iter,",                 # printing frequency, iters to print\n\t",
format(seed,digits =3 ),");           # random seed
\n
Level {\n" ,sep="")
cat("\t\t Distrib (Tmig, Uniform,", Tmig_min,",", Tmig_max, ");\n")
cat("\t\t Distrib (pero, Uniform,", pero_min, ",", pero_max,");\n"); 
cat("\t\t Distrib (sigmasq_AM, InvGamma,",sigmasq_AM_par1, ",", sigmasq_AM_par2, ");\n");

cat("\n\n")
cat("\t\t Depot = NDoses(")
cat(nrow(df_Depot),Depot,Date_Depot,sep=",")
cat(");\n")
cat("\n")

cat("\t\t Release = NDoses(")
cat(nrow(df_Release)+1,Release,Date_Release,sep=",")
cat(");\n")

cat("\n")
cat("\t\t Date_min = NDoses(")
cat(nrow(df_Carot),Date_min_values,Date_min_dates,sep=",")
cat(");\n")
cat("\n")
cat("\t\t Date_max = NDoses(")
cat(nrow(df_Carot),Date_max_values,Date_max_dates,sep=",")
cat(");\n")
cat("\n")

cat("\t\t Averaged = NDoses(")
cat(nrow(df_Carot),init_averaged,time_averaged,sep=",")
cat(");\n")
cat("\n")


cat("\t\t Likelihood (Averaged_out, LogNormal_v, Prediction(Averaged_out),  sigmasq_AM);\n");
cat("\n")
cat("\t\t Simulation { \n");

cat(param)
cat("\n")
cat("\n")
cat("\t\t\t\t  Print(Averaged_out", time_averaged[!is.na(df_Carot$Cesium137_Bq.kg..depose.)],sep=",")
cat(");\n")
cat("\t\t\t\t  Data(Averaged_out", df_Carot[!is.na(df_Carot$Cesium137_Bq.kg..depose.),"Cesium137_Bq.kg..depose."],sep=",")
cat(");\n")

cat("\t\t\t\t  Print(sigmasq_AM_prop", time_averaged[!is.na(df_Carot$Cesium137_Bq.kg..depose.)],sep=",")
cat(");\n")
cat("\t\t\t\t  Data(sigmasq_AM_prop", df_Carot[!is.na(df_Carot$Cesium137_Bq.kg..depose.),"Cesium137_Bq.kg..depose."],sep=",")
cat(");\n")

cat("\n")
cat("\t\t }\n")
cat("}\n\n End.")
sink()
```

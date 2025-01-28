# I.2.a. Simulation pour la calibration

## Détermination de la loi de distribution a priori

**Il faut commencer par déterminer les lois de distribution a priori de nos paramètres, afin de pouvoir par la suite utiliser ces lois dans la simulation des petites chaînes de Markov et des grandes chaînes de Markov**

**_Dans notre cas, on utilise cette distribution a priori :_**

| Paramètres | Loi de distribution a priori | par1 | par2 |
| ------ | ------ | ------ | ------ |
| **Tmig (j)** | Uniforme | 100 | 5000 |
| **%ero** | Uniforme | 0,5 | 10 |

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

## Création des fichiers supp.in

**On utilise les premiers fichiers .in pour en créer de nouveaux qui permettent de simuler des chaînes de Markov à 5000 itérations (les 200 premières étant les anciennes chaînes). On le fait pour les trois différents fichiers .in de l'étape précédente.**

**Premier fichier permettant de simuler une chaîne de 200 itérations :**

```in
#------------------------------------------------------------------------------
# trajectory.MCMC.in
#
# Input file for MCMC simulations of a trajectory model. 
# The output of this file is a Monte Carlo sample from the joint posterior
# distribution of the parameters Tmig and pero.
#
# Copyright (c) 1993-2008 Free Software Foundation, Inc.
#------------------------------------------------------------------------------

Integrate(Euler, 1);

MCMC ("Loire/Out/Chain1/trajectory.MCMC_1.out",
	"",                     # name of restart file
	"",                     # name of data file
	200, 0,                 # iterations, print predictions flag,
	 1,200,                 # printing frequency, iters to print
	8695215);           # random seed


Level {
		 Distrib (Tmig, Uniform, 100 , 5000 );
		 Distrib (pero, Uniform, 0.5 , 10 );
		 Distrib (sigmasq_AM, InvGamma, 3 , 0.5 );


		 Depot = NDoses(49,6.19797e-07,4.42630e-07,6.82999e-09,6.67469e-07,1.34807e-07,8.49948e-09,3.59244e-06,3.59193e-06,1.48740e-05,3.77930e-05,5.51164e-05,4.97911e-05,4.79354e-05,6.16946e-05,1.00889e-04,2.44800e-05,3.21729e-05,1.29151e-04,2.30055e-04,1.41516e-04,6.45591e-05,2.67660e-05,1.34524e-05,1.51690e-05,1.12142e-05,1.52919e-05,1.37644e-05,6.12360e-06,2.21597e-06,8.18517e-06,3.86203e-06,1.75273e-06,5.15005e-06,6.19355e-06,1.89761e-06,1.77986e-06,2.57263e-06,7.22686e-07,4.97362e-07,3.98564e-07,1.14000e-07,3.57534e-04,3.17553e-09,1.41866e-09,6.93201e-10,4.23400e-10,2.48264e-10,1.61746e-10,7.90341e-11,0,365,730,1095,1460,1825,2190,2555,2920,3285,3650,4015,4380,4745,5110,5475,5840,6205,6570,6935,7300,7665,8030,8395,8760,9125,9490,9855,10220,10585,10950,11315,11680,12045,12410,12775,13140,13505,13870,14235,14600,14965,15330,15695,16060,16425,16790,17155,17520);

		 Release = NDoses(45,1490.36022300,1490.36022300,1490.36022300,1490.36022300,1728.18366300, 510.52765090, 412.22729580, 602.48604770, 665.90563170,  79.27447996, 130.01014710, 228.31050230,  47.56468798, 651.63622530, 700.78640280,1950.15220700, 998.85844750,1312.78538800,1312.78538800,1312.78538800,   0.00000000,   0.00000000,   0.00000000,   0.00000000,   0.00000000,  69.76154236,   0.00000000,  91.00710299, 149.35312020,  47.88178590,  50.41856925,  10.46423135,   2.82851345,  19.05758498,   5.99315068,   7.00786403,   5.29553526,  13.09614409,   6.72881786,   8.83434805,   4.83891426,   4.55669711,   3.93201421,  12.02118214,0,7300,7665,8030,8395,8760,9125,9490,9855,10220,10585,10950,11315,11680,12045,12410,12775,13140,13505,13870,14235,14600,14965,15330,15695,16060,16425,16790,17155,17520,17885,18250,18615,18980,19345,19710,20075,20440,20805,21170,21535,21900,22265,22630,22995,23360);

		 Date_min = NDoses(39,0,1186,1843,2500,3158,3815,4582,5312,6043,6737,7286,7869,8454,9002,9513,9952,10426,10901,11376,11851,12289,12764,13202,13604,13932,14298,14627,15138,16161,17037,17950,18827,19740,20617,21530,22479,23575,24818,26059,0,1186,1843,2500,3158,3815,4582,5312,6043,6737,7286,7869,8454,9002,9513,9952,10426,10901,11376,11851,12289,12764,13202,13604,13932,14298,14627,15138,16161,17037,17950,18827,19740,20617,21530,22479,23575,24818,26059);

		 Date_max = NDoses(39,1186,1843,2500,3158,3815,4582,5312,6043,6737,7286,7869,8454,9002,9513,9952,10426,10901,11376,11851,12289,12764,13202,13604,13932,14298,14627,15138,16161,17037,17950,18827,19740,20617,21530,22479,23575,24818,26059,27374,1186,1843,2500,3158,3815,4582,5312,6043,6737,7286,7869,8454,9002,9513,9952,10426,10901,11376,11851,12289,12764,13202,13604,13932,14298,14627,15138,16161,17037,17950,18827,19740,20617,21530,22479,23575,24818,26059,27374);

		 Averaged = NDoses(39,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,877,1530,2182,2834,3486,4217,4947,5678,6408,6992,7575,8158,8742,9267,9733,10201,10667,11133,11601,12067,12534,13001,13409,13759,14109,14459,14809,15705,16601,17497,18393,19289,20185,21081,21977,23022,24216,25411,27667);

		 Likelihood (Averaged_out, LogNormal_v, Prediction(Averaged_out),  sigmasq_AM);

		 Simulation { 
						 n0 =  0.8 ;
             nsol =  0.55 ;
             z0 =  0.5 ;
             zmax =  10 ;
             ro =  0.00265 ;
             lrn = 5.9344800000000001e-05 ;
             Dt = 1 ;
             Kdd = 68000 ;	
             d = 1 ;	
             Q = 2500 ;	
             SS = 30 ;
             d50 = 35 ;
             nsed = 0.8 ;
             nDepot = 49 ;
             nRelease = 45 ;
             nOutput = 39 ;
             Nj = 27667 ;
             NjD = 17885 ;
             NjR = 23360 ;

				  Print(Averaged_out,877,2182,3486,4217,4947,5678,6408,6992,7575,8158,8742,9267,9733,10201,10667,11133,11601,12067,12534,13001,13409,13759,14109,14459,14809,15705,16601,17497,18393,19289,20185,21081,21977,23022,24216,25411,27667);
				  Data(Averaged_out,1.109201,1.73629,4.420123,28.73544,38.15568,99.47335,208.3335,178.1828,117.6312,79.42852,58.00321,54.1511,48.45839,44.2811,42.9929,44.93082,40.52784,35.24999,44.30616,51.00247,43.17532,36.82834,33.62038,39.22608,136.7602,52.10019,33.2299,25.77814,22.16008,16.78586,14.38933,12.36043,12.11735,11.06874,11.02335,10.22104,8.416843);
				  Print(sigmasq_AM_prop,877,2182,3486,4217,4947,5678,6408,6992,7575,8158,8742,9267,9733,10201,10667,11133,11601,12067,12534,13001,13409,13759,14109,14459,14809,15705,16601,17497,18393,19289,20185,21081,21977,23022,24216,25411,27667);
				  Data(sigmasq_AM_prop,1.109201,1.73629,4.420123,28.73544,38.15568,99.47335,208.3335,178.1828,117.6312,79.42852,58.00321,54.1511,48.45839,44.2811,42.9929,44.93082,40.52784,35.24999,44.30616,51.00247,43.17532,36.82834,33.62038,39.22608,136.7602,52.10019,33.2299,25.77814,22.16008,16.78586,14.38933,12.36043,12.11735,11.06874,11.02335,10.22104,8.416843);

		 }
}

 End.
```  

**Fichier modifié permettant de simuler une chaîne à 5000 itérations :**

```in
#------------------------------------------------------------------------------
# trajectory.MCMC.in
#
# Input file for MCMC simulations of a trajectory model. 
# The output of this file is a Monte Carlo sample from the joint posterior
# distribution of the parameters Tmig and pero.
#
# Copyright (c) 1993-2008 Free Software Foundation, Inc.
#------------------------------------------------------------------------------

Integrate(Euler, 1);

MCMC ("Loire/Out/Chain1/trajectory.MCMC_supp1.out",
	"Loire/Out/Chain1/trajectory.MCMC_1.out",                     # name of restart file
	"",                     # name of data file
	5000, 2,                 # iterations, print predictions flag,
	 1,5000,                 # printing frequency, iters to print
	8695215);           # random seed


Level {
		 Distrib (Tmig, Uniform, 100 , 5000 );
		 Distrib (pero, Uniform, 0.5 , 10 );
		 Distrib (sigmasq_AM, InvGamma, 3 , 0.5 );


		 Depot = NDoses(49,6.19797e-07,4.42630e-07,6.82999e-09,6.67469e-07,1.34807e-07,8.49948e-09,3.59244e-06,3.59193e-06,1.48740e-05,3.77930e-05,5.51164e-05,4.97911e-05,4.79354e-05,6.16946e-05,1.00889e-04,2.44800e-05,3.21729e-05,1.29151e-04,2.30055e-04,1.41516e-04,6.45591e-05,2.67660e-05,1.34524e-05,1.51690e-05,1.12142e-05,1.52919e-05,1.37644e-05,6.12360e-06,2.21597e-06,8.18517e-06,3.86203e-06,1.75273e-06,5.15005e-06,6.19355e-06,1.89761e-06,1.77986e-06,2.57263e-06,7.22686e-07,4.97362e-07,3.98564e-07,1.14000e-07,3.57534e-04,3.17553e-09,1.41866e-09,6.93201e-10,4.23400e-10,2.48264e-10,1.61746e-10,7.90341e-11,0,365,730,1095,1460,1825,2190,2555,2920,3285,3650,4015,4380,4745,5110,5475,5840,6205,6570,6935,7300,7665,8030,8395,8760,9125,9490,9855,10220,10585,10950,11315,11680,12045,12410,12775,13140,13505,13870,14235,14600,14965,15330,15695,16060,16425,16790,17155,17520);

		 Release = NDoses(45,1490.36022300,1490.36022300,1490.36022300,1490.36022300,1728.18366300, 510.52765090, 412.22729580, 602.48604770, 665.90563170,  79.27447996, 130.01014710, 228.31050230,  47.56468798, 651.63622530, 700.78640280,1950.15220700, 998.85844750,1312.78538800,1312.78538800,1312.78538800,   0.00000000,   0.00000000,   0.00000000,   0.00000000,   0.00000000,  69.76154236,   0.00000000,  91.00710299, 149.35312020,  47.88178590,  50.41856925,  10.46423135,   2.82851345,  19.05758498,   5.99315068,   7.00786403,   5.29553526,  13.09614409,   6.72881786,   8.83434805,   4.83891426,   4.55669711,   3.93201421,  12.02118214,0,7300,7665,8030,8395,8760,9125,9490,9855,10220,10585,10950,11315,11680,12045,12410,12775,13140,13505,13870,14235,14600,14965,15330,15695,16060,16425,16790,17155,17520,17885,18250,18615,18980,19345,19710,20075,20440,20805,21170,21535,21900,22265,22630,22995,23360);

		 Date_min = NDoses(39,0,1186,1843,2500,3158,3815,4582,5312,6043,6737,7286,7869,8454,9002,9513,9952,10426,10901,11376,11851,12289,12764,13202,13604,13932,14298,14627,15138,16161,17037,17950,18827,19740,20617,21530,22479,23575,24818,26059,0,1186,1843,2500,3158,3815,4582,5312,6043,6737,7286,7869,8454,9002,9513,9952,10426,10901,11376,11851,12289,12764,13202,13604,13932,14298,14627,15138,16161,17037,17950,18827,19740,20617,21530,22479,23575,24818,26059);

		 Date_max = NDoses(39,1186,1843,2500,3158,3815,4582,5312,6043,6737,7286,7869,8454,9002,9513,9952,10426,10901,11376,11851,12289,12764,13202,13604,13932,14298,14627,15138,16161,17037,17950,18827,19740,20617,21530,22479,23575,24818,26059,27374,1186,1843,2500,3158,3815,4582,5312,6043,6737,7286,7869,8454,9002,9513,9952,10426,10901,11376,11851,12289,12764,13202,13604,13932,14298,14627,15138,16161,17037,17950,18827,19740,20617,21530,22479,23575,24818,26059,27374);

		 Averaged = NDoses(39,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,877,1530,2182,2834,3486,4217,4947,5678,6408,6992,7575,8158,8742,9267,9733,10201,10667,11133,11601,12067,12534,13001,13409,13759,14109,14459,14809,15705,16601,17497,18393,19289,20185,21081,21977,23022,24216,25411,27667);

		 Likelihood (Averaged_out, LogNormal_v, Prediction(Averaged_out),  sigmasq_AM);

		 Simulation { 
						 n0 =  0.8 ;
             nsol =  0.55 ;
             z0 =  0.5 ;
             zmax =  10 ;
             ro =  0.00265 ;
             lrn = 5.9344800000000001e-05 ;
             Dt = 1 ;
             Kdd = 68000 ;	
             d = 1 ;	
             Q = 2500 ;	
             SS = 30 ;
             d50 = 35 ;
             nsed = 0.8 ;
             nDepot = 49 ;
             nRelease = 45 ;
             nOutput = 39 ;
             Nj = 27667 ;
             NjD = 17885 ;
             NjR = 23360 ;

				  Print(Averaged_out,877,2182,3486,4217,4947,5678,6408,6992,7575,8158,8742,9267,9733,10201,10667,11133,11601,12067,12534,13001,13409,13759,14109,14459,14809,15705,16601,17497,18393,19289,20185,21081,21977,23022,24216,25411,27667);
				  Data(Averaged_out,1.109201,1.73629,4.420123,28.73544,38.15568,99.47335,208.3335,178.1828,117.6312,79.42852,58.00321,54.1511,48.45839,44.2811,42.9929,44.93082,40.52784,35.24999,44.30616,51.00247,43.17532,36.82834,33.62038,39.22608,136.7602,52.10019,33.2299,25.77814,22.16008,16.78586,14.38933,12.36043,12.11735,11.06874,11.02335,10.22104,8.416843);
				  Print(sigmasq_AM_prop,877,2182,3486,4217,4947,5678,6408,6992,7575,8158,8742,9267,9733,10201,10667,11133,11601,12067,12534,13001,13409,13759,14109,14459,14809,15705,16601,17497,18393,19289,20185,21081,21977,23022,24216,25411,27667);
				  Data(sigmasq_AM_prop,1.109201,1.73629,4.420123,28.73544,38.15568,99.47335,208.3335,178.1828,117.6312,79.42852,58.00321,54.1511,48.45839,44.2811,42.9929,44.93082,40.52784,35.24999,44.30616,51.00247,43.17532,36.82834,33.62038,39.22608,136.7602,52.10019,33.2299,25.77814,22.16008,16.78586,14.38933,12.36043,12.11735,11.06874,11.02335,10.22104,8.416843);

		 }
}

 End.
```


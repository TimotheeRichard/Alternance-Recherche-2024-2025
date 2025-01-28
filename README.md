# I.2.c. Distribution a postériori des paramètres

## 1. Obtention des deux distributions a postériori

**Grâce au script R ci-dessous, à partir des 500 dernières réalisations d'une des chaînes de Markov on trace les densités de probabilité et les densités prédictives pour chacun des paramètres**

```R
##########################################################
##
## Posterior prediction : 
##
## A partir des 500 derniers realisations d'une des chaines 
## on trace les densites de probabilite et les densites predictives
##
##
##
##########################################################
source("../R/plotDensityResults.r")
source("../R/get_densities.r")
source("../R/getPredictiveDistribution2.R")
source("../R/getCredibleIntervals2.r")
source("../R/getPredictiveIntervals1.r")
source("../R/plotTimeSeriesResults1.r")
########################################################
outchain = outchain3[(nrow(outchain3)-500):nrow(outchain3),]
head(outchain)
#rownames(unique(outchain[,c("Tmig.1.","pero.1.", "sigmasq_AM.1.", "LnPrior","LnData", "LnPosterior")]))

outchain = outchain[rownames(unique(outchain[,c("Tmig.1.","pero.1.", "sigmasq_AM.1.", "LnPrior","LnData", "LnPosterior")]))
,]
names(outchain)[2] = "Tmig(1)"
names(outchain)[3] = "pero(1)"
names(outchain)[4] = "sigmasq_AM(1)"

write.table(outchain,file =paste(Name_catchment,"/temp.out",sep=""),sep="\t",quote=FALSE,row.names = FALSE)
## create temp.fit.in

mName = "ModelTrajectory.model"
simMCMCNameFITtemp = "model_Trajectory_temp.fit.in"

model <-function(outchain, ...)
{
  write.table(outchain,file =paste(Name_catchment,"/temp.out",sep=""),sep="\t",quote=FALSE,row.names = FALSE)
  system(paste("../../mcsim_under_R/MCSim_under_R/Trajectory/mcsim_", mName, ".exe ", Name_catchment,"/",simMCMCNameFITtemp, sep = ""))
  #system(paste("C:/Users/richa/OneDrive/Desktop/Alternance recherche/Bayesien Informatique/Deal_MCMC/TRAJECTORY/Moselle/", mName, ".exe ", Name_catchment,"/", simMCMCNameFITtemp, sep = ""))
  run = read.table(file = paste(Name_catchment,"/trajectory.temp.out",sep=""),sep="\t", header = TRUE)
  #print(head(run))
  Output = run[which(run["Output_Var"] == "Averaged_out"),"Prediction"]
  return(Output)
}


outputbayes = outchain3[,c("Tmig.1.","pero.1.","sigmasq_AM.1.")]
names(outputbayes) = c("Tmig","pero","sigma")



pred = getPredictiveDistribution2(outchain, model = model)


run = read.table(file = paste(Name_catchment,"/trajectory.temp.out",sep=""),sep="\t", header = TRUE)

Date_Trajectory = run[which(run["Output_Var"] == "Averaged_out"),"Time"]
Core_Trajectory = run[which(run["Output_Var"] == "Averaged_out"),"Data"] #Data donne les données de la carotte
postInterval = getPredictiveIntervals1(outputbayes, pred, error=NULL)
```

## 2. Distribution a posteriori de Tmig

**En utilisant le code donné avant, on obtient une distribution a posteriori pour le temps de migration vertical dans les sols.**

**Dans le cas de la Moselle, on obtient ceci par exemple :**

![image](https://github.com/user-attachments/assets/e7223eae-1871-4d34-a0f6-acdd657d2aaf)

## 3. Distribution a posteriori de pero

**En utilisant le code donné avant, on obtient une distribution a posteriori pour le pourcentage d'érosion des sols (pero ou %ero).**

**Dans le cas de la Moselle, on obtient ceci par exemple :**

![image](https://github.com/user-attachments/assets/7430f78e-d10d-4012-bdbe-9e1905f07438)

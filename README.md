# I.2.b Analyse de la convergence des chaînes de Markov

## 1. Code d'analyse de convergence des chaînes

**Le code ci-dessous permet d'analyser si les chaînes de Markov produites sont convergentes ou non selon différents facteurs. Un fichier .out résumant ce que les différents critères affirment sur la convergence sera alors produit. La convergence des chaînes est nécessaire pour utiliser la méthode MCMC.**

```R
##########################libraries###################
library(coda)
library(KernSmooth)
library(ggplot2)
library(RColorBrewer)
library(latex2exp)
library(scales)
library(lubridate)

####################################################

getwd()
setwd("C:/Users/richa/OneDrive/Desktop/Alternance recherche/Bayesien Informatique/Deal_MCMC/TRAJECTORY")
rm(list = ls())
source("../R/diagnoseChains.R") #apporte plein de fonction que l'on va utiliser dans la suite du code

### Traitement d'un bassin versant
List_Catchment = c("Meuse","Loire","Moselle", "Rhin", "Rhone")

Name_catchment = List_Catchment[4]
Rep_MCMC = "../../mcsim_under_R/MCSim_under_R/Trajectory/"

file1 = paste(Rep_MCMC,Name_catchment,"/Out/Chain1/trajectory.MCMC_supp",1,".out",sep="")
file2 = paste(Rep_MCMC,Name_catchment,"/Out/Chain2/trajectory.MCMC_supp",2,".out",sep="")
file3 = paste(Rep_MCMC,Name_catchment,"/Out/Chain3/trajectory.MCMC_supp",3,".out",sep="")

### Recuperation des 3 chaines supp

outchain1 = read.table(file = file1, sep ="\t", header = TRUE) # Première chaîne de  Markov à 4800 itérations
outchain2 = read.table(file = file2, sep ="\t", header = TRUE) # Deuxième chaîne de  Markov à 4800 itérations
outchain3 = read.table(file = file3, sep ="\t", header = TRUE) # Troisième chaîne de  Markov à 4800 itérations
head(outchain1)
NbChains = 3 # Nombre de CM
res = list() # Initialisation avec une liste vide
chain=c() # Initialisation avec une liste de chaînes de caractères vide
#i=1
for(i in 1:NbChains)
{
  chain <- append(chain, paste('chain',i,sep='')) # ["chain1","chain2","chain3"]
  res[[i]]=list(paste("LnPosterior.chain",i,sep=""),paste("output.chain",i,sep='')) #Titre des deux listes de res[[i]]
  
  data = read.table(file = paste(Rep_MCMC,Name_catchment,"/Out/Chain",i,"/trajectory.MCMC_supp",i,".out",sep=""), sep ="\t", header = TRUE) # Récupère la i-ème chaîne de Markov
  res[[i]][[1]] = data[,"LnPosterior"] #Sélectionne la colonne des LnPosterior de Data et le met dans la première liste de res[[i]]
  data = as.data.frame(data[,c(-dim(data)[2],-dim(data)[2]+1,-dim(data)[2]+2)]) # Suppression des trois dernières colonnes de data dans data (LnPrior, LnData, LnPosterior)
  res[[i]][[2]] = as.data.frame(data[,c(-1)]) # Met toutes les colonnes de data dans res[[i]][[2]] (excepté la première) (donc Tmig, pero et sigmasq_AM)
  num = length(names(data)[2:dim(data)[2]]) # Met dans num le nbr de colonnes de data, à l'exception de la première colonne (ce sera 3 ici du coup)
  Nbiteration = dim(paste('output.chain',i,sep=''))[1] # ça donne Nbiteration = NULL donc jsp à quoi ça sert
  for(j in 1:num)
  {
    names(res[[i]][[2]])[j] = substr(names(data)[j+1],1, nchar(names(data)[j+1])-3) # Donne le nom de Tmig, etc aux listes de output.chaini
  }
  names(res[[i]]) <- c(paste("LnPosterior.chain",i,sep=""), paste("output.chain",i,sep='')) # ça redonne les noms au deux sous listes mais jsp pourquoi
}
names(res) <- chain # Nomme les listes de res (Chain1, Chain2, Chain3)

parNamesVal = NULL
for(i in 1:num)
{
  parNamesVal <- c(parNamesVal,list(substr(names(data)[i+1],1, nchar(names(data)[i+1])-3)))
}
# On a donc parNamesVal = ["Tmig", "pero",sigmasq_AM]
output.list<-list() # Initialisation d'une liste vide
for(i in res)
{
  output.list[[length(output.list)+1]] <- mcmc(i[[2]]) # mcmc permet de le rendre compatible avec coda
}
output.list <- mcmc.list(output.list) # On a output.list qui est la concaténation des trois chaîne de Markov et qui est sous une forme compatible avec la librairie coda

codachain<-list() # Initialisation d'une liste vide
codalnposterior<-list() # Pareil

for (i in 1:NbChains)
{
  codachain[[i]]=res[[i]][[2]] # codachain contient Tmig, pero et sigmasq_AM
  codalnposterior[[i]]=res[[i]][[1]] # codalnposterior contient lnposterior
}

num= ncol(codachain[[1]]) # La valeur de num change pas du coup, cette ligne ne sert à rien je pense
list_read_coda = list(num=num, codachain=codachain,codalnposterior=codalnposterior,output.list=output.list) # Crée une liste contenant les 4 éléments : num, codachain, codalnposterior, output.list
list_coda_convergence = deal_coda_convergence(list_read_coda[["codachain"]],list_read_coda[["codalnposterior"]],list_read_coda[["output.list"]], N_chain=NbChains)  

fileprefix=paste(Name_catchment,"/Imagessupp/Trajectory",sep="") # Crée juste un chemin vers Imagesupp
cat("   preparing plots\n") #Envoir un message à la console pour dire où on en est
plot_trails(fileprefix,list_read_coda[["num"]],list_coda_convergence[["sum"]], list_read_coda[["codachain"]],list_read_coda[["codalnposterior"]], N_chain=NbChains) # Permet d'obtenir Trajectory_trails.jpg dans Loire/Imagessupp/. On y trace les différente valeurs de Tmig, pero, sigmasq_AM et lnPosterior à chaque itération

densities = plot_density(fileprefix,list_read_coda[["num"]],list_coda_convergence[["sum"]], list_coda_convergence[["hpd"]],list_coda_convergence[["burnin.output.pooled"]]) #Trace les densité des trois paramètres en faisant le fichier Trajectory_dens.jpg dans Imagessupp. Pour chaque paramètre, il va estimer la densité avec la méthode de l'estimateur de noyau (bkde) avec une largeur de bande déterminée par dpik. Ensuite ça trace deux traits verticaux pour les quantiles 2,5% et 97,5% et aussi aux limites inférieure et supérieure de l'intervalle de haute densité postérieure

plot_lag(fileprefix,list_read_coda[["num"]],list_coda_convergence[["burnin.output.pooled"]]) # Fais le fichier Trajectory_lag.jpg qui trace pour chaque itération n sa valeur sur l'axe des x et la valeur de l'itération n+1 sur celle des y, si on observe que ça suit une droite linéaire c'est que ça converge sûrement pas, si ça commence à former une biule c'est que y a convergence. On veut donc voir une sorte de boule se former

plot_autocorrelation(fileprefix,list_read_coda[["num"]],list_coda_convergence[["burnin.output.pooled"]]) # Crée le fichier Trajectory_autocorr.jpg qui trace la corrélation d'une série avec elle-même, pour analyser l'indépendance des échantillons de la MCMC

plot_gelmanRubin(fileprefix,list_coda_convergence[["burnin.output.list"]]) # Crée le graphique Trajectoryhat_gelmanRhat.jpg, ça trace le ration de réduction de variancee de Gelman-Rubin (Rhat) pour chaque paramètre au fil des itérations. Un Rhat proche de 1 indique une bonne convergence

acceptrate  = acceptance_rate(list_coda_convergence[["burnin.output.pooled"]]) # Calcule le taux d'acceptation de chaque MCMC, ça correspond au pourcentage d'échantillons proposés qui sont acceptés lors de la méthode de M-H
gelman      = test_gelman(list_read_coda[["num"]],list_coda_convergence[["burnin.output.list"]]) # Calcule le diagnostique de Gelman-Rubin, ça donne le psrf (Potential Scale Reduction Factor) (c'est le Rhat) et le mpsrf (Multivariate Potential Scale Reduction Factor) (un peu comme le psfr mais ça prend en compte la corrélation entre les différents paramètres et donc si c'est proche de 1 ça indique que les chaînes ont convergé)
geweke      = test_geweke(list_read_coda[["num"]],list_coda_convergence[["burnin.output.list"]],list_coda_convergence[["chaintodisplay"]]) # Renseigne toi sur le diagnostic de Geweke qui renvoie un score Z (la différence entre les deux moyennes d’échantillons divisée par son erreur standard estimée) ( L’erreur standard est estimée à partir de la densité spectrale à zéro, ce qui prend en compte toute autocorrélation)
heidelberg  = test_heidelberg(list_read_coda[["num"]],list_coda_convergence[["burnin.output.list"]],list_coda_convergence[["chaintodisplay"]]) # Renseigne toi sur le test de Heiselberg
raftery     = list_coda_convergence[["raft"]]
parameters  = list_coda_convergence[["sum"]]

###
### sorties texte, ici on résume tout ce qu'on vient d'obtenir dans un fichier texte
###
cat("   preparing text outputs\n")
nametxt=paste0(fileprefix, "_diagnoseChains.txt")
sink(nametxt)
cat("################################################################################################\n")
cat("\n\nRAFTERY\n\n")
print(raftery)
cat("################################################################################################\n")
cat("\n\nGEWEKE\n\n")
print(geweke)
cat("################################################################################################\n")
cat("\n\nHEIDELBERG\n\n")
print(heidelberg)
cat("################################################################################################\n")
cat("\n\nGELMAN\n\n")
print(gelman)
cat("################################################################################################\n")
cat("\n\nPARAMETERS\n\n")
print(parameters)
cat("################################################################################################\n")
sink()

###
### sortie RData
###
cat("   preparing .RData outputs\n")
nameRData=paste0(fileprefix, "_diagnoseChains.RData")
save(list=c( "parameters", "acceptrate", "densities", "raftery", "geweke", "heidelberg"), file=nameRData)
```

## 2. Critère de Gelman-Rubin

**Sert à évaluer la convergence des MCMC, permet de déterminer si les chaines MCMC ont convergé vers la distribution cible.**

On a plusieurs chaînes MCMC avec des conditions initiales différentes. On va alors comparer les variances intra-chaîne et inter-chaîne. 

Si les chaînes ont convergé vers la même distribution cible, les variances devraient être similaires.
On a m chaînes de longueur n.

**_Calculer la moyenne de chaque chaîne :_**

$$
\bar{\theta_i} = \frac{1}{n} \sum_{j=1}^{n} \theta_{i,j}
$$

**_Calculer la moyenne globale :_**

$$
\bar{\theta} = \frac{1}{m} \sum_{i=1}^{m} \bar{\theta_i}
$$

**_Calculer la variance intra-chaîne W :_**

$$
W = \frac{1}{m} \sum_{i=1}^{m} (\frac{1}{n-1} \sum_{j=1}^{n} (\theta_{i,j} - \bar{\theta_i})^2)
$$
 
**_Calculer la variance inter-chaîne B :_**

$$
B = \frac{n}{m-1} \sum_{i=1}^{m} (\bar{\theta_i} - \bar{\theta})^2
$$

**_Combiner les variances pour obtenir l'estimateur de la variance totale :_**

$$
\hat{V} = \frac{n-1}{n} W + \frac{1}{n} B
$$

**_Calculer le critère de Gelman-Rubin :_**

$$
\hat{R} = \sqrt{\frac{\hat{V}}{W}}
$$
 
**_Interprétation :_**

- **R≈1** : Indique que les chaînes ont probablement convergé vers la même distribution cible. Un R proche de 1 (typiquement R<1.1) est souvent utilisé comme critère de convergence.

- **R>1** : Indique que les chaînes n'ont pas encore convergé. Cela signifie qu'il y a encore une différence notable entre les variances intra-chaîne et inter-chaîne, suggérant que plus de simulations sont nécessaires.

## 3. Diagnostic de convergence de Geweke

**Ce diagnostic permet de vérifier la convergence des chaînes MCMC, ça permet de vérifier si les échantillons provenant des différentes parties de la chaîne proviennent de la même distribution stationnaire, ce qui indiquerait la convergence de la chaîne.**

Ça compare les moyennes de deux segments de la chaîne : le segment initial et le segment final. Si les deux segments proviennent de la même distribution alors leurs moyennes devraient être similaires et la différence normalisée devrait suivre une distribution normale standard.

**_Diviser la chaîne en segments :_**

Diviser la chaîne MCMC en deux segments non superposés. Par exemple, en utilisant les 10 % premiers et les 50 % derniers échantillons de la chaîne.

**_Calculer les moyennes et les variances :_**

- Moyenne et variance du segment initial :

$$
\bar{X_A};\sigma_A^2
$$

- Moyenne et variance du segment final :

$$
\bar{X_B};\sigma_B^2
$$

**_Calculer la statistique de Geweke (Z-score) :_**

$$
Z = \frac{\bar{X_A} - \bar{X_B}}{\sqrt{\sigma_A^2 + \sigma_B^2}}
$$

**_Interprétation :_**

- **Z-scores proches de zéro** : indiquent que les segments initiaux et finaux de la chaîne ont des moyennes similaires, suggérant que la chaîne a convergé.

- **Z-scores éloignés de zéro** (au-delà de ±1.96 ou d'autres seuils selon le niveau de confiance choisi) : indiquent une possible non-convergence de la chaîne, suggérant que plus d'itérations ou un réajustement du modèle pourraient être nécessaires.

## 4. Test de stationarité de Heidelberger Welch

**Ce test examine la stationnarité de la chaîne et ça permet de déterminer si une partie initiale de la chaîne (le burn-in) doit être supprimée pour obtenir des échantillons stationnaires.**

Ce critère s'articule en deux tests : le test de stationnarité et celui de demi-largeur.

- **Test de stationnarité** : Vérifie si la chaîne est stationnaire en examinant si les moyennes des sous-séquences de la chaîne sont stables.

- **Test de demi-largeur** : Évalue la précision des estimations en vérifiant si la demi-largeur de l'intervalle de confiance pour la moyenne est suffisamment petite.


### Test de stationnarité

**_Diviser la chaîne en segments :_**

Diviser la chaîne en plusieurs segments (typiquement 10).

**_Calculer les moyennes des segments :_**

Calculer la moyenne de chaque segment.

**_Effectuer le test :_**

Utiliser un test statistique (comme un test de Student) pour comparer les moyennes des segments. Si les moyennes des segments ne sont pas significativement différentes, la chaîne est considérée comme stationnaire.


### Test de demi-largeur

**_Calculer la moyenne et la variance de la chaîne :_**

Utiliser les échantillons restants après le burn-in pour en calculer la moyenne et la variance.

**_Calculer la demi-largeur de l'intervalle de confiance pour la moyenne :_**

$$
Demi largeur = z \frac{\sigma}{\sqrt{n}}
$$

où z est le quantile de la distribution normale standard correspondant au niveau de confiance choisi, 𝜎 est l'écart-type estimé des échantillons, et 𝑛 est le nombre d'échantillons.

**_Comparer avec la tolérance :_**

Si la demi-largeur est inférieure à un seuil de tolérance spécifié (par exemple, 0.1 fois la moyenne), les échantillons sont considérés comme suffisamment précis.

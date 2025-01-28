# II.2.c. Résultats obtenus

## 1. Résultats incomplets

Comme nous l'avons vu dans l'apport hydraulique, il me manque encore les concentrations de sol dans l'apport.
Ainsi, les résultats que j'ai à ce jour sont encore incomplets et ne traduisent pas parfaitement la concentration en Cs137 dans la distribution qu'on obtient.

Je réglerai ce problème après le rendu de ce rapport, mais ce github sera tout de même modifié en ajoutant les nouvelles avancées sur les résultats.

## 2. Distribution hydraulique et distribution des nucléotides

**Distribution hydraulique :**

En faisant tourner CASTEAURX sur toutes la plage temporelle de données, et en utilisant le réseau discrétisé par pas d'espace de 50 mètres, on obtient une distribution du débit sur tout le réseau.
À chaque bief, on obtient la distribution du débit sur toute la plage temporelle. Par exemple, au bief d'entrée (là où a été rentré le débit), on retrouve notre débit d'entrée : 

![Capture d'écran 2025-01-16 151249](https://github.com/user-attachments/assets/9750a194-ae37-4789-90f6-3150533481e7)

**Distribution de nucléotides :**

C'est ici que les résultats sont incomplets, on obtient une distribution temporelle de la concentration en Cs137 pour chaque bief.
Seulement, ça ne traduit que l'apport de la centrale de Cattenom pour le moment. Par exemple, au niveau de Cattenom on obtient bien ce qu'on avait rentré en terme de rejets liquides :

![Capture d'écran 2025-01-16 152024](https://github.com/user-attachments/assets/c4431552-cc48-44a1-a72f-daec7780bd1b)

## 3. Calibration de la pente et du coefficient de Strickler

Enfin, il nous faut calibrer **la pente de notre réseau et le coefficient de Strickler** qui sont deux paramètres dont la valeur est peu précise.
Pour y parvenir, nous prenons les hauteurs d'eau obtenues à la sortie de CASTEAURX au niveau de la station de mesure ; nous les comparons aux hauteurs d'eau mesurées par la station de mesure (obtenues sur HydroPortail).

On règle ainsi la pente et le coefficient de Strickler pour avoir la meilleure concordance des valeurs de hauteurs d'eau. Voici la meilleure concordance que j'ai obtenue :

![image](https://github.com/user-attachments/assets/9428ac7d-8a76-4fda-b1f4-8c6649d2d4b3)

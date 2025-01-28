# II.2.b. Apports et classes sédimentaires

## 1. Classes de particules

Dans le modèle, désormais, les particules sont départagées selon leur taille. 
Il est alors introduit les classes de particules, une classe étant réservée à une certaine taille (c'est-à-dire diamètre) pour les particules. Chaque classe à ainsi ses propres paramètres.
Ces classes interviennent dans les apports, comme nous le verrons en 2.

M. Patrick Boyer m'a communiqué toutes les classes de particules à rentrer sous CASTEAURX. En voici une partie : 

![Capture d'écran 2025-01-16 145605](https://github.com/user-attachments/assets/02d4f179-f087-430a-8cb0-36b223d93711)

## 2. Apport hydraulique

Cet apport traduira la part des retombées de Tchernobyl et des essais nucléaires dans le modèle.

**Mesures de la station :**

Tout d'abord, on doit introduire les apports du fleuve lui même au niveau de l'entrée de notre réseau.
Or, j'avais placé en entrée du réseau une station de mesure qui fournit directement les débits du fleuve des années 60 à aujourd'hui.
Ainsi, je prélève ces données pour les entrées sous CASTEAIURX en précisant que cet apport se fait au niveau de l'entrée du réseau, là ooù se situe la station.

![Capture d'écran 2025-01-16 145703](https://github.com/user-attachments/assets/9f1bd8a2-bf2e-49a5-9555-a62e1b357e11)

**Classe de particule :**

On donne ensuite à cet apport une certaine classe de particule, dans notre cas, parmis celle disponible c'est celle à 3,4 μm qui est choisie.

**Concentration de sol :**

Enfin, à cet apport il faut ajouter la concentration de sol que l'on obtient par le code développé au cours de la première année (cf. I. Première année). 
Une fois les concentrations de sol obtenues pour chaque jour de l'apport, on le rajoute à cet apport.
Cette concentration traduira l'apport en Cs137 qu'aura ce débit d'eau sachant que l'on a une classe de particule à 3,4 μm.
Je n'ai pas encore réussi à introduire ces concentration de sol à cause de certains bugs de CASTEAURX. 


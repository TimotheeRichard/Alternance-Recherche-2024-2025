# III.1 Conclusion sur les résultats de la première année

## 1. Retour sur la détermination de Csol

Comme nous l'avons vu en I.1., le premier objectif était de produire un programme capable de suivre le modèle semi-empirique en un temps minimal, malgré sa grande quantité de données. Cet objectif a été rempli, on est passé d'un code sur excel qui prenait plusieurs minutes à tourner, à un code python permettant d'obtenir les résultats en une trentaine secondes. La version améliorée de Mme Valérie Nicoulaud Gouin qui reprenait quelques modifications du modèle semi-empirique a encore amélioré le temps d'exécution, le code tourne en une vingtaine de secondes.

Ce temps d'exécution étant satisfaisant, on s'en est suffi pour la suite pour le calcul de Csol pour les différents fleuves étudiés.

J'ai beaucoup été aidé dans cette partie, par Mme Valérie Nicoulaud Gouin, même si je restais assez indépendant dans l'élaboration du code. J'ai pu apprendre énormément sur python et ses bibliothèques, mais aussi sur la minimisation du temps d'exécution. Le code amélioré qui n'était pas de moi m'a bien fait comprendre aussi qu'il me restait beaucoup à apprendre sur python, notamment sur la gestion des classes.

## 2. Retour sur la calibration de Tmig et pero

Comme nous l'avons vu en I.2., l'objectif était de calibrer Tmig et pero, deux paramètres du modèle, par inférences bayésiennes. Nous avons bien réussi à calibrer ces paramètres, à l'aide de la méthode numérique de Monte-Carlo par chaînes de Markov (MCMC).

Ici, j'ai dû faire une énorme partie de bibliographie pour comprendre les inférences bayésiennes et les maîtriser, pareil pour les chaînes de Markov. Il m'a aussi fallu apprendre à utiliser RStudio qui a été utilisé pour faire tourner MCMC.

Dans cette partie, je n'ai quasiment pas créé de script, je n'ai fait que d'apporter des modifications aux scripts de Mme Valérie Nicoulaud Gouin qui m'a aidé énormément. Je devais comprendre ses codes puis les manier pour obtenir les différentes calibrations du modèle. Ce qui s'est révélé concluant : nous avons obtenu une calibration de Tmig et de pero pour chaque fleuve.

## Ouverture vers la suite

La première année se terminant et les paramètres calibrés, nous avions aussi fait les différentes contributions des phénomènes dans le modèle. Cependant, il semblait que les rejets liquides des centrales soient négligeables devant les essais nucléaires et Tchernobyl.

Cela pourrait venir du fait que les carottes sédimentaires soient prélevées en zones inondables sur les berges, et donc ne sont approvisionnées que lors des inondations. Ainsi, elles ne représentent pas toute la plage temporelle, mais une moyenne qui pourrait apporter des erreurs. Donc, ces carottes pourraient ne pas être représentatives de tout l'apport des rejets liquides des centrales nucléaires.

De ce fait, ce que j'ai fait en deuxième année combiné à ce que fera la personne prenant la suite de mon alternance pourra résoudre ce problème en reconstruisant une carotte sédimentaire qui sera alimentée tout le temps, non pas seulement par périodes de crues.

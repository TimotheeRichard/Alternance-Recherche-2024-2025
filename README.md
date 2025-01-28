# Alternance-Recherche-2024-2025
Rapport de l'alternance recherche de Timothée Richard au laboratoire IRPHE. L'alternance a eu lieu de décembre 2023 à janvier 2025.

## Chercheurs et laboratoires

**IRPHE :**

- Fabien Anselmet

**IRSN :**

- Patrick Boyer
- Valérie Nicoulaud Gouin

**M2P2 :**

- Mitra Fouladirad

## Remerciements

Un immense merci à toute l'équipe de chercheurs qui a encadré mon alternance. 

Tout particulièrement merci à Mme. Valérie Nicoulaud Gouin qui m'a accompagné pas à pas et aidé énormément dans toute ma première année d'alternance dans le domaine informatique ; je ne serais arrivé à rien sans elle.

De plus merci à Mme. Mitra Fouladirad qui m'a accordé son temps pour suivre l'évolution de mon alternance, mais surtout pour m'apprendre des concepts mathématiques qui fondent toute mon alternance.

Je remercie aussi M. Fabien Anselmet qui m'a accueilli au laboratoire IRPHE, tout en suivant l'évolution de mon alternance et en me faisant découvrir le monde de la recherche : la vie de laboratoire, la richesse des sujets qui y regorgent, etc.

Enfin, un grand merci à M. Patrick Boyer sans qui le sujet n'existerait pas, qui a fourni tout ce sur quoi j'ai travaillé et qui m'a particulièrement accompagné la deuxième année.

Finalement, je souhaite aussi remercier l'IRPHE, l'IRSN et Centrale Méditerranée m'avoir offert cette alternance.

## Contexte

### Résumé

Pour des raisons sanitaires, économiques et sociales, il est essentiel de modéliser les transferts de contaminants dans l’environnement. Cela permet d’évaluer l’évolution de leurs concentrations et de faciliter la prise de décisions visant à limiter leur impact. Dans ce contexte, les bassins versants jouent un rôle crucial. Ils accumulent des polluants provenant de diverses sources industrielles, urbaines et agricoles, et leur lessivage régit la contamination à long terme des cours d’eau. Cela dépend de plusieurs paramètres tels que l’érosivité, les connectivités hydrologiques, les pentes, la distribution des dépôts, et le couvert végétal.

Pour évaluer les flux aux exutoires des bassins versants, il existe différents types de modèles. Ceux-ci vont des modèles mécanistes et distribués, qui sont complexes à mettre en œuvre, aux fonctions de transfert, qui sont empiriques et difficilement généralisables. Dans ce contexte et pour des raisons opérationnelles, l’Institut de Radioprotection et de Sûreté Nucléaire (IRSN) propose une approche intermédiaire. Celle-ci repose sur un ensemble limité mais robuste de paramètres physiques.

### Source de pollution

La pollution par les nucléotides des bassins versants vient de trois grandes sources. 

Tout d'abord, à partir des années 50, des essais nucléaires ont eu lieu sur le globe, les retombées de ces essais ont atteint l'entièreté de la Terre. La catastrophe de Tchernobyl en 1986 a aussi engendré d'énormes retombées de nucléotides en Europe. Les retombées des essais nucléaires et de Tchernobyl tombaient soit directement dans les bassins versants, soit étaient lessivés jusqu'aux bassins versants. Enfin, les centrales nucléaires ont commencé à partir des années 1990 à rejeter des déchets nucléaires dans les cours d'eau. 

Ces trois phénomènes ont ainsi alimenté les bassins versants en nucléotides, dont le Césium 137 qui à cause de sa demi-vie de 30 ans est particulièrement problématique et sera le sujet de notre étude.

### Méthode 

Différents fleuves français seront étudiés pour trouver l'évolution de la concentration en Césium des années 50 à aujourd'hui : le Rhin, la Moselle, la Meuse et la Loire. 
Les données d'entrée du modèle sont les carottes sédimentaires et les données de rejets des centrales. Les carottes sédimentaires fournissent une évolution temporelle des années 50 à aujourd'hui de l'effet des retombées atmosphériques et du lessivage.

Un modèle a donc été développé, utilisant les différentes données d'entrées et de la mécanique des fluides pour fournir un profil de concentration en Césium 137 des années 50 à aujourd'hui. Cependant, les carottes sédimentaires fournissent des données pour chaque jour sur 70 ans, ce qui représente une très grande quantité de données à traiter. Ainsi, une première problématique est de trouver un code pouvant traiter cette quantité de données en un temps le plus court possible.

## Sommaire

### I. Première année (décembre 2023 à juillet 2024)
- [I.1. Détermination de Csol](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/I.1.-Détermination-de-Csol)
- [I.2. Calibration de Tmig et pero](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/I.2.-Calibration-de-Tmig-et-pero)
  - [I.2.a. Simulation pour la calibration](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/I.2.a.-Simultation-pour-la-calibration)
  - [I.2.b. Analyse de la convergence des chaînes de Markov](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/I.2.b.-Analyse-de-la-convergence-des-chaînes-de-Markov)
  - [I.2.c. Distribution a posteriori des paramètres](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/I.2.c.-Distribution-a-posteriori-des-paramètres)
  - [I.2.d. Comparaison prédictions/mesures](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/I.2.d.-Comparaison-prédictions/mesures)
  - [I.2.e. Indicateurs de performance du modèle](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/I.2.e.-Indicateurs-de-performance-du-modèle)
  - [I.2.f. Contributions](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/I.2.f.-Contributions)

### II. Deuxième année (septembre 2024 à janvier 2025)
- [II.1. Github pour l'IRSN](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/II.1.-Github-pour-l'IRSN)
- [II.2. CASTEAURX](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/II.2.-CASTEAURX)
  - [II.2.a. Réseau hydraulique](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/II.2.a.-Réseau-hydraulique)
  - [II.2.b. Apports et classes sédimentaires](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/II.2.b.-Apports-et-classes-sédimentaires)
  - [II.2.c. Résultats obtenus](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/II.2.c.-Résultats-obtenus)
- [II.3. Transmission de l'alternance à Camille Renaux](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/II.3.-Transmission-de-l'alternance-à-Camille-Renaux)

### III. Synthèse finale
- [III.1. Conclusion sur les résultats de la première année](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/III.1.-Conclusion-sur-les-résultats-de-la-première-année)
- [III.1. Conclusion sur les résultats de la deuxième année](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/III.1.-Conclusion-sur-les-résultats-de-la-deuxième-année)
- [III.1. Retour personnel sur l'alternance](https://github.com/TimotheeRichard/Alternance-Recherche-2024-2025/tree/III.1.-Retour-personnel-sur-l'alternance)

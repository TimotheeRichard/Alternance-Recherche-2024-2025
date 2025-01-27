# Contexte

On vient d'établir un code python qui rapidement fait tourner le modèle pour avoir les concentration en césium 137. Désormais, on cherche à calibrer deux paramètres du modèle dont on ne connaît que partiellement les valeurs.

# Objectif

Calibrer le temps de migration dans le sol des particules (Tmig) et le pourcentage d'érosion des sols (pero) à l'aide d'une méthode statistique : les inférences bayésiennes. On utilisere la méthode numérique Monte-Carlo par chaîne de Markov qui utilise ces inférences bayésiennes combinées aux chaînes de Markov.

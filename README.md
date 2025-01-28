# I.2.e. Indicateurs de performance du modèle

## 1. Code calculant les indicateurs de performance

**Il ne suffit pas de comparer graphiquement le modèle moyen avec les mesures pour voir si le modèle est performant ou non. Pour cela, il faut des indicateurs de performance. Les différents indicateurs sont détaillés dans les pages qui suivent.**

**Le script python ci-dessous permet de calculer ces différents indicateurs grâce aux tableaux de valeurs du modèle et des mesures.**

```python
## calcul du Nash-stucliffe
NSE   = lambda y_true, y_pred: 1 - (np.sum((y_true - y_pred) ** 2) / np.sum((y_true - np.mean(y_true)) ** 2))
## calcul du coefficient de détermination
rho2 = lambda y_true, y_pred: (np.sum((y_true-np.nanmean(y_true))*(y_pred-np.nanmean(y_pred))) ** 2)/np.sum((y_true-np.nanmean(y_true)) **2)/np.sum((y_pred-np.nanmean(y_pred)) **2)
## calcul du root mean square error
rmse = lambda y_true, y_pred: np.nanmean(np.sqrt(((np.array(y_true) - np.array(y_pred)) ** 2)))
## calcul du Kling-Gupta efficiency
kge = lambda y_true, y_pred: 1-np.sqrt((np.sqrt(rho2(y_true,y_pred))-1) **2 + (np.nanmean(y_pred)/np.nanmean(y_true) -1) **2 + (np.nanstd(y_pred)/np.nanstd(y_true) -1) **2)
## calcul du Root Relative Mean Square Error
def rrmse(true, pred):
    n = len(true) # update
    num = np.sum(np.square(true - pred)) / n  # update
    den = np.sum(np.square(pred))
    squared_error = num/den
    rrmse_loss = np.sqrt(squared_error)
    return rrmse_loss
## calcul Coefficient de Corrélation de Concordance
def ccc(x, y):
    mean_x = np.mean(x)
    mean_y = np.mean(y)
    var_x = np.var(x)
    var_y = np.var(y)
    covariance = np.cov(x, y)[0, 1]
    
    ccc_valeur = (2 * covariance) / (var_x + var_y + (mean_x - mean_y) ** 2)
    return ccc_valeur
```

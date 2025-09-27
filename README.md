## Projet météo (SQLite)

Lancez ce projet directement dans Google Colab en un clic :

[![Ouvrir dans Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alminza/meteo/blob/main/notebooks/Run_in_Colab.ipynb)

### Description
Deux scripts Python :
- `injection_dans_bdd.py` : insère des données (Date, Time) depuis un fichier texte dans `SQLite`.
- `meteo_methodo.py` : lit la table `info_meteolite` via SQLAlchemy et affiche les enregistrements triés par `Date`.

### Prérequis (local)
```bash
pip install -r requirements.txt
```

### Exécution (local)
```bash
python injection_dans_bdd.py --file data/meteo_stat.txt --db BDDlite.db
python meteo_methodo.py
```

### Fichier d'exemple
Un exemple de données est fourni dans `data/meteo_stat.txt` (les 3 premières lignes sont des en-têtes ignorés).

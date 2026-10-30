# MesPlaylists

Gérer ses playlists de musique et comprendre ses habitudes d'écoute :
titres, artistes, favoris, nombre d'écoutes, et un tableau de bord qui
ne se contente pas d'afficher des graphiques — il explique ce que les
chiffres montrent.

## Fonctionnalités

- **Playlists** : création, consultation, suppression (avec leurs titres).
- **Titres** : titre, artiste, genre, durée, année, favori, compteur d'écoutes.
- **Bouton « Écouté »** : chaque écoute alimente les statistiques.
- **Tableau de bord** : indicateurs clés (KPI), écoutes par genre et par
  playlist en graphiques SVG, top des titres les plus écoutés, et une
  interprétation rédigée en français (« l'artiste le plus écouté est… »,
  « le genre dominant est… »).
- **Qualité des données** : nettoyage des titres et artistes (espaces
  superflus), validation (durée positive, année plausible), détection
  des doublons (même titre, même artiste, casse indifférente).
- **Import CSV** : import de titres avec un rapport qualité — lignes
  ajoutées, lignes rejetées avec leur raison (durée invalide, doublon…).

## Stack

Python, Flask, SQLAlchemy, SQLite, HTML/CSS, Docker, GitHub Actions.

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

```bash
python seed.py   # remplit la base avec des exemples (facultatif)
python run.py    # puis ouvrir http://localhost:5000
```

- Accueil : liste des playlists et indicateurs globaux.
- Page d'une playlist : ajouter un titre, compter une écoute, mettre en favori.
- `/stats` : tableau de bord des écoutes.
- `/import` : importer un fichier CSV (voir `exemples/titres.csv`).

Exemple de CSV accepté :

```csv
titre,artiste,genre,duree_secondes,annee
Blinding Lights,The Weeknd,Pop,200,2020
Bohemian Rhapsody,Queen,Rock,354,1975
```

## Structure du projet

```
MesPlaylists/
├── app/
│   ├── __init__.py      # fabrique de l'application Flask
│   ├── models.py        # playlists et titres
│   ├── routes.py        # pages et actions
│   ├── stats.py         # nettoyage, KPI, graphiques, interprétation
│   ├── templates/       # pages HTML
│   └── static/          # feuille de style
├── tests/               # tests pytest
├── exemples/
│   └── titres.csv       # exemple d'import
├── run.py               # point d'entrée
└── seed.py              # données d'exemple
```

## Tests

```bash
python -m pytest -q
```

## Licence

MIT.

# Dashboard — Défi 1 Environnement (Togo AI Lab)

Application Streamlit de diagnostic de l'accès à l'eau potable au Togo.
Le dossier est autonome pour la soumission : il contient l'application, ses
dépendances et les données préparées nécessaires à son fonctionnement.

## Lancer l'application

Depuis la racine du projet :

```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

Ou depuis ce dossier :

```bash
pip install -r requirements.txt
streamlit run app.py
```

Pour régénérer les indicateurs depuis le dossier autonome :

```bash
python analysis/analyze.py
```

## Contenu

La structure de l'archive `dashboard.zip` est volontairement proche de celle
du dépôt Togo AI Lab de référence :

```text
dashboard/
├── app.py                    # application Streamlit principale
├── analysis/
│   └── analyze.py            # pipeline de préparation des données
├── assets/                   # indicateurs, GeoJSON, favicon et référentiels
├── data/                     # données sources incluses dans l'archive
├── docs/                     # liens officiels des données
├── .streamlit/config.toml    # configuration Streamlit
├── requirements.txt          # dépendances de l'application
└── README.md                 # documentation de lancement
```

- `app.py` : interface Streamlit, filtres, indicateurs, graphiques, cartes Folium et exports CSV.
- `analysis/analyze.py` : code du pipeline d'analyse inclus dans le dossier soumis, pour rendre la chaîne de production des indicateurs visible.
- `assets/data.json` : indicateurs calculés par le pipeline d'analyse.
- `assets/points.geojson` : ouvrages géolocalisés TdE/COSO.
- `assets/cantons.geojson` : cantons avec classe FRI et population.
- `assets/regions.csv` : référentiel régional utilisé par l'application.
- `assets/opendata-favicon.png` : favicon local de la plateforme Open Data Togo.
- `.streamlit/config.toml` : réglages visuels et de serveur pour l'application.

Les fichiers `assets/data.json` et GeoJSON sont régénérés par
`src/analysis/analyze.py` à partir des données de `data/`. Une copie exécutable
du pipeline est également fournie dans `dashboard/analysis/analyze.py` pour la
soumission du code.

## Limites d'interprétation

Les sources ouvertes ne publient pas les champs « fonctionnel », « en panne »
et « abandonné ». Le taux de fonctionnalité réel n'est donc pas calculé.
Le score COSO est un outil indicatif de ciblage des visites terrain, et non une
prédiction de panne. Un relevé futur devra ajouter l'état, la date du contrôle
et la cause de panne.

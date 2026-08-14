# Défi 1 Environnement — Accès à l'eau potable au Togo

Projet analytique Togo AI Lab construit à partir des données ouvertes TdE,
COSO, INSEED et ISRI-TG. Le dépôt contient le code source de l'analyse, le
dashboard Streamlit, les scripts de vérification et le rapport PowerPoint.

## Organisation fonctionnelle

```text
data/                 Données sources téléchargées et audit de couverture
dashboard/            Application Streamlit, pipeline inclus et données préparées
src/analysis/         Pipeline pandas/geopandas et génération des indicateurs
src/reporting/        Générateur du rapport PowerPoint
scripts/verification/ Vérifications Playwright du dashboard
scripts/package/      Scripts de création des archives de soumission
reports/assets/       Graphiques, logo et carte utilisés dans le rapport
docs/                 Liens officiels des données et documentation complémentaire
```

Le fichier principal de l'application reste volontairement dans un seul
`dashboard/app.py` : l'interface fait environ 620 lignes et les fonctions
Streamlit sont directement lisibles. Le traitement lourd et la génération du
rapport sont séparés dans `src/`.

## Installation

Pour utiliser uniquement la plateforme :

```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

Pour reproduire toute la chaîne d'analyse et du rapport :

```bash
pip install -r requirements-project.txt
python3 src/analysis/analyze.py
python3 src/reporting/build_pptx.py
```

Le pipeline lit `data/` et produit `dashboard/assets/data.json`,
`dashboard/assets/points.geojson` et `dashboard/assets/cantons.geojson`.
Une copie du pipeline est incluse dans `dashboard/analysis/analyze.py` afin que
le dossier de la plateforme contienne également le code d'analyse soumis.

## Vérifications

Le dashboard Streamlit peut être vérifié avec :

```bash
streamlit run dashboard/app.py --server.port 8502
python3 scripts/verification/_verify_streamlit.py
python3 scripts/verification/_verify_streamlit2.py
```

Le rapport peut être contrôlé avec :

```bash
mkdir -p /tmp/rapport_preview
libreoffice --headless --convert-to pdf --outdir /tmp/rapport_preview rapport.pptx
pdftoppm -png -r 120 /tmp/rapport_preview/rapport.pdf /tmp/rapport_preview/slide
```

## Archives de soumission

Créer l'archive autonome du dashboard :

```bash
bash scripts/package/make_dashboard_zip.sh
```

Créer l'archive contenant le code, les données nécessaires et la
documentation :

```bash
bash scripts/package/make_code_zip.sh
```

Les livrables générés sont `dashboard.zip`, `code_source.zip` et
`rapport.pptx`. `dashboard.zip` contient l'application, le pipeline d'analyse,
les données sources et les liens officiels nécessaires à la reproduction.

## Limite méthodologique importante

Les données TdE et COSO ne publient pas les états « fonctionnel », « en panne »
et « abandonné ». Le projet ne calcule donc pas de taux de fonctionnalité réel.
Le score COSO sert uniquement à cibler les premières visites terrain ; il devra
être remplacé par des observations répétées pour produire un taux régional fiable.

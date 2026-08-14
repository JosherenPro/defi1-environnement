# AGENTS.md — Défi 1 Environnement (Togo AI Lab)

Dashboard analytique de l'accès à l'eau potable au Togo, construit à partir
des données ouvertes TdE, COSO, INSEED et ISRI-TG.

## Livrables

- `dashboard.zip` — application Streamlit autonome avec pipeline et données sources.
- `code_source.zip` — code, pipeline, données nécessaires et documentation.
- `rapport.pptx` — rapport en français de 9 pages.

## Structure du projet

```text
data/                 Données sources et audit de récupération
dashboard/            Application Streamlit + copie du pipeline d'analyse
src/analysis/         Pipeline pandas/geopandas
src/reporting/        Générateur du rapport PPTX
scripts/verification/ Tests Playwright du dashboard
scripts/package/      Création des archives de livraison
reports/assets/       Images et logo du rapport
docs/                 Liens officiels des données
```

## Lancer la plateforme

```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

## Reproduire l'analyse et le rapport

```bash
pip install -r requirements-project.txt
python3 src/analysis/analyze.py
python3 src/reporting/build_pptx.py
```

Le pipeline lit `data/` et produit les fichiers nécessaires dans
`dashboard/assets/` : `data.json`, `points.geojson` et `cantons.geojson`.

## Créer les archives de soumission

```bash
bash scripts/package/make_dashboard_zip.sh
bash scripts/package/make_code_zip.sh
```

## Contrôles avant livraison

```bash
streamlit run dashboard/app.py --server.port 8502
python3 scripts/verification/_verify_streamlit.py
python3 scripts/verification/_verify_streamlit2.py
mkdir -p /tmp/rapport_preview
libreoffice --headless --convert-to pdf --outdir /tmp/rapport_preview rapport.pptx
pdftoppm -png -r 120 /tmp/rapport_preview/rapport.pdf /tmp/rapport_preview/slide
```

## Décisions méthodologiques

- L'inventaire est hétérogène : TdE est concentré sur Maritime et COSO sur le
  Nord du pays.
- Les coordonnées nulles `(0,0)` sont exclues des cartes.
- Les données ouvertes ne publient pas les états « fonctionnel », « en panne »
  et « abandonné » : aucun taux de fonctionnalité réel n'est calculé.
- Le score COSO est un outil indicatif de ciblage des visites, pas une
  prédiction de panne.
- Les recommandations prévoient un relevé terrain trimestriel avec état,
  date et cause de panne pour obtenir ultérieurement un taux régional fiable.

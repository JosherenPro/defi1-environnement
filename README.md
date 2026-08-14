# Défi 1 Environnement — Accès à l'eau potable au Togo

Projet analytique Togo AI Lab construit à partir des données ouvertes TdE,
COSO, INSEED et ISRI-TG. Le dépôt contient uniquement les éléments nécessaires
à l'exécution et à l'analyse du dashboard.

## Structure du dépôt

```text
app.py                Lanceur Streamlit Cloud
requirements.txt      Dépendances uniques du projet
dashboard/app.py      Application Streamlit
dashboard/assets/     Données préparées et favicon
dashboard/analyze.py  Copie du pipeline pour la plateforme
src/analyze.py        Pipeline principal d'analyse
data/                 Données sources et audit de récupération
reports/rapport.pptx  Rapport final
reports/rapport.pdf   Version PDF du rapport
```

Les scripts de vérification et les ressources intermédiaires du rapport restent
localement disponibles, mais ne sont pas suivis dans le dépôt.

## Installation

Pour utiliser uniquement la plateforme :

```bash
pip install -r requirements.txt
streamlit run app.py
```

Les indicateurs et les GeoJSON sont déjà préparés dans `dashboard/assets/`.

Pour régénérer les indicateurs :

```bash
python3 src/analyze.py
```

Le pipeline est également copié dans `dashboard/analyze.py` pour accompagner
la plateforme.

## Limite méthodologique importante

Les données TdE et COSO ne publient pas les états « fonctionnel », « en panne »
et « abandonné ». Le projet ne calcule donc pas de taux de fonctionnalité réel.
Le score COSO sert uniquement à cibler les premières visites terrain ; il devra
être remplacé par des observations répétées pour produire un taux régional fiable.

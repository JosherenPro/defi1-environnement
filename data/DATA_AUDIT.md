# Audit de récupération et de couverture des données

Vérification effectuée le 13 août 2026 à partir des fiches Open Data Togo listées dans
[`../docs/liens_data.md`](../docs/liens_data.md) et de la page du défi :
<https://datalab.gouv.tg/data-challenges/defis/environnement-defi-1>.

## Résultat

Les fichiers téléchargés temporairement depuis les ressources officielles correspondent
aux fichiers locaux suivants lorsque la comparaison a été possible :

| Thème | Ressource locale | Utilisée dans le pipeline | Contrôle |
|---|---|---:|---|
| Ouvrages TdE | `chateaux_forages.csv` | Oui | SHA-256 identique à la ressource officielle |
| Métadonnées TdE | `chateaux_forages_meta.csv` | Non, documentation | Fichier présent; utile pour le dictionnaire de données |
| Projet COSO | `coso.csv` + `coso.geojson` | CSV oui; GeoJSON non | 218 lignes dans les deux formats; GeoJSON est une représentation redondante |
| Population | `pop.csv` | Oui | SHA-256 identique à la ressource officielle |
| Ventes d'eau | `ventes_eau.csv` | Oui | SHA-256 identique à la ressource officielle |
| FRI cantons | `fri_cantons.gpkg` | Oui | SHA-256 identique à la ressource officielle; jointure spatiale principale |
| FRI grille 1 km | `fri_grid_1km.gpkg` | Présente, non agrégée | SHA-256 identique; ressource de détail, non nécessaire au croisement par canton |
| FRI grille 500 m | `fri_grid_500m.gpkg` | Présente, non agrégée | Ressource de détail, non nécessaire au croisement par canton |

La fiche FRI officielle propose également un ZIP raster brut et des cartes PNG. Ces
ressources servent à produire/illustrer le FSI/FRI; elles ne sont pas nécessaires pour
recalculer le diagnostic cantonal déjà fourni dans `fri_cantons.gpkg`, et ne sont donc
pas incluses dans le ZIP dashboard afin de respecter la limite de taille.

## Couverture analytique

- 285 ouvrages sont assemblés : 67 TdE + 218 COSO.
- 150 ouvrages ont une localisation exploitable après exclusion des coordonnées nulles
  ou non joignables à un canton FRI.
- Les 388 cantons FRI sont utilisés pour la population, la classe de risque et la
  jointure ouvrages × risque.
- La population régionale 2010 est maintenant chargée directement depuis `pop.csv`;
  le pipeline vérifie la présence des cinq régions avant de produire les indicateurs.
- Les grilles FRI 1 km et 500 m sont conservées comme ressources de précision, mais le
  dashboard emploie la couche cantonale pour une lecture comparable avec la population
  et les recommandations.
- Les ventes d'eau couvrent 2018–2022 et sont utilisées dans l'onglet Consommation.
- Le champ panne/abandon n'existe pas dans les données ouvertes TdE/COSO : aucun taux de
  fonctionnalité réel ne doit être déduit des statuts de réception. Le taux de plan
  d'entretien documenté (20,6 % sur COSO) est présenté comme proxy de durabilité.
- Un score indicatif de priorité de contrôle est calculé pour les 218 projets COSO à
  partir de l'entretien, du statut, de la remise à la communauté et du FRI disponible.
  Il sert à cibler les visites et ne constitue pas une prédiction de panne; les 67
  ouvrages TdE restent non évaluables par ce score faute de variables d'état.

## Contrôles de cohérence ajoutés

- Le seuil FRI « Élevé » est harmonisé à `FRI > 0,13`, le même seuil que la classification
  du pipeline. Le croisement donne 77 ouvrages géolocalisés en classe élevée.
- Le dashboard propose un mode cartographique « Croisement FRI + ouvrages ».
- Les priorités régionales combinent pression démographique, déficit relatif d'ouvrages
  et part de population en FRI élevé; les cantons prioritaires sont listés séparément.

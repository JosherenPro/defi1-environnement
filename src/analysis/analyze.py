#!/usr/bin/env python3
"""Prépare les indicateurs et les GeoJSON du dashboard du Défi 1."""
import os, json
import numpy as np
import pandas as pd
import geopandas as gpd

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(BASE, "data")
OUT  = os.path.join(BASE, "dashboard", "assets", "data.json")

# Régions du Togo
REGIONS = ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]
FRI_HIGH_THRESHOLD = 0.13
# Normalisation des noms
CANON = {r.upper(): r for r in REGIONS}
CANON.update({r: r for r in REGIONS})

# ----------------------------------------------------------------------------
def load_points():
    """Charge et unifie les points d'eau TdE + COSO en CRS 32631 (UTM 31N)."""
    # TdE
    td = pd.read_csv(os.path.join(DATA, "chateaux_forages.csv"))
    lon = td["geometry"].str.extract(r"POINT \(([-\d.]+) ")[0].astype(float)
    lat = td["geometry"].str.extract(r"POINT \([-\d.]+ ([-\d.]+)")[0].astype(float)
    tdg = gpd.GeoDataFrame(
        td.assign(region=td["region_nom_bdd"].map(CANON).fillna(td["region_nom_bdd"])),
        geometry=gpd.points_from_xy(lon, lat), crs=4326,
    ).to_crs(32631)
    tdg["src"] = "TdE"
    tdg["type"] = td["forage_chateau_nom"]
    tdg["name"] = td["forage_chateau_nom"]
    tdg["valid_coord"] = True
    tdg["project_status"] = pd.NA
    tdg["maintenance_plan"] = pd.NA
    tdg["handover_date"] = pd.NA

    # COSO
    cs = pd.read_csv(os.path.join(DATA, "coso.csv"), low_memory=False)
    cs["region"] = cs["hierarchy"].astype(str).str.split(">").str[-1].str.strip().map(CANON)
    valid = cs["latitude"].notna() & cs["longitude"].notna() & \
            ~((cs["latitude"] == 0) & (cs["longitude"] == 0))
    csg = gpd.GeoDataFrame(
        cs.assign(valid_coord=valid),
        geometry=gpd.points_from_xy(cs["longitude"], cs["latitude"]), crs=4326,
    ).to_crs(32631)
    csg["src"] = "COSO"
    csg["type"] = cs["subproject_type_designation"]
    csg["name"] = cs["location_name"]
    csg["project_status"] = cs["current_status_of_the_site"]
    csg["maintenance_plan"] = cs["existence_of_maintenance_plan"]
    csg["handover_date"] = cs["official_handover_date_to_community"]

    point_fields = [
        "region", "src", "type", "name", "valid_coord", "project_status",
        "maintenance_plan", "handover_date", "geometry",
    ]
    pts = gpd.GeoDataFrame(
        pd.concat([
            tdg[point_fields],
            csg[point_fields],
        ], ignore_index=True), crs=32631)
    return tdg, csg, pts


def load_population_2010():
    """Charge les populations régionales depuis la ressource INSEED officielle."""
    pop = pd.read_csv(os.path.join(DATA, "pop.csv"), low_memory=False)
    required = {"indicateurs", "Date", "Value"}
    missing = required.difference(pop.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans pop.csv : {sorted(missing)}")

    pop["indicator_key"] = pop["indicateurs"].astype(str).str.strip().str.upper()
    pop["Date"] = pd.to_numeric(pop["Date"], errors="coerce")
    pop["Value"] = pd.to_numeric(pop["Value"], errors="coerce")
    region_keys = [region.upper() for region in REGIONS]
    regional = (
        pop.loc[pop["Date"].eq(2010) & pop["indicator_key"].isin(region_keys)]
        .set_index("indicator_key")["Value"]
        .reindex(region_keys)
    )
    if regional.isna().any():
        missing_regions = regional[regional.isna()].index.tolist()
        raise ValueError(
            "Populations régionales 2010 absentes de pop.csv : "
            + ", ".join(missing_regions)
        )
    return regional.round().astype(int).set_axis(REGIONS)


def add_control_score(points):
    """Calcule un score transparent de priorité de contrôle, pas un état réel."""
    points = points.copy()
    is_coso = points["src"].eq("COSO")
    status = points["project_status"].astype("string").str.strip()
    maintenance = points["maintenance_plan"].astype("boolean")
    handover_missing = points["handover_date"].isna()
    fri = pd.to_numeric(points["FRI_canton"], errors="coerce")

    # Pondération renormalisée si le FRI manque.
    components = pd.DataFrame(index=points.index)
    components["maintenance"] = (~maintenance).astype("float64")
    components["status"] = (~status.isin(["Réception définitive", "Achevé"])).astype("float64")
    components["handover"] = handover_missing.astype("float64")
    components["fri"] = pd.Series(
        np.select([fri > FRI_HIGH_THRESHOLD, fri > 0.07], [1.0, 0.5], default=0.0),
        index=points.index,
        dtype="float64",
    )
    components.loc[fri.isna(), "fri"] = np.nan
    weights = pd.Series({"maintenance": 0.45, "status": 0.25, "handover": 0.15, "fri": 0.15})
    available_weight = components.notna().mul(weights, axis=1).sum(axis=1)
    score = components.mul(weights, axis=1).sum(axis=1).div(available_weight).mul(100)
    score = score.where(is_coso).round(1)

    points["control_score"] = score
    points["control_class"] = "Non évaluable (TdE)"
    points.loc[is_coso & score.isna(), "control_class"] = "Données insuffisantes"
    points.loc[is_coso & score.ge(60), "control_class"] = "Priorité de contrôle"
    points.loc[is_coso & score.ge(35) & score.lt(60), "control_class"] = "À vérifier"
    points.loc[is_coso & score.lt(35), "control_class"] = "Risque indicatif faible"
    return points


def analyze():
    fc = gpd.read_file(os.path.join(DATA, "fri_cantons.gpkg"))
    fc["region"] = fc["region_nom"].map(CANON)
    # Populations FRI et RGPH
    pop_model = fc.groupby("region")["total_pop"].sum().round(0).astype(int)

    tdg, csg, pts = load_points()

    # Jointure points / cantons FRI
    fcj = gpd.sjoin(pts, fc[["canton_id", "canton_nom", "region", "FRI", "total_pop", "geometry"]],
                    how="left", predicate="within")
    pts = pts.reset_index(drop=True)
    pts["canton"] = fcj["canton_nom"].values
    pts["FRI_canton"] = fcj["FRI"].values
    pts = add_control_score(pts)

    # Indicateurs régionaux
    pop2010 = load_population_2010()
    tab = pd.DataFrame(index=REGIONS)
    tab["pop_model"] = pop_model.reindex(REGIONS).fillna(0).astype(int)
    tab["pop_2010"] = pop2010.reindex(REGIONS)
    tab["n_tde"] = tdg.groupby("region").size().reindex(REGIONS).fillna(0).astype(int)
    tab["n_coso"] = csg.groupby("region").size().reindex(REGIONS).fillna(0).astype(int)
    tab["n_points"] = pts.groupby("region").size().reindex(REGIONS).fillna(0).astype(int)
    # La pression repose sur la population INSEED 2010.
    tab["points_per_100k"] = (tab["n_points"] / tab["pop_2010"] * 1e5).round(2)

    # maintenance COSO (taux de plans d'entretien existants)
    maint = csg.groupby("region")["existence_of_maintenance_plan"].mean().reindex(REGIONS)
    tab["maint_rate_coso"] = (maint * 100).round(1).fillna(0)

    # Exposition FRI
    tab["fri_mean_canton"] = fc.groupby("region")["FRI"].mean().reindex(REGIONS).round(3)
    pts_hi = pts[(pts["FRI_canton"] > FRI_HIGH_THRESHOLD) & (pts["FRI_canton"].notna())]
    tab["pts_high_FRI"] = pts_hi.groupby("region").size().reindex(REGIONS).fillna(0).astype(int)
    high_cantons = fc[fc["FRI"] > FRI_HIGH_THRESHOLD]
    high_pop = high_cantons.groupby("region")["total_pop"].sum().reindex(REGIONS).fillna(0)
    tab["fri_high_cantons"] = fc.groupby("region")["FRI"].apply(lambda s: int((s > FRI_HIGH_THRESHOLD).sum())).reindex(REGIONS).fillna(0).astype(int)
    tab["fri_high_population"] = high_pop.round(0).astype(int)
    tab["fri_high_population_pct"] = (high_pop / tab["pop_model"] * 100).round(1).fillna(0)
    tab["population_per_point"] = (tab["pop_2010"] / tab["n_points"].replace(0, np.nan)).round(0)
    tab["maintenance_missing_coso"] = (tab["n_coso"] * (100 - tab["maint_rate_coso"]) / 100).round(0).astype(int)

    # Score indicatif de besoin de nouveaux ouvrages.
    density_max = max(float(tab["points_per_100k"].max()), 1.0)
    tab["pressure_score"] = (tab["pop_2010"] / tab["pop_2010"].max() * 100).round(1)
    tab["equipment_deficit_score"] = ((1 - tab["points_per_100k"] / density_max) * 100).clip(0, 100).round(1)
    tab["new_forages_score"] = (0.40 * tab["pressure_score"] +
                                0.35 * tab["equipment_deficit_score"] +
                                0.25 * tab["fri_high_population_pct"]).round(1)

    tab = tab.sort_values("pop_model", ascending=False)

    # Classification FRI
    fc["fri_class"] = pd.cut(fc["FRI"], [-0.01, 0.07, FRI_HIGH_THRESHOLD, 1.0],
                             labels=["Faible", "Moyen", "Élevé"])
    cnt = pts.groupby("canton").size().rename("n_pts")
    fc2 = fc.merge(cnt, left_on="canton_nom", right_index=True, how="left")
    fc2["n_pts"] = fc2["n_pts"].fillna(0)
    # Priorité cantonale
    def minmax(series):
        span = series.max() - series.min()
        return (series - series.min()) / span if span else series * 0
    fc2["priority_score"] = (100 * (0.45 * minmax(fc2["total_pop"]) +
                                    0.35 * minmax(fc2["FRI"]) +
                                    0.20 * (fc2["n_pts"] == 0))).round(1)
    fc2["priority_class"] = pd.cut(fc2["priority_score"], [-0.1, 33, 66, 100.1],
                                    labels=["Surveiller", "Renforcer", "Priorité"])
    agg = fc2.groupby("fri_class", observed=True).agg(
        n_cantons=("canton_id", "size"), points=("n_pts", "sum"),
        pop=("total_pop", "sum")).reset_index()

    # Ventes d'eau
    w = pd.read_csv(os.path.join(DATA, "ventes_eau.csv"))
    w["indicateur"] = w["indicateur"].str.strip()
    sales_cat = (w.pivot_table(index="indicateur", columns="Date", values="Value")
                   .sort_values(2022, ascending=False))
    sales_cat = sales_cat.reset_index().rename(columns={"indicateur": "categorie"})
    total_2022 = float(w[w["Date"] == 2022]["Value"].sum())

    # COSO : statut et maintenance
    cs = csg
    status_counts = cs["current_status_of_the_site"].value_counts().to_dict()
    coso_total = int(len(cs))
    coso_with_coord = int(cs["valid_coord"].sum())
    coso_maint_overall = round(100 * float(cs["existence_of_maintenance_plan"].mean()), 1)
    coso_type = cs["subproject_type_designation"].value_counts().to_dict()
    # Bénéficiaires
    ben = pd.to_numeric(cs["estimated_number_of_beneficiaries"], errors="coerce").dropna().sum()
    ben_pop = pd.to_numeric(cs["population"], errors="coerce").dropna().sum()
    coso_pts = pts[pts["src"].eq("COSO")].copy()
    control_class_counts = coso_pts["control_class"].value_counts().to_dict()
    control_priority_count = int((coso_pts["control_class"] == "Priorité de contrôle").sum())
    monitoring_columns = [
        "name", "region", "canton", "FRI_canton", "project_status",
        "maintenance_plan", "handover_date", "valid_coord", "control_score",
        "control_class",
    ]
    monitoring_records = json.loads(
        coso_pts[monitoring_columns].to_json(orient="records", force_ascii=False)
    )

    # Exports GeoJSON
    os.makedirs(os.path.join(BASE, "dashboard", "assets"), exist_ok=True)
    pts_ll = pts[pts["FRI_canton"].notna()].to_crs(4326)
    pts_ll.to_file(os.path.join(BASE, "dashboard", "assets", "points.geojson"),
                   driver="GeoJSON")
    fc2.to_crs(4326)[["canton_nom", "region", "FRI", "fri_class", "total_pop", "n_pts", "geometry"]
                    ].to_file(os.path.join(BASE, "dashboard", "assets", "cantons.geojson"),
                              driver="GeoJSON")

    # Résumé
    summary = {
        "n_points_total": int(len(pts)),
        "n_points_geoloc_ok": int(pts["FRI_canton"].notna().sum()),
        "n_tde": int(len(tdg)),
        "n_coso": int(len(csg)),
        "coso_with_coord": coso_with_coord,
        "coso_coord_quality_pct": round(100 * coso_with_coord / coso_total, 1),
        "coso_maint_overall_pct": coso_maint_overall,
        "n_regions_covered": int((tab["n_points"] > 0).sum()),
        "total_2022_m3": round(total_2022, 0),
        "points_high_FRI": int(pts_hi.shape[0]),
        "cantons_high_FRI": int((fc["FRI"] > FRI_HIGH_THRESHOLD).sum()),
        "population_high_FRI": int(high_cantons["total_pop"].sum()),
        "functionality_rate_available": False,
        "control_score_available": True,
        "coso_control_priority_count": control_priority_count,
    }

    status_values = sorted(cs["current_status_of_the_site"].dropna().unique().tolist())
    status_by_region = {
        r: {s: int(((cs["region"] == r) & (cs["current_status_of_the_site"] == s)).sum())
            for s in status_values}
        for r in REGIONS
    }
    source_links = []
    links_path = os.path.join(BASE, "docs", "liens_data.md")
    if os.path.exists(links_path):
        with open(links_path, encoding="utf-8") as f:
            source_links = list(dict.fromkeys(line.strip() for line in f if line.strip().startswith("http")))

    data = {
        "generated": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
        "summary": summary,
        "regions": {
            "labels": tab.index.tolist(),
            "pop_model": tab["pop_model"].tolist(),
            "pop_2010": tab["pop_2010"].tolist(),
            "n_tde": tab["n_tde"].tolist(),
            "n_coso": tab["n_coso"].tolist(),
            "n_points": tab["n_points"].tolist(),
            "points_per_100k": tab["points_per_100k"].tolist(),
            "maint_rate_coso": tab["maint_rate_coso"].tolist(),
            "fri_mean_canton": tab["fri_mean_canton"].tolist(),
            "pts_high_FRI": tab["pts_high_FRI"].tolist(),
            "fri_high_cantons": tab["fri_high_cantons"].tolist(),
            "fri_high_population": tab["fri_high_population"].tolist(),
            "fri_high_population_pct": tab["fri_high_population_pct"].tolist(),
            "population_per_point": tab["population_per_point"].where(tab["population_per_point"].notna(), None).tolist(),
            "maintenance_missing_coso": tab["maintenance_missing_coso"].tolist(),
            "pressure_score": tab["pressure_score"].tolist(),
            "equipment_deficit_score": tab["equipment_deficit_score"].tolist(),
            "new_forages_score": tab["new_forages_score"].tolist(),
        },
        "fri_classes": {
            "class": agg["fri_class"].tolist(),
            "n_cantons": agg["n_cantons"].tolist(),
            "points": agg["points"].astype(int).tolist(),
            "pop": agg["pop"].astype(int).tolist(),
        },
        "water_sales": {
            "categories": sales_cat["categorie"].tolist(),
            "years": [int(c) for c in sales_cat.columns if str(c).isdigit()],
            "matrix": sales_cat[[c for c in sales_cat.columns if str(c).isdigit()]]
                       .fillna(0).round(0).astype(int).values.tolist(),
        },
        "coso": {
            "total": coso_total,
            "status": status_counts,
            "type": coso_type,
            "beneficiaries_est": int(ben),
            "population_covered": int(ben_pop),
            "maint_by_region": {r: (round(100*float(csg[csg["region"]==r]["existence_of_maintenance_plan"].mean()),1)
                                    if (csg["region"]==r).any() else 0) for r in REGIONS},
            "status_by_region": status_by_region,
            "status_values": status_values,
            "control_class_counts": control_class_counts,
            "functionality_note": "Le score de contrôle COSO est un proxy transparent de priorité d'inspection. Il ne prédit pas l'état réel et ne remplace pas un relevé terrain.",
        },
        "coso_monitoring": monitoring_records,
        "priority_cantons": {
            "canton": fc2.sort_values("priority_score", ascending=False)["canton_nom"].head(15).tolist(),
            "region": fc2.sort_values("priority_score", ascending=False)["region"].head(15).tolist(),
            "score": fc2.sort_values("priority_score", ascending=False)["priority_score"].head(15).tolist(),
            "fri": fc2.sort_values("priority_score", ascending=False)["FRI"].head(15).round(3).tolist(),
            "population": fc2.sort_values("priority_score", ascending=False)["total_pop"].head(15).round(0).astype(int).tolist(),
            "points": fc2.sort_values("priority_score", ascending=False)["n_pts"].head(15).astype(int).tolist(),
        },
        "sources": source_links,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Wrote", OUT)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return data


if __name__ == "__main__":
    analyze()

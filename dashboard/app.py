#!/usr/bin/env python3
"""Dashboard Streamlit — Accès à l'Eau Potable au Togo."""
import os, json
import numpy as np
import pandas as pd
import geopandas as gpd
import folium
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

BASE = os.path.dirname(os.path.abspath(__file__))
AST  = os.path.join(BASE, "assets")
FAVICON = os.path.join(AST, "opendata-favicon.png")

# Style
st.set_page_config(page_title="Accès à l'Eau Potable au Togo", page_icon=FAVICON,
                   layout="wide", initial_sidebar_state="collapsed")

# Style Togo AI Lab
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');
html, body, .stApp, p, label, button, input, textarea, select,
div[data-testid="stMarkdownContainer"] { font-family: 'Poppins', sans-serif !important; }
[data-testid="stIconMaterial"] { font-family: 'Material Symbols Rounded' !important; }
.stApp { background: #F3F6F5 !important; color: #16302C; }
.stApp > header { background: #F3F6F5 !important; }
.block-container { padding-top: 1.5rem !important; padding-left: 2.5rem !important; padding-right: 2.5rem !important; max-width: 100% !important; }
.main .block-container { background: #F3F6F5; }
.main [data-testid="stMarkdownContainer"] p:not(.note-limite),
.main [data-testid="stMarkdownContainer"] li,
.main [data-testid="stWidgetLabel"] p,
.main [data-testid="stWidgetLabel"] label { color:#16302C !important; }
.main [data-testid="stMarkdownContainer"] p:not(.note-limite),
.main [data-testid="stMarkdownContainer"] li { font-size:15px; line-height:1.55; }
.hero-banner p { color:rgba(255,255,255,.82) !important; }
.note-limite { color:#5D726E !important; }
.hero-banner {
    background: radial-gradient(circle at 15% 20%, rgba(244,180,0,.10), transparent 42%), linear-gradient(120deg, #0B4F4A 0%, #106B63 55%, #14877D 100%);
    padding: 2.75rem 2.5rem 4.8rem; border-radius: 0.9rem; color: white; margin: -1rem -0.2rem 1.3rem -0.2rem;
    position: relative; overflow: hidden;
}
.hero-banner::after { content:""; position:absolute; right:-50px; top:-50px; width:220px; height:220px; border-radius:50%; border:1px solid rgba(255,255,255,0.12); }
.hero-eyebrow {
    display:inline-block; font-size:11px; font-weight:600; letter-spacing:1.5px; text-transform:uppercase;
    color:#F4B400; background:rgba(244,180,0,0.12); border:1px solid rgba(244,180,0,0.35);
    padding:5px 12px; border-radius:20px; margin-bottom:12px;
}
.hero-banner h1 { margin:0; font-size:clamp(1.9rem, 3vw, 2.2rem); font-weight:700; letter-spacing:-.02em; position:relative; z-index:1; font-family:'Space Grotesk',sans-serif; }
.hero-banner p { margin:10px 0 0 0; color:rgba(255,255,255,0.82); font-size:15px; line-height:1.5; max-width:42rem; position:relative; z-index:1; }
div[data-testid="stMetric"] { background:white; border-radius:0.9rem; padding:1.25rem 1.1rem 1.1rem; box-shadow:0 10px 30px rgba(11,79,74,.14); border-bottom:3px solid #F4B400; transition:transform .2s ease, box-shadow .2s ease; }
div[data-testid="stMetric"]:hover { transform:translateY(-3px); box-shadow:0 16px 36px rgba(11,79,74,.20); }
div[data-testid="stMetricValue"] { font-family:'Space Grotesk',sans-serif !important; color:#0B4F4A; }
label[data-testid="stMetricLabel"],
label[data-testid="stMetricLabel"] *,
label[data-testid="stMetricLabel"] p { font-size:13.5px !important; color:#5D726E !important; font-weight:500 !important; line-height:1.4; opacity:1 !important; }
div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] * { color:#0B4F4A !important; opacity:1 !important; }
div[data-testid="stHorizontalBlock"] { gap:14px; }
.note-limite { font-style:italic; color:#5D726E; background:#FFF8E6; border-left:4px solid #F4B400; padding:13px 16px; border-radius:8px; margin-top:16px; font-size:14px; line-height:1.55; }
.interpretation { color:#16302C !important; background:#EAF4F2; border-left:4px solid #14877D; padding:12px 15px; border-radius:8px; margin:10px 0 16px; font-size:14px; line-height:1.55; }
.interpretation strong { color:#0B4F4A !important; }
.stTabs { width:100% !important; }
.stTabs [data-baseweb="tab-list"] { gap:6px; background:white; padding:6px; border-radius:12px; box-shadow:0 1px 3px rgba(11,79,74,0.08); width:100% !important; max-width:none; }
.stTabs [data-baseweb="tab"] { flex:1 1 0; justify-content:center; background-color:transparent; border-radius:8px; padding:11px 14px; font-weight:600; font-size:14px; color:#5D726E; transition:all .2s ease; }
.stTabs [data-baseweb="tab"]:hover { color:#0B4F4A; background:rgba(11,79,74,.06); }
.stTabs [aria-selected="true"] { background:linear-gradient(120deg, #0B4F4A, #106B63) !important; color:white !important; box-shadow:0 4px 12px rgba(11,79,74,.25); }
.stTabs [data-baseweb="tab-highlight"] { display:none; }
.stTabs [data-baseweb="tab-border"] { display:none; }
# Responsive
@media (max-width: 767px) {
  .block-container { padding: 0.75rem 0.75rem 1.5rem !important; }
  .hero-banner { padding: 1.5rem 1.25rem 3.2rem; margin-bottom: 0.75rem; }
  .hero-banner h1 { font-size: 1.55rem; line-height: 1.15; }
  .hero-banner p { font-size: 0.875rem; }
  .stTabs [data-baseweb="tab-list"] { width: 100% !important; overflow-x: auto; flex-wrap: nowrap; }
  .stTabs [data-baseweb="tab"] { flex:0 0 auto; min-height:44px; padding:0.65rem 0.8rem; white-space:nowrap; }
  div[data-testid="stMetric"] { padding: 0.75rem; }
}
@media (min-width: 768px) {
  .hero-banner h1 { font-size: clamp(1.8rem, 3vw, 2.4rem); }
}
#MainMenu { visibility:hidden; }
footer { visibility:hidden; }

/* Sidebar: branded companion panel, inspired by the reference dashboard. */
section[data-testid="stSidebar"] { background:linear-gradient(180deg, #0B4F4A 0%, #106B63 100%) !important; border-right:1px solid rgba(244,180,0,.35); }
section[data-testid="stSidebar"] > div { background:transparent !important; }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color:rgba(255,255,255,.86) !important; }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] b { color:#FFFFFF !important; }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 { color:#FFFFFF !important; font-family:'Space Grotesk',sans-serif !important; }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:rgba(255,255,255,.76) !important; line-height:1.5; }
section[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,.18) !important; }
section[data-testid="stSidebar"] [data-baseweb="select"] > div { background:#FFFFFF !important; border:0 !important; border-radius:10px !important; min-height:44px; }
section[data-testid="stSidebar"] [data-baseweb="select"] * { color:#16302C !important; }
section[data-testid="stSidebar"] a { color:#F4B400 !important; font-weight:500; }
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label { color:#FFFFFF !important; }
section[data-testid="stSidebar"] [data-testid="stExpander"] { border:1px solid rgba(255,255,255,.2); border-radius:12px; background:rgba(255,255,255,.06); }
section[data-testid="stSidebar"] [data-testid="stExpander"] summary { color:#FFFFFF !important; }
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button,
section[data-testid="stSidebar"] button { color:#FFFFFF !important; }
.sidebar-brand { padding:.5rem .25rem 1.25rem; }
.sidebar-kicker { display:inline-block; color:#F4B400; font-size:.7rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }
.sidebar-brand h2 { color:#FFFFFF; font-family:'Space Grotesk',sans-serif; font-size:1.55rem; line-height:1.05; margin:.65rem 0 .5rem; }
.sidebar-brand p { color:rgba(255,255,255,.72); font-size:.82rem; margin:0; }
.sidebar-label { color:#F4B400; font-size:.72rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; margin:.3rem 0 .35rem; }
.sidebar-source-chip { display:inline-block; background:rgba(244,180,0,.12); border:1px solid rgba(244,180,0,.45); color:#FFFFFF !important; border-radius:20px; padding:.4rem .7rem; font-size:.7rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-banner">
  <div class="hero-eyebrow">TOGO AI LAB · DEFI 1 · ENVIRONNEMENT</div>
  <h1>Accès à l'Eau Potable au Togo</h1>
  <p>Diagnostic des infrastructures hydrauliques, de l'état du parc, de la pression démographique et du risque d'inondation — à partir des données ouvertes TdE, COSO, INSEED et ISRI-TG.</p>
</div>
""", unsafe_allow_html=True)

# Palette
C_TEAL, C_GOLD, C_TURQ, C_ORG, C_PURP = "#0B4F4A", "#F4B400", "#14877D", "#D9622B", "#7A4FA0"
INK = "#16302C"
REGION_COLORS = {"Maritime": C_TEAL, "Plateaux": C_TURQ, "Centrale": C_GOLD, "Kara": C_ORG, "Savanes": C_PURP}
COLORWAY = [C_TEAL, C_GOLD, C_TURQ, C_ORG, C_PURP]

def style_figure(fig):
    fig.update_layout(
        font=dict(family="Poppins, sans-serif", color=INK, size=12),
        plot_bgcolor="white", paper_bgcolor="white",
        title_text="", title_font=dict(size=15, color=C_TEAL), colorway=COLORWAY,
        margin=dict(t=50, l=40, r=20, b=40))
    return fig

# Données
@st.cache_data
def load_data(data_version):
    data = json.load(open(os.path.join(AST, "data.json"), encoding="utf-8"))
    pts = gpd.read_file(os.path.join(AST, "points.geojson"))
    cant = gpd.read_file(os.path.join(AST, "cantons.geojson"))
    return data, pts, cant

DATA_VERSION = tuple(
    os.path.getmtime(os.path.join(AST, filename))
    for filename in ("data.json", "points.geojson", "cantons.geojson")
)
data, pts_gdf, cant_gdf = load_data(DATA_VERSION)
R, F, W, C, S = data["regions"], data["fri_classes"], data["water_sales"], data["coso"], data["summary"]

# Barre latérale
st.sidebar.markdown("""
<div class="sidebar-brand">
  <div class="sidebar-kicker">TOGO AI LAB · DÉFI 1</div>
  <h2>Diagnostic<br>de l'eau</h2>
  <p>Explorez la couverture, la maintenance, la pression démographique et le risque d'inondation.</p>
</div>
<div class="sidebar-label">Filtrer l'analyse</div>
""", unsafe_allow_html=True)
region_options = R["labels"]
selected_regions = st.sidebar.multiselect(
    "Régions", region_options, default=region_options,
    help="Sélectionnez une ou plusieurs régions. Les tableaux et la carte sont actualisés.",
)
if not selected_regions:
    st.sidebar.warning("Sélectionnez au moins une région; toutes les régions sont réaffichées.")
    selected_regions = region_options
source_options = ["TdE", "COSO"]
selected_sources = st.sidebar.multiselect(
    "Sources des ouvrages", source_options, default=source_options,
)
fri_options = ["Faible", "Moyen", "Élevé"]
selected_fri_classes = st.sidebar.multiselect(
    "Classes FRI", fri_options, default=fri_options,
    help="Le filtre FRI s'applique aux ouvrages joignables à un canton.",
)
basemap_option = st.sidebar.radio(
    "Fond cartographique", ["CartoDB Positron · en ligne", "Sans fond · hors ligne"],
    index=0, help="Le mode hors ligne conserve les cantons et ouvrages sans appeler de tuiles externes.",
)

# Filtre régional partagé entre les onglets.
ridx = [i for i, label in enumerate(R["labels"]) if label in selected_regions]
if not ridx:
    st.sidebar.warning("Sélectionnez au moins une région.")
    ridx = list(range(len(R["labels"])))
def rv(key):
    # Compatibilité avec les anciens indicateurs.
    if key in R:
        values = R[key]
    elif key == "maintenance_missing_coso":
        values = [round(n * (100 - m) / 100) for n, m in zip(R["n_coso"], R["maint_rate_coso"])]
    elif key == "population_per_point":
        population = R.get("pop_2010", R["pop_model"])
        values = [round(p / n) if n else None for p, n in zip(population, R["n_points"])]
    elif key == "pressure_score":
        population = R.get("pop_2010", R["pop_model"])
        maximum = max(population) or 1
        values = [round(p / maximum * 100, 1) for p in population]
    elif key == "equipment_deficit_score":
        maximum = max(R["points_per_100k"]) or 1
        values = [round(max(0, (1 - d / maximum) * 100), 1) for d in R["points_per_100k"]]
    elif key == "new_forages_score":
        pressure = rv("pressure_score")
        deficit = rv("equipment_deficit_score")
        exposure = R.get("fri_high_population_pct", [0] * len(R["labels"]))
        values = [round(.40 * p + .35 * d + .25 * e, 1) for p, d, e in zip(pressure, deficit, exposure)]
    else:
        values = [0] * len(R["labels"])
    return [values[i] for i in ridx]
rlabels = rv("labels")

def filtered_points_frame():
    """Filtre les ouvrages selon la barre latérale."""
    df = pts_gdf.dropna(subset=["geometry"]).copy()
    if selected_regions:
        df = df[df["region"].isin(selected_regions)]
    if not selected_sources:
        return df.iloc[0:0]
    else:
        df = df[df["src"].isin(selected_sources)]
    fri = pd.to_numeric(df["FRI_canton"], errors="coerce")
    classes = pd.Series("Faible", index=df.index, dtype="object")
    classes.loc[fri.isna()] = "Non classé"
    classes.loc[fri > 0.07] = "Moyen"
    classes.loc[fri > 0.13] = "Élevé"
    df["FRI_classe"] = classes
    if not selected_fri_classes:
        df = df.iloc[0:0]
    elif set(selected_fri_classes) != set(fri_options):
        df = df[df["FRI_classe"].isin(selected_fri_classes)]
    return df

filtered_points = filtered_points_frame()
selected_point_counts = [int((filtered_points["region"] == label).sum()) for label in rlabels]
selected_points_per_100k = [
    round(count / pop * 100000, 2) if pop else 0
    for count, pop in zip(selected_point_counts, rv("pop_2010"))
]

st.sidebar.markdown("---")
st.sidebar.markdown('<span class="sidebar-source-chip">TdE · COSO · INSEED · ISRI-TG</span>', unsafe_allow_html=True)
st.sidebar.markdown('<p style="font-style:italic;font-size:12px">Pipeline Python · pandas · geopandas · folium · plotly · streamlit.</p>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-label">Sources officielles</div>', unsafe_allow_html=True)
for source_no, source_url in enumerate(data.get("sources", []), 1):
    st.sidebar.markdown(f"[Source {source_no} · Open Data Togo]({source_url})")

# Fonctions utilitaires
def section_h(t):
    st.markdown(f'<div style="font-size:16px;font-weight:600;color:{C_TEAL};border-left:5px solid {C_GOLD};padding-left:10px;margin:18px 0 10px;font-family:\'Poppins\',Arial,sans-serif">{t}</div>', unsafe_allow_html=True)
def card(open_=True):
    if open_: st.markdown('<div style="background:#fff;border-radius:12px;padding:14px;box-shadow:0 1px 6px rgba(11,79,74,.10);margin-bottom:12px">', unsafe_allow_html=True)
    else: st.markdown('</div>', unsafe_allow_html=True)
def note(t):
    st.markdown(f'<p class="note-limite">{t}</p>', unsafe_allow_html=True)
def interpretation(t):
    st.markdown(f'<div class="interpretation"><strong>Interprétation :</strong> {t}</div>', unsafe_allow_html=True)

def bar(x, y, color, height=300):
    fig = go.Figure(go.Bar(x=x, y=y, marker_color=color, text=y, textposition="auto"))
    fig.update_layout(height=height, margin=dict(t=30,r=10,b=30,l=40), showlegend=False)
    return style_figure(fig)

def folium_map(mode, points, region_filters=None, fri_filters=None, basemap="CartoDB Positron · en ligne"):
    """Construit la carte Folium."""
    import json as _json
    tiles = "CartoDB positron" if basemap.startswith("CartoDB") else None
    fmap = folium.Map(
        location=[8.6, 1.0], zoom_start=7, min_zoom=6, max_zoom=12,
        tiles=tiles, control_scale=True, prefer_canvas=True,
    )
    cantons = _json.load(open(os.path.join(AST, "cantons.geojson"), encoding="utf-8"))
    if region_filters and set(region_filters) != set(R["labels"]):
        cantons["features"] = [f for f in cantons["features"] if f["properties"].get("region") in region_filters]
    if fri_filters and set(fri_filters) != set(fri_options):
        cantons["features"] = [f for f in cantons["features"] if f["properties"].get("fri_class") in fri_filters]

    def fri_color(value):
        value = float(value or 0)
        if value > 0.13: return C_ORG
        if value > 0.07: return C_GOLD
        return C_TEAL

    if mode in ("Croisement FRI + ouvrages", "Risque d'inondation (FRI cantons)"):
        folium.GeoJson(
            cantons, name="FRI cantons", show=True,
            style_function=lambda feature: {
                "fillColor": fri_color(feature["properties"].get("FRI")),
                "color": "#16302C", "weight": 0.45, "fillOpacity": 0.38,
            },
            highlight_function=lambda feature: {"weight": 2, "fillOpacity": 0.62},
            tooltip=folium.GeoJsonTooltip(
                fields=["canton_nom", "region", "FRI", "fri_class", "total_pop", "n_pts"],
                aliases=["Canton", "Région", "FRI", "Classe", "Population", "Ouvrages"],
                localize=True, sticky=False, labels=True,
            ),
        ).add_to(fmap)

    if mode in ("Ouvrages TdE + COSO", "Croisement FRI + ouvrages"):
        pts = points
        layer_tde = folium.FeatureGroup(name="TdE", show=True)
        layer_coso = folium.FeatureGroup(name="COSO", show=True)
        for _, row in pts.iterrows():
            is_tde = row.get("src") == "TdE"
            target = layer_tde if is_tde else layer_coso
            color = C_ORG if is_tde else C_TEAL
            popup = folium.Popup(
                f"<b>{row.get('name', 'Ouvrage')}</b><br>Source : {row.get('src', '')}"
                f"<br>Région : {row.get('region', '')}<br>Canton : {row.get('canton', 'Non renseigné')}"
                f"<br>FRI du canton : {row.get('FRI_canton', 'Non disponible')}"
                f"<br>Contrôle : {row.get('control_class', 'Non évaluable')}"
                f"<br>Score indicatif : {row.get('control_score', '—')}", max_width=300,
            )
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x], radius=5,
                color=color, fill=True, fill_color=color, fill_opacity=.86,
                weight=1.2, popup=popup,
            ).add_to(target)
        layer_tde.add_to(fmap)
        layer_coso.add_to(fmap)
    legend_html = f"""
    <div style="position:fixed;bottom:18px;left:18px;z-index:9999;background:white;border:1px solid #D6E2DF;border-radius:10px;padding:10px 12px;box-shadow:0 2px 10px rgba(11,79,74,.18);font:12px Poppins,Arial,sans-serif;color:#16302C;">
      <div style="font-weight:700;color:#0B4F4A;margin-bottom:6px;">Légende FRI</div>
      <div><span style="display:inline-block;width:12px;height:12px;background:{C_TEAL};margin-right:6px;border-radius:2px;"></span>Faible ≤ 0,07</div>
      <div><span style="display:inline-block;width:12px;height:12px;background:{C_GOLD};margin-right:6px;border-radius:2px;"></span>Moyen 0,07–0,13</div>
      <div><span style="display:inline-block;width:12px;height:12px;background:{C_ORG};margin-right:6px;border-radius:2px;"></span>Élevé &gt; 0,13</div>
      <div style="border-top:1px solid #E4EBE9;margin-top:6px;padding-top:6px;"><span style="color:{C_ORG};font-size:16px;">●</span> TdE &nbsp; <span style="color:{C_TEAL};font-size:16px;">●</span> COSO</div>
      <div style="font-size:10px;color:#5D726E;margin-top:5px;">Fond : {"hors ligne" if tiles is None else "CartoDB Positron"}</div>
    </div>
    """
    fmap.get_root().html.add_child(folium.Element(legend_html))
    folium.LayerControl(collapsed=False, position="topright").add_to(fmap)
    return fmap

def render_folium(fmap):
    """Affiche Folium dans une iframe isolée."""
    html = fmap.get_root().render()
    html = html.replace(
        "</head>",
        "<style>html,body{margin:0;padding:0;width:100%;height:590px;overflow:hidden}.folium-map{width:100%!important;height:590px!important}</style></head>",
        1,
    )
    # Iframe isolée pour éviter les conflits Leaflet/Streamlit.
    st.iframe(html, height=590, width="stretch")

# Onglets
tabs = st.tabs(["Vue d'ensemble","Cartographie","État & Maintenance","Pression démographique","Risque d'inondation","Consommation","Recommandations"])

# 1. Vue d'ensemble
with tabs[0]:
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Ouvrages recensés (TdE + COSO)", f"{S['n_points_total']:,}")
    c2.metric("Ouvrages géolocalisés sélectionnés", f"{len(filtered_points):,}")
    c3.metric("Qualité coordonnées COSO (à corriger)", f"{S['coso_coord_quality_pct']} %")
    c4.metric("Ouvrages COSO avec plan d'entretien", f"{S['coso_maint_overall_pct']} %")
    c5.metric("Volume vendu 2022 (m³)", f"{int(S['total_2022_m3']):,}")
    c1, c2 = st.columns(2)
    with c1:
        section_h("Points d'eau par région")
        st.plotly_chart(bar(rlabels, selected_point_counts, [REGION_COLORS[r] for r in rlabels]), width="stretch")
        top_region, top_count = max(zip(rlabels, selected_point_counts), key=lambda item: item[1])
        low_region, low_count = min(zip(rlabels, selected_point_counts), key=lambda item: item[1])
        interpretation(
            f"{top_region} concentre le plus grand nombre d'ouvrages recensés ({top_count}), tandis que {low_region} en compte le moins ({low_count}). Cet écart décrit la couverture de l'inventaire TdE + COSO, mais ne mesure ni la capacité ni la fonctionnalité des ouvrages."
        )
    with c2:
        section_h("Densité de points / 100 000 hab.")
        st.plotly_chart(bar(rlabels, selected_points_per_100k, C_TURQ), width="stretch")
        dense_region, dense_value = max(zip(rlabels, selected_points_per_100k), key=lambda item: item[1])
        sparse_region, sparse_value = min(zip(rlabels, selected_points_per_100k), key=lambda item: item[1])
        interpretation(
            f"La densité apparente est la plus élevée en {dense_region} ({dense_value:.2f} points pour 100 000 habitants) et la plus faible en {sparse_region} ({sparse_value:.2f}). Ce ratio signale un déficit relatif d'équipement, sans équivaloir à un taux de desserte."
        )
    section_h("Synthèse du diagnostic")
    st.markdown(
        f"Le diagnostic révèle une **couverture très hétérogène** du parc hydraulique togolais : l'inventaire TdE est concentré sur la région **Maritime** (Lomé et périphérie) tandis que le Projet COSO a équipé massivement le **Nord** (Savanes, Kara, Centre). "
        f"Seuls **{S['n_points_geoloc_ok']}/{S['n_points_total']}** ouvrages disposent de coordonnées utilisables, limitant l'analyse spatiale. "
        f"Le taux de plans d'entretien documentés est faible (**{S['coso_maint_overall_pct']} %**) — un risque pour la durabilité. "
        f"Enfin, la consommation domestique reste marginale face aux usages industriel/zone franche, signalant un accès à l'eau de boisson encore à développer.")
    st.markdown(f"**Croisement FRI corrigé :** {S['points_high_FRI']} ouvrages géolocalisés sont en cantons FRI « Élevé », dont {S.get('cantons_high_FRI', 0)} cantons regroupant {S.get('population_high_FRI', 0):,} habitants.")
    note("Attention : le nombre de points est un inventaire, pas une mesure de capacité ou de desserte. Les données de panne/abandon ne sont pas publiées ; la fonctionnalité ne peut donc pas être calculée directement.")

# 2. Cartographie
with tabs[1]:
    section_h("Carte interactive — Folium · ouvrages & risque d'inondation")
    mode = st.radio("Couche cartographique", ["Croisement FRI + ouvrages", "Ouvrages TdE + COSO", "Risque d'inondation (FRI cantons)"], horizontal=True)
    fmap = folium_map(mode, filtered_points, selected_regions, selected_fri_classes, basemap_option)
    render_folium(fmap)
    export_points = filtered_points.copy()
    export_points["longitude"] = export_points.geometry.x
    export_points["latitude"] = export_points.geometry.y
    export_points = pd.DataFrame(export_points.drop(columns=["geometry"], errors="ignore"))
    st.download_button(
        "Télécharger les ouvrages filtrés (CSV)",
        data=export_points.to_csv(index=False).encode("utf-8-sig"),
        file_name="ouvrages_eau_filtres.csv", mime="text/csv", width="stretch",
    )
    if mode == "Croisement FRI + ouvrages":
        interpretation(f"Les points permettent de repérer les ouvrages situés dans les cantons exposés au FRI, tandis que les polygones montrent l'intensité du risque. Les secteurs à risque élevé avec ouvrages existants sont prioritaires pour la protection et la maintenance. {len(filtered_points)} ouvrage(s) sont actuellement sélectionnés.")
    elif mode == "Ouvrages TdE + COSO":
        interpretation(f"La carte compare la couverture spatiale TdE/COSO. Les concentrations de points reflètent les zones documentées, tandis que les espaces vides peuvent aussi signaler une absence de géolocalisation. {len(filtered_points)} ouvrage(s) répondent aux filtres; les coordonnées nulles ou non joignables sont exclues.")
    else:
        interpretation("Lecture de la carte : les teintes claires correspondent à une exposition faible, l'ocre à une exposition intermédiaire et l'orange à une exposition élevée. Les secteurs orange doivent recevoir des mesures de protection avant toute création ou réhabilitation d'ouvrage.")

# 3. État & Maintenance
with tabs[2]:
    st.info("Mesure à compléter : les données TdE et COSO décrivent les ouvrages et l'avancement des projets, mais ne renseignent pas leur état opérationnel. Le dashboard ne calcule donc pas de taux de fonctionnalité. Un score indicatif de contrôle est proposé pour les projets COSO, à confirmer sur le terrain. Un prochain relevé devra ajouter les champs « fonctionnel », « en panne », « abandonné », la date de contrôle et la cause de panne.")
    monitoring_records = data.get("coso_monitoring", [])
    monitoring_all = pd.DataFrame(monitoring_records)
    control_counts = C.get("control_class_counts", {})
    if not monitoring_all.empty and "control_class" in monitoring_all:
        control_counts = monitoring_all["control_class"].value_counts().to_dict()
    priority_count = int(S.get("coso_control_priority_count") or control_counts.get("Priorité de contrôle", 0))
    if not monitoring_all.empty and "control_class" in monitoring_all:
        priority_count = int((monitoring_all["control_class"] == "Priorité de contrôle").sum())
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Microprojets COSO", f"{C['total']:,}")
    c2.metric("COSO géolocalisés", f"{S['coso_with_coord']:,}")
    c3.metric("Plans d'entretien documentés", f"{S['coso_maint_overall_pct']} %")
    c4.metric("Bénéficiaires estimés (COSO)", f"{int(C['beneficiaries_est']):,}")
    c5.metric("COSO à contrôler en priorité", f"{priority_count:,}")
    c1, c2 = st.columns(2)
    with c1:
        section_h("Statut des ouvrages COSO")
        stt = sorted(C["status"].items(), key=lambda x:-x[1])
        st.plotly_chart(bar([s[0] for s in stt][::-1], [s[1] for s in stt][::-1], C_TEAL, height=280), width="stretch")
        if stt:
            main_status, main_status_count = max(stt, key=lambda item: item[1])
            interpretation(
                f"Le statut dominant est « {main_status} » ({main_status_count} projets). Il renseigne l'avancement administratif ou la réception du projet, mais ne permet pas de conclure que les ouvrages sont effectivement fonctionnels sur le terrain."
            )
    with c2:
        section_h("Taux de plan d'entretien par région")
        regional_coso_counts = rv("n_coso")
        covered_regions = [r for r, count in zip(rlabels, regional_coso_counts) if count > 0]
        covered_rates = [rate for rate, count in zip(rv("maint_rate_coso"), regional_coso_counts) if count > 0]
        if covered_regions:
            st.plotly_chart(bar(covered_regions, covered_rates, C_TURQ, height=280), width="stretch")
            best_region, best_rate = max(zip(covered_regions, covered_rates), key=lambda item: item[1])
            weak_region, weak_rate = min(zip(covered_regions, covered_rates), key=lambda item: item[1])
            interpretation(
                f"Parmi les régions couvertes par COSO, {best_region} présente le taux de plans d'entretien documentés le plus élevé ({best_rate:.1f} %), contre {weak_rate:.1f} % en {weak_region}. Les régions sans projet COSO ne sont pas interprétées comme ayant un taux nul."
            )
        else:
            st.warning("Aucun projet COSO n'est recensé dans les régions sélectionnées.")
    section_h("Détail régional — maintenance COSO")
    regional_coso_counts = rv("n_coso")
    maintenance_rates = rv("maint_rate_coso")
    maintenance_missing = rv("maintenance_missing_coso")
    tdf = pd.DataFrame({"Région":rlabels,"Ouvrages COSO":regional_coso_counts,"Couverture COSO":["Aucun projet recensé" if n == 0 else "Projet(s) recensé(s)" for n in regional_coso_counts],"Plans documentés (%)":[rate if n > 0 else None for rate, n in zip(maintenance_rates, regional_coso_counts)],"Plans manquants (proxy)":[missing if n > 0 else None for missing, n in zip(maintenance_missing, regional_coso_counts)]})
    st.dataframe(tdf, hide_index=True, width="stretch")
    st.download_button("Télécharger le suivi maintenance (CSV)", tdf.to_csv(index=False).encode("utf-8-sig"), "maintenance_regionale.csv", "text/csv", width="stretch")
    section_h("Statut de réalisation des microprojets COSO")
    status_rows = []
    for r, count in zip(rlabels, regional_coso_counts):
        if count == 0:
            continue
        row = {"Région": r}
        row.update(C.get("status_by_region", {}).get(r, {}))
        status_rows.append(row)
    status_df = pd.DataFrame(status_rows).fillna(0)
    if status_df.empty:
        st.caption("Aucun statut COSO n'est disponible pour les régions sélectionnées.")
    else:
        st.dataframe(status_df, hide_index=True, width="stretch")
    st.download_button("Télécharger les statuts COSO (CSV)", status_df.to_csv(index=False).encode("utf-8-sig"), "statuts_coso_regionaux.csv", "text/csv", width="stretch")
    section_h("Score indicatif de contrôle des projets COSO")
    note("Méthode du proxy : absence de plan d'entretien (45 %), statut non définitif (25 %), remise à la communauté non documentée (15 %) et exposition FRI (15 % lorsque disponible). Le score est renormalisé lorsque le FRI manque. Score ≥ 60 : priorité de contrôle ; 35–59,9 : à vérifier ; < 35 : risque indicatif faible.")
    score_order = ["Priorité de contrôle", "À vérifier", "Risque indicatif faible", "Données insuffisantes"]
    score_counts = [int(control_counts.get(label, 0)) for label in score_order]
    if any(score_counts):
        st.plotly_chart(bar(score_order, score_counts, [C_ORG, C_GOLD, C_TEAL, "#8B9B98"], height=260), width="stretch")
        interpretation(
            f"La classe la plus représentée est « {score_order[int(np.argmax(score_counts))]} » ({max(score_counts)} projets). Cette répartition sert à organiser les visites et ne doit pas être présentée comme une estimation de la fonctionnalité réelle."
        )
    monitoring_df = monitoring_all.copy()
    if not monitoring_df.empty:
        monitoring_df = monitoring_df[monitoring_df["region"].isin(rlabels)].copy()
        class_order = {"Priorité de contrôle": 0, "À vérifier": 1, "Risque indicatif faible": 2, "Données insuffisantes": 3}
        monitoring_df["_order"] = monitoring_df["control_class"].map(class_order).fillna(4)
        monitoring_df = monitoring_df.sort_values(["_order", "control_score"], ascending=[True, False])
        monitoring_view = monitoring_df.rename(columns={
            "name": "Ouvrage", "region": "Région", "canton": "Canton",
            "FRI_canton": "FRI canton", "project_status": "Statut projet",
            "maintenance_plan": "Plan entretien", "handover_date": "Remise communauté",
            "valid_coord": "Coordonnées valides", "control_score": "Score contrôle",
            "control_class": "Classe de contrôle",
        })
        display_columns = ["Ouvrage", "Région", "Canton", "FRI canton", "Statut projet", "Plan entretien", "Remise communauté", "Coordonnées valides", "Score contrôle", "Classe de contrôle"]
        st.dataframe(monitoring_view[display_columns].head(25), hide_index=True, width="stretch")
        st.download_button("Télécharger les scores de contrôle COSO (CSV)", monitoring_view[display_columns].to_csv(index=False).encode("utf-8-sig"), "scores_controle_coso.csv", "text/csv", width="stretch")
        priority_rows = int((monitoring_df["control_class"] == "Priorité de contrôle").sum())
        interpretation(
            f"Le score classe {priority_rows} projet(s) COSO de la sélection en priorité de contrôle. Il combine l'absence de plan d'entretien, le statut du projet, la remise à la communauté et, lorsqu'il est disponible, l'exposition FRI. Il s'agit d'un outil de ciblage des visites, pas d'une prédiction de panne."
        )
    note("À retenir : le statut COSO indique l'avancement ou la réception du projet, pas l'état de fonctionnement sur le terrain. Le plan d'entretien documenté sert uniquement de proxy de durabilité ; il devra être complété par des contrôles réguliers pour mesurer les pannes et les abandons.")

# 4. Pression démographique
with tabs[3]:
    section_h("Population INSEED 2010 vs points d'eau par région")
    fig = go.Figure()
    fig.add_bar(name="Population INSEED (2010)", x=rlabels, y=rv("pop_2010"), marker_color=C_TURQ)
    fig.add_bar(name="Points d'eau", x=rlabels, y=rv("n_points"), marker_color=C_TEAL, yaxis="y2")
    fig.update_layout(barmode="group", height=340, margin=dict(t=20,r=10,b=30,l=60), yaxis2=dict(overlaying="y", side="right", showgrid=False))
    st.plotly_chart(style_figure(fig), width="stretch")
    population_values = rv("pop_2010")
    population_region, population_value = max(zip(rlabels, population_values), key=lambda item: item[1])
    interpretation(
        f"{population_region} concentre la population INSEED 2010 la plus importante ({population_value:,} habitants), mais la comparaison avec les ouvrages doit rester prudente : un point peut desservir plusieurs localités et sa capacité n'est pas renseignée."
    )
    section_h("Densité d'équipement (points / 100 000 hab.)")
    st.plotly_chart(bar(rlabels, selected_points_per_100k, C_GOLD), width="stretch")
    dense_region, dense_value = max(zip(rlabels, selected_points_per_100k), key=lambda item: item[1])
    sparse_region, sparse_value = min(zip(rlabels, selected_points_per_100k), key=lambda item: item[1])
    interpretation(
        f"La densité calculée avec la population INSEED est maximale en {dense_region} ({dense_value:.2f}) et minimale en {sparse_region} ({sparse_value:.2f}). {sparse_region} constitue donc un secteur à examiner pour de nouveaux ouvrages, sous réserve d'une étude hydrogéologique et de la vérification de la fonctionnalité existante."
    )
    pdf = pd.DataFrame({"Région": rlabels, "Population INSEED (2010)": rv("pop_2010"), "Points sélectionnés": selected_point_counts, "Habitants / point": [round(p / n) if n else None for p, n in zip(rv("pop_2010"), selected_point_counts)], "Déficit équipement (score)": rv("equipment_deficit_score")})
    st.dataframe(pdf, hide_index=True, width="stretch")
    st.download_button("Télécharger la pression démographique (CSV)", pdf.to_csv(index=False).encode("utf-8-sig"), "pression_demographique.csv", "text/csv", width="stretch")
    note("Population régionale = INSEED/RGPH 2010. La densité est un indicateur de pression, pas une estimation de desserte : un ouvrage peut couvrir plusieurs villages et sa capacité n'est pas fournie. La population modélisée des cantons FRI est utilisée séparément pour l'analyse d'exposition au risque.")

# 5. Risque d'inondation
with tabs[4]:
    selected_fri_counts = [int((filtered_points["FRI_classe"] == cls).sum()) for cls in F["class"]]
    c1, c2 = st.columns(2)
    with c1:
        section_h("Classes de risque d'inondation (cantons)")
        fig = go.Figure(go.Pie(labels=F["class"], values=F["n_cantons"], hole=.4, marker_colors=[C_TEAL,C_GOLD,C_ORG]))
        st.plotly_chart(style_figure(fig), width="stretch")
        canton_class, canton_count = max(zip(F["class"], F["n_cantons"]), key=lambda item: item[1])
        interpretation(
            f"La classe FRI « {canton_class} » regroupe le plus grand nombre de cantons ({canton_count}). La répartition décrit l'exposition territoriale au risque d'inondation et doit guider le dimensionnement des mesures de protection."
        )
    with c2:
        section_h("Ouvrages localisés par classe FRI")
        st.plotly_chart(bar(F["class"], selected_fri_counts, [C_TEAL,C_GOLD,C_ORG]), width="stretch")
        point_class, point_count = max(zip(F["class"], selected_fri_counts), key=lambda item: item[1])
        high_index = F["class"].index("Élevé") if "Élevé" in F["class"] else None
        high_count = selected_fri_counts[high_index] if high_index is not None else 0
        interpretation(
            f"La classe « {point_class} » contient le plus d'ouvrages sélectionnés ({point_count}). {high_count} ouvrage(s) se situent dans des cantons FRI « Élevé » : ils doivent être examinés pour le drainage, la surélévation et la protection des équipements."
        )
    section_h("Croisement ouvrages × exposition FRI")
    fdf = pd.DataFrame({"Classe FRI":F["class"],"Cantons":F["n_cantons"],"Ouvrages sélectionnés":selected_fri_counts,"Population de référence":[int(x) for x in F["pop"]]})
    st.dataframe(fdf, hide_index=True, width="stretch")
    st.download_button("Télécharger le croisement FRI (CSV)", fdf.to_csv(index=False).encode("utf-8-sig"), "croisement_fri_ouvrages.csv", "text/csv", width="stretch")
    rdf = pd.DataFrame({"Région": rlabels, "Ouvrages en FRI élevé": rv("pts_high_FRI"), "Cantons FRI élevé": rv("fri_high_cantons"), "Population en FRI élevé": rv("fri_high_population"), "Part population exposée (%)": rv("fri_high_population_pct")})
    st.dataframe(rdf, hide_index=True, width="stretch")
    note(f"Le seuil « Élevé » est FRI > 0,13, conformément à la classification du pipeline. Les cantons « Élevé » regroupent {S.get('population_high_FRI', 0):,} habitants et {S['points_high_FRI']} ouvrages géolocalisés : toute création ou réhabilitation doit intégrer drainage, surélévation et protection de la tête de forage.")

# 6. Consommation
with tabs[5]:
    years = W["years"]; ysel = st.selectbox("Année", years, index=len(years)-1)
    yi = years.index(ysel)
    section_h(f"Ventes d'eau par catégorie d'abonnés — {ysel} (m³)")
    vals = [r[yi] for r in W["matrix"]]
    st.plotly_chart(bar(W["categories"], vals, [C_TEAL,C_TURQ,C_GOLD,C_ORG,C_PURP,"#43a842","#b34000","#0B99BD","#929292"]), width="stretch")
    leading_category, leading_value = max(zip(W["categories"], vals), key=lambda item: item[1])
    interpretation(
        f"En {ysel}, la catégorie « {leading_category} » représente le plus grand volume vendu ({leading_value:,} m³). Cette structure des ventes décrit la consommation facturée par catégorie, mais ne constitue pas directement une mesure de l'accès domestique à l'eau potable."
    )
    section_h("Évolution 2018 → 2022")
    fig = go.Figure()
    for i,cat in enumerate(W["categories"]):
        fig.add_trace(go.Scatter(x=years, y=W["matrix"][i], mode="lines+markers", name=cat))
    fig.update_layout(height=340, margin=dict(t=20,r=10,b=30,l=50), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(style_figure(fig), width="stretch")
    end_values = [row[-1] for row in W["matrix"]]
    start_values = [row[0] for row in W["matrix"]]
    trend_category, trend_end = max(zip(W["categories"], end_values), key=lambda item: item[1])
    trend_index = W["categories"].index(trend_category)
    trend_start = start_values[trend_index]
    trend_change = ((trend_end - trend_start) / trend_start * 100) if trend_start else 0
    direction = "progressé" if trend_change > 0 else "reculé" if trend_change < 0 else "est resté stable"
    interpretation(
        f"Sur 2018–2022, « {trend_category} » reste la catégorie la plus volumique en 2022 et a {direction} de {abs(trend_change):.1f} % sur la période. Une hausse des volumes ne permet toutefois pas de conclure à une amélioration de la couverture des ménages."
    )
    note("Données « Ventes d'eau par catégorie d'abonnés » (TdE). Les catégories « Forage Usage Industries / Autres » et « Zone Franche » dominent les volumes, tandis que la consommation des ménages (Concessions TdE, Collectivités) reste marginale.")

# 7. Recommandations
with tabs[6]:
    section_h("Recommandations stratégiques")
    RECOS = [
        f"Maintenance immédiate : auditer les ouvrages COSO sans plan documenté ({sum(rv('maintenance_missing_coso'))} dans la sélection) et programmer une visite trimestrielle avec statut panne/abandon.",
        "Suivi de fonctionnalité : organiser un relevé terrain trimestriel pour chaque ouvrage et publier les champs « fonctionnel », « en panne », « abandonné », la date du contrôle et la cause de panne. Le score COSO sert uniquement à cibler les premières visites ; après plusieurs campagnes, ces observations permettront de calculer un taux régional fiable.",
        "Qualité des données : corriger les coordonnées nulles (0,0), conserver la source/date de mesure et documenter les contrôles terrain pour éviter qu'un taux de fonctionnalité régional soit trompeur.",
        "Nouveaux forages : cibler d'abord les cantons à score de priorité élevé, en particulier les zones à forte population, faible densité d'ouvrages et FRI élevé.",
        "Résilience : surélever les équipements électriques, protéger les têtes de forage et prévoir drainage/accès de secours pour les 77 ouvrages situés en FRI élevé.",
        "Équité territoriale : compléter la couverture hors Maritime et hors corridor COSO des Savanes, avec une étude hydrogéologique et un test de qualité de l'eau avant implantation.",
        "Accès domestique : flécher les investissements vers les branchements sociaux et points de desserte, la consommation industrielle/zone franche dominant les volumes TdE 2022.",
    ]
    for i,r in enumerate(RECOS,1):
        st.markdown(f"**{i}.** {r}")
    section_h("Priorisation régionale des nouveaux forages")
    pr = pd.DataFrame({"Région": rlabels, "Score priorité": rv("new_forages_score"), "Pression démo": rv("pressure_score"), "Déficit équipement": rv("equipment_deficit_score"), "Exposition FRI élevé (%)": rv("fri_high_population_pct")}).sort_values("Score priorité", ascending=False)
    st.dataframe(pr, hide_index=True, width="stretch")
    st.download_button("Télécharger les priorités régionales (CSV)", pr.to_csv(index=False).encode("utf-8-sig"), "priorites_regionales.csv", "text/csv", width="stretch")
    note("Score indicatif = 40 % pression démographique + 35 % déficit relatif d'équipement + 25 % part de population en FRI élevé. Il aide à ordonner les études; il ne remplace pas la faisabilité hydrogéologique, le coût, la qualité de l'eau ni la concertation locale.")
    section_h("Cantons à examiner en premier")
    P = data.get("priority_cantons", {})
    top = pd.DataFrame({"Canton": P.get("canton", []), "Région": P.get("region", []), "Score": P.get("score", []), "FRI": P.get("fri", []), "Population": P.get("population", []), "Ouvrages": P.get("points", [])})
    st.dataframe(top, hide_index=True, width="stretch")
    st.download_button("Télécharger les cantons prioritaires (CSV)", top.to_csv(index=False).encode("utf-8-sig"), "cantons_prioritaires.csv", "text/csv", width="stretch")
    note("Les cantons sont classés par une combinaison population + FRI + absence d'ouvrage documenté. Vérifier sur le terrain la localisation, la fonctionnalité, la demande et la disponibilité de la ressource avant décision.")

# Pied de page
st.markdown('<p style="text-align:center;color:#5D726E;font-size:11px;margin-top:30px">Togo AI Lab — Défi 1 Environnement — Dashboard réalisé à partir des données ouvertes TdE · COSO · INSEED · ISRI-TG.</p>', unsafe_allow_html=True)

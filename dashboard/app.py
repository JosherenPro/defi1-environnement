"""
Portail National d'Aide à la Décision — Accès à l'Eau Potable au Togo
Design System : Service Public de l'Administration Togolaise (service-public.gouv.tg / opendata.gouv.tg)
Identité Visuelle : République Togolaise (Vert #006A4E / #0B4F4A, Or #FFCE00 / #F4B400, Rouge #D21034)
"""
import os, json, base64
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
LOGO_PNG = os.path.join(AST, "logo-datalab.png")

# Configuration de la page
st.set_page_config(
    page_title="Accès à l'Eau Potable — Service Public Togo",
    page_icon=FAVICON if os.path.exists(FAVICON) else "🇹🇬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Chargement du logo en base64 pour insertion fluide
LOGO_B64 = ""
if os.path.exists(LOGO_PNG):
    with open(LOGO_PNG, "rb") as f:
        LOGO_B64 = base64.b64encode(f.read()).decode("utf-8")

# Palette Service Public / République Togolaise
C_GREEN = "#006A4E"      # Vert République Togolaise
C_TEAL  = "#0B4F4A"      # Vert Forêt profond
C_GOLD  = "#F4B400"      # Jaune Or drapeau
C_RED   = "#D21034"      # Rouge drapeau
C_BLUE  = "#116E9B"      # Bleu démarche numérique
C_TURQ  = "#14877D"      # Turquoise secondaire
C_ORG   = "#D9622B"      # Orange risque
C_PURP  = "#7A4FA0"      # Violet Savanes
C_INK   = "#16302C"      # Texte principal
C_MUTED = "#5D726E"      # Texte atténué
C_BG    = "#F4F7F6"      # Arrière-plan institutionnel

REGION_COLORS = {
    "Maritime": C_TEAL,
    "Plateaux": C_TURQ,
    "Centrale": C_GOLD,
    "Kara": C_ORG,
    "Savanes": C_PURP,
}
COLORWAY = [C_TEAL, C_GOLD, C_TURQ, C_ORG, C_PURP]

# Style CSS aux normes de l'administration togolaise (service-public.gouv.tg)
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');

html, body, .stApp, p, label, button, input, textarea, select,
div[data-testid="stMarkdownContainer"] {{
    font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}}

.stApp {{
    background-color: {C_BG} !important;
    color: {C_INK};
}}

.stApp > header {{
    background: transparent !important;
}}

.block-container {{
    padding-top: 0.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 100% !important;
}}

/* Ruban National Tricolore du Togo */
.national-ribbon {{
    display: flex;
    height: 5px;
    width: 100%;
    margin-bottom: 0.75rem;
    border-radius: 3px;
    overflow: hidden;
}}
.national-ribbon .stripe-green {{ flex: 2; background-color: {C_GREEN}; }}
.national-ribbon .stripe-gold {{ flex: 2; background-color: {C_GOLD}; }}
.national-ribbon .stripe-red {{ flex: 1; background-color: {C_RED}; }}

/* Header Institutionnel - Service Public Togo */
.gouv-header {{
    background: #FFFFFF;
    border-radius: 12px;
    padding: 1.25rem 1.75rem;
    margin-bottom: 1rem;
    border: 1px solid #E2ECE9;
    box-shadow: 0 4px 16px rgba(11, 79, 74, 0.06);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}}

.gouv-brand-block {{
    display: flex;
    align-items: center;
    gap: 1.25rem;
}}

.republique-badge {{
    border-right: 2px solid #E2ECE9;
    padding-right: 1.25rem;
    text-align: left;
}}

.republique-title {{
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.8px;
    color: {C_GREEN};
    text-transform: uppercase;
    margin: 0;
    line-height: 1.2;
}}

.republique-motto {{
    font-size: 9.5px;
    font-weight: 500;
    color: {C_MUTED};
    margin: 2px 0 0 0;
    font-style: italic;
    letter-spacing: 0.5px;
}}

.portal-title-block h1 {{
    font-size: clamp(1.35rem, 2.2vw, 1.75rem);
    font-weight: 700;
    color: {C_TEAL};
    margin: 0;
    line-height: 1.2;
}}

.portal-title-block p {{
    font-size: 13px;
    color: {C_MUTED};
    margin: 3px 0 0 0;
    line-height: 1.35;
}}

.gouv-header-badges {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    flex-wrap: wrap;
}}

.badge-opendata {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #EAF4F2;
    color: {C_TEAL};
    font-size: 11.5px;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 20px;
    border: 1px solid #C4DFD9;
}}

.badge-datalab {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #FFF8E6;
    color: #946C00;
    font-size: 11.5px;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 20px;
    border: 1px solid #FFE699;
}}

/* Bannière d'alerte officielle (Style service-public.gouv.tg) */
.announcement-banner {{
    background-color: #FFF9E6;
    border-left: 4px solid {C_GOLD};
    border-radius: 8px;
    padding: 0.75rem 1.25rem;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: #4A3B00;
    font-size: 13px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}}

.announcement-banner strong {{
    color: #805B00;
    font-weight: 700;
}}

/* Métriques - Cartes Administratives */
div[data-testid="stMetric"] {{
    background: #FFFFFF !important;
    border-radius: 10px !important;
    padding: 1.1rem 1rem 0.95rem !important;
    box-shadow: 0 2px 8px rgba(11, 79, 74, 0.06) !important;
    border: 1px solid #E2ECE9 !important;
    border-top: 3px solid {C_GREEN} !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}

div[data-testid="stMetric"]:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(11, 79, 74, 0.10) !important;
}}

label[data-testid="stMetricLabel"] p {{
    font-size: 12.5px !important;
    color: {C_MUTED} !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    line-height: 1.3 !important;
}}

div[data-testid="stMetricValue"] {{
    font-family: 'Space Grotesk', sans-serif !important;
    color: {C_TEAL} !important;
    font-size: clamp(1.4rem, 2vw, 1.85rem) !important;
    font-weight: 700 !important;
}}

/* Onglets de Navigation - Style Service Public */
.stTabs {{
    width: 100% !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    background: #FFFFFF;
    padding: 6px;
    border-radius: 10px;
    border: 1px solid #E2ECE9;
    box-shadow: 0 2px 6px rgba(11, 79, 74, 0.04);
    width: 100% !important;
}}

.stTabs [data-baseweb="tab"] {{
    flex: 1 1 0;
    justify-content: center;
    background-color: transparent;
    border-radius: 7px;
    padding: 10px 12px;
    font-weight: 600;
    font-size: 13.5px;
    color: {C_MUTED};
    transition: all 0.2s ease;
}}

.stTabs [data-baseweb="tab"]:hover {{
    color: {C_GREEN};
    background: #F4F7F6;
}}

.stTabs [aria-selected="true"] {{
    background: {C_TEAL} !important;
    color: #FFFFFF !important;
    box-shadow: 0 3px 8px rgba(11, 79, 74, 0.22);
}}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {{
    display: none;
}}

/* Titres de sections administratives */
.gouv-section-title {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    font-weight: 700;
    color: {C_TEAL};
    padding: 6px 0;
    margin: 18px 0 10px;
    border-bottom: 2px solid #E2ECE9;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.gouv-section-title span.bar {{
    display: inline-block;
    width: 4px;
    height: 18px;
    background: {C_GOLD};
    border-radius: 2px;
}}

/* Encadrés d'interprétation et avis méthodologiques */
.gouv-callout-info {{
    background-color: #EBF5F3;
    border-left: 4px solid {C_TURQ};
    border-radius: 6px;
    padding: 10px 14px;
    margin: 10px 0 14px;
    font-size: 13.5px;
    color: {C_INK};
    line-height: 1.5;
}}
.gouv-callout-info strong {{ color: {C_TEAL}; }}

.gouv-callout-warning {{
    background-color: #FFF8E6;
    border-left: 4px solid {C_GOLD};
    border-radius: 6px;
    padding: 10px 14px;
    margin: 12px 0 16px;
    font-size: 13.5px;
    color: #5A4700;
    line-height: 1.5;
}}

.gouv-callout-alert {{
    background-color: #FEF2F2;
    border-left: 4px solid {C_RED};
    border-radius: 6px;
    padding: 10px 14px;
    margin: 10px 0 14px;
    font-size: 13.5px;
    color: #7F1D1D;
    line-height: 1.5;
}}

/* Sidebar - Administration */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #004D38 0%, #0B4F4A 100%) !important;
    border-right: 1px solid rgba(244, 180, 0, 0.3);
}}

section[data-testid="stSidebar"] > div {{
    background: transparent !important;
}}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    color: rgba(255, 255, 255, 0.88) !important;
}}

section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    color: #FFFFFF !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 700;
}}

section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: #FFFFFF !important;
    border-radius: 8px !important;
    min-height: 42px;
}}

section[data-testid="stSidebar"] [data-baseweb="select"] * {{
    color: {C_INK} !important;
}}

section[data-testid="stSidebar"] a {{
    color: {C_GOLD} !important;
    font-weight: 500;
}}

.sidebar-header-gouv {{
    padding: 0.5rem 0.25rem 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    margin-bottom: 1rem;
}}

.sidebar-flag {{
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    color: {C_GOLD};
    letter-spacing: 1.5px;
    text-transform: uppercase;
}}

.sidebar-header-gouv h2 {{
    font-size: 1.35rem;
    margin: 0.4rem 0 0.2rem;
    line-height: 1.2;
}}

.sidebar-header-gouv p {{
    font-size: 12px;
    color: rgba(255, 255, 255, 0.72);
    margin: 0;
}}

/* Pied de page officiel République Togolaise */
.gouv-footer {{
    background: #FFFFFF;
    border: 1px solid #E2ECE9;
    border-radius: 12px;
    padding: 1.75rem 2rem 1.25rem;
    margin-top: 2.5rem;
    box-shadow: 0 4px 12px rgba(11, 79, 74, 0.04);
}}

.gouv-footer-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1.5rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid #E2ECE9;
}}

.gouv-footer-col h4 {{
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    color: {C_TEAL};
    letter-spacing: 1px;
    margin: 0 0 0.6rem 0;
}}

.gouv-footer-col p, .gouv-footer-col a {{
    font-size: 12.5px;
    color: {C_MUTED};
    text-decoration: none;
    line-height: 1.6;
    margin: 0 0 0.35rem 0;
    display: block;
}}

.gouv-footer-col a:hover {{
    color: {C_GREEN};
    text-decoration: underline;
}}

.gouv-footer-bottom {{
    padding-top: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
    font-size: 11.5px;
    color: #7A8E8B;
}}

/* Responsive */
@media (max-width: 768px) {{
    .block-container {{ padding: 0.5rem 0.75rem 2rem !important; }}
    .gouv-header {{ padding: 1rem; }}
    .republique-badge {{ border-right: none; padding-right: 0; }}
    .stTabs [data-baseweb="tab-list"] {{ overflow-x: auto; flex-wrap: nowrap; }}
    .stTabs [data-baseweb="tab"] {{ flex: 0 0 auto; white-space: nowrap; }}
}}
</style>
""", unsafe_allow_html=True)

# Ruban Tricolore National
st.markdown("""
<div class="national-ribbon">
  <div class="stripe-green"></div>
  <div class="stripe-gold"></div>
  <div class="stripe-red"></div>
</div>
""", unsafe_allow_html=True)

# Logo HTML
logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" height="42" alt="Togo AI Lab Logo" />' if LOGO_B64 else '🏛️'

# En-tête officiel Service Public
st.markdown(f"""
<div class="gouv-header">
  <div class="gouv-brand-block">
    <div class="republique-badge">
      <div class="republique-title">RÉPUBLIQUE TOGOLAISE</div>
      <div class="republique-motto">Travail — Liberté — Patrie</div>
    </div>
    <div class="portal-title-block">
      <h1>Portail National de l'Eau Potable</h1>
      <p>Système de diagnostic spatial, de durabilité du parc et de résilience climatique</p>
    </div>
  </div>
  <div class="gouv-header-badges">
    <span class="badge-opendata">🌐 Données Ouvertes certifiées</span>
    <span class="badge-datalab">🔬 Togo AI Lab · Défi 1</span>
    {logo_html}
  </div>
</div>
""", unsafe_allow_html=True)

# Bannière d'information officielle
st.markdown("""
<div class="announcement-banner">
  <span>📢</span>
  <div><strong>Plateforme Officielle d'Aide à la Décision :</strong> Diagnostic territorial fondé sur le croisement des jeux de données ouverts de la <strong>TdE</strong>, du <strong>Projet COSO</strong>, du <strong>RGPH INSEED</strong> et des indices <strong>ISRI-TG</strong>.</div>
</div>
""", unsafe_allow_html=True)

# Chargement des données
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

# Barre latérale - Filtres de pilotage
st.sidebar.markdown("""
<div class="sidebar-header-gouv">
  <span class="sidebar-flag">RÉPUBLIQUE TOGOLAISE</span>
  <h2>Pilotage de l'Analyse</h2>
  <p>Filtrez les données géographiques et administratives pour ajuster le diagnostic.</p>
</div>
""", unsafe_allow_html=True)

region_options = R["labels"]
selected_regions = st.sidebar.multiselect(
    "Régions administratives", region_options, default=region_options,
    help="Sélectionnez une ou plusieurs régions. Les indicateurs et la carte s'actualisent en temps réel.",
)
if not selected_regions:
    st.sidebar.warning("Sélectionnez au moins une région.")
    selected_regions = region_options

source_options = ["TdE", "COSO"]
selected_sources = st.sidebar.multiselect(
    "Source des données", source_options, default=source_options,
)

fri_options = ["Faible", "Moyen", "Élevé"]
selected_fri_classes = st.sidebar.multiselect(
    "Exposition au risque d'inondation (FRI)", fri_options, default=fri_options,
    help="Classement de vulnérabilité aux crues par canton (ISRI-TG).",
)

basemap_option = st.sidebar.radio(
    "Fond cartographique", ["CartoDB Positron · en ligne", "Sans fond · hors ligne"],
    index=0, help="Le mode hors ligne permet l'affichage en réseau restreint.",
)

# Indice et filtres régionaux
ridx = [i for i, label in enumerate(R["labels"]) if label in selected_regions]
if not ridx:
    ridx = list(range(len(R["labels"])))

def rv(key):
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
st.sidebar.markdown('<p style="font-size:11.5px;color:rgba(255,255,255,0.7);">🏛️ <strong>Ministère de l\'Eau et de l\'Assainissement</strong><br>Système certifié Togo AI Lab</p>', unsafe_allow_html=True)
st.sidebar.markdown('<p style="font-size:11px;color:rgba(255,255,255,0.6);">Sources ouvertes sur <a href="https://opendata.gouv.tg" target="_blank" style="color:#F4B400;">opendata.gouv.tg</a></p>', unsafe_allow_html=True)

# Fonctions graphiques et helpers
def style_figure(fig):
    fig.update_layout(
        font=dict(family="Poppins, sans-serif", color=C_INK, size=12),
        plot_bgcolor="white", paper_bgcolor="white",
        title_text="", title_font=dict(size=14, color=C_TEAL), colorway=COLORWAY,
        margin=dict(t=35, l=40, r=20, b=35),
    )
    return fig

def section_h(title_text):
    st.markdown(f'<div class="gouv-section-title"><span class="bar"></span>{title_text}</div>', unsafe_allow_html=True)

def gouv_info(t):
    st.markdown(f'<div class="gouv-callout-info"><strong>ℹ️ Information officielle :</strong> {t}</div>', unsafe_allow_html=True)

def gouv_warning(t):
    st.markdown(f'<div class="gouv-callout-warning"><strong>⚠️ Note méthodologique :</strong> {t}</div>', unsafe_allow_html=True)

def gouv_alert(t):
    st.markdown(f'<div class="gouv-callout-alert"><strong>🚨 Alerte priorité :</strong> {t}</div>', unsafe_allow_html=True)

def bar(x, y, color, height=290):
    fig = go.Figure(go.Bar(x=x, y=y, marker_color=color, text=y, textposition="auto"))
    fig.update_layout(height=height, margin=dict(t=25, r=10, b=25, l=35), showlegend=False)
    return style_figure(fig)

def folium_map(mode, points, region_filters=None, fri_filters=None, basemap="CartoDB Positron · en ligne"):
    tiles = "CartoDB positron" if basemap.startswith("CartoDB") else None
    fmap = folium.Map(
        location=[8.6, 1.0], zoom_start=7, min_zoom=6, max_zoom=12,
        tiles=tiles, control_scale=True, prefer_canvas=True,
    )
    cantons = json.load(open(os.path.join(AST, "cantons.geojson"), encoding="utf-8"))
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
                aliases=["Canton", "Région", "Indice FRI", "Classe", "Population", "Ouvrages recensés"],
                localize=True, sticky=False, labels=True,
            ),
        ).add_to(fmap)

    if mode in ("Ouvrages TdE + COSO", "Croisement FRI + ouvrages"):
        layer_tde = folium.FeatureGroup(name="TdE (Châteaux / Forages)", show=True)
        layer_coso = folium.FeatureGroup(name="COSO (Microprojets)", show=True)
        for _, row in points.iterrows():
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
    <div style="position:fixed;bottom:18px;left:18px;z-index:9999;background:white;border:1px solid #D6E2DF;border-radius:8px;padding:10px 14px;box-shadow:0 3px 12px rgba(11,79,74,.15);font:12px Poppins,Arial,sans-serif;color:#16302C;">
      <div style="font-weight:700;color:{C_TEAL};margin-bottom:6px;border-bottom:1px solid #E2ECE9;padding-bottom:4px;">LÉGENDE OFFICIELLE</div>
      <div style="margin-bottom:3px;"><span style="display:inline-block;width:12px;height:12px;background:{C_TEAL};margin-right:6px;border-radius:2px;"></span>FRI Faible (≤ 0,07)</div>
      <div style="margin-bottom:3px;"><span style="display:inline-block;width:12px;height:12px;background:{C_GOLD};margin-right:6px;border-radius:2px;"></span>FRI Moyen (0,07–0,13)</div>
      <div style="margin-bottom:4px;"><span style="display:inline-block;width:12px;height:12px;background:{C_ORG};margin-right:6px;border-radius:2px;"></span>FRI Élevé (&gt; 0,13)</div>
      <div style="border-top:1px solid #E2ECE9;margin-top:6px;padding-top:6px;"><span style="color:{C_ORG};font-size:15px;">●</span> TdE &nbsp; <span style="color:{C_TEAL};font-size:15px;">●</span> COSO</div>
    </div>
    """
    fmap.get_root().html.add_child(folium.Element(legend_html))
    folium.LayerControl(collapsed=False, position="topright").add_to(fmap)
    return fmap

def render_folium(fmap):
    html = fmap.get_root().render()
    html = html.replace(
        "</head>",
        "<style>html,body{margin:0;padding:0;width:100%;height:590px;overflow:hidden}.folium-map{width:100%!important;height:590px!important}</style></head>",
        1,
    )
    st.iframe(html, height=590, width="stretch")

# ==============================================================================
# ONGLETS DU PORTAIL SERVICE PUBLIC
# ==============================================================================
tabs = st.tabs([
    "📊 Vue d'ensemble",
    "🗺️ Cartographie SIG",
    "🔧 État & Maintenance",
    "👥 Pression Démographique",
    "🌊 Risque d'Inondation (FRI)",
    "🚰 Consommation & Ventes",
    "📋 Recommandations Stratégiques",
])

# ------------------------------------------------------------------------------
# 1. VUE D'ENSEMBLE
# ------------------------------------------------------------------------------
with tabs[0]:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Ouvrages Recensés", f"{S['n_points_total']:,}", help="Total des ouvrages TdE (67) et microprojets COSO (218)")
    c2.metric("Ouvrages Géolocalisés", f"{len(filtered_points):,}", help="Ouvrages avec coordonnées exploitables")
    c3.metric("Qualité Coordonnées", f"{S['coso_coord_quality_pct']} %", delta=f"-{round(100 - S['coso_coord_quality_pct'], 1)} % nulles", delta_color="inverse")
    c4.metric("Plans d'Entretien COSO", f"{S['coso_maint_overall_pct']} %", help="Projets COSO avec maintenance documentée")
    c5.metric("Volume Vendu 2022", f"{int(S['total_2022_m3']):,} m³", help="Total facturé TdE en 2022")

    c1, c2 = st.columns(2)
    with c1:
        section_h("Répartition territoriale des infrastructures")
        st.plotly_chart(bar(rlabels, selected_point_counts, [REGION_COLORS[r] for r in rlabels]), width="stretch")
        top_region, top_count = max(zip(rlabels, selected_point_counts), key=lambda item: item[1])
        low_region, low_count = min(zip(rlabels, selected_point_counts), key=lambda item: item[1])
        gouv_info(
            f"La région <strong>{top_region}</strong> regroupe le plus grand effectif d'ouvrages publiés ({top_count}), contre {low_count} en <strong>{low_region}</strong>. Cette disparité reflète le découpage des inventaires actuels (TdE centré sur le littoral et COSO sur le septentrion)."
        )
    with c2:
        section_h("Densité d'équipement par habitant")
        st.plotly_chart(bar(rlabels, selected_points_per_100k, C_TURQ), width="stretch")
        dense_region, dense_value = max(zip(rlabels, selected_points_per_100k), key=lambda item: item[1])
        sparse_region, sparse_value = min(zip(rlabels, selected_points_per_100k), key=lambda item: item[1])
        gouv_info(
            f"Densité apparente maximale : <strong>{dense_region}</strong> ({dense_value:.2f} points / 100k hab.) ; minimale : <strong>{sparse_region}</strong> ({sparse_value:.2f}). Ce ratio sert d'alerte pour cibler les zones sous-équipées."
        )

    section_h("Synthèse exécutive du diagnostic")
    st.markdown(
        f"""
        L'analyse intégrée des données ouvertes nationales met en évidence trois constats majeurs pour le pilotage de l'eau au Togo :
        - **Hétérogénéité spatiale marquée :** L'inventaire TdE couvre quasi-exclusivement la région Maritime ({R['n_tde'][0]}/{S['n_tde']} ouvrages), tandis que le programme COSO se concentre dans les Savanes ({R['n_coso'][2]}/{S['n_coso']} microprojets).
        - **Enjeu de complétude géographique :** Seuls **{S['n_points_geoloc_ok']} sur {S['n_points_total']} ouvrages** disposent de coordonnées valides ({round(100 - S['coso_coord_quality_pct'], 1)} % des points COSO sont enregistrés à 0,0).
        - **Vulnérabilité aux inondations (FRI) :** **{S['points_high_FRI']} ouvrages géolocalisés** se situent dans des cantons classés en risque FRI « Élevé » (> 0,13), regroupant plus de **{S.get('population_high_FRI', 0):,} habitants**.
        """
    )
    gouv_warning("Les données publiques ne comportant pas l'état « fonctionnel/en panne », le taux de panne réel ne peut être calculé directement. Le score COSO constitue un proxy indicatif pour organiser les campagnes d'inspection.")

# ------------------------------------------------------------------------------
# 2. CARTOGRAPHIE SIG
# ------------------------------------------------------------------------------
with tabs[1]:
    section_h("Système d'Information Géographique — Ouvrages & Risque FRI")
    mode = st.radio("Sélectionner la vue cartographique :", ["Croisement FRI + ouvrages", "Ouvrages TdE + COSO", "Risque d'inondation (FRI cantons)"], horizontal=True)
    fmap = folium_map(mode, filtered_points, selected_regions, selected_fri_classes, basemap_option)
    render_folium(fmap)

    export_points = filtered_points.copy()
    export_points["longitude"] = export_points.geometry.x
    export_points["latitude"] = export_points.geometry.y
    export_points = pd.DataFrame(export_points.drop(columns=["geometry"], errors="ignore"))
    st.download_button(
        "📥 Exporter les données géographiques filtrées (CSV)",
        data=export_points.to_csv(index=False).encode("utf-8-sig"),
        file_name="donnees_eau_togo_sig.csv", mime="text/csv", width="stretch",
    )

    if mode == "Croisement FRI + ouvrages":
        gouv_info(f"Visualisation spatiale combinée : les cantons colorés indiquent l'intensité du risque FRI et les points repèrent les ouvrages TdE/COSO. {len(filtered_points)} ouvrage(s) affiché(s).")
    elif mode == "Ouvrages TdE + COSO":
        gouv_info("Cartographie des points d'eau répertoriés : les pastilles orange représentent les forages/châteaux TdE et les turquoises les microprojets COSO.")
    else:
        gouv_info("Cartographie du risque d'inondation (FRI) à l'échelle des 388 cantons togolais selon le modèle ISRI-TG.")

# ------------------------------------------------------------------------------
# 3. ÉTAT & MAINTENANCE
# ------------------------------------------------------------------------------
with tabs[2]:
    gouv_info("Transparence des données : en l'absence de statut opérationnel de panne/abandon dans les bases sources, un score indicatif de contrôle est modélisé pour orienter les missions de terrain.")
    monitoring_records = data.get("coso_monitoring", [])
    monitoring_all = pd.DataFrame(monitoring_records)
    control_counts = C.get("control_class_counts", {})
    if not monitoring_all.empty and "control_class" in monitoring_all:
        control_counts = monitoring_all["control_class"].value_counts().to_dict()
    priority_count = int(S.get("coso_control_priority_count") or control_counts.get("Priorité de contrôle", 0))

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Microprojets COSO", f"{C['total']:,}")
    c2.metric("COSO Géolocalisés", f"{S['coso_with_coord']:,}")
    c3.metric("Plans d'Entretien", f"{S['coso_maint_overall_pct']} %")
    c4.metric("Bénéficiaires Estimés", f"{int(C['beneficiaries_est']):,}")
    c5.metric("Priorité de Contrôle", f"{priority_count:,}")

    c1, c2 = st.columns(2)
    with c1:
        section_h("Statut d'avancement des microprojets COSO")
        stt = sorted(C["status"].items(), key=lambda x: -x[1])
        st.plotly_chart(bar([s[0] for s in stt][::-1], [s[1] for s in stt][::-1], C_TEAL, height=270), width="stretch")
        if stt:
            main_status, main_count = max(stt, key=lambda item: item[1])
            gouv_info(f"Statut administratif dominant : « <strong>{main_status}</strong> » ({main_count} projets).")
    with c2:
        section_h("Taux de plans d'entretien documentés")
        regional_coso_counts = rv("n_coso")
        covered_regions = [r for r, count in zip(rlabels, regional_coso_counts) if count > 0]
        covered_rates = [rate for rate, count in zip(rv("maint_rate_coso"), regional_coso_counts) if count > 0]
        if covered_regions:
            st.plotly_chart(bar(covered_regions, covered_rates, C_TURQ, height=270), width="stretch")
            best_r, best_v = max(zip(covered_regions, covered_rates), key=lambda item: item[1])
            gouv_info(f"Meilleur taux de formalisation : <strong>{best_r}</strong> ({best_v:.1f} %).")
        else:
            st.warning("Aucun projet COSO dans les régions filtrées.")

    section_h("Classification indicative de priorité d'inspection")
    score_order = ["Priorité de contrôle", "À vérifier", "Risque indicatif faible", "Données insuffisantes"]
    score_counts = [int(control_counts.get(label, 0)) for label in score_order]
    st.plotly_chart(bar(score_order, score_counts, [C_ORG, C_GOLD, C_TEAL, "#8B9B98"], height=250), width="stretch")

    if not monitoring_all.empty:
        monitoring_df = monitoring_all[monitoring_all["region"].isin(rlabels)].copy()
        display_columns = ["name", "region", "canton", "FRI_canton", "project_status", "maintenance_plan", "control_score", "control_class"]
        col_names = {"name": "Ouvrage", "region": "Région", "canton": "Canton", "FRI_canton": "Indice FRI", "project_status": "Statut", "maintenance_plan": "Plan entretien", "control_score": "Score indicatif", "control_class": "Classe de contrôle"}
        monitoring_view = monitoring_df[display_columns].rename(columns=col_names)
        st.dataframe(monitoring_view.head(25), hide_index=True, width="stretch")
        st.download_button("📥 Télécharger le registre de contrôle COSO (CSV)", monitoring_view.to_csv(index=False).encode("utf-8-sig"), "registre_controle_coso.csv", "text/csv", width="stretch")

# ------------------------------------------------------------------------------
# 4. PRESSION DÉMOGRAPHIQUE
# ------------------------------------------------------------------------------
with tabs[3]:
    section_h("Comparaison Population (INSEED 2010) vs Réseau d'ouvrages")
    fig = go.Figure()
    fig.add_bar(name="Population légale (RGPH 2010)", x=rlabels, y=rv("pop_2010"), marker_color=C_TURQ)
    fig.add_bar(name="Nombre d'ouvrages", x=rlabels, y=rv("n_points"), marker_color=C_TEAL, yaxis="y2")
    fig.update_layout(barmode="group", height=330, margin=dict(t=25, r=10, b=25, l=55), yaxis2=dict(overlaying="y", side="right", showgrid=False))
    st.plotly_chart(style_figure(fig), width="stretch")

    pdf = pd.DataFrame({
        "Région": rlabels,
        "Population légale (2010)": rv("pop_2010"),
        "Ouvrages recensés": selected_point_counts,
        "Ratio Habitants / Point d'eau": [round(p / n) if n else None for p, n in zip(rv("pop_2010"), selected_point_counts)],
        "Indicateur de déficit d'équipement": rv("equipment_deficit_score"),
    })
    st.dataframe(pdf, hide_index=True, width="stretch")
    st.download_button("📥 Télécharger la table démographique (CSV)", pdf.to_csv(index=False).encode("utf-8-sig"), "pression_demographique_togo.csv", "text/csv", width="stretch")
    gouv_warning("La densité d'équipement constitue un indicateur de cadrage : elle ne mesure pas le rayon de couverture effectif ni la puissance des forages.")

# ------------------------------------------------------------------------------
# 5. RISQUE D'INONDATION (FRI)
# ------------------------------------------------------------------------------
with tabs[4]:
    selected_fri_counts = [int((filtered_points["FRI_classe"] == cls).sum()) for cls in F["class"]]
    c1, c2 = st.columns(2)
    with c1:
        section_h("Répartition des cantons par niveau FRI")
        fig = go.Figure(go.Pie(labels=F["class"], values=F["n_cantons"], hole=.4, marker_colors=[C_TEAL, C_GOLD, C_ORG]))
        st.plotly_chart(style_figure(fig), width="stretch")
    with c2:
        section_h("Ouvrages situés en zone inondable")
        st.plotly_chart(bar(F["class"], selected_fri_counts, [C_TEAL, C_GOLD, C_ORG]), width="stretch")

    fdf = pd.DataFrame({
        "Niveau de Risque FRI": F["class"],
        "Nombre de Cantons": F["n_cantons"],
        "Ouvrages Géolocalisés": selected_fri_counts,
        "Population Exposée Estimée": [int(x) for x in F["pop"]],
    })
    st.dataframe(fdf, hide_index=True, width="stretch")
    st.download_button("📥 Exporter la synthèse FRI (CSV)", fdf.to_csv(index=False).encode("utf-8-sig"), "exposition_inondation_fri.csv", "text/csv", width="stretch")
    gouv_alert(f"{S['points_high_FRI']} ouvrages recensés se trouvent en cantons à risque élevé (FRI > 0,13). Des mesures de surélévation des dalles et d'étanchéité des forages s'imposent.")

# ------------------------------------------------------------------------------
# 6. CONSOMMATION & VENTES
# ------------------------------------------------------------------------------
with tabs[5]:
    years = W["years"]
    ysel = st.selectbox("Sélectionner l'exercice budgétaire / année :", years, index=len(years)-1)
    yi = years.index(ysel)
    vals = [r[yi] for r in W["matrix"]]

    section_h(f"Volume d'eau distribué par catégorie d'abonnés — {ysel} (m³)")
    st.plotly_chart(bar(W["categories"], vals, [C_TEAL, C_TURQ, C_GOLD, C_ORG, C_PURP, "#43a842", "#b34000", "#0B99BD", "#929292"]), width="stretch")

    section_h("Évolution des ventes d'eau TdE (2018 → 2022)")
    fig = go.Figure()
    for i, cat in enumerate(W["categories"]):
        fig.add_trace(go.Scatter(x=years, y=W["matrix"][i], mode="lines+markers", name=cat))
    fig.update_layout(height=330, margin=dict(t=25, r=10, b=25, l=45), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(style_figure(fig), width="stretch")
    gouv_info("Les usages industriels et de zone franche représentent la part majoritaire des volumes facturés. Le raccordement social domestique demeure un axe prioritaire de développement.")

# ------------------------------------------------------------------------------
# 7. RECOMMANDATIONS STRATÉGIQUES
# ------------------------------------------------------------------------------
with tabs[6]:
    section_h("Plan d'Action Ministériel — Recommandations R1 à R7")
    recommandations = [
        ("R1", "Audit et Maintenance Immédiate", f"Auditer en urgence les {sum(rv('maintenance_missing_coso'))} ouvrages COSO sans plan d'entretien documenté dans les régions sélectionnées et programmer une visite trimestrielle.", C_TEAL),
        ("R2", "Relevé Régulier de Fonctionnalité", "Instituer un relevé périodique des statuts fonctionnel / en panne / abandonné avec publication ouverte sur opendata.gouv.tg.", C_TURQ),
        ("R3", "Standardisation et Qualité Géographique", "Corriger les coordonnées nulles (0,0) et unifier les identifiants territoriaux (codes cantons / Pcode).", C_BLUE),
        ("R4", "Ciblage des Nouveaux Forages", "Prioriser les investissements sur les cantons combinant forte population, faible équipement et risque FRI modéré.", C_PURP),
        ("R5", "Résilience Climatique des Équipements", f"Mettre en place des têtes de forage surélevées et dalles étanches sur les {S['points_high_FRI']} ouvrages exposés au FRI élevé.", C_ORG),
        ("R6", "Équité Territoriale Interrégionale", "Équilibrer les financements publics hors de la région Maritime et du corridor COSO après études hydrogéologiques.", C_GOLD),
        ("R7", "Extension des Branchements Sociaux", "Développer les bornes-fontaines et le réseau de distribution domestique pour les ménages vulnérables.", C_TEAL),
    ]

    for code, title_r, desc_r, col_r in recommandations:
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2ECE9; border-left:5px solid {col_r}; border-radius:8px; padding:12px 16px; margin-bottom:10px; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
            <span style="background:{col_r}; color:white; font-size:11px; font-weight:700; padding:2px 8px; border-radius:4px;">{code}</span>
            <strong style="color:{C_TEAL}; font-size:14px;">{title_r}</strong>
          </div>
          <p style="margin:0; font-size:13px; color:{C_INK}; line-height:1.45;">{desc_r}</p>
        </div>
        """, unsafe_allow_html=True)

    section_h("Cantons prioritaires pour les prochaines implantations")
    P = data.get("priority_cantons", {})
    top = pd.DataFrame({
        "Canton": P.get("canton", []),
        "Région": P.get("region", []),
        "Score Priorité": P.get("score", []),
        "Indice FRI": P.get("fri", []),
        "Population": P.get("population", []),
        "Ouvrages Actuels": P.get("points", []),
    })
    st.dataframe(top, hide_index=True, width="stretch")
    st.download_button("📥 Télécharger la liste des cantons prioritaires (CSV)", top.to_csv(index=False).encode("utf-8-sig"), "cantons_prioritaires_togo.csv", "text/csv", width="stretch")

# ==============================================================================
# PIED DE PAGE OFFICIEL (SERVICE PUBLIC TOGO)
# ==============================================================================
st.markdown("""
<div class="gouv-footer">
  <div class="gouv-footer-grid">
    <div class="gouv-footer-col">
      <h4>RÉPUBLIQUE TOGOLAISE</h4>
      <p><strong>Ministère de l'Eau et de l'Assainissement</strong></p>
      <p>Ministère de l'Économie Numérique et de la Transformation Digitale</p>
      <p style="font-style:italic; margin-top:8px;">Travail — Liberté — Patrie</p>
    </div>
    <div class="gouv-footer-col">
      <h4>Portails Officiels</h4>
      <a href="https://service-public.gouv.tg" target="_blank">Service Public Togo (service-public.gouv.tg)</a>
      <a href="https://opendata.gouv.tg" target="_blank">Portail Open Data National (opendata.gouv.tg)</a>
      <a href="https://presidence.gouv.tg" target="_blank">Présidence de la République (presidence.gouv.tg)</a>
      <a href="https://datalab.gouv.tg" target="_blank">Togo AI Lab (datalab.gouv.tg)</a>
    </div>
    <div class="gouv-footer-col">
      <h4>Données Sources</h4>
      <p>Société Togolaise des Eaux (TdE) — Inventaire & Ventes</p>
      <p>Projet COSO — Microprojets communautaires Nord</p>
      <p>INSEED — Recensement Général (RGPH 2010)</p>
      <p>ISRI-TG — Cartographie du risque inondation (FRI)</p>
    </div>
    <div class="gouv-footer-col">
      <h4>À Propos du Défi</h4>
      <p><strong>Data Challenge Environnement (Défi 1)</strong></p>
      <p>Conçu pour l'aide à la décision publique et l'optimisation des investissements hydrauliques.</p>
      <p>Version : 2.0 (Norme Service Public)</p>
    </div>
  </div>
  <div class="gouv-footer-bottom">
    <div>&copy; 2026 République Togolaise — Portail officiel de diagnostic de l'accès à l'eau potable.</div>
    <div>Développé dans le cadre du Concours National Togo AI Lab.</div>
  </div>
</div>
""", unsafe_allow_html=True)

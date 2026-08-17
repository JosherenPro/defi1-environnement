"""Dashboard Streamlit du défi Environnement : accès à l'eau potable au Togo."""
import os, json, base64
import pandas as pd
import geopandas as gpd
import folium
import plotly.graph_objects as go
import streamlit as st

BASE = os.path.dirname(os.path.abspath(__file__))
AST  = os.path.join(BASE, "assets")
FAVICON = os.path.join(AST, "opendata-favicon.png")
LOGO_PNG = os.path.join(AST, "logo-datalab.png")

# Configuration de la page
st.set_page_config(
    page_title="Accès à l'Eau Potable au Togo — Togo AI Lab",
    page_icon=FAVICON if os.path.exists(FAVICON) else "💧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Chargement du logo en base64 pour insertion dans la bannière
LOGO_B64 = ""
if os.path.exists(LOGO_PNG):
    with open(LOGO_PNG, "rb") as f:
        LOGO_B64 = base64.b64encode(f.read()).decode("utf-8")

# Palette officielle Togo AI Lab
C_TEAL  = "#0B4F4A"
C_GOLD  = "#F4B400"
C_TURQ  = "#14877D"
C_ORG   = "#D9622B"
C_PURP  = "#7A4FA0"
C_INK   = "#16302C"
C_MUTED = "#5D726E"
C_BG    = "#F3F6F5"

REGION_COLORS = {
    "Maritime": C_TEAL,
    "Plateaux": C_TURQ,
    "Centrale": C_GOLD,
    "Kara": C_ORG,
    "Savanes": C_PURP,
}
COLORWAY = [C_TEAL, C_GOLD, C_TURQ, C_ORG, C_PURP]

# ---------------------------------------------------------------- SVG Icons
SVG_INFO = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#14877D" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>"""
SVG_WARN = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F4B400" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>"""
SVG_ALERT = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D9622B" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>"""
SVG_DOWNLOAD = """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:5px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>"""
SVG_BAR = """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0B4F4A" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px;"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>"""

# ---------------------------------------------------------------- Style CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');

html, body, .stApp, p, label, button, input, textarea, select,
div[data-testid="stMarkdownContainer"] {{
    font-family: 'Poppins', sans-serif !important;
}}

.stApp {{
    background: {C_BG} !important;
    color: {C_INK};
}}

.stApp > header {{
    background: {C_BG} !important;
}}

.block-container {{
    padding-top: 1.25rem !important;
    padding-left: 2.25rem !important;
    padding-right: 2.25rem !important;
    padding-bottom: 3rem !important;
    max-width: 100% !important;
}}

.main .block-container {{
    background: {C_BG};
}}

.main [data-testid="stMarkdownContainer"] p:not(.note-limite),
.main [data-testid="stMarkdownContainer"] li,
.main [data-testid="stWidgetLabel"] p,
.main [data-testid="stWidgetLabel"] label {{
    color: {C_INK} !important;
}}

.main [data-testid="stMarkdownContainer"] p:not(.note-limite),
.main [data-testid="stMarkdownContainer"] li {{
    font-size: 14.5px;
    line-height: 1.55;
}}

/* Banderole Hero avec Logo DataLab */
.hero-banner {{
    background: radial-gradient(circle at 12% 25%, rgba(244,180,0,0.14), transparent 45%),
                radial-gradient(circle at 85% 75%, rgba(20,135,125,0.25), transparent 50%),
                linear-gradient(120deg, #0B4F4A 0%, #106B63 55%, #14877D 100%);
    padding: 2.4rem 2.5rem 2.6rem;
    border-radius: 14px;
    color: white;
    margin: -0.5rem 0 1.5rem 0;
    position: relative;
    overflow: hidden;
    box-shadow: 0 12px 36px rgba(11, 79, 74, 0.18);
    border: 1px solid rgba(255, 255, 255, 0.12);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
}}

.hero-banner::after {{
    content: "";
    position: absolute;
    right: -40px;
    top: -40px;
    width: 240px;
    height: 240px;
    border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.10);
    pointer-events: none;
}}

.hero-content {{
    flex: 1;
    position: relative;
    z-index: 2;
}}

.hero-eyebrow {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    color: {C_GOLD};
    background: rgba(244, 180, 0, 0.14);
    border: 1px solid rgba(244, 180, 0, 0.40);
    padding: 5px 12px;
    border-radius: 20px;
    margin-bottom: 12px;
}}

.hero-banner h1 {{
    margin: 0;
    font-size: clamp(1.75rem, 2.7vw, 2.3rem);
    font-weight: 700;
    letter-spacing: -0.02em;
    font-family: 'Space Grotesk', sans-serif;
    color: #FFFFFF;
    line-height: 1.2;
}}

.hero-banner p {{
    margin: 10px 0 0 0;
    color: rgba(255, 255, 255, 0.88) !important;
    font-size: 14.5px;
    line-height: 1.55;
    max-width: 48rem;
}}

.hero-logo-box {{
    background: rgba(255, 255, 255, 0.95);
    padding: 14px 20px;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    border: 2px solid rgba(244, 180, 0, 0.6);
    flex-shrink: 0;
    position: relative;
    z-index: 2;
}}

.hero-logo-box span {{
    font-size: 10.5px;
    font-weight: 700;
    color: {C_TEAL};
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}

/* Cartes Métriques KPI */
div[data-testid="stMetric"] {{
    background: #FFFFFF !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.1rem 1.05rem !important;
    box-shadow: 0 8px 24px rgba(11, 79, 74, 0.08) !important;
    border: 1px solid #E2ECE9 !important;
    border-bottom: 3.5px solid {C_GOLD} !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}

div[data-testid="stMetric"]:hover {{
    transform: translateY(-3px);
    box-shadow: 0 14px 32px rgba(11, 79, 74, 0.14) !important;
}}

div[data-testid="stMetricValue"] {{
    font-family: 'Space Grotesk', sans-serif !important;
    color: {C_TEAL} !important;
    font-size: clamp(1.4rem, 2vw, 1.85rem) !important;
    font-weight: 700 !important;
}}

label[data-testid="stMetricLabel"],
label[data-testid="stMetricLabel"] *,
label[data-testid="stMetricLabel"] p {{
    font-size: 12.5px !important;
    color: {C_MUTED} !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.4px !important;
    line-height: 1.3 !important;
}}

/* Onglets de navigation - Navigation Pills */
.stTabs {{
    width: 100% !important;
    max-width: none !important;
}}

.stTabs > div,
.stTabs > div > div,
.stTabs [role="tablist"] {{
    width: 100% !important;
    max-width: none !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    display: flex !important;
    gap: 6px;
    background: #FFFFFF;
    padding: 6px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(11, 79, 74, 0.05);
    border: 1px solid #E2ECE9;
    width: 100% !important;
    min-width: 100% !important;
    max-width: none !important;
    justify-content: stretch !important;
}}

.stTabs [data-baseweb="tab"] {{
    flex: 1 1 0 !important;
    min-width: 0 !important;
    max-width: none !important;
    justify-content: center;
    text-align: center;
    background-color: transparent;
    border-radius: 8px;
    padding: 10px 14px;
    font-weight: 600;
    font-size: 13.5px;
    color: {C_MUTED};
    transition: all 0.2s ease;
}}

.stTabs [data-baseweb="tab"]:hover {{
    color: {C_TEAL};
    background: rgba(11, 79, 74, 0.06);
}}

.stTabs [aria-selected="true"] {{
    background: linear-gradient(120deg, #0B4F4A 0%, #106B63 100%) !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 12px rgba(11, 79, 74, 0.22);
}}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {{
    display: none;
}}

/* Encadrés et avis */
.interpretation {{
    color: {C_INK} !important;
    background: #EAF4F2;
    border-left: 4px solid {C_TURQ};
    padding: 12px 16px;
    border-radius: 8px;
    margin: 12px 0 16px;
    font-size: 14px;
    line-height: 1.55;
    box-shadow: 0 1px 4px rgba(0,0,0,0.02);
}}
.interpretation strong {{
    color: {C_TEAL} !important;
}}

.note-limite {{
    color: #5A4700 !important;
    background: #FFF8E6;
    border-left: 4px solid {C_GOLD};
    padding: 12px 16px;
    border-radius: 8px;
    margin-top: 14px;
    font-size: 13.5px;
    line-height: 1.55;
    box-shadow: 0 1px 4px rgba(0,0,0,0.02);
}}

.section-head {{
    display: flex;
    align-items: center;
    font-size: 15px;
    font-weight: 700;
    color: {C_TEAL};
    padding: 6px 0;
    margin: 18px 0 10px;
    border-bottom: 2px solid #E2ECE9;
    letter-spacing: 0.3px;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0B4F4A 0%, #106B63 100%) !important;
    border-right: 1px solid rgba(244, 180, 0, 0.35);
}}

section[data-testid="stSidebar"] > div {{
    background: transparent !important;
}}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    color: rgba(255, 255, 255, 0.88) !important;
}}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] b {{
    color: #FFFFFF !important;
}}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {{
    color: #FFFFFF !important;
    font-family: 'Space Grotesk', sans-serif !important;
}}

section[data-testid="stSidebar"] hr {{
    border-color: rgba(255, 255, 255, 0.18) !important;
}}

section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: #FFFFFF !important;
    border: 0 !important;
    border-radius: 10px !important;
    min-height: 42px;
}}

section[data-testid="stSidebar"] [data-baseweb="select"] * {{
    color: {C_INK} !important;
}}

section[data-testid="stSidebar"] [data-baseweb="input"] > div {{
    background: #FFFFFF !important;
    border: 0 !important;
    border-radius: 10px !important;
}}

section[data-testid="stSidebar"] [data-baseweb="input"] input {{
    color: {C_INK} !important;
}}

section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
    color: rgba(255, 255, 255, 0.78) !important;
    line-height: 1.45 !important;
}}

section[data-testid="stSidebar"] a {{
    color: {C_GOLD} !important;
    font-weight: 500;
}}

section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label {{
    color: #FFFFFF !important;
}}

.sidebar-brand {{
    padding: 0.5rem 0.25rem 1.25rem;
}}

.sidebar-kicker {{
    display: inline-block;
    color: {C_GOLD};
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}}

.sidebar-brand h2 {{
    color: #FFFFFF;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.55rem;
    line-height: 1.05;
    margin: 0.65rem 0 0.5rem;
}}

.sidebar-brand p {{
    color: rgba(255, 255, 255, 0.76);
    font-size: 0.82rem;
    margin: 0;
    line-height: 1.45;
}}

.sidebar-label {{
    color: {C_GOLD};
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 0.3rem 0 0.35rem;
}}

/* Responsive */
@media (max-width: 768px) {{
    .block-container {{ padding: 0.75rem 0.75rem 2rem !important; }}
    .hero-banner {{ flex-direction: column; align-items: flex-start; padding: 1.5rem; }}
    .hero-logo-box {{ align-self: flex-start; }}
    .stTabs [data-baseweb="tab-list"] {{ overflow-x: auto; flex-wrap: nowrap; }}
    .stTabs [data-baseweb="tab"] {{ flex: 0 0 auto; white-space: nowrap; }}
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- Banderole Hero
logo_img_html = f'<img src="data:image/png;base64,{LOGO_B64}" height="52" alt="Togo AI Lab Logo" />' if LOGO_B64 else '<div style="font-size:32px;font-weight:700;color:#0B4F4A;">DATA LAB</div>'

st.markdown(f"""
<div class="hero-banner">
  <div class="hero-content">
    <div class="hero-eyebrow">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="{C_GOLD}"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>
      TOGO AI LAB · DÉFI 1 · ENVIRONNEMENT
    </div>
    <h1>Accès à l'Eau Potable au Togo</h1>
    <p>Diagnostic spatial des infrastructures hydrauliques, durabilité du parc d'équipements, pression démographique et résilience face au risque d'inondation (FRI) — fondé sur les données ouvertes <strong>TdE</strong>, <strong>COSO</strong>, <strong>INSEED</strong> et <strong>ISRI-TG</strong>.</p>
  </div>
  <div class="hero-logo-box">
    {logo_img_html}
    <span>Togo AI Lab</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- Chargement des données
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

# ---------------------------------------------------------------- Barre latérale
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
    key="filter_regions",
)
if not selected_regions:
    st.sidebar.warning("Sélectionnez au moins une région; toutes les régions sont réaffichées.")
    selected_regions = region_options

source_options = ["TdE", "COSO"]
selected_sources = st.sidebar.multiselect(
    "Sources des ouvrages", source_options, default=source_options,
    key="filter_sources",
)

fri_options = ["Faible", "Moyen", "Élevé", "Non classé"]
selected_fri_classes = st.sidebar.multiselect(
    "Classes FRI", fri_options, default=fri_options,
    help="Le filtre FRI s'applique aux ouvrages joignables à un canton.",
    key="filter_fri",
)

search_query = st.sidebar.text_input(
    "Rechercher un ouvrage ou un canton",
    placeholder="Ex. Agoè-Nyivé, forage…",
    help="La recherche s'applique aux noms d'ouvrages, cantons et régions.",
    key="filter_search",
)

basemap_option = st.sidebar.radio(
    "Fond cartographique", ["CartoDB Positron · en ligne", "Sans fond · hors ligne"],
    index=0, help="Le mode hors ligne conserve les cantons et ouvrages sans appeler de tuiles externes.",
    key="filter_basemap",
)

if st.sidebar.button("Réinitialiser les filtres", icon=":material/refresh:", width="stretch"):
    for key in ("filter_regions", "filter_sources", "filter_fri", "filter_search", "filter_basemap", "map_mode", "sales_year"):
        st.session_state.pop(key, None)
    st.rerun()

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
region_index = {label: i for i, label in enumerate(R["labels"])}
national_tde_maritime = int(R["n_tde"][region_index["Maritime"]])
national_coso_savanes = int(R["n_coso"][region_index["Savanes"]])

def filtered_points_frame():
    df = pts_gdf.dropna(subset=["geometry"]).copy()
    if selected_regions:
        df = df[df["region"].isin(selected_regions)]
    if not selected_sources:
        df = df.iloc[0:0]
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
    if search_query.strip():
        query = search_query.strip().casefold()
        searchable = df[["name", "canton", "region"]].fillna("").astype(str).agg(" ".join, axis=1).str.casefold()
        df = df[searchable.str.contains(query, regex=False)]
    return df

filtered_points = filtered_points_frame()
selected_point_counts = [int((filtered_points["region"] == label).sum()) for label in rlabels]
selected_points_per_100k = [
    round(count / pop * 100000, 2) if pop else 0
    for count, pop in zip(selected_point_counts, rv("pop_2010"))
]
selected_points_high_fri = int((filtered_points["FRI_classe"] == "Élevé").sum())

def selected_equipment_deficit():
    densities = selected_points_per_100k
    maximum = max(densities) if densities else 0
    return [round(max(0, (1 - density / maximum) * 100), 1) if maximum else 0 for density in densities]

selected_equipment_deficit = selected_equipment_deficit()
selected_pressure_score = rv("pressure_score")
selected_new_forages_score = [
    round(.40 * pressure + .35 * deficit + .25 * exposure, 1)
    for pressure, deficit, exposure in zip(
        selected_pressure_score,
        selected_equipment_deficit,
        rv("fri_high_population_pct"),
    )
]

active_regions_label = ", ".join(selected_regions) if selected_regions else "aucune"
active_sources_label = ", ".join(selected_sources) if selected_sources else "aucune"
active_fri_label = ", ".join(selected_fri_classes) if selected_fri_classes else "aucune"
st.sidebar.caption(
    f"{len(filtered_points)} ouvrage(s) dans la sélection\n\n"
    f"Régions : {active_regions_label}\n\nSources : {active_sources_label}\n\nFRI : {active_fri_label}"
)

st.sidebar.markdown("---")
st.sidebar.markdown('<p style="font-size:11.5px;color:rgba(255,255,255,0.7);">🔬 <strong>Togo AI Lab</strong> · Défi 1 Environnement</p>', unsafe_allow_html=True)
st.sidebar.markdown('<p style="font-size:11px;color:rgba(255,255,255,0.6);">Données ouvertes : <a href="https://opendata.gouv.tg" target="_blank">opendata.gouv.tg</a></p>', unsafe_allow_html=True)

# ---------------------------------------------------------------- Helpers graphiques
def style_figure(fig):
    fig.update_layout(
        font=dict(family="Poppins, sans-serif", color=C_INK, size=12),
        plot_bgcolor="white", paper_bgcolor="white",
        title_text="", title_font=dict(size=14, color=C_TEAL), colorway=COLORWAY,
        margin=dict(t=30, l=40, r=20, b=30),
    )
    return fig

def section_h(t):
    st.markdown(f'<div class="section-head">{SVG_BAR} {t}</div>', unsafe_allow_html=True)

def interpretation(t):
    st.markdown(f'<div class="interpretation">{SVG_INFO} <strong>Constat analytique :</strong> {t}</div>', unsafe_allow_html=True)

def note(t):
    st.markdown(f'<div class="note-limite">{SVG_WARN} <strong>Précision méthodologique :</strong> {t}</div>', unsafe_allow_html=True)

def alert_box(t):
    st.markdown(f'<div style="background:#FFF1ED; border-left:4px solid {C_ORG}; padding:12px 16px; border-radius:8px; margin:12px 0 16px; font-size:13.5px; color:#6B2200; line-height:1.55;">{SVG_ALERT} <strong>Alerte de vigilance :</strong> {t}</div>', unsafe_allow_html=True)

def bar(x, y, color, height=280):
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
        try:
            value = float(value)
        except (TypeError, ValueError):
            return "#8B9B98"
        if pd.isna(value):
            return "#8B9B98"
        if value > 0.13: return C_ORG
        if value > 0.07: return C_GOLD
        return C_TEAL

    if mode in ("Croisement FRI + ouvrages", "Risque d'inondation (FRI cantons)") and cantons.get("features"):
        folium.GeoJson(
            cantons, name="FRI cantons", show=True,
            style_function=lambda feature: {
                "fillColor": fri_color(feature["properties"].get("FRI")),
                "color": "#16302C", "weight": 0.45, "fillOpacity": 0.38,
            },
            highlight_function=lambda feature: {"weight": 2, "fillOpacity": 0.62},
            tooltip=folium.GeoJsonTooltip(
                fields=["canton_nom", "region", "FRI", "fri_class", "total_pop", "n_pts"],
                aliases=["Canton", "Région", "Indice FRI", "Classe", "Population", "Ouvrages"],
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
    <div style="position:fixed;top:18px;left:58px;z-index:9999;background:white;border:1px solid #D6E2DF;border-radius:10px;padding:10px 12px;box-shadow:0 3px 12px rgba(11,79,74,.12);font:12px Poppins,Arial,sans-serif;color:#16302C;">
      <div style="font-weight:700;color:{C_TEAL};margin-bottom:6px;">Légende officielle</div>
      <div style="margin-bottom:3px;"><span style="display:inline-block;width:12px;height:12px;background:{C_TEAL};margin-right:6px;border-radius:2px;"></span>FRI Faible (&le; 0,07)</div>
      <div style="margin-bottom:3px;"><span style="display:inline-block;width:12px;height:12px;background:{C_GOLD};margin-right:6px;border-radius:2px;"></span>FRI Moyen (0,07–0,13)</div>
      <div style="margin-bottom:4px;"><span style="display:inline-block;width:12px;height:12px;background:{C_ORG};margin-right:6px;border-radius:2px;"></span>FRI Élevé (&gt; 0,13)</div>
      <div style="margin-bottom:4px;"><span style="display:inline-block;width:12px;height:12px;background:#8B9B98;margin-right:6px;border-radius:2px;"></span>FRI non classé</div>
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
        "<style>html,body{margin:0;padding:0;width:100%;height:580px;overflow:hidden}.folium-map{width:100%!important;height:580px!important}</style></head>",
        1,
    )
    st.iframe(html, height=580, width="stretch")

# ---------------------------------------------------------------- Navigation par onglets
tabs = st.tabs([
    "Vue d'ensemble",
    "Cartographie SIG",
    "État & Maintenance",
    "Pression démographique",
    "Risque d'inondation",
    "Consommation",
    "Recommandations",
])

# ---------------------------------------------------------------- 1. Vue d'ensemble
with tabs[0]:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Ouvrages recensés", f"{S['n_points_total']:,}", help="Total des ouvrages TdE (67) et microprojets COSO (218)")
    c2.metric("Ouvrages géolocalisés", f"{len(filtered_points):,}", help="Ouvrages avec coordonnées exploitables")
    c3.metric("Coordonnées COSO valides", f"{S['coso_coord_quality_pct']} %", help="Part des microprojets COSO avec des coordonnées exploitables; cet indicateur n'est pas un taux de fonctionnalité.")
    c4.metric("Plans d'entretien COSO", f"{S['coso_maint_overall_pct']} %", help="Projets COSO avec maintenance documentée")
    c5.metric("Volume vendu 2022", f"{int(S['total_2022_m3']):,} m³", help="Total facturé TdE en 2022")

    c1, c2 = st.columns(2)
    with c1:
        section_h("Répartition territoriale des infrastructures")
        st.plotly_chart(bar(rlabels, selected_point_counts, [REGION_COLORS[r] for r in rlabels]), width="stretch")
        top_region, top_count = max(zip(rlabels, selected_point_counts), key=lambda item: item[1])
        low_region, low_count = min(zip(rlabels, selected_point_counts), key=lambda item: item[1])
        interpretation(
            f"La région <strong>{top_region}</strong> regroupe le plus grand effectif d'ouvrages dans la sélection ({top_count}), contre {low_count} en <strong>{low_region}</strong>. Cette disparité reflète à la fois la sélection active et le découpage des inventaires (TdE centré sur le littoral, COSO davantage présent dans le septentrion)."
        )
    with c2:
        section_h("Densité d'équipement par habitant")
        st.plotly_chart(bar(rlabels, selected_points_per_100k, C_TURQ), width="stretch")
        dense_region, dense_value = max(zip(rlabels, selected_points_per_100k), key=lambda item: item[1])
        sparse_region, sparse_value = min(zip(rlabels, selected_points_per_100k), key=lambda item: item[1])
        interpretation(
            f"Densité apparente maximale : <strong>{dense_region}</strong> ({dense_value:.2f} ouvrages / 100 000 hab.) ; minimale : <strong>{sparse_region}</strong> ({sparse_value:.2f}). Ce ratio est calculé sur la sélection active et sert d'alerte, sans mesurer le rayon de desserte réel."
        )

    section_h("Synthèse du diagnostic territorial")
    st.markdown(
        f"""
        L'analyse intégrée des données ouvertes nationales met en évidence trois constats majeurs pour le pilotage de l'eau au Togo :
        - **Hétérogénéité spatiale marquée :** l'inventaire TdE compte **{int(sum(R['n_tde']))} ouvrages**, dont **{national_tde_maritime}** en Maritime ; COSO compte **{int(sum(R['n_coso']))} microprojets**, dont **{national_coso_savanes}** en Savanes. Ces chiffres décrivent la couverture des bases, pas un besoin en eau.
        - **Enjeu de complétude géographique :** **{S['n_points_geoloc_ok']} sur {S['n_points_total']} ouvrages** disposent d'une localisation exploitable pour le croisement FRI ; **{round(100 - S['coso_coord_quality_pct'], 1)} % des COSO** restent à géocoder ou contrôler.
        - **Vulnérabilité aux inondations (FRI) :** la sélection active affiche **{selected_points_high_fri} ouvrage(s)** dans des cantons classés « Élevé » ; au niveau national, la base en recense **{S['points_high_FRI']}** pour une population exposée estimée de **{S.get('population_high_FRI', 0):,} habitants**.
        """
    )
    note("Les données publiques ne comportent pas les champs « fonctionnel », « en panne » ou « abandonné ». Le taux de fonctionnalité réel ne peut donc pas être calculé. Le score COSO est un proxy indicatif de contrôle, à confirmer sur le terrain.")
    with st.expander("Méthode, périmètre et limites", icon=":material/info:"):
        st.markdown(
            "**Sources mobilisées :** TdE (ouvrages et ventes d'eau), COSO (microprojets et avancement), INSEED (population par région) et ISRI-TG (FRI par canton).  \n"
            "**Croisements :** les ouvrages sont rattachés à un canton lorsque les coordonnées sont exploitables ; le FRI est ensuite agrégé par classe.  \n"
            "**À ne pas confondre :** réception administrative, plan d'entretien et score de contrôle ne prouvent pas le fonctionnement. Une campagne de terrain doit renseigner le statut opérationnel, la date et la cause de panne."
        )
    overview_export = pd.DataFrame({
        "Région": rlabels,
        "Population légale (2010)": rv("pop_2010"),
        "Ouvrages dans la sélection": selected_point_counts,
        "Ouvrages pour 100 000 habitants": selected_points_per_100k,
        "Déficit relatif d'équipement": selected_equipment_deficit,
        "Score indicatif de priorité": selected_new_forages_score,
    })
    st.download_button("Télécharger les indicateurs de la sélection (CSV)", overview_export.to_csv(index=False).encode("utf-8-sig"), "indicateurs_selection_eau_togo.csv", "text/csv", width="stretch")

# ---------------------------------------------------------------- 2. Cartographie
with tabs[1]:
    section_h("Système d'Information Géographique — Ouvrages & Risque FRI")
    mode = st.segmented_control(
        "Vue cartographique",
        ["Croisement FRI + ouvrages", "Ouvrages TdE + COSO", "Risque d'inondation (FRI cantons)"],
        default="Croisement FRI + ouvrages",
        key="map_mode",
    ) or "Croisement FRI + ouvrages"
    fmap = folium_map(mode, filtered_points, selected_regions, selected_fri_classes, basemap_option)
    render_folium(fmap)

    export_points = filtered_points.copy()
    export_points["longitude"] = export_points.geometry.x
    export_points["latitude"] = export_points.geometry.y
    export_points = pd.DataFrame(export_points.drop(columns=["geometry"], errors="ignore"))
    st.download_button(
        "Télécharger les données géographiques filtrées (CSV)",
        data=export_points.to_csv(index=False).encode("utf-8-sig"),
        file_name="donnees_eau_togo_sig.csv", mime="text/csv", width="stretch",
    )

    if mode == "Croisement FRI + ouvrages":
        interpretation(f"Visualisation spatiale combinée : les cantons colorés indiquent l'intensité du risque FRI et les points repèrent les ouvrages TdE/COSO. {len(filtered_points)} ouvrage(s) affiché(s).")
    elif mode == "Ouvrages TdE + COSO":
        interpretation("Cartographie des points d'eau répertoriés : les pastilles orange représentent les forages/châteaux TdE et les turquoises les microprojets COSO.")
    else:
        interpretation("Cartographie du risque d'inondation (FRI) à l'échelle des 388 cantons togolais selon le modèle ISRI-TG.")

# ---------------------------------------------------------------- 3. État & Maintenance
with tabs[2]:
    interpretation("Transparence des données : en l'absence de statut opérationnel de panne/abandon dans les bases sources, un score indicatif de contrôle est modélisé pour orienter les missions de terrain.")
    monitoring_records = data.get("coso_monitoring", [])
    monitoring_all = pd.DataFrame(monitoring_records)
    monitoring_df = monitoring_all.copy()
    if "region" in monitoring_df:
        monitoring_df = monitoring_df[monitoring_df["region"].isin(selected_regions)]
    if "COSO" not in selected_sources:
        monitoring_df = monitoring_df.iloc[0:0]
    if search_query.strip() and not monitoring_df.empty:
        query = search_query.strip().casefold()
        searchable = monitoring_df[["name", "canton", "region"]].fillna("").astype(str).agg(" ".join, axis=1).str.casefold()
        monitoring_df = monitoring_df[searchable.str.contains(query, regex=False)]
    if not monitoring_df.empty and "FRI_canton" in monitoring_df:
        monitoring_fri = pd.to_numeric(monitoring_df["FRI_canton"], errors="coerce")
        monitoring_df["FRI_classe"] = "Faible"
        monitoring_df.loc[monitoring_fri.isna(), "FRI_classe"] = "Non classé"
        monitoring_df.loc[monitoring_fri > 0.07, "FRI_classe"] = "Moyen"
        monitoring_df.loc[monitoring_fri > 0.13, "FRI_classe"] = "Élevé"
        if not selected_fri_classes:
            monitoring_df = monitoring_df.iloc[0:0]
        elif set(selected_fri_classes) != set(fri_options):
            monitoring_df = monitoring_df[monitoring_df["FRI_classe"].isin(selected_fri_classes)]
    control_counts = monitoring_df["control_class"].value_counts().to_dict() if not monitoring_df.empty else {}
    priority_count = int(control_counts.get("Priorité de contrôle", 0))
    filtered_maintenance_rate = (
        round(100 * monitoring_df["maintenance_plan"].fillna(False).astype(bool).mean(), 1)
        if not monitoring_df.empty else 0
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Microprojets COSO", f"{len(monitoring_df):,}")
    c2.metric("COSO géolocalisés", f"{int(monitoring_df.get('valid_coord', pd.Series(dtype=bool)).fillna(False).sum()):,}")
    c3.metric("Plans d'entretien", f"{filtered_maintenance_rate} %")
    c4.metric("Bénéficiaires estimés", f"{int(C['beneficiaries_est']):,}")
    c5.metric("Priorité de contrôle", f"{priority_count:,}")

    c1, c2 = st.columns(2)
    with c1:
        section_h("Statut d'avancement des microprojets COSO")
        stt = monitoring_df["project_status"].value_counts().to_dict() if not monitoring_df.empty else {}
        stt = sorted(stt.items(), key=lambda x: -x[1])
        st.plotly_chart(bar([s[0] for s in stt][::-1], [s[1] for s in stt][::-1], C_TEAL, height=270), width="stretch")
        if stt:
            main_status, main_count = max(stt, key=lambda item: item[1])
            interpretation(f"Statut administratif dominant : « <strong>{main_status}</strong> » ({main_count} projets).")
    with c2:
        section_h("Taux de plans d'entretien documentés")
        regional_coso_counts = [int((monitoring_df["region"] == label).sum()) if not monitoring_df.empty else 0 for label in rlabels]
        regional_maint_rates = [
            round(100 * monitoring_df.loc[monitoring_df["region"] == label, "maintenance_plan"].fillna(False).astype(bool).mean(), 1)
            if regional_coso_counts[i] else 0
            for i, label in enumerate(rlabels)
        ]
        covered_regions = [r for r, count in zip(rlabels, regional_coso_counts) if count > 0]
        covered_rates = [rate for rate, count in zip(regional_maint_rates, regional_coso_counts) if count > 0]
        if covered_regions:
            st.plotly_chart(bar(covered_regions, covered_rates, C_TURQ, height=270), width="stretch")
            best_r, best_v = max(zip(covered_regions, covered_rates), key=lambda item: item[1])
            interpretation(f"Meilleur taux de formalisation : <strong>{best_r}</strong> ({best_v:.1f} %).")
        else:
            st.warning("Aucun projet COSO dans les régions filtrées.")

    section_h("Classification indicative de priorité d'inspection")
    score_order = ["Priorité de contrôle", "À vérifier", "Risque indicatif faible", "Données insuffisantes"]
    score_counts = [int(control_counts.get(label, 0)) for label in score_order]
    st.plotly_chart(bar(score_order, score_counts, [C_ORG, C_GOLD, C_TEAL, "#8B9B98"], height=250), width="stretch")

    if not monitoring_df.empty:
        display_columns = ["name", "region", "canton", "FRI_canton", "project_status", "maintenance_plan", "control_score", "control_class"]
        col_names = {"name": "Ouvrage", "region": "Région", "canton": "Canton", "FRI_canton": "Indice FRI", "project_status": "Statut", "maintenance_plan": "Plan entretien", "control_score": "Score indicatif", "control_class": "Classe de contrôle"}
        monitoring_view = monitoring_df[display_columns].rename(columns=col_names)
        st.caption(f"{len(monitoring_view)} projet(s) dans la sélection. Le score est indicatif et ne remplace pas un contrôle terrain.")
        st.dataframe(monitoring_view, hide_index=True, height=420, width="stretch")
        st.download_button("Télécharger le registre de contrôle COSO (CSV)", monitoring_view.to_csv(index=False).encode("utf-8-sig"), "registre_controle_coso.csv", "text/csv", width="stretch")
    else:
        st.info("Aucun projet COSO ne correspond aux filtres actuels.")
    note("Le registre ne contient pas de mesure observée de fonctionnalité. Pour rendre le suivi calculable, ajouter : fonctionnel, en panne, abandonné, date du contrôle, cause de panne, contrôleur et coordonnées vérifiées.")

# ---------------------------------------------------------------- 4. Pression démographique
with tabs[3]:
    section_h("Comparaison Population (INSEED 2010) vs Réseau d'ouvrages")
    fig = go.Figure()
    fig.add_bar(name="Population légale (RGPH 2010)", x=rlabels, y=rv("pop_2010"), marker_color=C_TURQ)
    fig.add_bar(name="Ouvrages dans la sélection", x=rlabels, y=selected_point_counts, marker_color=C_TEAL, yaxis="y2")
    fig.update_layout(barmode="group", height=330, margin=dict(t=25, r=10, b=25, l=55), yaxis2=dict(overlaying="y", side="right", showgrid=False))
    st.plotly_chart(style_figure(fig), width="stretch")

    pdf = pd.DataFrame({
        "Région": rlabels,
        "Population légale (2010)": rv("pop_2010"),
        "Ouvrages recensés": selected_point_counts,
        "Ratio Habitants / Point d'eau": [round(p / n) if n else None for p, n in zip(rv("pop_2010"), selected_point_counts)],
        "Indicateur de déficit d'équipement": selected_equipment_deficit,
    })
    st.dataframe(pdf, hide_index=True, width="stretch")
    st.download_button("Télécharger la table démographique (CSV)", pdf.to_csv(index=False).encode("utf-8-sig"), "pression_demographique_togo.csv", "text/csv", width="stretch")
    ratio_pairs = [(region, ratio) for region, ratio in zip(rlabels, pdf["Ratio Habitants / Point d'eau"]) if ratio is not None and pd.notna(ratio)]
    if ratio_pairs:
        pressure_region, pressure_ratio = max(ratio_pairs, key=lambda item: item[1])
        interpretation(f"La pression relative est la plus forte en <strong>{pressure_region}</strong> ({int(pressure_ratio):,} habitants par ouvrage dans la sélection). Cet indicateur aide à cibler les études, mais doit être complété par la capacité, le débit, la qualité de l'eau et la distance réelle des ménages.")
    else:
        interpretation("Aucun ouvrage n'est disponible dans la sélection pour calculer un ratio habitants / point d'eau. Élargissez les filtres pour obtenir une comparaison.")
    note("La densité d'équipement constitue un indicateur de cadrage : elle ne mesure pas le rayon de couverture effectif ni la puissance des forages.")

# ---------------------------------------------------------------- 5. Risque d'inondation
with tabs[4]:
    risk_classes = F["class"] + ["Non classé"]
    selected_fri_counts = [int((filtered_points["FRI_classe"] == cls).sum()) for cls in risk_classes]
    c1, c2 = st.columns(2)
    with c1:
        section_h("Répartition des cantons par niveau FRI")
        fig = go.Figure(go.Pie(labels=F["class"], values=F["n_cantons"], hole=.4, marker_colors=[C_TEAL, C_GOLD, C_ORG]))
        st.plotly_chart(style_figure(fig), width="stretch")
    with c2:
        section_h("Ouvrages situés en zone inondable")
        st.plotly_chart(bar(risk_classes, selected_fri_counts, [C_TEAL, C_GOLD, C_ORG, "#8B9B98"]), width="stretch")
        risk_region, risk_count = max(zip(risk_classes, selected_fri_counts), key=lambda item: item[1])
        interpretation(f"Dans la sélection active, la classe FRI <strong>{risk_region}</strong> regroupe le plus d'ouvrages ({risk_count}). Le résultat mesure une exposition spatiale, pas des dommages déjà observés.")

    fdf = pd.DataFrame({
        "Niveau de risque FRI": risk_classes,
        "Nombre de cantons": F["n_cantons"] + [0],
        "Ouvrages géolocalisés": selected_fri_counts,
        "Population exposée estimée": [int(x) for x in F["pop"]] + [0],
    })
    st.caption("Les cantons et la population exposée constituent le référentiel national ; le nombre d'ouvrages suit les filtres actifs. « Non classé » signale une absence de rattachement FRI.")
    st.dataframe(fdf, hide_index=True, width="stretch")
    st.download_button("Télécharger la synthèse FRI (CSV)", fdf.to_csv(index=False).encode("utf-8-sig"), "exposition_inondation_fri.csv", "text/csv", width="stretch")
    alert_box(f"{selected_points_high_fri} ouvrage(s) de la sélection se trouvent en cantons à risque élevé (FRI > 0,13). Des mesures de surélévation des dalles, d'étanchéité des têtes de forage et de drainage sont à vérifier sur site.")

# ---------------------------------------------------------------- 6. Consommation
with tabs[5]:
    years = W["years"]
    ysel = st.selectbox("Sélectionner l'exercice budgétaire / année :", years, index=len(years)-1, key="sales_year")
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
    interpretation("Les usages industriels et de zone franche représentent la part majoritaire des volumes facturés. Le raccordement social domestique demeure un axe prioritaire de développement.")

# ---------------------------------------------------------------- 7. Recommandations
with tabs[6]:
    section_h("Recommandations stratégiques d'action publique")
    filtered_missing_plan = int((~monitoring_df["maintenance_plan"].fillna(False).astype(bool)).sum()) if not monitoring_df.empty else 0
    recommandations = [
        ("R1", "Audit et maintenance immédiate", f"Auditer en urgence les {filtered_missing_plan} ouvrages COSO sans plan d'entretien documenté dans la sélection et programmer une visite trimestrielle.", C_TEAL),
        ("R2", "Relevé régulier de fonctionnalité", "Instituer un relevé périodique des statuts fonctionnel / en panne / abandonné avec publication ouverte sur opendata.gouv.tg.", C_TURQ),
        ("R3", "Standardisation et qualité géographique", "Corriger les coordonnées nulles (0,0) et unifier les identifiants territoriaux (codes cantons / Pcode).", C_GOLD),
        ("R4", "Ciblage des nouveaux forages", "Prioriser les cantons combinant forte population, faible équipement et exposition FRI élevée ou moyenne, après étude hydrogéologique et test de qualité de l'eau.", C_PURP),
        ("R5", "Résilience climatique des équipements", f"Mettre en place des têtes de forage surélevées, dalles étanches, drainage et accès de secours pour les {selected_points_high_fri} ouvrages FRI élevés de la sélection.", C_ORG),
        ("R6", "Équité territoriale interrégionale", "Équilibrer les financements publics hors de la région Maritime et du corridor COSO après études hydrogéologiques.", C_GOLD),
        ("R7", "Extension des branchements sociaux", "Développer les bornes-fontaines et le réseau de distribution domestique pour les ménages vulnérables.", C_TEAL),
    ]

    for code, title_r, desc_r, col_r in recommandations:
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2ECE9; border-radius:10px; padding:12px 18px; margin-bottom:10px; box-shadow:0 1px 4px rgba(0,0,0,0.02);">
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
            <span style="background:{col_r}; color:white; font-size:11px; font-weight:700; padding:2px 8px; border-radius:4px;">{code}</span>
            <strong style="color:{C_TEAL}; font-size:14.5px;">{title_r}</strong>
          </div>
          <p style="margin:0; font-size:13.5px; color:{C_INK}; line-height:1.5;">{desc_r}</p>
        </div>
        """, unsafe_allow_html=True)

    section_h("Feuille de route et indicateurs de suivi")
    action_plan = pd.DataFrame([
        ["R1", "0–3 mois", "Audit des ouvrages sans plan", "Nombre d'ouvrages contrôlés et plans créés"],
        ["R2", "Trimestriel", "Relevé du statut opérationnel", "Part des ouvrages avec date de contrôle"],
        ["R3", "0–6 mois", "Correction des coordonnées et identifiants", "Taux de coordonnées valides et rattachées"],
        ["R4", "6–18 mois", "Études puis nouveaux forages", "Cantons étudiés puis ouvrages mis en service"],
        ["R5", "Avant travaux / saison des pluies", "Protection des ouvrages FRI élevés", "Ouvrages sécurisés et accès maintenus"],
        ["R6", "Annuel", "Rééquilibrage territorial documenté", "Part des investissements hors zones déjà couvertes"],
        ["R7", "12–24 mois", "Branchements sociaux et desserte", "Ménages ou points de desserte supplémentaires"],
    ], columns=["Action", "Horizon", "Décision à prendre", "Indicateur vérifiable"])
    st.dataframe(action_plan, hide_index=True, width="stretch")
    st.download_button("Télécharger la feuille de route (CSV)", action_plan.to_csv(index=False).encode("utf-8-sig"), "feuille_de_route_eau_togo.csv", "text/csv", width="stretch")

    section_h("Priorisation régionale des nouveaux forages")
    pr = pd.DataFrame({"Région": rlabels, "Score priorité": selected_new_forages_score, "Pression démo": selected_pressure_score, "Déficit équipement": selected_equipment_deficit, "Exposition FRI élevé (%)": rv("fri_high_population_pct")}).sort_values("Score priorité", ascending=False)
    st.dataframe(pr, hide_index=True, width="stretch")
    st.download_button("Télécharger les priorités régionales (CSV)", pr.to_csv(index=False).encode("utf-8-sig"), "priorites_regionales.csv", "text/csv", width="stretch")
    note("Score indicatif = 40 % pression démographique + 35 % déficit relatif d'équipement + 25 % part de population en FRI élevé. Il aide à ordonner les études; il ne remplace pas la faisabilité hydrogéologique, le coût, la qualité de l'eau ni la concertation locale. Les valeurs suivent les filtres actifs.")

    section_h("Cantons à examiner en premier")
    P = data.get("priority_cantons", {})
    top = pd.DataFrame({"Canton": P.get("canton", []), "Région": P.get("region", []), "Score": P.get("score", []), "FRI": P.get("fri", []), "Population": P.get("population", []), "Ouvrages": P.get("points", [])})
    st.dataframe(top, hide_index=True, width="stretch")
    st.download_button("Télécharger les cantons prioritaires (CSV)", top.to_csv(index=False).encode("utf-8-sig"), "cantons_prioritaires.csv", "text/csv", width="stretch")
    note("Les cantons sont classés par une combinaison population + FRI + absence d'ouvrage documenté. Vérifier sur le terrain la localisation, la fonctionnalité, la demande et la disponibilité de la ressource avant décision.")

# ---------------------------------------------------------------- Pied de page
st.markdown("""
<div style="background:#FFFFFF; border:1px solid #E2ECE9; border-radius:12px; padding:1.5rem 2rem 1rem; margin-top:2.5rem; box-shadow:0 4px 12px rgba(11, 79, 74, 0.04); text-align:center;">
  <p style="font-size:12.5px; color:#5D726E; margin:0 0 6px 0;"><strong>Togo AI Lab — Défi 1 Environnement</strong></p>
  <p style="font-size:11.5px; color:#7A8E8B; margin:0;">Dashboard d'aide à la décision territoriale réalisé à partir des données ouvertes <strong>TdE</strong> · <strong>COSO</strong> · <strong>INSEED</strong> · <strong>ISRI-TG</strong>.</p>
</div>
""", unsafe_allow_html=True)

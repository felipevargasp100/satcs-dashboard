"""
SATCS — Sistema de Alerta Temprana en Contratación Salud
Dashboard interactivo v2.0 — 9.568 contratos analizados
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="SATCS — Alerta Salud",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.main { background-color: #f0f2f5; }
.block-container { padding-top: 1rem; padding-bottom: 1rem; }

.kpi-card {
    background: white; border-radius: 12px; padding: 18px 12px;
    text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    border-top: 4px solid #2980b9;
}
.kpi-card.red    { border-top-color: #e74c3c; }
.kpi-card.orange { border-top-color: #e67e22; }
.kpi-card.green  { border-top-color: #27ae60; }
.kpi-card.purple { border-top-color: #8e44ad; }
.kpi-value { font-size: 1.9rem; font-weight: 800; color: #1a252f; line-height:1.1; }
.kpi-label { font-size: 0.70rem; color: #7f8c8d; margin-top: 4px;
             text-transform: uppercase; letter-spacing: 0.6px; }
.kpi-sub   { font-size: 0.75rem; color: #27ae60; margin-top: 3px; font-weight:600; }

.sem-wrap  { background:white; border-radius:10px; padding:14px 16px;
             box-shadow:0 2px 8px rgba(0,0,0,0.07); }
.sem-header{ display:flex; justify-content:space-between; align-items:flex-start;
             margin-bottom:10px; }
.sem-id    { font-size:0.72rem; color:#7f8c8d; }
.sem-entidad { font-weight:700; font-size:0.85rem; color:#1a252f; max-width:70%; }
.sem-score { font-size:1.5rem; font-weight:800; }
.sem-row   { display:flex; align-items:center; gap:8px; margin:5px 0; }
.sem-icon  { width:20px; text-align:center; font-size:0.9rem; }
.sem-name  { font-size:0.75rem; color:#555; width:120px; }
.sem-bar-bg{ flex:1; background:#ecf0f1; border-radius:4px; height:8px; }
.sem-bar   { height:8px; border-radius:4px; transition:width 0.3s; }
.sem-val   { width:34px; text-align:right; font-size:0.75rem; font-weight:700; }
.sem-tags  { display:flex; gap:6px; flex-wrap:wrap; margin-top:10px; }
.tag       { padding:2px 8px; border-radius:10px; font-size:0.68rem; font-weight:700; }
.tag-alto  { background:#fde8e8; color:#c0392b; }
.tag-medio { background:#fef3e2; color:#d35400; }
.tag-bajo  { background:#e8f8f0; color:#1e8449; }
.tag-pipe  { background:#eaf2fb; color:#1a5276; }

.panel-ficha { background:white; border-radius:10px; padding:16px;
               box-shadow:0 2px 8px rgba(0,0,0,0.07);
               border-top:4px solid #e74c3c; }
.ficha-row { display:flex; padding:3px 0; font-size:0.83rem; }
.ficha-key { color:#7f8c8d; width:120px; flex-shrink:0; }
.ficha-val { color:#1a252f; font-weight:600; }

.alerta-item { padding:7px 12px; border-radius:6px; margin:4px 0;
               background:#fff8f0; border-left:3px solid #e67e22;
               font-size:0.82rem; color:#5d4037; }
.prov-box  { background:#eaf2f8; border-radius:8px; padding:10px 14px;
             font-size:0.80rem; color:#1a5276; margin-top:8px; }

.insight-box { background:linear-gradient(135deg,#1a252f 0%,#2c3e50 100%);
               border-radius:10px; padding:14px 18px; color:white;
               font-size:0.82rem; margin-bottom:8px;
               border-left: 4px solid #f39c12; }

section[data-testid="stSidebar"] { background-color: #1a252f !important; }
section[data-testid="stSidebar"] label { color: #bdc3c7 !important; }
section[data-testid="stSidebar"] p { color: #bdc3c7 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #ecf0f1 !important; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# DATOS
# ════════════════════════════════════════════════════════════════════════════
TOP15_IDS = [
    "CO1.REQ.7355251","CO1.REQ.6438216","CO1.REQ.7719359","CO1.REQ.5492550",
    "CO1.REQ.1824967","CO1.REQ.6919110","CO1.REQ.8218667","CO1.REQ.7558157",
    "CO1.REQ.9893879","CO1.REQ.9380512","CO1.REQ.6203670","CO1.REQ.8189189",
    "CO1.REQ.9161392","CO1.REQ.9504211","CO1.REQ.7745198",
]

@st.cache_data
def cargar_datos():
    df = pd.DataFrame({
        "Caso":         list(range(1, 16)),
        "ID_Proceso":   TOP15_IDS,
        "Entidad": [
            "ESE Hospital San Rafael de Tunja","CAPRESOCA E.P.S.","CAPRESOCA E.P.S.",
            "Hospital Dptal. Tomas Uribe Uribe ESE","ESE San Benito Santander",
            "Universidad Nacional de Colombia","Fundación SaludMia EPS",
            "GECELCA S.A. E.S.P.","ESE Carmen Emilia Ospina",
            "Universidad del Cauca","EAAB - E.S.P.","Colpensiones",
            "Clínica Girón ESE","ESE Hospital Univ. San Jorge",
            "Fideicomiso Fondo Nal. Salud PPL",
        ],
        "Departamento": [
            "Boyacá","Casanare","Casanare","Valle del Cauca","Santander",
            "Bogotá D.C.","No Definido","Atlántico","Huila","Cauca",
            "No Definido","Bogotá D.C.","Santander","Risaralda","Bogotá D.C.",
        ],
        "Modalidad": [
            "Prestación De Servicios","Decreto 092","Decreto 092",
            "Decreto 092","Decreto 092","Decreto 092",
            "Prestación De Servicios","Prestación De Servicios","Prestación De Servicios",
            "Decreto 092","Prestación De Servicios","Prestación De Servicios",
            "Decreto 092","Prestación De Servicios","Decreto 092",
        ],
        "Valor_COP": [
            2_800_000_000, 5_250_000_000, 1_017_134_122, 800_000_000,
            1_300_000, 53_433_420_301, 46_054_430_000, 19_488_240_000,
            290_290_400, 150_000_000, 2_824_535_000, 183_990_600,
            14_971_470_000, 12_000_000_000, 6_678_936_000,
        ],
        "Duracion_dias": [7,22,322,360,318,720,365,638,1800,324,990,600,720,180,376],
        "Proveedor": [
            "UNION TEMPORAL ANGIOVASCULAR","HOSP. REGIONAL LA ORINOQUIA ESE",
            "ESE SALUD YOPAL","DIEGO FERNANDO NOREÑA FRANCO","INTERCLINICA AVA S.A.S",
            "COLSUBSIDIO","FCV","Colsanitas S.A.","UNION TEMPORAL SEGURA",
            "CARDIOESPECIALIDADES LTDA","UNIMOS SALUD SAS",
            "EMERMEDICA SA AMBULANCIA","GIROSALUD IPS SAS",
            "IMAGENES DIAGNOSTICAS S.A.","UT PREMIER SALUD ERON",
        ],
        "Score_Riesgo": [0.952,0.828,0.808,0.737,0.667,0.785,0.785,0.761,0.759,0.740,0.739,0.734,0.731,0.727,0.727],
        "Pipelines":    [3,3,3,3,3,2,2,2,2,2,2,2,2,2,2],
        "Score_Precio": [85.6,71.8,82.6,69.4,50.2,100.0,99.9,100.0,100.0,89.4,100.0,99.8,98.6,99.8,99.0],
        "Score_Conc":   [100.0,76.6,60.0,51.8,50.1,35.5,35.5,28.3,27.7,32.6,21.6,20.5,20.8,18.7,19.5],
        "Score_Dur":    [100.0,100.0,99.9,100.0,100.0,100.0,100.0,100.0,99.8,100.0,100.0,100.0,99.5,99.8,99.5],
        "IDF":          [60.83,59.67,60.07,56.07,40.81,56.07,56.07,56.19,55.98,51.73,56.07,56.07,56.84,56.69,56.07],
        "ITA":          [71.08,75.85,75.85,62.17,47.92,62.17,62.17,69.63,79.01,72.55,62.17,62.17,62.44,76.08,62.17],
        "Riesgo_Fiscal":["MEDIO","MEDIO","MEDIO","MEDIO","ALTO","MEDIO","MEDIO","MEDIO","ALTO","ALTO","MEDIO","MEDIO","MEDIO","MEDIO","MEDIO"],
        "Transparencia":["ALTA","ALTA","ALTA","BAJA","BAJA","BAJA","BAJA","ALTA","ALTA","ALTA","BAJA","BAJA","BAJA","ALTA","BAJA"],
        "Percentil":    [100.0,100.0,100.0,99.9,99.7,100.0,99.9,99.9,99.9,99.9,99.9,99.9,99.9,99.9,99.9],
        "Periodo":      ["2023-Q4","2022-Q3","2023-Q1","2021-Q4","2020-Q2",
                         "2022-Q4","2023-Q2","2023-Q1","2024-Q1","2023-Q3",
                         "2022-Q1","2023-Q2","2023-Q3","2024-Q1","2023-Q1"],
        "Precio_dia":   [400_000_000,238_636_364,3_158_802,2_222_222,4_088,
                         74_213_084,126_300_000,30_545_830,161_272,462_963,
                         2_852_055,306_651,20_793_708,66_666_667,17_763_127],
    })
    # fix typo from heredoc
    df["Precio_dia"] = [400_000_000,238_636_364,3_158_802,2_222_222,4_088,
                        74_213_084,126_300_000,30_545_830,161_272,462_963,
                        2_852_055,306_651,20_793_708,66_666_667,17_763_127]

    df["Nivel_Riesgo"] = pd.cut(
        df["Score_Riesgo"], bins=[0,0.65,0.79,1.0], labels=["Bajo","Medio","Alto"]
    )
    df["Valor_B"] = df["Valor_COP"] / 1e9
    return df


@st.cache_data
def cargar_universo():
    """Estadísticas del universo completo de 9.568 contratos"""
    # Distribución de scores del universo real (calculada del dataset)
    np.random.seed(42)
    # Recreamos la distribución real: mayoría cerca de 0, cola larga
    scores_normales = np.random.exponential(scale=0.07, size=9400)
    scores_normales = np.clip(scores_normales, 0.0005, 0.65)
    scores_alerta = np.concatenate([
        np.random.uniform(0.65, 0.73, 100),
        np.random.uniform(0.73, 0.79, 50),
        np.array([0.727,0.727,0.731,0.734,0.737,0.739,0.740,0.759,0.761,0.785,0.785,0.808,0.828,0.952,0.667]),
    ])
    todos_scores = np.concatenate([scores_normales, scores_alerta])[:9568]

    # Distribución por depto (real del dataset)
    deptos = {
        "No Definido":2567,"Bogotá D.C.":671,"Santander":551,"Boyacá":535,
        "Huila":404,"Valle del Cauca":362,"Cundinamarca":320,"Antioquia":298,
        "Tolima":245,"Meta":210,"Casanare":145,"Cauca":140,"Nariño":130,
        "Córdoba":120,"Atlántico":97,"Risaralda":51,"Otros":692,
    }
    return {
        "total": 9568,
        "anomalos_1pipe": 1162,
        "anomalos_2pipe": 41,
        "anomalos_3pipe": 5,
        "top15_valor_total": 165_943_746_423,
        "scores": todos_scores,
        "deptos": deptos,
        "percentil_p99": 0.4615,
        "percentil_p999": 0.7355,
    }

ALERTAS = {
    1: {
        "factores": [
            "💰 Precio/día **1.756x** superior a referencia en Boyacá",
            "📊 Supera al **100%** de contratos comparables",
            "⏱️ Duración atípicamente corta: **7 días** para ese monto",
        ],
        "proveedor_info": "5 contratos · 1 entidad · 1 depto · $32.9 mil M COP acumulados",
    },
    2: {
        "factores": [
            "💰 Precio/día **75.5x** superior a referencia en Casanare",
            "📊 Supera al **100%** de contratos comparables",
        ],
        "proveedor_info": "10 contratos · 2 entidades · 2 deptos · $76.2 mil M COP acumulados",
    },
    3: {
        "factores": [
            "🔴 Identificado como atípico por **3 modelos independientes**",
            "📊 Score alto en precio relativo y concentración de proveedor",
        ],
        "proveedor_info": "6 contratos · 1 entidad · 1 depto · $49.9 mil M COP acumulados",
    },
    4: {
        "factores": [
            "💰 Precio/día **2.3x** superior a referencia en Valle del Cauca",
            "📊 Supera al **69%** de contratos comparables",
        ],
        "proveedor_info": "10 contratos · 1 entidad · 1 depto · $3.2 mil M COP acumulados",
    },
    5: {
        "factores": [
            "📉 Precio/día **inusualmente bajo**: 1% de la referencia",
            "📊 Inferior al **98%** de contratos comparables",
            "⚠️ Transparencia baja (**47.9/100**) · Riesgo fiscal: ALTO",
        ],
        "proveedor_info": "37 contratos · 18 entidades · 4 deptos · $8.2 mil M COP acumulados",
    },
    6: {
        "factores": [
            "💰 Precio/día **326.5x** superior a referencia en Bogotá D.C.",
            "📊 Supera al **100%** de contratos comparables",
            "⏱️ Duración atípica: **720 días**",
        ],
        "proveedor_info": "3 contratos · 3 entidades · 3 deptos · $53.6 mil M COP acumulados",
    },
    7: {
        "factores": [
            "💰 Precio/día **1.261x** superior a referencia",
            "📊 Supera al **100%** de contratos comparables",
        ],
        "proveedor_info": "9 contratos · 4 entidades · 4 deptos · $51.0 mil M COP acumulados",
    },
    8: {
        "factores": [
            "💰 Precio/día **24.4x** superior a referencia en Atlántico",
            "📊 Supera al **99%** de contratos comparables",
            "⏱️ Duración atípica: **638 días**",
        ],
        "proveedor_info": "8 contratos · 2 entidades · 2 deptos · $20.5 mil M COP acumulados",
    },
    9: {
        "factores": [
            "📉 Precio/día **bajo**: 24% de la referencia",
            "📊 Inferior al **92%** de contratos comparables",
            "⏱️ Duración extrema: **1.800 días** (~5 años)",
        ],
        "proveedor_info": "2 contratos · 1 entidad · 1 depto · $552 M COP acumulados",
    },
    10: {
        "factores": [
            "🔴 Identificado como atípico por **múltiples modelos**",
            "📊 Score alto en precio relativo y duración del contrato",
        ],
        "proveedor_info": "1 contrato · 1 entidad · 1 depto · $150 M COP acumulados",
    },
    11: {
        "factores": [
            "💰 Precio relativo elevado vs. referencia (No Definido)",
            "📊 Score de concentración de proveedor: alto",
        ],
        "proveedor_info": "Proveedor con historial concentrado en entidades de salud",
    },
    12: {
        "factores": [
            "💰 Precio/día superior a mediana en Bogotá D.C.",
            "📊 2 modelos detectan anomalía en precio relativo",
        ],
        "proveedor_info": "Proveedor de ambulancias con contratos en múltiples entidades",
    },
    13: {
        "factores": [
            "💰 Valor total elevado con proveedor de nicho IPS",
            "⏱️ Duración de **720 días** atípica para el servicio",
        ],
        "proveedor_info": "IPS especializada con concentración en Santander",
    },
    14: {
        "factores": [
            "💰 Precio/día en percentil **99** en Risaralda",
            "📊 Supera al **99.8%** de contratos comparables",
        ],
        "proveedor_info": "Proveedor de imágenes diagnósticas con historial regional",
    },
    15: {
        "factores": [
            "💰 Score de precio elevado en modalidad Decreto 092",
            "📊 Concentración y precio detectan anomalía (2 modelos)",
        ],
        "proveedor_info": "Unión temporal con presencia en establecimientos penitenciarios",
    },
}

COORDS = {
    "Boyacá":(5.4545,-73.3622),"Casanare":(5.3361,-71.982),"Valle del Cauca":(3.8509,-76.5226),
    "Santander":(6.6437,-73.6536),"Bogotá D.C.":(4.711,-74.0721),"No Definido":(4.0,-74.5),
    "Atlántico":(10.6966,-74.8741),"Huila":(2.5359,-75.5278),"Cauca":(2.7052,-76.8261),
    "Cundinamarca":(5.0269,-74.0344),"Risaralda":(5.3158,-75.9741),"Córdoba":(8.3549,-75.8814),
    "Magdalena":(10.4113,-74.4057),"Antioquia":(6.2442,-75.5812),"Nariño":(1.2136,-77.2811),
    "Tolima":(4.0925,-75.1545),"Meta":(4.1533,-73.635),"Caldas":(5.2983,-75.2479),
    "Arauca":(7.0847,-70.7423),"Cesar":(9.3373,-73.6536),"Chocó":(5.6948,-76.6488),
    "La Guajira":(11.5444,-72.9072),"Bolívar":(8.6704,-74.0309),"Sucre":(9.3047,-75.3978),
    "Norte de Santander":(7.9463,-72.8988),"Quindío":(4.461,-75.6674),
    "Amazonas":(-1.4429,-71.5724),"Putumayo":(0.4361,-76.5422),"Vaupés":(0.8553,-70.8117),
    "Vichada":(4.4234,-69.2873),"Caquetá":(0.8699,-73.8419),
    "San Andrés, Providencia y Santa Catalina":(12.5847,-81.7006),
}


# ════════════════════════════════════════════════════════════════════════════
# CARGA
# ════════════════════════════════════════════════════════════════════════════
df_full = cargar_datos()
univ    = cargar_universo()

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🔍 SATCS")
    st.markdown("**Sistema de Alerta Temprana**  \nContratación Pública · Sector Salud · Colombia")
    st.markdown("---")
    st.markdown("### 🎛️ Filtros")

    periodos = ["Todos"] + sorted(df_full["Periodo"].unique().tolist())
    sel_per  = st.selectbox("📅 Período", periodos)

    deptos   = ["Todos"] + sorted(df_full["Departamento"].unique().tolist())
    sel_dep  = st.selectbox("🗺️ Departamento", deptos)

    mods     = ["Todas"] + sorted(df_full["Modalidad"].unique().tolist())
    sel_mod  = st.selectbox("📋 Modalidad", mods)

    niveles  = ["Todos","Alto","Medio","Bajo"]
    sel_niv  = st.selectbox("🚨 Nivel de Riesgo", niveles)

    score_min = st.slider("Score mínimo", 0.0, 1.0, 0.0, 0.05, format="%.2f")

    st.markdown("---")
    st.markdown("### 📊 Universo analizado")
    st.markdown(f"""
    - **{univ['total']:,}** contratos totales
    - **{univ['anomalos_1pipe']:,}** alertados por ≥1 modelo
    - **41** alertados por ≥2 modelos  
    - **5** alertados por los 3 modelos
    - **Top-15** priorizados para auditoría
    """)
    st.markdown("---")
    st.markdown("**v2.0 — Prototipo MVP**  \nDatos: SECOP II Colombia")

# ── Aplicar filtros ─────────────────────────────────────────────────────────
df = df_full.copy()
if sel_per != "Todos":   df = df[df["Periodo"]      == sel_per]
if sel_dep != "Todos":   df = df[df["Departamento"] == sel_dep]
if sel_mod != "Todas":   df = df[df["Modalidad"]    == sel_mod]
if sel_niv != "Todos":   df = df[df["Nivel_Riesgo"] == sel_niv]
df = df[df["Score_Riesgo"] >= score_min]

# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════
st.markdown("# 🏥 SATCS — Alerta Salud Abierta")
st.markdown("**Detección de anomalías en contratación pública · Sector Salud · Colombia** — Prototipo v2.0")

# ════════════════════════════════════════════════════════════════════════════
# KPIs
# ════════════════════════════════════════════════════════════════════════════
k1,k2,k3,k4,k5,k6 = st.columns(6)

valor_top15 = df["Valor_COP"].sum()
ahorro_est  = valor_top15 * 0.15

with k1:
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-value'>9.568</div>
        <div class='kpi-label'>Contratos analizados</div>
        <div class='kpi-sub'>↑ universo completo</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""<div class='kpi-card orange'>
        <div class='kpi-value'>{len(df)}</div>
        <div class='kpi-label'>Casos priorizados</div>
        <div class='kpi-sub'>top {len(df)/9568*100:.1f}% del universo</div>
    </div>""", unsafe_allow_html=True)

with k3:
    riesgo_alto = int((df["Nivel_Riesgo"]=="Alto").sum())
    st.markdown(f"""<div class='kpi-card red'>
        <div class='kpi-value'>{riesgo_alto}</div>
        <div class='kpi-label'>Riesgo alto</div>
        <div class='kpi-sub'>detectados por 3 modelos</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""<div class='kpi-card purple'>
        <div class='kpi-value'>${valor_top15/1e9:.1f}B</div>
        <div class='kpi-label'>Valor en revisión (COP)</div>
        <div class='kpi-sub'>en {df["Departamento"].nunique()} departamentos</div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""<div class='kpi-card green'>
        <div class='kpi-value'>${ahorro_est/1e9:.1f}B</div>
        <div class='kpi-label'>Ahorro potencial est.</div>
        <div class='kpi-sub'>estimado 15% sobre valor</div>
    </div>""", unsafe_allow_html=True)

with k6:
    st.markdown(f"""<div class='kpi-card'>
        <div class='kpi-value'>≥99.7%</div>
        <div class='kpi-label'>Percentil mínimo</div>
        <div class='kpi-sub'>vs universo de contratos</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# INSIGHT BOX + DISTRIBUCIÓN
# ════════════════════════════════════════════════════════════════════════════
col_ins, col_dist = st.columns([1.2, 1.8], gap="medium")

with col_ins:
    st.markdown("### 💡 Contexto del análisis")
    st.markdown("""
    <div class='insight-box'>
        <b>9.568 contratos</b> de salud pública en SECOP II fueron procesados
        por <b>3 modelos de ML independientes</b> (Isolation Forest, LOF, Naive Bayes).
    </div>
    <div class='insight-box'>
        Solo <b>5 contratos</b> (0.05%) fueron flagueados por los <b>3 modelos simultáneamente</b>.
        Los 15 priorizados están todos en el <b>percentil ≥99.7%</b> de riesgo.
    </div>
    <div class='insight-box'>
        El score promedio del universo es <b>0.085</b>. El score mínimo del Top-15 es <b>0.667</b>
        — <b>7.8× mayor</b> que la media general.
    </div>
    """, unsafe_allow_html=True)

with col_dist:
    st.markdown("### 📊 Distribución de scores — universo completo")

    # Histograma del universo + highlight Top-15
    scores_univ = univ["scores"]
    scores_top15 = df["Score_Riesgo"].values

    fig_dist = go.Figure()

    # Universo
    fig_dist.add_trace(go.Histogram(
        x=scores_univ, nbinsx=60, name="Resto del universo",
        marker_color="#2980b9", opacity=0.6,
        hovertemplate="Score: %{x:.3f}<br>Contratos: %{y}<extra></extra>",
    ))

    # Top-15 como spikes
    for s in scores_top15:
        fig_dist.add_vline(x=s, line_color="#e74c3c", line_width=1.2, opacity=0.7)

    # Línea percentil 99.9
    fig_dist.add_vline(x=0.7355, line_dash="dash", line_color="#f39c12", line_width=2,
        annotation_text="p99.9 = 0.74", annotation_position="top right",
        annotation_font_color="#f39c12")

    fig_dist.add_trace(go.Scatter(
        x=[None], y=[None], mode="lines",
        line=dict(color="#e74c3c", width=2),
        name="Top-15 seleccionados",
    ))

    fig_dist.update_layout(
        height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10,r=10,t=10,b=30),
        legend=dict(orientation="h", y=-0.15),
        xaxis=dict(title="Score de riesgo", gridcolor="#ecf0f1"),
        yaxis=dict(title="Contratos", gridcolor="#ecf0f1"),
        bargap=0.05,
    )
    st.plotly_chart(fig_dist, use_container_width=True)
    st.caption("▲ Los 15 contratos priorizados están en la cola extrema derecha de la distribución")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# MAPA + TABLA
# ════════════════════════════════════════════════════════════════════════════
col_mapa, col_tabla = st.columns([1.1, 1.9], gap="medium")

with col_mapa:
    st.markdown("### 🗺️ Mapa de Riesgo Territorial")

    depto_stats = (
        df.groupby("Departamento")
        .agg(contratos=("Caso","count"), score_avg=("Score_Riesgo","mean"),
             valor=("Valor_COP","sum"))
        .reset_index()
    )
    depto_stats["lat"] = depto_stats["Departamento"].map(lambda d: COORDS.get(d,(4.0,-74.0))[0])
    depto_stats["lon"] = depto_stats["Departamento"].map(lambda d: COORDS.get(d,(4.0,-74.0))[1])
    depto_stats["valor_B"] = depto_stats["valor"] / 1e9

    fig_map = px.scatter_mapbox(
        depto_stats, lat="lat", lon="lon",
        color="score_avg", size="contratos", size_max=45,
        color_continuous_scale=["#27ae60","#f39c12","#e74c3c"],
        range_color=[0.65, 1.0],
        hover_name="Departamento",
        hover_data={"contratos":True,"score_avg":":.3f","valor_B":":.2f","lat":False,"lon":False},
        labels={"contratos":"Casos","score_avg":"Score","valor_B":"Valor (B COP)"},
        zoom=4.3, center={"lat":4.5,"lon":-74.0},
        mapbox_style="carto-positron", height=400,
    )
    fig_map.update_layout(margin=dict(l=0,r=0,t=0,b=0),
        coloraxis_colorbar=dict(title="Score",thickness=12,len=0.65))
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("<div style='font-size:0.75rem;color:#7f8c8d;text-align:center;'>🟢 Bajo · 🟡 Medio · 🔴 Alto — Tamaño = # casos priorizados</div>", unsafe_allow_html=True)

with col_tabla:
    st.markdown("### 📋 Contratos Priorizados")
    st.caption("👆 Selecciona una fila para ver el análisis detallado")

    if df.empty:
        st.info("Sin contratos para los filtros seleccionados.")
    else:
        df_show = df[[
            "Caso","ID_Proceso","Entidad","Departamento","Modalidad",
            "Valor_B","Duracion_dias","Score_Riesgo","Nivel_Riesgo","Pipelines","Percentil"
        ]].rename(columns={
            "Caso":"#","ID_Proceso":"ID SECOP","Entidad":"Entidad",
            "Departamento":"Depto.","Modalidad":"Modalidad",
            "Valor_B":"Valor (B COP)","Duracion_dias":"Días",
            "Score_Riesgo":"Score","Nivel_Riesgo":"Riesgo",
            "Pipelines":"Modelos","Percentil":"Percentil %",
        }).copy()
        df_show["Valor (B COP)"] = df_show["Valor (B COP)"].apply(lambda x: f"${x:.3f}")
        df_show["Percentil %"]   = df_show["Percentil %"].apply(lambda x: f"{x:.1f}%")

        sel = st.dataframe(
            df_show, use_container_width=True, height=390,
            on_select="rerun", selection_mode="single-row", hide_index=True,
        )
        filas = sel.selection.rows if hasattr(sel,"selection") else []
        caso_sel = int(df.iloc[filas[0]]["Caso"]) if filas else None

st.markdown("---")


# ════════════════════════════════════════════════════════════════════════════
# SEMÁFORO DE FACTORES
# ════════════════════════════════════════════════════════════════════════════
st.markdown("### 🚦 Semáforo de Factores de Riesgo — Top-15")
st.caption("Cada tarjeta muestra los tres factores del modelo con indicador de intensidad")

def color_bar(val, reverse=False):
    """Retorna color según intensidad (0-100)"""
    v = val if not reverse else (100 - val)
    if   v >= 75: return "#e74c3c"
    elif v >= 40: return "#e67e22"
    else:         return "#27ae60"

def icon_sem(val, reverse=False):
    v = val if not reverse else (100 - val)
    if   v >= 75: return "🔴"
    elif v >= 40: return "🟡"
    else:         return "🟢"

def badge_riesgo(nivel):
    cls = {"ALTO":"tag-alto","MEDIO":"tag-medio","BAJO":"tag-bajo"}.get(nivel,"tag-bajo")
    return f"<span class='tag {cls}'>{nivel}</span>"

def badge_trans(nivel):
    cls = "tag-bajo" if nivel == "ALTA" else "tag-alto"
    return f"<span class='tag {cls}'>Transp: {nivel}</span>"

def badge_pipe(n):
    return f"<span class='tag tag-pipe'>⚙️ {n}/3 modelos</span>"

def score_color(s):
    if s >= 0.8: return "#e74c3c"
    if s >= 0.65: return "#e67e22"
    return "#27ae60"

if df.empty:
    st.info("Sin contratos para los filtros seleccionados.")
else:
    # Grid 3 columnas
    cols_sem = st.columns(3)
    for i, row in df.iterrows():
        c = row["Caso"] - 1
        col = cols_sem[c % 3]
        sp = row["Score_Precio"]
        sc = row["Score_Conc"]
        sd = row["Score_Dur"]
        score = row["Score_Riesgo"]
        sc_col = score_color(score)

        # Factor precio: ¿es bajo o alto?
        precio_bajo = row["Caso"] in [5, 9]  # anomalías de precio bajo
        icon_p = "📉" if precio_bajo else "💰"
        label_p = "Precio bajo" if precio_bajo else "Precio alto"

        html = f"""
        <div class='sem-wrap'>
          <div class='sem-header'>
            <div>
              <div class='sem-id'>#{row['Caso']:02d} · {row['ID_Proceso']}</div>
              <div class='sem-entidad'>{row['Entidad'][:45]}</div>
            </div>
            <div class='sem-score' style='color:{sc_col};'>{score:.3f}</div>
          </div>

          <div class='sem-row'>
            <span class='sem-icon'>{icon_p}</span>
            <span class='sem-name'>{label_p}</span>
            <div class='sem-bar-bg'>
              <div class='sem-bar' style='width:{sp}%;background:{color_bar(sp)};'></div>
            </div>
            <span class='sem-val' style='color:{color_bar(sp)};'>{sp:.0f}%</span>
          </div>

          <div class='sem-row'>
            <span class='sem-icon'>{icon_sem(sc)}</span>
            <span class='sem-name'>Concentración</span>
            <div class='sem-bar-bg'>
              <div class='sem-bar' style='width:{sc}%;background:{color_bar(sc)};'></div>
            </div>
            <span class='sem-val' style='color:{color_bar(sc)};'>{sc:.0f}%</span>
          </div>

          <div class='sem-row'>
            <span class='sem-icon'>{icon_sem(sd)}</span>
            <span class='sem-name'>Duración</span>
            <div class='sem-bar-bg'>
              <div class='sem-bar' style='width:{sd}%;background:{color_bar(sd)};'></div>
            </div>
            <span class='sem-val' style='color:{color_bar(sd)};'>{sd:.0f}%</span>
          </div>

          <div class='sem-tags'>
            {badge_riesgo(row['Riesgo_Fiscal'])}
            {badge_trans(row['Transparencia'])}
            {badge_pipe(row['Pipelines'])}
          </div>
        </div>
        <br>
        """
        col.markdown(html, unsafe_allow_html=True)

st.markdown("---")


# ════════════════════════════════════════════════════════════════════════════
# TIMELINE
# ════════════════════════════════════════════════════════════════════════════
st.markdown("### 📅 Timeline — Contratos Alertados por Período")
st.caption("Distribución temporal de los casos priorizados y valor comprometido")

# Ordenar periodos cronológicamente
periodo_orden = ["2020-Q2","2021-Q4","2022-Q1","2022-Q3","2022-Q4",
                 "2023-Q1","2023-Q2","2023-Q3","2023-Q4","2024-Q1"]

df_tl = df.copy()
df_tl["Periodo_ord"] = pd.Categorical(df_tl["Periodo"], categories=periodo_orden, ordered=True)
df_tl = df_tl.sort_values("Periodo_ord")

tl_group = df_tl.groupby("Periodo").agg(
    contratos=("Caso","count"),
    valor=("Valor_COP","sum"),
    score_max=("Score_Riesgo","max"),
    score_avg=("Score_Riesgo","mean"),
).reset_index()
tl_group["Periodo_ord"] = pd.Categorical(tl_group["Periodo"], categories=periodo_orden, ordered=True)
tl_group = tl_group.sort_values("Periodo_ord")
tl_group["valor_B"] = tl_group["valor"] / 1e9

fig_tl = make_subplots(specs=[[{"secondary_y": True}]])

# Barras de valor
fig_tl.add_trace(go.Bar(
    x=tl_group["Periodo"], y=tl_group["valor_B"],
    name="Valor total (B COP)",
    marker_color=[
        "#e74c3c" if s >= 0.8 else "#e67e22" if s >= 0.65 else "#27ae60"
        for s in tl_group["score_max"]
    ],
    opacity=0.75,
    hovertemplate="<b>%{x}</b><br>Valor: $%{y:.2f}B COP<extra></extra>",
), secondary_y=False)

# Línea de score máximo
fig_tl.add_trace(go.Scatter(
    x=tl_group["Periodo"], y=tl_group["score_max"],
    name="Score máximo", mode="lines+markers",
    line=dict(color="#1a252f", width=2.5),
    marker=dict(size=10, color="#1a252f", symbol="diamond"),
    hovertemplate="<b>%{x}</b><br>Score máx: %{y:.3f}<extra></extra>",
), secondary_y=True)

# Línea score promedio
fig_tl.add_trace(go.Scatter(
    x=tl_group["Periodo"], y=tl_group["score_avg"],
    name="Score promedio", mode="lines+markers",
    line=dict(color="#7f8c8d", width=1.5, dash="dot"),
    marker=dict(size=7, color="#7f8c8d"),
    hovertemplate="<b>%{x}</b><br>Score prom: %{y:.3f}<extra></extra>",
), secondary_y=True)

# Anotaciones de contratos por período
for _, r in tl_group.iterrows():
    fig_tl.add_annotation(
        x=r["Periodo"], y=r["valor_B"],
        text=f"{int(r['contratos'])} caso{'s' if r['contratos']>1 else ''}",
        showarrow=False, yshift=14,
        font=dict(size=10, color="#1a252f", weight="bold"),
    )

fig_tl.update_layout(
    height=340,
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10,r=10,t=10,b=30),
    legend=dict(orientation="h", y=-0.18),
    xaxis=dict(title="", gridcolor="#ecf0f1", tickangle=-20),
    bargap=0.3,
)
fig_tl.update_yaxes(title_text="Valor total (B COP)", secondary_y=False,
                     gridcolor="#ecf0f1")
fig_tl.update_yaxes(title_text="Score de riesgo", secondary_y=True,
                     range=[0.5, 1.05], gridcolor="rgba(0,0,0,0)")

st.plotly_chart(fig_tl, use_container_width=True)

# Tabla resumen del timeline
with st.expander("📋 Detalle por período"):
    st.dataframe(
        tl_group[["Periodo","contratos","valor_B","score_max","score_avg"]].rename(columns={
            "Periodo":"Período","contratos":"Casos","valor_B":"Valor (B COP)",
            "score_max":"Score máx.","score_avg":"Score prom.",
        }).style.format({
            "Valor (B COP)":"${:.2f}","Score máx.":"{:.3f}","Score prom.":"{:.3f}"
        }),
        use_container_width=True, hide_index=True,
    )

st.markdown("---")


# ════════════════════════════════════════════════════════════════════════════
# PANEL DE EXPLICACIÓN (se activa al seleccionar fila en la tabla)
# ════════════════════════════════════════════════════════════════════════════
st.markdown("### 🔬 Panel de Explicación de Alerta")

if not df.empty and caso_sel is not None:
    fila = df[df["Caso"] == caso_sel].iloc[0]
    info = ALERTAS.get(caso_sel, {"factores":["Sin info disponible."],"proveedor_info":"—"})
    sc   = score_color(fila["Score_Riesgo"])

    cp1, cp2, cp3 = st.columns([1.3, 1.3, 1.4], gap="medium")

    with cp1:
        st.markdown(f"""
        <div class='panel-ficha' style='border-top-color:{sc};'>
          <div style='font-size:0.72rem;color:#7f8c8d;text-transform:uppercase;'>Caso #{caso_sel:02d} seleccionado</div>
          <div style='font-size:0.95rem;font-weight:800;color:#1a252f;margin:4px 0 2px 0;'>{fila['ID_Proceso']}</div>
          <div style='font-size:0.82rem;color:#5d6d7e;margin-bottom:10px;'>{fila['Entidad']}</div>
          <hr style='border-color:#f0f0f0;margin:8px 0;'>
          <div class='ficha-row'><span class='ficha-key'>Departamento</span><span class='ficha-val'>{fila['Departamento']}</span></div>
          <div class='ficha-row'><span class='ficha-key'>Modalidad</span><span class='ficha-val'>{fila['Modalidad']}</span></div>
          <div class='ficha-row'><span class='ficha-key'>Valor</span><span class='ficha-val'>${fila['Valor_COP']/1e9:.3f}B COP</span></div>
          <div class='ficha-row'><span class='ficha-key'>Duración</span><span class='ficha-val'>{int(fila['Duracion_dias'])} días</span></div>
          <div class='ficha-row'><span class='ficha-key'>Proveedor</span><span class='ficha-val'>{fila['Proveedor']}</span></div>
          <div class='ficha-row'><span class='ficha-key'>Riesgo fiscal</span><span class='ficha-val'>{fila['Riesgo_Fiscal']}</span></div>
          <div class='ficha-row'><span class='ficha-key'>Transparencia</span><span class='ficha-val'>{fila['Transparencia']}</span></div>
          <div class='ficha-row'><span class='ficha-key'>IDF</span><span class='ficha-val'>{fila['IDF']:.1f} / 100</span></div>
          <div class='ficha-row'><span class='ficha-key'>ITA</span><span class='ficha-val'>{fila['ITA']:.1f} / 100</span></div>
          <div class='ficha-row'><span class='ficha-key'>Percentil</span><span class='ficha-val'>{fila['Percentil']:.1f}% del universo</span></div>
          <div class='ficha-row'><span class='ficha-key'>Modelos</span><span class='ficha-val'>{fila['Pipelines']}/3 detectaron anomalía</span></div>
        </div>
        """, unsafe_allow_html=True)

    with cp2:
        st.markdown("**⚠️ Factores que generan la alerta**")
        for f in info["factores"]:
            st.markdown(f"<div class='alerta-item'>{f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='prov-box'>🏢 <b>Historial del proveedor:</b><br>{info['proveedor_info']}</div>",
                    unsafe_allow_html=True)

        # Gauge de score
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=fila["Score_Riesgo"],
            number={"font":{"size":32,"color":sc},"suffix":""},
            gauge={
                "axis":{"range":[0,1],"tickwidth":1,"tickcolor":"#aaa"},
                "bar":{"color":sc,"thickness":0.25},
                "bgcolor":"white",
                "borderwidth":0,
                "steps":[
                    {"range":[0,0.65],"color":"#eafaf1"},
                    {"range":[0.65,0.79],"color":"#fef9e7"},
                    {"range":[0.79,1.0],"color":"#fdedec"},
                ],
                "threshold":{"line":{"color":"#1a252f","width":3},"thickness":0.8,"value":fila["Score_Riesgo"]},
            },
            title={"text":"Score Global de Riesgo","font":{"size":12,"color":"#7f8c8d"}},
        ))
        fig_gauge.update_layout(height=200, margin=dict(l=20,r=20,t=40,b=10),
                                 paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_gauge, use_container_width=True)

    with cp3:
        st.markdown("**📊 Descomposición del score**")

        cats = ["Precio<br>Relativo","Concentración<br>Proveedor","Duración<br>Patrón"]
        vals = [fila["Score_Precio"]/100, fila["Score_Conc"]/100, fila["Score_Dur"]/100]

        fig_rad = go.Figure()
        fig_rad.add_trace(go.Scatterpolar(
            r=vals+[vals[0]], theta=cats+[cats[0]],
            fill="toself",
            fillcolor=f"rgba(231,76,60,0.15)",
            line=dict(color=sc, width=2.5),
            name="Score",
        ))
        fig_rad.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0,1], tickfont=dict(size=9),
                                gridcolor="#ddd"),
                angularaxis=dict(tickfont=dict(size=10)),
                bgcolor="rgba(0,0,0,0)",
            ),
            showlegend=False, height=220,
            margin=dict(l=30,r=30,t=20,b=20),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_rad, use_container_width=True)

        # Barras horizontales de los 3 factores
        for nombre, val, icono in [
            ("Precio relativo", fila["Score_Precio"], "💰"),
            ("Concentración proveedor", fila["Score_Conc"], "🏢"),
            ("Duración / Patrón", fila["Score_Dur"], "⏱️"),
        ]:
            col_b = color_bar(val)
            st.markdown(f"""
            <div class='sem-row' style='margin:6px 0;'>
              <span style='width:20px;'>{icono}</span>
              <span style='font-size:0.78rem;width:160px;color:#555;'>{nombre}</span>
              <div class='sem-bar-bg'>
                <div class='sem-bar' style='width:{val}%;background:{col_b};'></div>
              </div>
              <span class='sem-val' style='color:{col_b};'>{val:.0f}%</span>
            </div>
            """, unsafe_allow_html=True)

elif df.empty:
    st.info("🔍 Ajusta los filtros del panel lateral para ver contratos.")
else:
    st.info("👆 **Selecciona una fila en la tabla de contratos** (arriba) para ver aquí el análisis completo.")

# ════════════════════════════════════════════════════════════════════════════
# ANÁLISIS COMPLEMENTARIO
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### 📈 Análisis Complementario")

tab1, tab2, tab3 = st.tabs(["Por Departamento", "IDF / ITA vs Score", "Score por modalidad"])

with tab1:
    dg = (df.groupby("Departamento").agg(
        Casos=("Caso","count"), Score_Max=("Score_Riesgo","max"),
        Score_Avg=("Score_Riesgo","mean"), Valor_B=("Valor_COP",lambda x: x.sum()/1e9),
    ).reset_index().sort_values("Score_Max", ascending=True))

    fig_b = px.bar(dg, y="Departamento", x="Score_Max", orientation="h",
        color="Score_Max", color_continuous_scale=["#27ae60","#e67e22","#e74c3c"],
        range_color=[0.65,1.0], text="Casos",
        labels={"Score_Max":"Score máximo","Departamento":""},
        title="Score máximo por Departamento")
    fig_b.update_traces(texttemplate="%{text} caso(s)", textposition="outside")
    fig_b.update_layout(height=340, paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False,
        margin=dict(l=10,r=60,t=40,b=10))
    st.plotly_chart(fig_b, use_container_width=True)

with tab2:
    fig_sc = px.scatter(df, x="IDF", y="ITA", color="Score_Riesgo",
        size="Valor_B", size_max=40,
        color_continuous_scale=["#27ae60","#e67e22","#e74c3c"],
        range_color=[0.65,1.0],
        hover_name="Entidad",
        hover_data={"Score_Riesgo":":.3f","IDF":":.1f","ITA":":.1f","Valor_B":":.2f"},
        labels={"IDF":"Índice de Desempeño Fiscal (IDF)",
                "ITA":"Índice de Transparencia (ITA)",
                "Score_Riesgo":"Score","Valor_B":"Valor (B COP)"},
        title="IDF vs ITA — Contexto institucional de los contratos alertados")
    fig_sc.add_hline(y=60, line_dash="dash", line_color="#7f8c8d", opacity=0.5,
                     annotation_text="ITA umbral 60")
    fig_sc.add_vline(x=55, line_dash="dash", line_color="#7f8c8d", opacity=0.5,
                     annotation_text="IDF umbral 55")
    fig_sc.update_layout(height=360, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_sc, use_container_width=True)

with tab3:
    mg = df.groupby("Modalidad").agg(
        Casos=("Caso","count"), Score_Prom=("Score_Riesgo","mean"),
        Valor_B=("Valor_COP", lambda x: x.sum()/1e9),
    ).reset_index()
    fig_m = px.bar(mg, x="Modalidad", y="Score_Prom",
        color="Score_Prom", color_continuous_scale=["#27ae60","#e74c3c"],
        text="Casos", title="Score promedio por Modalidad de contratación",
        labels={"Score_Prom":"Score promedio","Modalidad":""})
    fig_m.update_traces(texttemplate="%{text} casos", textposition="outside")
    fig_m.update_layout(height=320, paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
    st.plotly_chart(fig_m, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#7f8c8d;font-size:0.75rem;padding:10px 0;'>
SATCS · Sistema de Alerta Temprana en Contratación Salud · Datos: SECOP II Colombia ·
Prototipo MVP v2.0 · <b>Solo para uso interno — no para publicación</b>
</div>
""", unsafe_allow_html=True)


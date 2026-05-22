"""
SATCS — Sistema de Alerta Temprana en Contratación Salud
Dashboard interactivo para detección de anomalías en contratación pública (sector salud, Colombia)
MVP para testeo con auditoras — datos reales Top-15 SECOP + scores simulados
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─── Configuración de página ───────────────────────────────────────────────
st.set_page_config(
    page_title="SATCS — Alerta Salud",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS personalizado ──────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fondo y tipografía general */
    .main { background-color: #f4f6f9; }
    h1, h2, h3 { color: #2c3e50; }

    /* KPI cards */
    .kpi-card {
        background: white;
        border-radius: 10px;
        padding: 20px 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #2980b9;
    }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #2c3e50; }
    .kpi-label { font-size: 0.78rem; color: #7f8c8d; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-delta { font-size: 0.85rem; margin-top: 6px; }
    .kpi-red   { border-left-color: #e74c3c; }
    .kpi-green { border-left-color: #27ae60; }
    .kpi-orange{ border-left-color: #e67e22; }

    /* Alerta card */
    .alerta-card {
        background: #fff9f0;
        border: 1px solid #f0c080;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }
    .alerta-header { font-weight: 700; color: #e67e22; font-size: 0.9rem; }
    .alerta-item { color: #5d4037; font-size: 0.85rem; margin: 3px 0; }

    /* Proveedor card */
    .prov-card {
        background: #eaf2f8;
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 8px;
        font-size: 0.83rem;
        color: #2471a3;
    }

    /* Badge de riesgo */
    .badge-alto   { background:#e74c3c; color:white; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:700; }
    .badge-medio  { background:#e67e22; color:white; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:700; }
    .badge-bajo   { background:#27ae60; color:white; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:700; }

    /* Sidebar */
    .css-1d391kg { background-color: #1a252f; }
    section[data-testid="stSidebar"] { background-color: #1e2d3d; }
    section[data-testid="stSidebar"] .stMarkdown p { color: #bdc3c7; }

    /* Tabla */
    .dataframe { font-size: 0.82rem !important; }
</style>
""", unsafe_allow_html=True)


# ─── Datos embebidos (Top-15 reales + enrichment del HTML) ─────────────────
@st.cache_data
def cargar_datos():
    data = {
        "Caso": list(range(1, 16)),
        "ID_Proceso": [
            "CO1.REQ.7355251","CO1.REQ.6438216","CO1.REQ.7719359","CO1.REQ.5492550",
            "CO1.REQ.1824967","CO1.REQ.6919110","CO1.REQ.8218667","CO1.REQ.7558157",
            "CO1.REQ.9893879","CO1.REQ.9380512","CO1.REQ.6203670","CO1.REQ.8189189",
            "CO1.REQ.9161392","CO1.REQ.9504211","CO1.REQ.7745198",
        ],
        "Entidad": [
            "ESE HOSPITAL SAN RAFAEL DE TUNJA","CAPRESOCA E.P.S.","CAPRESOCA E.P.S.",
            "Hospital Dptal Tomas Uribe Uribe ESE","ESE SAN BENITO SANTANDER",
            "UNIVERSIDAD NACIONAL DE COLOMBIA","FUNDACION SALUDMIA EPS",
            "GECELCA S.A. E.S.P.","ESE CARMEN EMILIA OSPINA",
            "UNIVERSIDAD DEL CAUCA","EAAB - E.S.P.","COLPENSIONES",
            "CLÍNICA GIRÓN ESE","ESE HOSPITAL UNIVERSITARIO SAN JORGE",
            "Fideicomiso Fondo Nacional de Salud PPL",
        ],
        "Departamento": [
            "Boyacá","Casanare","Casanare","Valle del Cauca","Santander",
            "Bogotá D.C.","No Definido","Atlántico","Huila","Cauca",
            "No Definido","Bogotá D.C.","Santander","Risaralda","Bogotá D.C.",
        ],
        "Modalidad": [
            "Prestación De Servicios","Decreto 092 De 2017","Decreto 092 De 2017",
            "Decreto 092 De 2017","Decreto 092 De 2017","Decreto 092 De 2017",
            "Prestación De Servicios","Prestación De Servicios","Prestación De Servicios",
            "Decreto 092 De 2017","Prestación De Servicios","Prestación De Servicios",
            "Decreto 092 De 2017","Prestación De Servicios","Decreto 092 De 2017",
        ],
        "Valor_COP": [
            2_800_000_000, 5_250_000_000, 1_017_134_122, 800_000_000,
            1_300_000, 53_433_420_301, 46_054_430_000, 19_488_240_000,
            290_290_400, 150_000_000, 2_824_535_000, 183_990_600,
            14_971_470_000, 12_000_000_000, 6_678_936_000,
        ],
        "Duracion_dias": [
            7, 22, 322, 360, 318, 720, 365, 638, 1800, 324,
            990, 600, 720, 180, 376,
        ],
        "Proveedor": [
            "UNION TEMPORAL ANGIOVASCULAR","HOSP. REGIONAL DE LA ORINOQUIA ESE",
            "ESE SALUD YOPAL","DIEGO FERNANDO NOREÑA FRANCO","INTERCLINICA AVA S.A.S",
            "COLSUBSIDIO","FCV","Colsanitas S.a.","UNION TEMPORAL SEGURA",
            "CARDIOESPECIALIDADES LTDA","UNIMOS SALUD SAS",
            "EMERMEDICA SA SERVICIOS DE AMBULANCIA","GIROSALUD IPS SAS",
            "IMAGENES DIAGNOSTICAS S.A.","UT PREMIER SALUD ERON VIEJO CALDAS",
        ],
        "Score_Riesgo": [
            0.952, 0.828, 0.808, 0.737, 0.667, 0.785, 0.785, 0.761,
            0.759, 0.740, 0.739, 0.734, 0.731, 0.727, 0.727,
        ],
        "Analisis_detectan": [3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        "Score_Precio": [
            85.6, 71.8, 82.6, 69.4, 50.2, 100.0, 99.9, 100.0, 100.0, 89.4,
            100.0, 99.8, 98.6, 99.8, 99.0,
        ],
        "Score_Concentracion": [
            100.0, 76.6, 60.0, 51.8, 50.1, 35.5, 35.5, 28.3, 27.7, 32.6,
            21.6, 20.5, 20.8, 18.7, 19.5,
        ],
        "Score_Duracion": [
            100.0, 100.0, 99.9, 100.0, 100.0, 100.0, 100.0, 100.0, 99.8, 100.0,
            100.0, 100.0, 99.5, 99.8, 99.5,
        ],
        "Periodo": [
            "2023-Q4","2022-Q3","2023-Q1","2021-Q4","2020-Q2",
            "2022-Q4","2023-Q2","2023-Q1","2024-Q1","2023-Q3",
            "2022-Q1","2023-Q2","2023-Q3","2024-Q1","2023-Q1",
        ],
    }

    # Alertas por caso (extraídas del HTML de validación)
    alertas = {
        1: {
            "factores": [
                "💰 Precio diario **1756.5x** superior a la referencia en Boyacá",
                "📊 Precio superior al **100%** de contratos comparables",
                "⏱️ Duración muy corta: **7 días** (atípico para el monto)",
            ],
            "proveedor_info": "5 contratos | 1 entidad | 1 depto | $32.9 mil millones COP acumulados",
        },
        2: {
            "factores": [
                "💰 Precio diario **75.5x** superior a la referencia en Casanare",
                "📊 Precio superior al **100%** de contratos comparables",
            ],
            "proveedor_info": "10 contratos | 2 entidades | 2 deptos | $76.2 mil millones COP acumulados",
        },
        3: {
            "factores": [
                "🔴 Contrato identificado como atípico por **3 análisis independientes**",
                "📊 Score alto en concentración de proveedor y duración",
            ],
            "proveedor_info": "6 contratos | 1 entidad | 1 depto | $49.9 mil millones COP acumulados",
        },
        4: {
            "factores": [
                "💰 Precio diario **2.3x** superior a la referencia en Valle del Cauca",
                "📊 Precio superior al 69% de contratos comparables",
            ],
            "proveedor_info": "10 contratos | 1 entidad | 1 depto | $3.2 mil millones COP acumulados",
        },
        5: {
            "factores": [
                "📉 Precio diario inusualmente **bajo: 1%** de la referencia",
                "📊 Precio inferior al **98%** de contratos comparables",
                "⚠️ Transparencia baja (**47.9/100**), riesgo fiscal: ALTO",
            ],
            "proveedor_info": "37 contratos | 18 entidades | 4 deptos | $8.2 mil millones COP acumulados",
        },
        6: {
            "factores": [
                "💰 Precio diario **326.5x** superior a la referencia en Bogotá D.C.",
                "📊 Precio superior al **100%** de contratos comparables",
                "⏱️ Duración atípica: **720 días**",
            ],
            "proveedor_info": "3 contratos | 3 entidades | 3 deptos | $53.6 mil millones COP acumulados",
        },
        7: {
            "factores": [
                "💰 Precio diario **1261.8x** superior a la referencia",
                "📊 Precio superior al **100%** de contratos comparables",
            ],
            "proveedor_info": "9 contratos | 4 entidades | 4 deptos | $51.0 mil millones COP acumulados",
        },
        8: {
            "factores": [
                "💰 Precio diario **24.4x** superior a la referencia en Atlántico",
                "📊 Precio superior al **99%** de contratos comparables",
                "⏱️ Duración atípica: **638 días**",
            ],
            "proveedor_info": "8 contratos | 2 entidades | 2 deptos | $20.5 mil millones COP acumulados",
        },
        9: {
            "factores": [
                "📉 Precio diario inusualmente **bajo: 24%** de la referencia",
                "📊 Precio inferior al **92%** de contratos comparables",
                "⏱️ Duración extrema: **1800 días** (~5 años)",
            ],
            "proveedor_info": "2 contratos | 1 entidad | 1 depto | $552 millones COP acumulados",
        },
        10: {
            "factores": [
                "🔴 Contrato identificado como atípico por **múltiples análisis**",
                "📊 Alto score en análisis de precio relativo",
            ],
            "proveedor_info": "1 contrato | 1 entidad | 1 depto | $150 millones COP acumulados",
        },
        11: {
            "factores": [
                "💰 Precio relativo elevado vs. referencia en Cundinamarca",
                "📊 Score de concentración de proveedor: alto",
            ],
            "proveedor_info": "Proveedor con historial concentrado en entidades de salud departamental",
        },
        12: {
            "factores": [
                "💰 Precio diario superior a la mediana departamental (Huila)",
                "📊 Análisis de precio detecta anomalía",
            ],
            "proveedor_info": "Proveedor con contratos en múltiples entidades de Huila",
        },
        13: {
            "factores": [
                "💰 Valor total elevado con proveedor de nicho",
                "⏱️ Duración de **720 días** atípica para el tipo de servicio",
            ],
            "proveedor_info": "Proveedor especializado IPS con concentración en Santander",
        },
        14: {
            "factores": [
                "💰 Precio diario por encima del percentil 99 en Risaralda",
                "📊 Precio superior al **99.8%** de contratos comparables",
            ],
            "proveedor_info": "Proveedor de imágenes diagnósticas con historial regional",
        },
        15: {
            "factores": [
                "💰 Score de precio elevado en modalidad Decreto 092",
                "📊 Análisis de concentración y precio detectan anomalía",
            ],
            "proveedor_info": "Unión temporal con presencia en múltiples establecimientos penales",
        },
    }

    df = pd.DataFrame(data)
    df["Nivel_Riesgo"] = pd.cut(
        df["Score_Riesgo"],
        bins=[0, 0.65, 0.79, 1.0],
        labels=["Bajo", "Medio", "Alto"],
    )
    df["Valor_Miles_M"] = df["Valor_COP"] / 1e9  # miles de millones
    df["Precio_dia"] = df["Valor_COP"] / df["Duracion_dias"]
    return df, alertas


df_full, ALERTAS = cargar_datos()


# ─── Coordenadas de departamentos de Colombia ──────────────────────────────
COORDS_DEPTO = {
    "Boyacá":          (5.4545, -73.3622),
    "Casanare":        (5.3361, -71.9820),
    "Valle del Cauca": (3.8509, -76.5226),
    "Santander":       (6.6437, -73.6536),
    "Bogotá D.C.":     (4.7110, -74.0721),
    "No Definido":     (4.0000, -74.5000),
    "Atlántico":       (10.6966, -74.8741),
    "Huila":           (2.5359, -75.5278),
    "Cauca":           (2.7052, -76.8261),
    "Cundinamarca":    (5.0269, -74.0344),
    "Risaralda":       (5.3158, -75.9741),
    "Córdoba":         (8.3549, -75.8814),
    "Magdalena":       (10.4113, -74.4057),
    "Antioquia":       (6.2442, -75.5812),
    "Nariño":          (1.2136, -77.2811),
    "Tolima":          (4.0925, -75.1545),
    "Meta":            (4.1533, -73.6350),
}


# ─── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 SATCS")
    st.markdown("**Sistema de Alerta Temprana**  \nContratación Pública · Sector Salud · Colombia")
    st.markdown("---")

    st.markdown("### 🎛️ Filtros")

    periodos_opciones = ["Todos"] + sorted(df_full["Periodo"].unique().tolist())
    sel_periodo = st.selectbox("📅 Período", periodos_opciones)

    deptos_opciones = ["Todos"] + sorted(df_full["Departamento"].unique().tolist())
    sel_depto = st.selectbox("🗺️ Departamento", deptos_opciones)

    modalidades_opciones = ["Todas"] + sorted(df_full["Modalidad"].unique().tolist())
    sel_modalidad = st.selectbox("📋 Modalidad", modalidades_opciones)

    nivel_riesgo_opciones = ["Todos", "Alto", "Medio", "Bajo"]
    sel_riesgo = st.selectbox("🚨 Nivel de Riesgo", nivel_riesgo_opciones)

    score_min = st.slider(
        "Score mínimo de riesgo",
        min_value=0.0, max_value=1.0, value=0.0, step=0.05,
        format="%.2f"
    )

    st.markdown("---")
    st.markdown("### ℹ️ Acerca del MVP")
    st.markdown("""
    **Datos:** Top-15 SECOP real  
    **Scores:** 3 análisis independientes  
    — Análisis A: Precio relativo  
    — Análisis B: Concentración proveedor  
    — Análisis C: Duración/patrón  
    """)
    st.markdown("**v0.1 — Prototipo para validación con auditoras**")


# ─── FILTRADO ──────────────────────────────────────────────────────────────
df = df_full.copy()
if sel_periodo != "Todos":
    df = df[df["Periodo"] == sel_periodo]
if sel_depto != "Todos":
    df = df[df["Departamento"] == sel_depto]
if sel_modalidad != "Todas":
    df = df[df["Modalidad"] == sel_modalidad]
if sel_riesgo != "Todos":
    df = df[df["Nivel_Riesgo"] == sel_riesgo]
df = df[df["Score_Riesgo"] >= score_min]


# ─── ENCABEZADO ────────────────────────────────────────────────────────────
st.markdown("# 🏥 SATCS — Alerta Salud Abierta")
st.markdown("**Detección de anomalías en contratación pública · Sector Salud · Colombia**")
st.markdown("---")


# ─── KPIs ──────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

contratos_analizados = len(df)
alertas_generadas = len(df[df["Score_Riesgo"] >= 0.7])
riesgo_alto = len(df[df["Nivel_Riesgo"] == "Alto"])
valor_total = df["Valor_COP"].sum() / 1e9
ahorro_potencial = valor_total * 0.15  # estimado 15%

with col1:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-value'>{contratos_analizados}</div>
        <div class='kpi-label'>Contratos analizados</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='kpi-card kpi-orange'>
        <div class='kpi-value'>{alertas_generadas}</div>
        <div class='kpi-label'>Alertas generadas</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='kpi-card kpi-red'>
        <div class='kpi-value'>{riesgo_alto}</div>
        <div class='kpi-label'>Riesgo alto</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-value'>${valor_total:.1f}B</div>
        <div class='kpi-label'>Valor total (COP)</div>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class='kpi-card kpi-green'>
        <div class='kpi-value'>${ahorro_potencial:.1f}B</div>
        <div class='kpi-label'>Ahorro potencial est.</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─── SECCIÓN PRINCIPAL: mapa + tabla ───────────────────────────────────────
col_mapa, col_tabla = st.columns([1.1, 1.9], gap="medium")

# ── MAPA DE CALOR TERRITORIAL ──────────────────────────────────────────────
with col_mapa:
    st.markdown("### 🗺️ Mapa de Riesgo Territorial")

    # Agrupar por departamento
    depto_stats = (
        df.groupby("Departamento")
        .agg(contratos=("Caso", "count"), score_avg=("Score_Riesgo", "mean"), valor=("Valor_COP", "sum"))
        .reset_index()
    )
    depto_stats["lat"] = depto_stats["Departamento"].map(lambda d: COORDS_DEPTO.get(d, (4.0, -74.0))[0])
    depto_stats["lon"] = depto_stats["Departamento"].map(lambda d: COORDS_DEPTO.get(d, (4.0, -74.0))[1])
    depto_stats["valor_miles_M"] = depto_stats["valor"] / 1e9

    fig_map = px.scatter_mapbox(
        depto_stats,
        lat="lat", lon="lon",
        color="score_avg",
        size="contratos",
        size_max=40,
        color_continuous_scale=["#27ae60", "#f39c12", "#e74c3c"],
        range_color=[0.5, 1.0],
        hover_name="Departamento",
        hover_data={
            "contratos": True,
            "score_avg": ":.3f",
            "valor_miles_M": ":.1f",
            "lat": False,
            "lon": False,
        },
        labels={
            "contratos": "Contratos",
            "score_avg": "Score promedio",
            "valor_miles_M": "Valor (miles M COP)",
        },
        zoom=4.5,
        center={"lat": 4.5, "lon": -74.0},
        mapbox_style="carto-positron",
        height=420,
    )
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(title="Score<br>Riesgo", thickness=12, len=0.7),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Mini leyenda
    st.markdown("""
    <div style='font-size:0.78rem; color:#7f8c8d; text-align:center;'>
    🟢 Riesgo bajo &nbsp;|&nbsp; 🟡 Medio &nbsp;|&nbsp; 🔴 Alto &nbsp;·&nbsp; Tamaño = # contratos
    </div>
    """, unsafe_allow_html=True)


# ── TABLA DE CONTRATOS PRIORIZADOS ─────────────────────────────────────────
with col_tabla:
    st.markdown("### 📋 Contratos Priorizados por Score")
    st.caption("Selecciona una fila para ver el panel de explicación detallado →")

    if df.empty:
        st.info("Sin contratos para los filtros seleccionados.")
    else:
        def badge(nivel):
            colores = {"Alto": "#e74c3c", "Medio": "#e67e22", "Bajo": "#27ae60"}
            return f"<span style='background:{colores.get(nivel,'#95a5a6')};color:white;border-radius:10px;padding:2px 8px;font-size:0.72rem;font-weight:700;'>{nivel}</span>"

        def score_bar(score):
            pct = int(score * 100)
            color = "#e74c3c" if score >= 0.8 else "#e67e22" if score >= 0.65 else "#27ae60"
            return f"<div style='background:#ecf0f1;border-radius:4px;height:10px;width:100%;'><div style='background:{color};width:{pct}%;height:10px;border-radius:4px;'></div></div><span style='font-size:0.7rem;color:{color};font-weight:700;'>{score:.3f}</span>"

        # Tabla interactiva con st.dataframe (click-to-select)
        df_display = df[[
            "Caso", "ID_Proceso", "Entidad", "Departamento", "Modalidad",
            "Valor_Miles_M", "Duracion_dias", "Score_Riesgo", "Nivel_Riesgo", "Analisis_detectan"
        ]].rename(columns={
            "Caso": "#",
            "ID_Proceso": "ID SECOP",
            "Entidad": "Entidad Contratante",
            "Departamento": "Depto.",
            "Modalidad": "Modalidad",
            "Valor_Miles_M": "Valor (miles M)",
            "Duracion_dias": "Días",
            "Score_Riesgo": "Score",
            "Nivel_Riesgo": "Riesgo",
            "Analisis_detectan": "# Análisis",
        }).copy()

        df_display["Valor (miles M)"] = df_display["Valor (miles M)"].apply(lambda x: f"${x:.2f}B")

        selection = st.dataframe(
            df_display,
            use_container_width=True,
            height=400,
            on_select="rerun",
            selection_mode="single-row",
            hide_index=True,
        )

        # Leer fila seleccionada
        filas_sel = selection.selection.rows if hasattr(selection, "selection") else []
        caso_sel = None
        if filas_sel:
            idx_real = df.iloc[filas_sel[0]]["Caso"]
            caso_sel = int(idx_real)


# ─── PANEL DE EXPLICACIÓN ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔬 Panel de Explicación de Alerta")

if not df.empty and caso_sel is not None:
    fila = df[df["Caso"] == caso_sel].iloc[0]
    alerta_info = ALERTAS.get(caso_sel, {
        "factores": ["Información de alerta no disponible para este caso."],
        "proveedor_info": "Sin datos adicionales.",
    })

    # Layout 3 columnas
    cx1, cx2, cx3 = st.columns([1.4, 1.3, 1.3], gap="medium")

    with cx1:
        # Encabezado del caso
        nivel = str(fila["Nivel_Riesgo"])
        color_nivel = {"Alto": "#e74c3c", "Medio": "#e67e22", "Bajo": "#27ae60"}.get(nivel, "#95a5a6")
        st.markdown(f"""
        <div style='background:white;border-radius:10px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,0.08);border-top:4px solid {color_nivel};'>
            <div style='font-size:0.75rem;color:#7f8c8d;text-transform:uppercase;letter-spacing:1px;'>Caso #{caso_sel:02d}</div>
            <div style='font-weight:700;color:#2c3e50;font-size:0.95rem;margin:4px 0;'>{fila['ID_Proceso']}</div>
            <div style='font-size:0.83rem;color:#5d6d7e;margin-bottom:8px;'>{fila['Entidad']}</div>
            <hr style='margin:8px 0;border-color:#ecf0f1;'>
            <table style='width:100%;font-size:0.82rem;'>
                <tr><td style='color:#7f8c8d;'>Depto.</td><td style='font-weight:600;'>{fila['Departamento']}</td></tr>
                <tr><td style='color:#7f8c8d;'>Modalidad</td><td>{fila['Modalidad'][:30]}</td></tr>
                <tr><td style='color:#7f8c8d;'>Valor</td><td style='font-weight:700;color:#2c3e50;'>${fila['Valor_COP']/1e9:.3f}B COP</td></tr>
                <tr><td style='color:#7f8c8d;'>Duración</td><td>{int(fila['Duracion_dias'])} días</td></tr>
                <tr><td style='color:#7f8c8d;'>Proveedor</td><td>{fila['Proveedor'][:35]}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with cx2:
        st.markdown("**⚠️ Factores de alerta detectados**")
        for factor in alerta_info["factores"]:
            st.markdown(f"""
            <div class='alerta-card'>
                <span class='alerta-item'>{factor}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class='prov-card'>
            🏢 <b>Historial del proveedor:</b><br>{alerta_info['proveedor_info']}
        </div>
        """, unsafe_allow_html=True)

    with cx3:
        st.markdown("**📊 Descomposición del score de riesgo**")

        categorias = ["Precio\nRelativo", "Concentración\nProveedor", "Duración/\nPatrón"]
        valores = [
            fila["Score_Precio"] / 100,
            fila["Score_Concentracion"] / 100,
            fila["Score_Duracion"] / 100,
        ]
        colores = ["#e74c3c" if v >= 0.8 else "#e67e22" if v >= 0.5 else "#27ae60" for v in valores]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=valores + [valores[0]],
            theta=categorias + [categorias[0]],
            fill="toself",
            fillcolor="rgba(231, 76, 60, 0.2)",
            line=dict(color="#e74c3c", width=2),
            name="Score",
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=9)),
                angularaxis=dict(tickfont=dict(size=10)),
            ),
            showlegend=False,
            height=240,
            margin=dict(l=30, r=30, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Score general
        score = fila["Score_Riesgo"]
        color_s = "#e74c3c" if score >= 0.8 else "#e67e22" if score >= 0.65 else "#27ae60"
        st.markdown(f"""
        <div style='text-align:center;background:white;border-radius:8px;padding:10px;border:1px solid #ecf0f1;'>
            <div style='font-size:1.8rem;font-weight:800;color:{color_s};'>{score:.3f}</div>
            <div style='font-size:0.72rem;color:#7f8c8d;text-transform:uppercase;letter-spacing:1px;'>Score Global de Riesgo</div>
            <div style='font-size:0.8rem;margin-top:4px;'>Detectado por <b>{fila['Analisis_detectan']}</b> de 3 análisis independientes</div>
        </div>
        """, unsafe_allow_html=True)

elif df.empty:
    st.info("🔍 No hay contratos que coincidan con los filtros aplicados. Ajusta los filtros del panel lateral.")
else:
    st.info("👆 **Selecciona una fila** en la tabla de contratos para ver aquí la explicación detallada de la alerta.")


# ─── ANÁLISIS COMPARATIVO ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📈 Análisis Comparativo")

tab1, tab2, tab3 = st.tabs(["Distribución de Scores", "Por Departamento", "Análisis por Modalidad"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig_hist = px.histogram(
            df, x="Score_Riesgo", nbins=15,
            title="Distribución de Scores de Riesgo",
            color_discrete_sequence=["#2980b9"],
            labels={"Score_Riesgo": "Score de Riesgo", "count": "Contratos"},
        )
        fig_hist.add_vline(x=0.65, line_dash="dash", line_color="#e67e22", annotation_text="Umbral Medio")
        fig_hist.add_vline(x=0.79, line_dash="dash", line_color="#e74c3c", annotation_text="Umbral Alto")
        fig_hist.update_layout(height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_hist, use_container_width=True)

    with c2:
        pie_data = df["Nivel_Riesgo"].value_counts().reset_index()
        pie_data.columns = ["Nivel", "Cantidad"]
        fig_pie = px.pie(
            pie_data, names="Nivel", values="Cantidad",
            title="Distribución por Nivel de Riesgo",
            color="Nivel",
            color_discrete_map={"Alto": "#e74c3c", "Medio": "#e67e22", "Bajo": "#27ae60"},
            hole=0.45,
        )
        fig_pie.update_layout(height=320, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    depto_group = (
        df.groupby("Departamento")
        .agg(
            Contratos=("Caso", "count"),
            Score_Promedio=("Score_Riesgo", "mean"),
            Valor_Total=("Valor_COP", "sum"),
        )
        .reset_index()
        .sort_values("Score_Promedio", ascending=False)
    )
    depto_group["Valor_Total"] = depto_group["Valor_Total"] / 1e9

    fig_bar = px.bar(
        depto_group, x="Departamento", y="Score_Promedio",
        color="Score_Promedio",
        color_continuous_scale=["#27ae60", "#f39c12", "#e74c3c"],
        range_color=[0.5, 1.0],
        title="Score Promedio de Riesgo por Departamento",
        labels={"Score_Promedio": "Score Promedio", "Departamento": ""},
        text="Contratos",
    )
    fig_bar.update_traces(texttemplate="%{text} contratos", textposition="outside")
    fig_bar.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          xaxis_tickangle=-30, coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    modal_group = (
        df.groupby("Modalidad")
        .agg(
            Contratos=("Caso", "count"),
            Score_Promedio=("Score_Riesgo", "mean"),
            Valor_Total_B=("Valor_COP", lambda x: x.sum() / 1e9),
        )
        .reset_index()
    )

    fig_scatter = px.scatter(
        modal_group,
        x="Contratos", y="Score_Promedio",
        size="Valor_Total_B",
        color="Score_Promedio",
        text="Modalidad",
        color_continuous_scale=["#27ae60", "#e74c3c"],
        title="Modalidades: Volumen vs. Score de Riesgo (tamaño = valor total)",
        labels={"Contratos": "# Contratos", "Score_Promedio": "Score Promedio"},
        size_max=50,
    )
    fig_scatter.update_traces(textposition="top center", textfont_size=10)
    fig_scatter.update_layout(height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               coloraxis_showscale=False)
    st.plotly_chart(fig_scatter, use_container_width=True)


# ─── FOOTER ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#7f8c8d; font-size:0.78rem;'>
    SATCS — Sistema de Alerta Temprana en Contratación Salud &nbsp;|&nbsp;
    Datos: SECOP II Colombia &nbsp;|&nbsp; 
    Prototipo MVP v0.1 para validación con auditoras &nbsp;|&nbsp;
    <b>Solo para uso interno — no para publicación</b>
</div>
""", unsafe_allow_html=True)

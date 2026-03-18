import io
import json
import os
import re
import time
from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st
from google import generativeai as genai


st.set_page_config(
    page_title="BioExtract — Structured Literature Triage",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@300;400;500&display=swap');

:root {
    --bg:          #F8FAFC;
    --surface:     #FFFFFF;
    --surface-2:   #F1F5F9;
    --border:      #E2E8F0;
    --border-2:    #CBD5E1;
    --ink:         #0F172A;
    --ink-2:       #334155;
    --muted:       #64748B;
    --accent:      #2563EB;
    --accent-dim:  #EFF6FF;
    --accent-hover:#1D4ED8;
    --success:     #15803D;
    --success-bg:  #F0FDF4;
    --success-bd:  #86EFAC;
    --warning:     #92400E;
    --warning-bg:  #FFFBEB;
    --warning-bd:  #FDE68A;
    --danger:      #B91C1C;
    --danger-bg:   #FEF2F2;
    --danger-bd:   #FECACA;
    --shadow-sm:   0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
    --shadow-md:   0 4px 12px rgba(0,0,0,.08), 0 2px 4px rgba(0,0,0,.04);
    --radius:      8px;
    --radius-sm:   6px;
}

/* ── Base ─────────────────────────────────────────── */
.stApp {
    background: var(--bg) !important;
    color: var(--ink) !important;
    font-family: 'DM Sans', system-ui, sans-serif !important;
}

div.block-container {
    padding: 24px 32px !important;
    max-width: 720px !important;
    margin: 0 auto !important;
}

section[data-testid="stSidebar"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
.stDeployButton { visibility: hidden; }

/* ── File uploader — compact ──────────────────────── */
[data-testid="stFileUploader"] { padding: 0 !important; }
[data-testid="stFileUploader"] section {
    padding: 6px 10px !important;
    min-height: 38px !important;
    border-radius: var(--radius-sm) !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stFileUploader"] label { display: none !important; }

/* ── Primary button ──────────────────────────────── */
.stButton button[kind="primary"] {
    background: var(--accent) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    height: 40px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.2px !important;
    box-shadow: var(--shadow-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: background 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease !important;
}
.stButton button[kind="primary"]:hover {
    background: var(--accent-hover) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px) !important;
}
.stButton button[kind="primary"]:active {
    transform: translateY(1px) !important;
    box-shadow: 0 1px 2px rgba(0,0,0,.06) !important;
}
.stButton button[kind="primary"]:focus-visible {
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25) !important;
}

/* ── KPI metric cards ────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 16px 20px !important;
    box-shadow: var(--shadow-sm) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-md) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 26px !important;
    font-weight: 500 !important;
    color: var(--ink) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.7px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Section label ──────────────────────────────── */
.section-label {
    font-size: 11px;
    font-weight: 500;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin: 0 0 14px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
    font-family: 'DM Sans', sans-serif;
}

/* ── Status badges ──────────────────────────────── */
.status-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 2px 6px;
    border-radius: 4px;
    font-variant-numeric: tabular-nums;
}

/* ── Run button ──────────────────────────────────── */
div[data-testid="stButton"] > button[kind="primary"] {
    min-width: 160px !important;
    padding: 10px 32px !important;
    width: 100% !important;
}

/* ── Clear button — muted secondary ──────────────── */
div[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid var(--border-2) !important;
    color: var(--muted) !important;
    font-size: 12px !important;
    padding: 8px 12px !important;
    width: 100% !important;
    transition: border-color 0.15s, color 0.15s !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: var(--ink-2) !important;
    color: var(--ink-2) !important;
    background: transparent !important;
}

/* ── API key — max-width 400px, left-aligned ─────── */
div[data-testid="stTextInput"] input[type="password"] {
    max-width: 400px !important;
}

/* ── Reduce gap between controls row and textarea ── */
div[data-testid="stColumns"] {
    margin-bottom: 4px !important;
}

/* ── Progress bar — breathing room ──────────────── */
div[data-testid="stProgressBar"] {
    margin-top: 28px !important;
    margin-bottom: 8px !important;
}
div[data-testid="stProgressBar"] > div {
    border-radius: 4px !important;
}

/* ── Controls card ──────────────────────────────── */
.controls-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 20px;
    margin-bottom: 20px;
    box-shadow: var(--shadow-sm);
}

/* ── Text area ──────────────────────────────────── */
.stTextArea textarea {
    font-family: 'DM Sans', system-ui, sans-serif !important;
    font-size: 13px !important;
    line-height: 1.65 !important;
    color: var(--ink-2) !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    padding: 12px !important;
    resize: vertical !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
}
.stTextArea textarea::placeholder {
    color: var(--muted) !important;
    font-style: italic !important;
}

/* ── Verdict cards ──────────────────────────────── */
.verdict-ok,
.verdict-warning,
.verdict-critical {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    font-size: 13px;
    font-weight: 400;
    color: var(--ink-2);
    line-height: 1.6;
}
.verdict-ok    .verdict-title { color: var(--success); }
.verdict-warning .verdict-title { color: var(--warning); }
.verdict-critical .verdict-title { color: var(--danger); }

/* ── Signal pill badges ─────────────────────────── */
.alert-success { background: var(--success-bg); color: var(--success); padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; border: 1px solid var(--success-bd); }
.alert-warning { background: var(--warning-bg); color: var(--warning); padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; border: 1px solid var(--warning-bd); }
.alert-danger  { background: var(--danger-bg);  color: var(--danger);  padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; border: 1px solid var(--danger-bd);  }
.alert-clinical {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--border-2);
    padding: 10px 16px;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    box-shadow: var(--shadow-sm);
}
.alert-review     { border-left-color: var(--danger) !important; }
.alert-acceptable { border-left-color: #D97706 !important; }

/* ── Data table ─────────────────────────────────── */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
}
.stDataFrame thead th {
    background: var(--surface-2) !important;
    color: var(--muted) !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.7px !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 10px 12px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stDataFrame tbody tr { border-bottom: 1px solid var(--border) !important; transition: background 0.1s ease !important; }
.stDataFrame tbody tr:hover { background: var(--accent-dim) !important; }
.stDataFrame tbody td {
    font-size: 12px !important;
    color: var(--ink-2) !important;
    padding: 9px 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-variant-numeric: tabular-nums !important;
    white-space: normal !important;
    word-break: break-word !important;
    max-width: 220px !important;
}

/* ── JSON dark block ────────────────────────────── */
.json-display {
    background: #18181B;
    color: #A1A1AA;
    border-radius: var(--radius);
    padding: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 11.5px;
    line-height: 1.7;
    max-height: 500px;
    overflow-y: auto;
    border: 1px solid #27272A;
    white-space: pre-wrap;
}

/* ── Expander ───────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--surface) !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="stExpander"] summary {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--ink-2) !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: color 0.15s ease !important;
}
[data-testid="stExpander"] summary:hover {
    color: var(--ink) !important;
}

/* ── Select / text inputs ───────────────────────── */
[data-testid="stSelectbox"] select,
[data-testid="stTextInput"] input {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
    color: var(--ink) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
[data-testid="stSelectbox"] select:focus,
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
}

/* ── Tabs ───────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--muted) !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--ink) !important;
    border-bottom-color: var(--accent) !important;
}

/* ── Download button ────────────────────────────── */
[data-testid="stDownloadButton"] button {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--ink-2) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    box-shadow: var(--shadow-sm) !important;
    transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: var(--surface-2) !important;
    border-color: var(--border-2) !important;
    transform: translateY(-1px) !important;
    box-shadow: var(--shadow-md) !important;
}
[data-testid="stDownloadButton"] button:active {
    transform: translateY(1px) !important;
    box-shadow: 0 1px 2px rgba(0,0,0,.06) !important;
}

/* Progress bar */
.stProgress > div > div > div > div {
    background: linear-gradient(
        90deg, #2563EB, #3B82F6
    ) !important;
    border-radius: 4px !important;
}
.stProgress > div > div {
    background: #E4E4E7 !important;
    border-radius: 4px !important;
    height: 6px !important;
}
/* Texto de progreso */
.stProgress {
    margin-bottom: 4px !important;
}
/* Progress text — el container ocupa todo el ancho disponible */
.stProgress [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    min-width: 0 !important;
}
.stProgress [data-testid="stMarkdownContainer"] p {
    width: 100% !important;
    margin: 0 0 4px 0 !important;
    white-space: normal !important;
}

/* Separación entre barra y texto */
[data-testid="stText"] {
    font-size: 12px !important;
    color: #71717A !important;
    font-family: 'DM Sans', sans-serif !important;
    margin-top: 8px !important;
    display: block !important;
}

/* ── KPI band ───────────────────────────────────── */
.kpi-band {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 4px 0;
    margin-bottom: 20px;
    box-shadow: var(--shadow-sm);
}

/* ── Keyframes ──────────────────────────────────── */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0);   }
}
@keyframes pulseHex {
    0%, 100% { opacity: 0.15; }
    50%       { opacity: 0.28; }
}

/* ── Verdict cards — entrance ───────────────────── */
.verdict-ok,
.verdict-warning,
.verdict-critical {
    animation: fadeSlideUp 0.2s ease-out both;
}

/* ── Empty state icon — breathing ──────────────── */
.pulse-hex {
    font-size: 36px;
    animation: pulseHex 3s ease-in-out infinite;
}

/* ── Signal cards ───────────────────────────────── */
.signal-card {
    transition: border-left-width 0.15s ease, box-shadow 0.15s ease !important;
}
.signal-card:hover {
    border-left-width: 4px !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── Fragment source cards ──────────────────────── */
.fragment-card {
    transition: background 0.15s ease, box-shadow 0.15s ease !important;
}
.fragment-card:hover {
    box-shadow: var(--shadow-sm) !important;
    filter: brightness(0.98);
}

/* ── Reduced motion ─────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown('''
<div style="
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 18px 0 18px 0;
    margin-bottom: 20px;
    border-bottom: 1px solid #E4E4E7;
">
    <div style="
        width: 34px; height: 34px;
        background: #09090B;
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
    ">
        <span style="
            font-family: 'DM Mono', monospace;
            font-size: 12px;
            font-weight: 500;
            color: #FAFAFA;
            letter-spacing: -0.5px;
        ">BE</span>
    </div>
    <div style="display: flex; flex-direction: column; gap: 1px;">
        <span style="
            font-family: 'DM Sans', sans-serif;
            font-size: 15px;
            font-weight: 600;
            color: #09090B;
            letter-spacing: -0.3px;
            line-height: 1.2;
        ">BioExtract</span>
        <span style="
            font-family: 'DM Sans', sans-serif;
            font-size: 12px;
            font-weight: 400;
            color: #71717A;
            line-height: 1.2;
        ">Structured Literature Triage</span>
    </div>
    <span style="
        font-family: 'DM Mono', monospace;
        font-size: 10px;
        font-weight: 400;
        color: #71717A;
        background: #F4F4F5;
        border: 1px solid #E4E4E7;
        border-radius: 5px;
        padding: 2px 7px;
        align-self: center;
        margin-left: 2px;
    ">v1.2.28</span>
    <span style="
        font-size: 12px;
        color: #A1A1AA;
        font-family: 'DM Sans', sans-serif;
        margin-left: auto;
        padding-left: 20px;
        border-left: 1px solid #E4E4E7;
        line-height: 1.5;
        max-width: 420px;
        text-align: right;
    ">Extrae entidades biomédicas · Detecta anomalías matemáticas<br>
    No evalúa calidad metodológica · No reemplaza el paper original</span>
</div>
''', unsafe_allow_html=True)




run_button = False

# ── 1. TEXTAREA — acción primaria ────────────────────
_clear = st.session_state.pop("_clear_input", False)
abstract_text = st.text_area(
    "",
    placeholder="Introducir abstract científico para análisis biomédico...",
    height=160,
    key="abstract_input",
    value="" if _clear else st.session_state.get("abstract_input", "")
)

# ── 2. FILA: Modo + Ejecutar ─────────────────────────
ctrl_mode, ctrl_btn, ctrl_clear = st.columns([2, 3, 1])
with ctrl_mode:
    mode = st.radio(
        "modo",
        options=["Individual", "Masivo"],
        horizontal=True,
        label_visibility="collapsed"
    )
with ctrl_btn:
    run_button = st.button(
        "⬡  Ejecutar análisis",
        type="primary",
    )
with ctrl_clear:
    if st.session_state.get("last_results") is not None:
        if st.button("✕ Limpiar", help="Borrar análisis y empezar de nuevo"):
            st.session_state.last_results = None
            st.session_state.last_df = None
            st.session_state.last_json = None
            st.session_state["_clear_input"] = True
            st.rerun()

# ── 3. API KEY — secundario ──────────────────────────
user_api_key = st.text_input(
    "api_key_input",
    type="password",
    placeholder="Gemini API key  —  5 análisis gratuitos si la dejas en blanco",
    label_visibility="collapsed"
)

file_df = pd.DataFrame()
selected_column = None
uploaded_file = None


def load_file_data(uploaded_file) -> pd.DataFrame:
    if uploaded_file is None:
        return pd.DataFrame()
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(uploaded_file)
    raise ValueError("Formato no soportado. Usa CSV o Excel.")


if mode == "Masivo":
    st.markdown(
        '<div class="section-label">ARCHIVO CSV / EXCEL</div>',
        unsafe_allow_html=True
    )
    up1, up2 = st.columns([3, 2])
    with up1:
        uploaded_file = st.file_uploader(
            "CSV/Excel",
            type=["csv", "xlsx", "xls"],
            accept_multiple_files=False,
            label_visibility="collapsed"
        )
    with up2:
        if uploaded_file is not None:
            try:
                file_df = load_file_data(uploaded_file)
                if file_df.empty:
                    st.warning("⚠️ Archivo vacío")
                else:
                    selected_column = st.selectbox(
                        "Columna de abstracts",
                        options=list(file_df.columns)
                    )
                    st.caption(f"✅ {len(file_df)} registros cargados")
            except Exception as exc:
                st.error(f"❌ Error: {exc}")

model_preference = "Automático (recomendado)"


def build_prompt(abstract: str) -> str:
    return f"""
Extrae entidades biomedicas del siguiente abstract.

REGLAS:
1. Extrae biomarcadores, grupos demograficos y metricas estadisticas.
2. Para subtipos clinicos agrupados, descompón en biomarcadores implicitos:
   - hormone receptor-positive → ER+, PR+ (inferido)
   - triple-negative → ER-, PR-, HER2- (inferido)
   - HER2-positive → ERBB2 amplificado (inferido)
   Aplica esta logica para cualquier patologia.
3. Captura TODOS los numeros del texto: porcentajes, tasas, HR, OR, p-values.
   Cada numero debe estar asociado a la entidad correcta.
   REGLA ESPECIAL para comparativas:
   - "38% higher mortality than X" → mortalidad_pct=38 (diferencial vs referencia)
   - "5% lower incidence than X" → incidencia_anual_pct=-5 (negativo = menor)
   - "10% less likely" → diagnostico_estadio_pct=-10
   Siempre captura el número aunque sea una comparación relativa.
4. REGLA CAUSAL: asigna una metrica a una entidad SOLO si el texto
   lo relaciona directamente. Preserva cualificadores: "partly",
   "only", "significantly".
5. REGLA OBLIGATORIA — INTERVALOS DE CONFIANZA:
   Si el texto menciona un IC, CI, 95% CI, confidence interval,
   o cualquier rango entre paréntesis asociado a HR, OR, RR:
   - Extrae SIEMPRE los límites como campos separados en metricas:
     ci_lower: valor_numérico_inferior
     ci_upper: valor_numérico_superior
   - Nunca los omitas aunque ya estén en el texto del fragmento
   - Nunca los metas solo en el campo 'otros'
   - Ejemplo: 'HR=0.73 (95% CI 0.74-0.89)' →
     HR=0.73, ci_lower=0.74, ci_upper=0.89
6. Genera señales_prioritarias para hallazgos relevantes:
   paradojas, disparidades, tendencias emergentes, vacios de conocimiento.

REGLA 7 — riesgo_omision:
Asigna "CRÍTICO" SOLO si el valor numérico extraído es matemáticamente imposible:
- Supervivencia o cualquier porcentaje > 100
- HR <= 0
- OR <= 0
- NNT < 1
- p-value < 0 o p-value > 1
- Intervalo de confianza donde ci_lower >= ci_upper
Asigna "Aceptable" en TODOS los demás casos, incluyendo:
- Texto libre sin número concreto ("significant increase", "continues to rise",
  "leading causes", cualquier descripción cualitativa)
- Porcentajes entre 0% y 100%
- Valores posibles aunque sean altos o bajos dentro de su rango fisiológico

REGLA 8 — CONTAMINACIÓN DE PROTOCOLO:
Si el abstract menciona cualquier parámetro de procesamiento
de muestras, extráelo como entidad separada con tipo="protocolo"
y relacion_causal="contaminacion". No lo omitas aunque parezca
irrelevante. Ejemplos de lo que debes capturar:
- Temperaturas de almacenamiento o procesamiento ("stored at -20°C",
  "processed at 37°C", "room temperature")
- Velocidades de centrifugación ("centrifuged at 1500 rpm")
- Tiempos de incubación ("incubated for 48 hours")
- Condiciones instrumentales ("absorbance at 450nm")
- Concentraciones de reactivos ("0.1% Triton X-100")
Cualquier valor que describa cómo se procesó la muestra,
no qué le ocurre al paciente o al tejido biológico.

REGLA 9 — TIPO DE ESTUDIO:
Detecta y clasifica el tipo de estudio del abstract. Usa uno de estos
valores exactos en los campos "tipo_estudio" de metadata y resumen_ejecutivo:
- "in_vitro"           (líneas celulares, cultivos, ensayos en placa)
- "in_vivo"            (modelo animal: ratón, rata, primate, zebrafish)
- "clinico_fase1"      (fase I, first-in-human, dose-escalation)
- "clinico_fase2"      (fase II, proof-of-concept, piloto clínico)
- "clinico_fase3"      (fase III, confirmatory trial)
- "rct"                (randomized controlled trial, RCT, aleatorizado con control)
- "meta_analisis"      (meta-analysis, systematic review, revisión sistemática)
- "revision_narrativa" (narrative review, revisión narrativa, expert review)
- "epidemiologico"     (cohorte, caso-control, registro, prevalencia, incidencia)
- "desconocido"        (si no puede determinarse con certeza)

REGLA 10 — GAP DE TRASLACIÓN CLÍNICA:
Basándote en el tipo_estudio detectado, asigna gaps_criticos["traslacion_clinica"]:
- Si tipo_estudio = "in_vitro": "Estudio preclínico — resultados obtenidos en líneas celulares. No trasladables directamente a pacientes. Requiere validación clínica."
- Si tipo_estudio = "in_vivo": "Estudio preclínico — resultados obtenidos en modelo animal. No trasladables directamente a pacientes. Requiere validación clínica."
- En cualquier otro caso (clinico, rct, meta_analisis, revision_narrativa, epidemiologico, desconocido): "NO APLICA"

REGLA 11 — NIVEL DE EVIDENCIA POR ENTIDAD:
El campo "nivel_evidencia" de cada entidad en entidades_de_riesgo debe reflejar
el tipo_estudio detectado para el abstract completo:
- "in_vitro"                                  → "preclínico_in_vitro"
- "in_vivo"                                   → "preclínico_in_vivo"
- "rct" / "clinico_fase3" / "meta_analisis"   → "clinico_alto"
- "clinico_fase1" / "clinico_fase2"           → "clinico_exploratorio"
- "revision_narrativa"                        → "narrativo"
- "epidemiologico"                            → "epidemiologico"
- "desconocido"                               → "desconocido"

FORMATO JSON (respeta las claves exactas):
{{
  "entidades_de_riesgo": [
    {{
      "nombre": "nombre exacto del texto",
      "tipo": "molecular|demografico|epidemiologico|clinico|protocolo",
      "resolucion": "literal|agregado_clinico|epidemiologico",
      "biomarcadores_implicitos": [
        {{"marcador": "ER+", "estado": "inferido"}}
      ],
      "metricas": {{
        "p_value": null,
        "HR": null,
        "OR": null,
        "ci_lower": null,
        "ci_upper": null,
        "LFC": null,
        "incidencia_anual_pct": null,
        "mortalidad_pct": null,
        "tasa_100k": null,
        "reduccion_mortalidad_pct": null,
        "diagnostico_estadio_pct": null,
        "n_absoluto": null,
        "otros": "string con metricas no clasificables o null"
      }},
      "poblacion_afectada": ["grupo"],
      "relacion_causal": "causal|correlacional|asociativo|parcial",
      "cualificador_original": "texto con partly/only/significantly si existe",
      "nivel_evidencia": "preclínico_in_vitro|preclínico_in_vivo|clinico_alto|clinico_exploratorio|narrativo|epidemiologico|desconocido",
      "riesgo_omision": "CRÍTICO|Aceptable",
      "fragmento_fuente": "texto exacto del abstract"
    }}
  ],
  "señales_prioritarias": [
    {{
      "tipo": "paradoja|disparidad|tendencia_emergente|vacio_conocimiento",
      "descripcion": "descripcion concisa del hallazgo",
      "poblacion_afectada": ["grupo"],
      "impacto_clinico": "alto|medio|bajo"
    }}
  ],
  "gaps_criticos": {{
    "microbiota": "NO DISPONIBLE",
    "biomarcadores_moleculares": "descripcion o NO DISPONIBLE",
    "metricas_estadisticas": "descripcion o NO DISPONIBLE",
    "traslacion_clinica": "segun REGLA 10"
  }},
  "metadata": {{
    "nivel_evidencia": "epidemiologico|clinico|in_vitro|meta-analisis",
    "tipo_estudio": "in_vitro|in_vivo|clinico_fase1|clinico_fase2|clinico_fase3|rct|meta_analisis|revision_narrativa|epidemiologico|desconocido"
  }},
  "resumen_ejecutivo": {{
    "tipo_estudio": "mismo valor que metadata.tipo_estudio"
  }}
}}

ABSTRACT: {abstract}

Responde SOLO con JSON valido. Sin explicaciones. Sin markdown.
"""


def parse_json_response(raw_text: str) -> Dict[str, Any]:
    raw_text = raw_text.strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", raw_text)
        if not match:
            return {"results": []}
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"results": []}


def _safe_string(value: Any) -> str:
    """Converteix qualsevol valor a string de forma segura."""
    if value is None:
        return ""
    return str(value).strip()


def _safe_list(value: Any) -> List[str]:
    """Converteix qualsevol valor a llista de strings de forma segura."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _safe_float(value: Any) -> float:
    """Converteix qualsevol valor a float de forma segura."""
    if value is None:
        return None
    try:
        if isinstance(value, str):
            # Netejar strings amb percentatges o altres caràcters
            cleaned = value.replace('%', '').replace(',', '.').strip()
            if not cleaned:
                return None
            return float(cleaned)
        return float(value)
    except (ValueError, TypeError):
        return None


def _safe_float_absolute(value: Any) -> float:
    """Para números absolutos grandes con coma de miles (517,900 → 517900.0)"""
    if value is None:
        return None
    try:
        if isinstance(value, str):
            # Eliminar comas de miles ANTES de convertir
            cleaned = value.replace(',', '').replace('%', '').strip()
            if not cleaned:
                return None
            return float(cleaned)
        return float(value)
    except (ValueError, TypeError):
        return None


def _safe_int(value: Any) -> int:
    """Converteix qualsevol valor a int de forma segura."""
    if value is None:
        return None
    try:
        if isinstance(value, str):
            cleaned = value.replace(',', '').strip()
            if not cleaned:
                return None
            return int(float(cleaned))  # Primer a float per gestionar decimals
        return int(float(value))
    except (ValueError, TypeError):
        return None


def validate_biomedical_coherence(text: str) -> Tuple[bool, str]:
    content = (text or "").strip()
    if not content or len(content) < 30:
        return False, "Dato No Fiable: texto insuficiente para análisis."

    # Filtro relajado: solo bloquea basura real, no abstracts científicos legítimos
    garbage_patterns = [
        r"^[^a-zA-Z]*$",  # Solo números/símbolos
        r"\b(fuck|shit|damn|idiot|stupid)\b",  # Insultos obvios
        r"^(hola|hello|hi|test|prueba)[\s\.,!]*$",  # Saludos simples
        r"^\d+[\s\+\-\*\/\=\(\)]*\d*$",  # Solo operaciones matemáticas
    ]
    
    for pattern in garbage_patterns:
        if re.search(pattern, content, flags=re.IGNORECASE):
            return False, "Dato No Fiable: contenido no válido para extracción científica."
    
    # Señales de estructura científica (muy permisivo)
    scientific_signals = [
        r"\b(study|studies|research|analysis|patient|subjects?|method|result|conclusion)\b",
        r"\b(p[\s-]?value|p[\s<>=]+\d|significant|correlation|association)\b",
        r"\b(treatment|therapy|drug|medication|intervention|control|placebo)\b",
        r"\b(protein|gene|biomarker|enzyme|hormone|antibody|receptor)\b",
        r"\b(disease|syndrome|condition|disorder|pathology|diagnosis)\b",
        r"\b(clinical|trial|cohort|randomized|double[\s-]?blind|prospective)\b",
        r"\b(abstract|background|objective|methods?|results?|conclusions?)\b",
    ]
    
    # Si tiene al menos UNA señal científica, lo acepta
    for pattern in scientific_signals:
        if re.search(pattern, content, flags=re.IGNORECASE):
            return True, ""
    
    # Si no tiene señales científicas pero tampoco es basura obvia, lo acepta (muy permisivo)
    if len(content) > 100:  # Textos largos probablemente son legítimos
        return True, ""
    
    return False, "Dato No Fiable: contenido no identificable como texto científico."


# ═══════════════════════════════════════════════════════
# SISTEMA DE VALIDACIÓN BIOMÉDICA UNIVERSAL
# Capa 1: Límites físicos absolutos
# Capa 2: Coherencia semántica por tipo de métrica  
# Capa 3: Coherencia interna entre métricas
# ═══════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════
# PARSER DE CAMPO "otros"
# Extrae pares (clave, valor) de strings como:
# "NNT=0.8", "340 mg/dL", "95% CI 0.74-0.89", "58%"
# Se ejecuta ANTES de cualquier validación
# ═══════════════════════════════════════════════════════

def parse_otros_field(otros_raw: str) -> Dict[str, Any]:
    """
    Extrae valores del campo 'otros' para los 6 invariantes matemáticos.
    Solo CLAVE=VALOR numérico y CI bounds — sin concentraciones ni porcentajes sueltos.
    """
    if not isinstance(otros_raw, str) or not otros_raw:
        return {}

    extracted = {}

    # Patrón 1 — CLAVE=VALOR numérico: "NNT=0.8", "HR=1.2"
    for match in re.finditer(r'([A-Za-z][A-Za-z0-9_/\-]*)\s*=\s*(-?\d+(?:\.\d+)?)', otros_raw):
        key = match.group(1).strip()
        val = _safe_float(match.group(2))
        if val is not None:
            extracted[key] = val

    # Patrón 2 — CI bounds: "CI 0.58-0.99", "95% CI 0.74-0.89"
    ci_match = re.search(r'CI\s*[=:]?\s*(-?\d+(?:\.\d+)?)\s*[-–]\s*(-?\d+(?:\.\d+)?)', otros_raw, re.IGNORECASE)
    if ci_match:
        extracted["ci_lower"] = _safe_float(ci_match.group(1))
        extracted["ci_upper"] = _safe_float(ci_match.group(2))

    return extracted


def enrich_metricas_from_otros(entidad: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriquece el dict de métricas con valores extraídos de 'otros'.
    Modifica entidad in-place y retorna las métricas enriquecidas.
    """
    metricas = entidad.get("metricas", {})
    if not isinstance(metricas, dict):
        metricas = {}

    otros_raw = metricas.get("otros", "")
    parsed = parse_otros_field(str(otros_raw))

    # Merge — solo añade claves que no existen ya en metricas
    for key, val in parsed.items():
        if key not in metricas:
            metricas[f"otros_{key}"] = val

    # Casos con nombre canónico conocido — normalizar
    canonical_map = {
        "NNT": "NNT",
        "nnt": "NNT",
        "ci_lower": "ci_lower",
        "ci_upper": "ci_upper",
    }
    for src, dst in canonical_map.items():
        if src in parsed and dst not in metricas:
            metricas[dst] = parsed[src]

    # Normalizar NNT a clave canónica siempre
    for key in list(metricas.keys()):
        if "NNT" in key.upper() and key != "NNT":
            val = _safe_float(metricas[key])
            if val is not None:
                metricas["NNT"] = val
                break

    entidad["metricas"] = metricas
    return metricas


def validate_physical_limits_hierarchical(entidad: Dict[str, Any]) -> List[str]:
    """
    Valida los 6 invariantes matemáticos universales.
    Solo errores físicos absolutos — matemáticamente imposibles en cualquier contexto.
    """
    errors = []
    metricas = entidad.get("metricas", {})
    if not isinstance(metricas, dict):
        return errors

    nombre = entidad.get("nombre", "DESCONOCIDO")

    # Extraer ci_lower/ci_upper si no existen — buscar en metricas_completas y fragmento_fuente
    if _safe_float(metricas.get("ci_lower")) is None or _safe_float(metricas.get("ci_upper")) is None:
        patron_ci = re.compile(
            r'CI\s*[=:]?\s*(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)',
            re.IGNORECASE
        )
        for texto in [
            str(entidad.get("metricas_completas", "")),
            str(entidad.get("fragmento_fuente", "")),
        ]:
            if not texto:
                continue
            m = patron_ci.search(texto)
            if m:
                lower_val = _safe_float(m.group(1))
                upper_val = _safe_float(m.group(2))
                if lower_val is not None and upper_val is not None:
                    if metricas.get("ci_lower") is None or _safe_float(metricas.get("ci_lower")) is None:
                        metricas["ci_lower"] = lower_val
                    if metricas.get("ci_upper") is None or _safe_float(metricas.get("ci_upper")) is None:
                        metricas["ci_upper"] = upper_val
                    break

    # 1. p-value fuera de [0.0, 1.0]
    p = _safe_float(metricas.get("p_value"))
    if p is not None and (p < 0.0 or p > 1.0):
        errors.append(
            f"Anomalía matemática: p-value={p} fuera de [0, 1] para '{nombre}' — imposible"
        )
        metricas["p_value"] = None

    # 2. HR <= 0
    hr = _safe_float(metricas.get("HR"))
    if hr is not None and hr <= 0:
        errors.append(
            f"Anomalía matemática: HR={hr} ≤ 0 para '{nombre}' — Hazard Ratio siempre positivo"
        )
        metricas["HR"] = None

    # 3. OR <= 0
    or_val = _safe_float(metricas.get("OR"))
    if or_val is not None and or_val <= 0:
        errors.append(
            f"Anomalía matemática: OR={or_val} ≤ 0 para '{nombre}' — Odds Ratio siempre positivo"
        )
        metricas["OR"] = None

    # 4. NNT < 1.0
    nnt = _safe_float(metricas.get("NNT"))
    if nnt is not None and nnt < 1.0:
        errors.append(
            f"Anomalía matemática: NNT={nnt} < 1 para '{nombre}' — NNT mínimo teórico es 1"
        )
        metricas["NNT"] = None

    # 5. IC invertido: ci_lower >= ci_upper
    ci_lower = _safe_float(metricas.get("ci_lower"))
    ci_upper = _safe_float(metricas.get("ci_upper"))
    if ci_lower is not None and ci_upper is not None and ci_lower >= ci_upper:
        errors.append(
            f"Anomalía matemática: IC=[{ci_lower}, {ci_upper}] invertido para '{nombre}' — imposible"
        )
        metricas["ci_lower"] = None
        metricas["ci_upper"] = None

    # 6. HR fuera de su propio IC
    if ci_lower is not None and ci_upper is not None and hr is not None:
        if hr < ci_lower or hr > ci_upper:
            errors.append(
                f"Anomalía matemática: HR={hr} fuera de su IC=[{ci_lower}, {ci_upper}] para '{nombre}'"
            )

    # 7. Porcentaje/supervivencia > 100 en campos numéricos de tasa
    PCT_KEYS = [
        "mortalidad_pct", "incidencia_anual_pct", "diagnostico_estadio_pct",
        "reduccion_mortalidad_pct", "supervivencia", "mortalidad",
    ]
    for pct_key in PCT_KEYS:
        pct_val = _safe_float(metricas.get(pct_key))
        if pct_val is not None and pct_val > 100.0:
            errors.append(
                f"Anomalía matemática: {pct_key}={pct_val}% > 100 para '{nombre}' — imposible"
            )
            metricas[pct_key] = None

    # 8. Porcentaje > 100 en campo otros (texto libre)
    #    Solo se marca CRÍTICO si se extrae un número concreto Y es > 100.
    #    "up to 90% survival rate" → pct=90 ≤ 100 → NO CRÍTICO
    #    "OS=127%"                 → pct=127 > 100 → CRÍTICO
    otros_valor = str(metricas.get("otros", "") or "")
    if otros_valor:
        match_pct = re.search(r'(\d+\.?\d*)\s*%', otros_valor)
        if match_pct:
            pct = float(match_pct.group(1))
            if pct > 100.0:
                errors.append(
                    f"Anomalía matemática: porcentaje={pct}% > 100 en campo 'otros' para '{nombre}' — imposible"
                )

    entidad["metricas"] = metricas
    return errors


def generate_signals_from_errors(
    entidades: List[Dict[str, Any]],
    validation_errors: List[str]
) -> List[Dict[str, Any]]:
    """
    Genera señales automáticas solo para entidades con riesgo_omision="CRÍTICO".
    Usa la descripción exacta del invariante violado desde validation_errors.
    """
    signals = []

    for entidad in entidades:
        if _safe_string(entidad.get("riesgo_omision", "")) != "CRÍTICO":
            continue

        nombre = entidad.get("nombre", "DESCONOCIDO")
        poblacion = entidad.get("poblacion_afectada", [])

        # Buscar el error de validación que corresponde a esta entidad
        for err in validation_errors:
            if nombre in err or f"'{nombre}'" in err:
                descripcion = err
                signals.append({
                    "tipo": "paradoja",
                    "descripcion": descripcion,
                    "poblacion_afectada": str(poblacion),
                    "impacto_clinico": "alto",
                    "origen": "validador_automatico"
                })
                break

    return signals


def merge_signals(
    signals_gemini: List[Dict],
    signals_validator: List[Dict]
) -> List[Dict]:
    """
    Combina señales de Gemini con señales del validador.
    Las señales del validador van PRIMERO — son deterministas.
    Elimina duplicados semánticos obvios.
    """
    # Señales del validador primero
    merged = list(signals_validator)

    # Añadir señales de Gemini que no estén ya cubiertas
    validator_keywords = set()
    for s in signals_validator:
        desc = s.get("descripcion", "").lower()
        # Extraer keywords de la descripción para dedup semántico
        for word in ["nnt", "hr=", "or=", "p-value", "ic", "protocolo", "centrifug", "temperatura"]:
            if word in desc:
                validator_keywords.add(word)

    for signal in signals_gemini:
        desc = signal.get("descripcion", "").lower()
        # Solo añadir si no es redundante con una señal del validador
        is_duplicate = any(kw in desc for kw in validator_keywords)
        if not is_duplicate:
            merged.append(signal)

    return merged


def coerce_payload(data: Dict[str, Any], abstract_text: str = "") -> Dict[str, Any]:
    """Procesa y valida el payload JSON jerárquico de alta densidad."""
    if not data:
        return {
            "metadata": {},
            "entidades_de_riesgo": [],
            "señales_prioritarias": [],
            "gaps_criticos": {},
            "validacion_alertas": []
        }
    
    validation_errors = []
    
    # Procesar metadata
    metadata = data.get("metadata", {})
    processed_metadata = {
        "doi": _safe_string(metadata.get("doi")),
        "fuente": _safe_string(metadata.get("fuente")),
        "nivel_evidencia": _safe_string(metadata.get("nivel_evidencia", "desconocido")),
        "periodo_datos": _safe_string(metadata.get("periodo_datos")),
        "tipo_estudio": _safe_string(metadata.get("tipo_estudio"))
    }
    
    # Procesar entidades de riesgo con exhaustividad (con fallback para compatibilidad)
    entidades = data.get("entidades_de_riesgo") or data.get("entitats_de_risc", [])
    processed_entidades = []
    
    for entidad in entidades if isinstance(entidades, list) else []:
        if not isinstance(entidad, dict):
            continue
            
        nombre = (entidad.get("nombre") or entidad.get("nom") or "").strip()
        if not nombre:
            continue
            
        # Procesar métricas de la entidad
        metricas = entidad.get("metricas") or entidad.get("metriques") or {}
        processed_metricas = {}
        
        if isinstance(metricas, dict):
            # Procesar métricas estándar
            NUMERIC_KEYS = {
                "HR", "OR", "p_value", "LFC", "IC95", "NNT",
                "ci_lower", "ci_upper",
                "incidencia_anual_pct", "mortalidad_pct",
                "tasa_100k", "reduccion_mortalidad_pct",
                "diagnostico_estadio_pct", "n_absoluto"
            }

            for key, value in metricas.items():
                if key == "n_absoluto":
                    processed_metricas[key] = _safe_float_absolute(value)
                elif key in NUMERIC_KEYS:
                    processed_metricas[key] = _safe_float(value)
                elif key == "otros":
                    # Intentar extraer números de strings como "38% higher"
                    if isinstance(value, str) and value:
                        nums = re.findall(r'-?\d+(?:\.\d+)?', value)
                        if nums:
                            processed_metricas[key] = value  # guardar string original
                        else:
                            processed_metricas[key] = _safe_string(value)
                    else:
                        processed_metricas[key] = _safe_string(value)
                elif key == "otros" and isinstance(value, dict):
                    # Procesar sub-métricas en "otros" - ahora también numéricas si corresponde
                    for sub_key, sub_value in value.items():
                        # Validación semántica para evitar errores como "517.900 muertes" → "517.9% mortalidad"
                        if sub_key in ["muertes_evitadas", "muertes", "deaths", "casos", "pacientes"]:
                            # Estas son cantidades absolutas, no porcentajes
                            processed_metricas[sub_key] = _safe_float(sub_value)
                        elif sub_key in ["mortalidad", "supervivencia", "incidencia", "incidencia_anual",
                                        "tasa_100k", "tasa_por_100k", "aumento_anual", "reduccion_mortalidad"]:
                            # Estas son tasas/porcentajes - validar rango
                            val = _safe_float(sub_value)
                            if val is not None and val > 100 and sub_key in ["mortalidad", "supervivencia", "incidencia_anual"]:
                                # Probable error: número absoluto interpretado como porcentaje
                                processed_metricas[f"{sub_key}_absoluto"] = val
                            else:
                                processed_metricas[sub_key] = val
                        else:
                            processed_metricas[sub_key] = _safe_string(sub_value)
                else:
                    processed_metricas[key] = _safe_string(value)
        
        processed_entidad = {
            "nombre": nombre,
            "tipo": _safe_string(entidad.get("tipo", "desconocido")),
            "resolucion": _safe_string(entidad.get("resolucion", "literal")),
            "biomarcadores_implicitos": _safe_list(entidad.get("biomarcadores_implicitos", [])),
            "es_literal": "true",  # Por defecto literal
            "metricas": processed_metricas,
            "poblacion_afectada": _safe_list(entidad.get("poblacion_afectada", [])),
            "relacion_causal": _safe_string(entidad.get("relacion_causal", "correlacional")),
            "calificador_original": _safe_string(entidad.get("cualificador_original") or entidad.get("calificador_original", "")),
            "estado_validacion": "OK",  # Por defecto OK
            "riesgo_omision": "Aceptable",  # Por defecto aceptable
            "nivel_evidencia": _safe_string(entidad.get("nivel_evidencia", "epidemiologico")),
            "fragmento_fuente": _safe_string(entidad.get("fragmento_fuente", ""))
        }
        
        # Enriquecer desde campo otros
        enrich_metricas_from_otros(processed_entidad)

        # Validación — solo 6 invariantes matemáticos universales
        layer1_errors = validate_physical_limits_hierarchical(processed_entidad)

        if layer1_errors:
            processed_entidad["riesgo_omision"] = "CRÍTICO"
            processed_entidad["estado_validacion"] = "🚨"

        validation_errors.extend(layer1_errors)
        processed_entidades.append(processed_entidad)
    
    # Procesar señales prioritarias (con fallback)
    señales = data.get("señales_prioritarias") or data.get("senyals_prioritaries", [])
    processed_señales = []
    
    for señal in señales if isinstance(señales, list) else []:
        if isinstance(señal, dict):
            processed_señal = {
                "tipo": _safe_string(señal.get("tipo", "desconocido")),
                "descripcion": _safe_string(señal.get("descripcion", "")),
                "poblacion_afectada": _safe_string(señal.get("poblacion_afectada", "")),
                "impacto_clinico": _safe_string(señal.get("impacto_clinico", "desconocido"))
            }
            processed_señales.append(processed_señal)

    # Generar señales desde errores del validador
    signals_from_validator = generate_signals_from_errors(
        processed_entidades,
        validation_errors
    )

    # Merge — validador primero (deterministas), luego Gemini (sin duplicados)
    processed_señales = merge_signals(processed_señales, signals_from_validator)
    
    # Procesar gaps críticos (con fallback)
    gaps = data.get("gaps_criticos") or data.get("gaps_critics", {})
    processed_gaps = {
        "microbiota": _safe_string(gaps.get("microbiota", "NO DISPONIBLE")),
        "biomarcadores_moleculares": _safe_string(gaps.get("biomarcadores_moleculares", "NO DISPONIBLE")),
        "metricas_estadisticas": _safe_string(gaps.get("metricas_estadisticas", "NO DISPONIBLE")),
        "datos_genomicos": _safe_string(gaps.get("datos_genomicos", "NO DISPONIBLE")),
        "interacciones_farmacologicas": _safe_string(gaps.get("interacciones_farmacologicas", "NO DISPONIBLE"))
    }
    
    return {
        "metadata": processed_metadata,
        "entidades_de_riesgo": processed_entidades,
        "señales_prioritarias": processed_señales,
        "gaps_criticos": processed_gaps,
        "validacion_alertas": validation_errors
    }


def analyze_orphan_data(abstract: str, extracted_results: List[Dict[str, Any]], auditoria: Dict[str, Any]) -> List[str]:
    """Auditoria de literalitat intel·ligent: detecta mètriques perdudes sense inventar biomarcadors"""
    import re
    
    orphan_alerts = []
    
    # Detectar mètriques numèriques no capturades
    numeric_pattern = r'\b\d+(?:\.\d+)?%?\b'
    found_numbers = set(re.findall(numeric_pattern, abstract))
    captured_numbers = set()
    
    for result in extracted_results:
        metricas = result.get("metricas", {})
        for key, value in metricas.items():
            if value is not None:
                captured_numbers.add(str(value))
    
    # Filtrar números massa petits o anys
    relevant_numbers = {n for n in found_numbers 
                       if len(n) > 1 and not n.startswith("0") 
                       and not (n.isdigit() and 1900 <= int(n) <= 2030)}
    
    uncaptured_numbers = relevant_numbers - captured_numbers
    if len(uncaptured_numbers) > 3:
        orphan_alerts.append(f"Mètriques numèriques no associades: {', '.join(list(uncaptured_numbers)[:6])}")
    
    # Detectar subtipus moleculars mencionats però no capturats
    text_lower = abstract.lower()
    molecular_subtypes = [
        "hormone receptor-positive", "hormone receptor positive", "hr-positive",
        "triple-negative", "triple negative", "tnbc",
        "her2-positive", "her2 positive", "her2-negative",
        "luminal a", "luminal b", "basal-like"
    ]
    
    found_subtypes = [subtype for subtype in molecular_subtypes if subtype in text_lower]
    captured_biomarcadores = [result.get("biomarcador", "").lower() for result in extracted_results]
    
    missing_subtypes = []
    for subtype in found_subtypes:
        if not any(subtype in captured for captured in captured_biomarcadores):
            missing_subtypes.append(subtype)
    
    if missing_subtypes:
        orphan_alerts.append(f"Subtipus moleculars no capturats: {', '.join(missing_subtypes)}")
    
    # Verificar cobertura adequada sense ser excessiu
    text_length = len(abstract.split())
    num_results = len(extracted_results)
    
    # Per abstracts epidemiològics, esperem menys registres que per abstracts moleculars
    if text_length > 200 and num_results == 0:
        orphan_alerts.append("POSSIBLE SUBEXTRACCIÓ: Text llarg sense biomarcadors capturats")
    
    return orphan_alerts


def analyze_hierarchical_density(abstract: str, entidades: List[Dict[str, Any]], gaps: Dict[str, Any]) -> List[str]:
    """Analiza la densidad de información y detecta posibles omisiones en la extracción jerárquica."""
    import re
    
    density_alerts = []
    abstract_length = len(abstract.split())
    
    # Detectar números decimales no capturados
    decimal_pattern = r'\b\d+\.\d+\b'
    decimals_in_text = re.findall(decimal_pattern, abstract)
    
    # Detectar percentatges no capturats
    percentage_pattern = r'\b\d+(?:\.\d+)?%\b'
    percentages_in_text = re.findall(percentage_pattern, abstract)
    
    # Verificar si hi ha mètriques perdudes
    captured_metrics = []
    for entidad in entidades:
        metricas = entidad.get("metricas", {})
        for key, value in metricas.items():
            if value is not None:
                captured_metrics.append(str(value))
    
    uncaptured_decimals = [d for d in decimals_in_text if d not in captured_metrics]
    uncaptured_percentages = [p for p in percentages_in_text if p.replace('%', '') not in captured_metrics]
    
    if len(uncaptured_decimals) > 2:
        density_alerts.append(f"ALERTA DENSITAT: {len(uncaptured_decimals)} números decimals no capturats: {', '.join(uncaptured_decimals[:3])}...")
    
    if len(uncaptured_percentages) > 1:
        density_alerts.append(f"ALERTA DENSITAT: {len(uncaptured_percentages)} percentatges no capturats: {', '.join(uncaptured_percentages[:2])}...")
    
    # Detectar possibles biomarcadors perduts
    biomarker_patterns = [
        r'\b[A-Z]{2,}\d*\b',  # Patró típic de biomarcadors (ex: ER, PR, HER2)
        r'\b\w+\s+receptor\b',  # Receptors
        r'\b\w+\s+protein\b',   # Proteïnes
        r'\b\w+\s+gene\b'       # Gens
    ]
    
    potential_biomarkers = set()
    for pattern in biomarker_patterns:
        matches = re.findall(pattern, abstract, re.IGNORECASE)
        potential_biomarkers.update(matches)
    
    captured_entities = {e.get("nombre", "").lower() for e in entidades}
    uncaptured_biomarkers = [b for b in potential_biomarkers if b.lower() not in captured_entities]
    
    if len(uncaptured_biomarkers) > 0:
        density_alerts.append(f"POSSIBLE SUBEXTRACCIÓ: Entitats potencials no capturades: {', '.join(list(uncaptured_biomarkers)[:3])}")
    
    # Alertes de densitat global
    if abstract_length > 200 and len(entidades) == 0:
        density_alerts.append("ALERTA CRÍTICA: Text llarg sense entitats capturades - Revisió manual obligatòria")
    elif abstract_length > 100 and len(entidades) < 2:
        density_alerts.append("ALERTA DENSITAT: Possible subextracció en text dens")
    
    return density_alerts


def detect_study_type(metadata: Dict[str, Any]) -> str:
    """Detecta el tipo de estudio desde metadata."""
    nivel = _safe_string(metadata.get("nivel_evidencia","")).lower()
    tipo  = _safe_string(metadata.get("tipo_estudio","")).lower()
    texto = f"{nivel} {tipo}"

    if any(k in texto for k in ["meta-analysis","systematic review"]):
        return "meta_analisis"
    if any(k in texto for k in ["randomized","rct","trial","placebo","double-blind","phase"]):
        return "rct"
    if any(k in texto for k in ["in vitro","in vivo","rna-seq","genomic","lfc","fold change"]):
        return "molecular"
    return "epidemiologico"


def calculate_hierarchical_confidence(
    entidades: List[Dict[str, Any]], 
    señales: List[Dict[str, Any]], 
    gaps: Dict[str, Any],
    metadata: Dict[str, Any] = None
) -> Tuple[int, str]:
    """
    Calcula confianza relativa al tipo de estudio.
    Retorna (score, tipo_estudio_detectado)
    """
    metadata = metadata or {}
    
    # ── DETECTAR TIPO DE ESTUDIO ──────────────────────────────────────
    nivel = _safe_string(metadata.get("nivel_evidencia", "")).lower()
    tipo  = _safe_string(metadata.get("tipo_estudio", "")).lower()
    
    keywords_epidemiologico = ["epidemiolog", "estadistic", "statistic", "registry",
                                "surveillance", "poblacional", "population"]
    keywords_rct            = ["randomized", "rct", "trial", "placebo", "double-blind",
                                "fase", "phase"]
    keywords_molecular      = ["in vitro", "in vivo", "rna-seq", "proteom", "genomic",
                                "cell line", "lfc", "fold change"]
    keywords_meta           = ["meta-analysis", "systematic review", "meta-anàlisi",
                                "revisió sistemàtica"]
    
    texto_eval = f"{nivel} {tipo}".lower()
    
    if any(k in texto_eval for k in keywords_meta):
        estudio = "meta_analisis"
    elif any(k in texto_eval for k in keywords_rct):
        estudio = "rct"
    elif any(k in texto_eval for k in keywords_molecular):
        estudio = "molecular"
    elif any(k in texto_eval for k in keywords_epidemiologico):
        estudio = "epidemiologico"
    elif nivel in ["epidemiologico", "revision"]:
        estudio = "epidemiologico"
    else:
        estudio = "epidemiologico"  # fallback conservador
    
    # ── PARÁMETROS POR TIPO ───────────────────────────────────────────
    config = {
        "epidemiologico": {
            "base": 50,              # ← era 65, bajamos base
            "bonus_entidades": 10,   # ← era 15
            "bonus_señales": 10,
            "bonus_cobertura": 5,
            "bonus_fragmentos": 5,
            "bonus_metricas": 10,    # ← NUEVO: bonus si >50% entidades tienen métricas
            "bonus_cualificadores": 5, # ← NUEVO: bonus si hay cualificadores causales
            "umbral_critico": 50,
            "umbral_excelencia": 80,
        },
        "rct": {
            "base": 40,
            "bonus_entidades": 10,
            "bonus_señales": 10,
            "bonus_cobertura": 5,
            "bonus_fragmentos": 5,
            "bonus_pvalue": 15,       # tiene p-values
            "bonus_hr_or": 15,        # tiene HR o OR
            "umbral_critico": 70,
            "umbral_excelencia": 88,
        },
        "molecular": {
            "base": 40,
            "bonus_entidades": 10,
            "bonus_señales": 10,
            "bonus_cobertura": 5,
            "bonus_fragmentos": 5,
            "bonus_pvalue": 10,
            "bonus_lfc": 20,          # tiene LFC — métrica core molecular
            "umbral_critico": 65,
            "umbral_excelencia": 85,
        },
        "meta_analisis": {
            "base": 50,
            "bonus_entidades": 10,
            "bonus_señales": 15,
            "bonus_cobertura": 5,
            "bonus_fragmentos": 5,
            "bonus_pvalue": 15,
            "umbral_critico": 70,
            "umbral_excelencia": 88,
        },
    }
    
    cfg = config.get(estudio, config["epidemiologico"])
    score = cfg["base"]
    
    # ── BONIFICACIONES COMUNES ────────────────────────────────────────
    if entidades:
        score += cfg["bonus_entidades"]
        
        if len(entidades) > 5:
            score += cfg.get("bonus_cobertura", 0)
        
        entidades_con_fragmento = sum(
            1 for e in entidades if len(e.get("fragmento_fuente", "").strip()) > 15
        )
        if entidades_con_fragmento / len(entidades) > 0.7:
            score += cfg.get("bonus_fragmentos", 0)
    
    if señales:
        score += cfg.get("bonus_señales", 0)
    
    # Bonus métricas — solo si más del 50% de entidades tienen métricas reales
    if entidades:
        entidades_con_metricas = sum(
            1 for e in entidades
            if e.get("metricas") and any(
                v is not None and v != "" and v != "NO DISPONIBLE"
                for v in e["metricas"].values()
            )
        )
        ratio_metricas = entidades_con_metricas / len(entidades)
        if ratio_metricas > 0.5:
            score += cfg.get("bonus_metricas", 0)
        elif ratio_metricas > 0.25:
            score += cfg.get("bonus_metricas", 0) // 2

    # Bonus cualificadores causales — indica precisión en asignación
    if entidades:
        con_cualificador = sum(
            1 for e in entidades
            if e.get("cualificador_original", "").strip()
        )
        if con_cualificador / len(entidades) > 0.3:
            score += cfg.get("bonus_cualificadores", 0)
    
    # ── BONIFICACIONES ESPECÍFICAS POR TIPO ──────────────────────────
    tiene_pvalue = any(
        e.get("metricas", {}).get("p_value") is not None
        for e in entidades
    )
    tiene_hr_or = any(
        e.get("metricas", {}).get("HR") is not None or
        e.get("metricas", {}).get("OR") is not None
        for e in entidades
    )
    tiene_lfc = any(
        e.get("metricas", {}).get("LFC") is not None
        for e in entidades
    )
    if estudio in ["rct", "molecular", "meta_analisis"]:
        if tiene_pvalue:
            score += cfg.get("bonus_pvalue", 0)
        if tiene_hr_or:
            score += cfg.get("bonus_hr_or", 0)
        if tiene_lfc:
            score += cfg.get("bonus_lfc", 0)
    elif estudio == "epidemiologico" and (tiene_pvalue or tiene_hr_or):
        score += cfg.get("bonus_metricas", 0)
    
    # Única penalización — errores matemáticos críticos
    criticos = sum(
        1 for e in entidades
        if str(e.get("riesgo_omision", "")).upper() == "CRÍTICO"
    )
    if criticos >= 2:
        score = min(score, 40)
    elif criticos == 1:
        score = min(score, 60)

    score = min(max(score, 0), 100)
    return score, estudio



def validate_with_ai(abstract: str, extracted_entities: List[Dict], api_key: str) -> Dict:
    """
    Segunda llamada a Gemini exclusivamente para validación científica.
    No extrae — solo evalúa coherencia del abstract y de lo extraído.
    """
    genai.configure(api_key=api_key)

    entities_summary = json.dumps([
        {
            "nombre": e.get("nombre"),
            "metricas": e.get("metricas", {}),
            "fragmento": e.get("fragmento_fuente", "")
        }
        for e in extracted_entities
    ], ensure_ascii=False)

    prompt = f"""
Eres un bioestadístico y revisor científico senior con 20 años
de experiencia revisando manuscripts para Nature Medicine y NEJM.

Tienes dos tareas:

TAREA 1 — VALIDACIÓN CIENTÍFICA
Analiza el abstract y detecta cualquier problema real.
No inventes errores. Solo reporta lo que claramente es incorrecto.

Categorías a evaluar:

REGLA DE GRAVEDAD — aplica ESTRICTAMENTE:
   CRITICO: SOLO para Category A (imposibles matemáticos). Nunca para B, C o D.
   ALTO:    Category B o C cuando el error es claro y documentable.
   MEDIO:   Category C o D con evidencia moderada.
   BAJO:    Category D o incertidumbre menor.

A) ERRORES FÍSICOS — matemáticamente imposibles en cualquier contexto:
   - p-value fuera de [0, 1]
   - HR, OR, RR negativos o igual a cero
   - Probabilidades fuera de [0, 100%]
   - Intervalos de confianza donde lower > upper
   → gravedad siempre CRITICO si se confirma.

B) ERRORES FISIOLÓGICOS — numéricamente posibles pero biológicamente
   imposibles dado el contexto específico del abstract:
   - Concentraciones séricas, tisulares o celulares fuera de rangos
     descritos en la literatura para esa molécula y compartimento
   - Dosis farmacológicas incompatibles con supervivencia
   - Tasas biológicas imposibles (crecimiento, división, expresión)
   Solo reporta si tienes certeza clínica. No inventes.
   → gravedad máxima ALTO, nunca CRITICO.

C) INCOHERENCIAS INTERNAS — valores que se contradicen entre sí:
   - HR/OR con efecto grande (< 0.7 o > 1.5) pero p-value > 0.05
   - Resultados primarios y secundarios que apuntan en direcciones
     opuestas sin explicación
   - Intervalos de confianza que no incluyen el valor nulo pero
     p-value no significativo, o viceversa
   Solo reporta si hay valores NUMÉRICOS que se contradicen.
   Si el abstract no tiene valores numéricos, errores: [].
   → gravedad máxima ALTO, nunca CRITICO.

D) CONTAMINACIÓN DE DATOS — parámetros que no son métricas
   clínicas del paciente sino condiciones de procesamiento:
   - Temperaturas de almacenamiento o procesamiento de muestras
   - Velocidades de centrifugación, tiempos de incubación
   - Concentraciones de reactivos o buffers
   - Condiciones instrumentales (absorbancia, voltaje, frecuencia)
   - Cualquier parámetro que describa cómo se procesó la muestra,
     no qué le ocurre al paciente o al tejido biológico
   → gravedad máxima MEDIO, nunca CRITICO ni ALTO.

TAREA 2 — VEREDICTO GLOBAL
Basándote en lo encontrado, asigna un veredicto:
   OPTIMA:       sin errores detectables
   ACEPTABLE:    advertencias menores, datos usables con precaución
   INCOHERENCIA: contradicciones estadísticas internas
   NO_FIABLE:    errores físicos o fisiológicos que invalidan los datos

ABSTRACT A EVALUAR:
{abstract}

MÉTRICAS EXTRAÍDAS:
{entities_summary}

Responde EXCLUSIVAMENTE en este JSON, sin texto adicional:
{{
  "tiene_errores": true|false,
  "nivel_confianza_cientifico": 0-100,
  "veredicto": "OPTIMA|ACEPTABLE|INCOHERENCIA|NO_FIABLE",
  "errores": [
    {{
      "categoria": "FISICO|FISIOLOGICO|INCOHERENCIA|CONTAMINACION",
      "entidad_afectada": "nombre exacto o descripción breve",
      "descripcion": "descripción concisa y accionable del problema",
      "gravedad": "CRITICO (solo Cat.A)|ALTO (Cat.B-C)|MEDIO (Cat.C-D)|BAJO"
    }}
  ],
  "resumen": "una frase que explica el veredicto al investigador"
}}

Si el abstract es correcto responde con:
tiene_errores: false, veredicto: OPTIMA, errores: []
"""

    try:
        validation_response = None
        for vmodel in ["gemini-2.5-flash", "gemini-1.5-flash"]:
            for vattempt in range(2):
                try:
                    model = genai.GenerativeModel(vmodel)
                    validation_response = model.generate_content(
                        prompt,
                        generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
                    )
                    break
                except Exception as vexc:
                    if "500" in str(vexc) and vattempt == 0:
                        time.sleep(2)
                        continue
                    break
            if validation_response is not None:
                break
        if validation_response is None:
            raise RuntimeError("Validacion IA sin respuesta")
        return json.loads(validation_response.text)
    except Exception:
        return {
            "tiene_errores": False,
            "nivel_confianza_cientifico": 50,
            "veredicto": "ACEPTABLE",
            "errores": [],
            "resumen": "Validación IA no disponible"
        }


def call_gemini_extract(abstract: str, api_key: str, model_preference: str = "Automático (recomendado)") -> Dict[str, Any]:
    coherent, coherence_msg = validate_biomedical_coherence(abstract)
    if not coherent:
        raise ValueError(coherence_msg)

    genai.configure(api_key=api_key)
    
    # Configurar models segons preferència
    if model_preference == "Gemini 2.5 Flash":
        model_candidates = ["gemini-2.5-flash"]
    elif model_preference == "Gemini 1.5 Flash":
        model_candidates = ["gemini-1.5-flash"]
    else:  # Automàtic
        model_candidates = ["gemini-2.5-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]
    
    # Garantizar gemini-1.5-flash como ultimo recurso
    if "gemini-1.5-flash" not in model_candidates:
        model_candidates = list(model_candidates) + ["gemini-1.5-flash"]

    response = None
    last_error = None
    for model_name in model_candidates:
        for attempt in range(2):
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    build_prompt(abstract),
                    generation_config={"temperature": 0.0, "response_mime_type": "application/json"},
                )
                break
            except Exception as exc:
                last_error = exc
                if "500" in str(exc) and attempt == 0:
                    time.sleep(2)
                    continue
                break
        if response is not None:
            break
    if response is None:
        raise ValueError(f"No ha estat possible invocar un model Gemini disponible: {last_error}")

    raw_text = response.text if hasattr(response, "text") else ""
    if not raw_text:
        return {"entidades_de_riesgo": [], "validacion_alertas": ["No se ha recibido respuesta de Gemini"]}
    
    parsed = parse_json_response(raw_text)
    
    coerced = coerce_payload(parsed, abstract_text=abstract)

    # Segunda llamada — validación científica universal
    entidades_para_validar = coerced.get("entidades_de_riesgo", [])
    validacion_ia = validate_with_ai(abstract, entidades_para_validar, api_key)

    # Propagar veredicto de la IA al payload
    coerced["validacion_cientifica"] = validacion_ia

    # Marcar entidades con errores detectados por la IA
    entidades_con_error = {
        _safe_string(e.get("entidad_afectada", "")).lower().strip()
        for e in validacion_ia.get("errores", [])
        if e.get("gravedad") == "CRITICO"
        and _safe_string(e.get("entidad_afectada", "")).strip()
    }

    for entidad in coerced.get("entidades_de_riesgo", []):
        nombre = _safe_string(entidad.get("nombre", "")).lower()
        if entidades_con_error and any(err in nombre or nombre in err for err in entidades_con_error):
            entidad["riesgo_omision"] = "CRÍTICO"
            entidad["estado_validacion"] = "🚨"

    # Calcular tipo de estudio (para metadata)
    entitats = coerced.get("entidades_de_riesgo", [])
    senyals = coerced.get("señales_prioritarias", [])
    gaps = coerced.get("gaps_criticos", {})
    tipo_estudio = detect_study_type(coerced.get("metadata", {}))

    # Confianza base desde Gemini
    confianza_ia = validacion_ia.get("nivel_confianza_cientifico", 70)
    confianza_ia = max(confianza_ia, 65)

    # La única penalización es por errores matemáticos críticos
    # detectados en entidades ya procesadas
    criticos = sum(
        1 for e in coerced.get("entidades_de_riesgo", [])
        if str(e.get("riesgo_omision", "")).upper() == "CRÍTICO"
    )

    if criticos >= 2:
        nivel_confianza_final = min(confianza_ia, 40)
    elif criticos == 1:
        nivel_confianza_final = min(confianza_ia, 60)
    else:
        nivel_confianza_final = confianza_ia

    coerced["nivel_confianza"] = nivel_confianza_final
    coerced["tipo_estudio_detectado"] = tipo_estudio

    # Analizar densidad de información
    orphan_alerts = analyze_hierarchical_density(abstract, entitats, gaps)
    coerced["alertas_densidad"] = orphan_alerts

    return coerced


def normalize_results_hierarchical(
    processed_data: Dict[str, Any], source_id: str, source_index: int
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Normaliza las entidades de riesgo según el nuevo protocolo biomédico."""
    rows: List[Dict[str, Any]] = []
    
    # Verificar si hay error de coherencia
    if "error" in processed_data:
        return [], {
            "error": processed_data.get("error"),
            "motiu": processed_data.get("motiu"),
            "total_entitats": 0
        }
    
    entitats = processed_data.get("entidades_de_riesgo", [])
    metadata = processed_data.get("metadata", {})
    senyals = processed_data.get("señales_prioritarias", [])
    gaps = processed_data.get("gaps_criticos", {})
    resum = processed_data.get("resumen_ejecutivo", {})
    
    for entitat in entitats:
        nom = entitat.get("nombre", "")
        tipus = entitat.get("tipo", "desconocido")
        resolucio = entitat.get("resolucion", "literal")
        biomarcadors_implicits = entitat.get("biomarcadores_implicitos", [])
        metriques = entitat.get("metricas", {})
        poblacio = entitat.get("poblacion_afectada", [])
        relacio = entitat.get("relacion_causal", "no_especificado")
        qualificador = entitat.get("calificador_original", "")
        fragmento = entitat.get("fragmento_fuente", "")
        
        # Determinar estado según el nuevo protocolo
        p_value = metriques.get("p_value")
        estat_validacio = entitat.get("estado_validacion", "⚠️")
        
        # Convertir p_value a float si es necesario
        try:
            p_value_num = float(p_value) if p_value is not None else None
        except (ValueError, TypeError):
            p_value_num = None
        
        if p_value_num is not None and p_value_num < 0.05:
            estado = "p<0.05"
        elif resolucio == "agregado_clinico" and biomarcadors_implicits:
            estado = "INFERIDO"
        elif len(fragmento.strip()) > 15 and estat_validacio == "OK":
            estado = "OK"
        elif tipus == "demografico":
            estado = "DEMOG."
        elif tipus == "epidemiologico":
            estado = "EPID."
        elif tipus == "molecular":
            estado = "MOL."
        else:
            estado = "–"
            
        # Construir métricas según nuevo esquema
        metriques_display = []
        
        # Métricas estándar del nuevo esquema
        if metriques.get("HR") is not None:
            try:
                metriques_display.append(f"HR={float(metriques['HR']):.2f}")
            except (ValueError, TypeError):
                metriques_display.append(f"HR={metriques['HR']}")
        if metriques.get("OR") is not None:
            try:
                metriques_display.append(f"OR={float(metriques['OR']):.2f}")
            except (ValueError, TypeError):
                metriques_display.append(f"OR={metriques['OR']}")
        if metriques.get("p_value") is not None:
            try:
                metriques_display.append(f"p={float(metriques['p_value']):.4f}")
            except (ValueError, TypeError):
                metriques_display.append(f"p={metriques['p_value']}")
        if metriques.get("LFC") is not None:
            try:
                metriques_display.append(f"LFC={float(metriques['LFC']):.2f}")
            except (ValueError, TypeError):
                metriques_display.append(f"LFC={metriques['LFC']}")
        if metriques.get("IC95"):
            metriques_display.append(f"IC95={metriques['IC95']}")
        if metriques.get("n_muestral") is not None:
            try:
                metriques_display.append(f"n={int(float(metriques['n_muestral']))}")
            except (ValueError, TypeError):
                metriques_display.append(f"n={metriques['n_muestral']}")
        if metriques.get("n_absoluto") is not None:
            val = metriques["n_absoluto"]
            # Mostrar con formato de miles
            try:
                metriques_display.append(f"n={int(val):,}")
            except (ValueError, TypeError):
                metriques_display.append(f"n={val}")
        
        # Otras métricas (ya procesadas en coerce_payload)
        for key, value in metriques.items():
            if key not in ["HR", "OR", "p_value", "LFC", "IC95", "n_muestral"] and value and value != "NO DISPONIBLE":
                # Formatear números si es posible, sino como string
                if isinstance(value, (int, float)):
                    if key in ["mortalidad_pct", "incidencia_anual_pct", "reduccion_mortalidad_pct", 
                              "diagnostico_estadio_pct", "mortalidad", "supervivencia", "incidencia", 
                              "incidencia_anual", "aumento_anual", "reduccion_mortalidad"]:
                        metriques_display.append(f"{key}={value:.1f}%")
                    elif key in ["tasa_100k", "tasa_por_100k", "tasa_2000_100k", "tasa_2021_100k"]:
                        metriques_display.append(f"{key}={value:.1f}/100k")
                    elif key in ["n_absoluto", "muertes_evitadas"]:
                        # Formatear números grandes correctamente
                        if value >= 1000:
                            metriques_display.append(f"{key}={value:,.0f}")
                        else:
                            metriques_display.append(f"{key}={value}")
                    else:
                        metriques_display.append(f"{key}={value}")
                else:
                    # Para strings, verificar si contienen números que se pueden extraer
                    import re
                    if '%' in str(value):
                        metriques_display.append(f"{key}={value}")
                    elif 'per 100' in str(value) or '/100k' in str(value):
                        metriques_display.append(f"{key}={value}")
                    else:
                        metriques_display.append(f"{key}={value}")
        
        metriques_str = " | ".join(metriques_display) if metriques_display else "—"
        poblacion_str = ", ".join(poblacio) if isinstance(poblacio, list) else ""
        
        # Biomarcadores implícitos como string
        biomarcadors_str = ""
        if biomarcadors_implicits:
            bio_list = []
            for bio in biomarcadors_implicits:
                if isinstance(bio, dict):
                    marcador = bio.get('marcador', '')
                    bio_estado = bio.get('estado', '')
                    bio_list.append(f"{marcador} ({bio_estado})")
                elif isinstance(bio, str):
                    bio_list.append(bio)
            biomarcadors_str = "; ".join(bio_list)
        
        # Riesgo de omisión de la IA
        risc_omissio = entitat.get("riesgo_omision", "Aceptable")
            
        rows.append({
            "Estado": estado,
            "ID_Abstract": source_id,
            "Fila_Origen": source_index,
            "Entidad": nom,
            "Tipo": tipus,
            "Resolución": resolucio,
            "Biomarcadores Implícitos": biomarcadors_str,
            "Población Afectada": poblacion_str,
            "Relación Causal": relacio,
            "Calificador": qualificador,
            "Métricas": metriques_str,
            "P-value": metriques.get("p_value") if metriques.get("p_value") is not None else "",
            "Nivel evidencia": entitat.get("nivel_evidencia", metadata.get("nivel_evidencia", "desconocido")),
            "Riesgo de Omisión": risc_omissio,
            "Fragmento fuente": fragmento
        })
    
    # Crear resum segons nou protocol
    summary = {
        "metadata": metadata,
        "senyals_prioritaries": senyals,
        "gaps_critics": gaps,
        "resum_executiu": resum,
        "total_entitats": len(entitats),
        "entitats_literals": sum(
            1 for e in entitats 
            if (e.get("resolucion") or e.get("resolucio")) == "literal"
        ),
        "entitats_agregades": sum(
            1 for e in entitats 
            if (e.get("resolucion") or e.get("resolucio")) == "agregado_clinico"
        ),
        "entitats_epidemiologiques": sum(
            1 for e in entitats 
            if (e.get("resolucion") or e.get("resolucio")) == "epidemiologico"
        )
    }
    
    return rows, summary


def normalize_results(
    results: List[Dict[str, Any]], source_id: str, source_index: int, auditoria: Dict[str, Any] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    auditoria = auditoria or {}
    
    for item in results:
        microbiota = item.get("microbiota_relacionada", [])
        microbiota_str = ", ".join(microbiota) if isinstance(microbiota, list) else ""
        
        poblacion = item.get("poblacion_estudiada", [])
        poblacion_str = ", ".join(poblacion) if isinstance(poblacion, list) else ""
        
        entidades_nc = item.get("entidades_no_clasificadas", [])
        entidades_str = ", ".join(entidades_nc) if isinstance(entidades_nc, list) else ""
        
        metricas = item.get("metricas", {}) or {}
        
        # Determinar estado amb auditoria de seguretat millorada
        p_value = metricas.get("p_value")
        fragmento = item.get("fragmento_fuente", "")
        riesgo_omision = auditoria.get("riesgo_omision", "bajo")
        
        # Prioritat per biomarcadors implícits detectats
        biomarcadors_implicits = auditoria.get("biomarcadores_implicitos", [])
        es_implicit = any(item.get("biomarcador", "").lower() in bio.lower() for bio in biomarcadors_implicits)
        
        # Lógica de seguridad biológica mejorada
        try:
            p_value_num = float(p_value) if p_value is not None else None
        except (ValueError, TypeError):
            p_value_num = None
            
        if p_value_num is not None and p_value_num < 0.05:
            estado = "🔥"  # Alta prioritat estadística
        elif es_implicit:
            estado = "🧬"  # Biomarcador implícit detectat
        elif fragmento and len(fragmento.strip()) > 15 and riesgo_omision == "bajo":
            estado = "✅"  # Verificat i segur
        elif riesgo_omision == "alto":
            estado = "🔍"  # Revisió manual requerida
        else:
            estado = "⚠️"  # Dubtós
            
        # Construir métriques concatenades adaptatives
        metricas_display = []
        
        # Mètriques estadístiques
        if metricas.get("p_value") is not None:
            metricas_display.append(f"p={metricas['p_value']:.4f}")
        if metricas.get("aor") is not None:
            metricas_display.append(f"aOR={metricas['aor']:.2f}")
        if metricas.get("or") is not None:
            metricas_display.append(f"OR={metricas['or']:.2f}")
        if metricas.get("hr") is not None:
            metricas_display.append(f"HR={metricas['hr']:.2f}")
        if metricas.get("rr") is not None:
            metricas_display.append(f"RR={metricas['rr']:.2f}")
        if metricas.get("ci_lower") is not None and metricas.get("ci_upper") is not None:
            metricas_display.append(f"CI=[{metricas['ci_lower']:.2f}-{metricas['ci_upper']:.2f}]")
        
        # Mètriques moleculars
        if metricas.get("lfc") is not None:
            metricas_display.append(f"LFC={metricas['lfc']:.2f}")
        if metricas.get("fold_change") is not None:
            metricas_display.append(f"FC={metricas['fold_change']:.2f}")
        if metricas.get("expresion_relativa") is not None:
            metricas_display.append(f"ExpRel={metricas['expresion_relativa']:.2f}")
        
        # Mètriques epidemiològiques
        if metricas.get("incidencia_anual") is not None:
            metricas_display.append(f"Inc={metricas['incidencia_anual']:.1f}%")
        if metricas.get("tasa_por_100k") is not None:
            metricas_display.append(f"Tasa={metricas['tasa_por_100k']:.1f}/100k")
        if metricas.get("mortalidad_reduccion") is not None:
            metricas_display.append(f"MortRed={metricas['mortalidad_reduccion']:.1f}%")
        if metricas.get("disparidad_racial") is not None:
            metricas_display.append(f"DispRac={metricas['disparidad_racial']:.1f}%")
        if metricas.get("porcentaje_diagnostico") is not None:
            metricas_display.append(f"Diag={metricas['porcentaje_diagnostico']:.1f}%")
        
        # Mètriques de laboratori
        if metricas.get("concentracion") is not None:
            metricas_display.append(f"Conc={metricas['concentracion']:.2f}")
        if metricas.get("sensibilidad") is not None:
            metricas_display.append(f"Sens={metricas['sensibilidad']:.1f}%")
        if metricas.get("especificidad") is not None:
            metricas_display.append(f"Esp={metricas['especificidad']:.1f}%")
        
        # Altres mètriques
        if metricas.get("otras_metricas"):
            metricas_display.append(str(metricas["otras_metricas"]))
        
        metricas_str = " | ".join(metricas_display) if metricas_display else ""
        
        # Determinar risc d'omissió per fila
        risc_omissio = "Revisió Manual Requerida" if riesgo_omision == "alto" else "Acceptable"
            
        rows.append(
            {
                "Estado": estado,
                "ID_Abstract": source_id,
                "Fila_Origen": source_index,
                "Biomarcador": item.get("biomarcador", ""),
                "Tipo": item.get("tipo_biomarcador", ""),
                "Subtipo Molecular": item.get("subtipo_molecular", ""),
                "Población Estudiada": poblacion_str,
                "Posología/Dosis": item.get("posologia_dosis", ""),
                "Tamaño Muestral (n)": item.get("tamano_muestral", ""),
                "Entidades No Clasificadas": entidades_str,
                "Efecto/Impacto": item.get("efecto_impacto", ""),
                "Patología": item.get("patologia_contexto", ""),
                "Microbiota relacionada": microbiota_str,
                "Métricas": metricas_str,
                "P-value": p_value,
                "Nivel de evidencia": item.get("nivel_evidencia", ""),
                "Riesgo de Omisión": risc_omissio,
                "Fragmento fuente": fragmento,
            }
        )
    
    return rows, auditoria


def build_txt_report(all_payloads, final_df):
    lines_txt = []
    lines_txt.append("BIOEXTRACT - INFORME DE EXTRACCION")
    lines_txt.append(
        "Generado: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')
    )
    lines_txt.append("Abstracts procesados: " + str(len(all_payloads)))
    lines_txt.append("=" * 55)
    lines_txt.append("")
    for i, p in enumerate(all_payloads, start=1):
        _payload = p.get("payload", {})
        _abstract_id = p.get("ID_Abstract", "file_" + str(i))
        _entidades = _payload.get("entidades_de_riesgo", [])
        _confianza = _cap_confianza_sin_metricas(_payload, _payload.get("nivel_confianza", 0))
        _senales = _payload.get("senales_prioritarias", [])
        _gaps = _payload.get("gaps_criticos", {})
        _criticos = [
            e for e in _entidades
            if str(e.get("riesgo_omision", "")).upper() == "CRITICO"
        ]
        if _criticos:
            _veredicto = "ANOMALIA CRITICA"
        elif _confianza >= 85:
            _veredicto = "EXTRACCION COMPLETA"
        elif _confianza >= 60:
            _veredicto = "EXTRACCION PARCIAL"
        else:
            _veredicto = "COBERTURA BAJA"
        lines_txt.append("ABSTRACT " + str(i) + " - " + str(_abstract_id))
        lines_txt.append(_veredicto + " - " + str(_confianza) + "% confianza")
        lines_txt.append("-" * 55)
        if _criticos:
            lines_txt.append("ANOMALIAS CRITICAS:")
            for e in _criticos:
                lines_txt.append(
                    "   * " + str(e.get("nombre", "")) + " - " + str(e.get("metricas_completas", ""))
                )
            lines_txt.append("")
        if _senales:
            lines_txt.append("SENALES PRIORITARIAS:")
            for s in _senales:
                _impacto = s.get("impacto_clinico", "").upper()
                _tipo = s.get("tipo", "").upper()
                _desc = s.get("descripcion", "")
                lines_txt.append("   [" + _impacto + "] " + _tipo)
                lines_txt.append("   " + _desc)
            lines_txt.append("")
        _metricas_entidades = [
            e for e in _entidades
            if e.get("metricas_completas", "") not in ["NO DISPONIBLE", "", None]
        ]
        if _metricas_entidades:
            lines_txt.append("METRICAS EXTRAIDAS:")
            for e in _metricas_entidades:
                _nombre = str(e.get("nombre", ""))
                _metricas = str(e.get("metricas_completas", ""))
                _metricas = _metricas.replace("otros=", "").replace(
                    "incidencia_anual_pct=", "").replace("mortalidad_pct=", "")
                lines_txt.append("   * " + _nombre + ": " + _metricas)
            lines_txt.append("")
        _gaps_relevantes = {
            k: v for k, v in _gaps.items()
            if v and v != "NO DISPONIBLE"
        }
        if _gaps_relevantes:
            lines_txt.append("GAPS DETECTADOS:")
            for k, v in _gaps_relevantes.items():
                lines_txt.append("   * " + str(k) + ": " + str(v))
            lines_txt.append("")
        lines_txt.append("=" * 55)
        lines_txt.append("")
    return "\n".join(lines_txt)


# Inicializar contador de sesión
if "demo_count" not in st.session_state:
    st.session_state.demo_count = 0
if "last_results" not in st.session_state:
    st.session_state.last_results = None
if "last_json" not in st.session_state:
    st.session_state.last_json = None
if "last_df" not in st.session_state:
    st.session_state.last_df = None

DEMO_LIMIT = 5


# Resolver API key activa
def resolve_api_key(user_input: str) -> tuple[str, bool]:
    """
    Retorna (api_key, es_demo).
    es_demo=True significa que usa la key de secrets.
    """
    user_key = (user_input or "").strip()
    if user_key:
        return user_key, False
    
    # Intentar key de secrets (demo)
    try:
        secrets_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
        if secrets_key:
            return secrets_key, True
    except Exception:
        pass
    
    # Intentar variable de entorno
    env_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if env_key:
        return env_key, True
    
    return "", False



# Variables para KPI (inicializadas antes del if)
processed_count = 0
entity_count = 0
total_alerts = 0
confidence_level = 0

# KPI BAR placeholder (se rellena al final con valores actuales)
kpi_placeholder = st.empty()

progress_text_placeholder = st.empty()
progress_bar_placeholder = st.empty()
# ZONA RESULTADOS
table_placeholder = st.empty()
summary_placeholder = st.empty()
if not run_button:
    table_placeholder.markdown(
        '<div style="padding:28px 0 48px 0;">'
        '<p style="font-size:15px;font-weight:500;color:var(--ink);line-height:1.55;margin:0 0 14px 0;">'
        'Pega el abstract de un paper y obtén sus entidades biomédicas estructuradas en segundos.'
        '</p>'
        '<div style="display:flex;flex-direction:column;gap:7px;margin-bottom:14px;">'
        '<div style="font-size:13px;color:var(--ink-2);line-height:1.6;">'
        'Detecta anomalías matemáticas imposibles — HR negativos, IC invertidos, supervivencias &gt;100%'
        '</div>'
        '<div style="font-size:13px;color:var(--ink-2);line-height:1.6;">'
        'Distingue entre evidencia preclínica y clínica — in vitro, RCT, revisión narrativa'
        '</div>'
        '</div>'
        '<p style="font-size:12px;color:var(--muted);line-height:1.5;font-style:italic;margin:0 0 28px 0;">'
        'No evalúa calidad metodológica ni reemplaza la lectura del paper original.'
        '</p>'
        '<div style="border-top:1px solid var(--border);padding-top:20px;">'
        '<div style="font-size:10px;font-weight:600;color:var(--muted);letter-spacing:0.8px;text-transform:uppercase;margin-bottom:14px;">'
        'Ejemplo de salida'
        '</div>'
        '<div style="font-size:10px;font-weight:600;color:var(--muted);letter-spacing:0.5px;text-transform:uppercase;margin-bottom:6px;">'
        'Input'
        '</div>'
        '<div style="font-size:12px;color:var(--ink-2);background:var(--surface-2);border:1px solid var(--border);border-radius:4px;padding:10px 14px;line-height:1.7;margin-bottom:16px;">'
        'A phase III randomized controlled trial evaluated capivasertib plus fulvestrant versus placebo '
        'in 523 patients with HR-positive HER2-negative metastatic breast cancer. '
        'Progression-free survival was significantly improved (HR=0.60, 95&#8239;CI&#8239;0.51&#8211;0.71, p&lt;0.001).'
        '</div>'
        '<div style="font-size:10px;font-weight:600;color:var(--muted);letter-spacing:0.5px;text-transform:uppercase;margin-bottom:10px;">'
        'Output'
        '</div>'
        '<div style="display:flex;flex-direction:column;gap:9px;">'
        '<div style="font-size:13px;color:var(--ink-2);line-height:1.6;">'
        '✅ <span style="color:var(--ink);font-weight:500;">Veredicto:</span> Extracción completa — 100%'
        '</div>'
        '<div style="font-size:13px;color:var(--ink-2);line-height:1.6;">'
        '<span style="color:var(--ink);font-weight:500;">Entidades:</span> '
        'capivasertib · fulvestrant · HR-positive HER2-negative metastatic breast cancer'
        '</div>'
        '<div style="font-size:13px;color:var(--ink-2);line-height:1.6;">'
        '<span style="color:var(--ink);font-weight:500;">Métricas:</span> HR=0.60 &middot; CI [0.51&#8211;0.71] &middot; p&lt;0.001'
        '</div>'
        '<div style="font-size:13px;color:var(--ink-2);line-height:1.6;">'
        '<span style="color:var(--ink);font-weight:500;">Tipo de estudio:</span> RCT clínico fase III'
        '</div>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

# Area inferior para controles adicionales
download_placeholder = st.empty()
json_placeholder = st.empty()

if run_button:
    api_key, es_demo = resolve_api_key(user_api_key)

    if not api_key:
        st.markdown('''
        <div class="verdict-warning">
            🔑 Introduce tu API key de Gemini para continuar, 
            o despliega la app con tu propia key en secrets.
            <a href="https://aistudio.google.com/app/apikey" 
               target="_blank" 
               style="color: #1A56DB; margin-left: 8px;">
                Obtener key gratuita →
            </a>
        </div>
        ''', unsafe_allow_html=True)
        st.stop()

    if es_demo and st.session_state.demo_count >= DEMO_LIMIT:
        st.markdown(f'''
        <div class="verdict-critical">
            🔒 Has usado los {DEMO_LIMIT} análisis gratuitos 
            de esta sesión. Introduce tu propia API key de 
            Gemini para continuar sin límite.
            <a href="https://aistudio.google.com/app/apikey" 
               target="_blank"
               style="color: #991B1B; margin-left: 8px; font-weight: 600;">
                Obtener key gratuita en 2 minutos →
            </a>
        </div>
        ''', unsafe_allow_html=True)
        st.stop()

    all_rows: List[Dict[str, Any]] = []
    all_payloads: List[Dict[str, Any]] = []
    errors: List[Tuple[int, str]] = []
    sensor_alerts: List[Tuple[int, str]] = []

    # Mapear preferencias de modelo
    model_map = {"Auto": "Automático (recomendado)", "Gemini 2.5": "Gemini 2.5 Flash", "Gemini 1.5": "Gemini 1.5 Flash"}
    model_pref = model_map.get(model_preference, "Automático (recomendado)")

    if mode == "Individual":
        current_abstract = abstract_text.strip()
        if not current_abstract:
            st.markdown('<div class="alert-warning">Texto de abstract requerido para el modo individual</div>', unsafe_allow_html=True)
            st.stop()

        def _set_progress(valor, texto):
            progress_text_placeholder.markdown(
                '<div style="padding:12px 0 8px 0;">'
                '<p style="margin:0 0 8px 0; font-family:\'DM Sans\',sans-serif; '
                f'font-size:13px; color:var(--ink);">{texto}</p></div>',
                unsafe_allow_html=True
            )
            progress_bar_placeholder.progress(valor)

        _set_progress(0, "⏳ Iniciando análisis...")
        time.sleep(0.3)
        _set_progress(15, "📖 Leyendo abstract...")
        time.sleep(0.4)
        _set_progress(30, "🧬 Extrayendo entidades biomédicas...")
        try:
            payload = call_gemini_extract(
                current_abstract, api_key, model_pref
            )

            _set_progress(65, "📊 Estructurando métricas estadísticas...")
            time.sleep(0.3)
            _set_progress(80, "🔍 Validando invariantes matemáticos...")
            time.sleep(0.3)

            all_payloads.append({"ID_Abstract": "manual_1", "payload": payload})

            # Procesar alertas de validación y densidad
            for alert in payload.get("validacion_alertas", []):
                sensor_alerts.append((1, alert))
            for alert in payload.get("alertas_densidad", []):
                sensor_alerts.append((1, f"Alerta Densidad: {alert}"))

            # Normalizar resultados con estructura jerárquica
            rows, summary = normalize_results_hierarchical(
                payload, "manual_1", 1
            )
            all_rows.extend(rows)

            _set_progress(95, "✅ Generando resultado estructurado...")
            time.sleep(0.4)
            _set_progress(100, "✅ Análisis completado")
            time.sleep(0.5)
            progress_text_placeholder.empty()
            progress_bar_placeholder.empty()
            st.markdown('<div style="margin-bottom:16px;"></div>', unsafe_allow_html=True)

            if es_demo:
                st.session_state.demo_count += 1
        except Exception as exc:
            if "Dato No Fiable" in str(exc) or "contenido no" in str(exc):
                coherence_reason = str(exc).split(":")[-1].strip() if ":" in str(exc) else str(exc)
                st.markdown(
                    f'<div class="alert-danger">🚫 Filtro de Coherencia: {coherence_reason}</div>',
                    unsafe_allow_html=True,
                )
            errors.append((1, str(exc)))
            _set_progress(100, "Error")

    else:  # Modo Masivo
        if uploaded_file is None or file_df.empty or not selected_column:
            st.markdown('<div class="alert-warning">Archivo y columna requeridos para el modo masivo</div>', unsafe_allow_html=True)
            st.stop()

        abstracts_series = file_df[selected_column].dropna().astype(str)
        abstracts_series = abstracts_series[abstracts_series.str.strip() != ""]
        total = len(abstracts_series)

        if total == 0:
            st.markdown('<div class="alert-warning">Ningún abstract válido encontrado</div>', unsafe_allow_html=True)
            st.stop()

        progress_text_placeholder.markdown(
            '<div style="padding:12px 0 8px 0;">'
            '<p style="margin:0 0 8px 0; font-family:\'DM Sans\',sans-serif; '
            f'font-size:13px; color:var(--ink);">Procesando {total} abstracts...</p></div>',
            unsafe_allow_html=True
        )
        progress_bar_placeholder.progress(0)

        for idx, (row_idx, abstract) in enumerate(abstracts_series.items(), start=1):
            percent = int(idx / total * 100)
            progress_text_placeholder.markdown(
                '<div style="padding:12px 0 8px 0;">'
                '<p style="margin:0 0 8px 0; font-family:\'DM Sans\',sans-serif; '
                f'font-size:13px; color:var(--ink);">🔄 Procesando abstract {idx}/{total}...</p></div>',
                unsafe_allow_html=True
            )
            progress_bar_placeholder.progress(percent)
            source_id = f"file_{row_idx + 1}"
            try:
                payload = call_gemini_extract(abstract.strip(), api_key, model_pref)
                all_payloads.append({"ID_Abstract": source_id, "payload": payload})
                
                # Procesar alertas de validación y densidad
                for alert in payload.get("validacion_alertas", []):
                    sensor_alerts.append((row_idx + 1, alert))
                for alert in payload.get("alertas_densidad", []):
                    sensor_alerts.append((row_idx + 1, f"Alerta Densidad: {alert}"))
                
                # Normalizar resultados con estructura jerárquica
                rows, summary = normalize_results_hierarchical(payload, source_id, row_idx + 1)
                all_rows.extend(rows)
            except Exception as exc:
                errors.append((row_idx + 1, str(exc)))
                continue

        progress_text_placeholder.markdown(
            '<div style="padding:12px 0 8px 0;">'
            '<p style="margin:0 0 8px 0; font-family:\'DM Sans\',sans-serif; '
            'font-size:13px; color:var(--ink);">✅ Procesamiento completado</p></div>',
            unsafe_allow_html=True
        )
        progress_bar_placeholder.progress(100)
        time.sleep(0.5)
        progress_text_placeholder.empty()
        progress_bar_placeholder.empty()
        st.markdown('<div style="margin-bottom:16px;"></div>', unsafe_allow_html=True)
        
        if es_demo:
            st.session_state.demo_count += len(all_payloads)

    final_df = pd.DataFrame(all_rows)
    processed_count = len(all_payloads)
    error_count = len(errors)
    sensor_error_count = len(sensor_alerts)
    entity_count = len(final_df) if not final_df.empty else 0
    
    # Calcular confianza con Protocolo de Seguridad Biológica
    verified_count = len(final_df[final_df["Estado"] == "✅"]) if not final_df.empty else 0
    high_priority_count = len(final_df[final_df["Estado"] == "🔥"]) if not final_df.empty else 0
    manual_review_count = len(final_df[final_df["Estado"] == "🔍"]) if not final_df.empty else 0
    
    # ── Helper: cap confianza si no hay métricas cuantitativas ──────
    _NO_METRICAS_PHRASES = (
        "no se encontraron métricas estadísticas cuantitativas",
        "no se proporcionan valores específicos",
        "no se reportan hr, or, p-values",
        "solo declaraciones cualitativas",
        "no disponible",
    )

    def _cap_confianza_sin_metricas(payload: dict, confianza: int) -> int:
        gaps = payload.get("gaps_criticos", {})
        met_gap = str(gaps.get("metricas_estadisticas", "")).lower()
        if not any(phrase in met_gap for phrase in _NO_METRICAS_PHRASES):
            return confianza
        entidades = payload.get("entidades_de_riesgo", [])
        con_metricas = sum(
            1 for e in entidades
            if isinstance(e.get("metricas"), dict) and any(
                e["metricas"].get(k) is not None
                for k in ("HR", "OR", "p_value", "ci_lower", "ci_upper", "NNT")
            )
        )
        return min(confianza, 70) if con_metricas < 2 else confianza

    # Nivel de confianza basado en calidad de p-values y auditoría
    if all_payloads:
        avg_confidence = sum(payload.get("payload", {}).get("nivel_confianza", 0) for payload in all_payloads) / len(all_payloads)
        confidence_level = int(avg_confidence)
        # Cap individual: un solo abstract sin métricas cuantitativas
        if len(all_payloads) == 1:
            confidence_level = _cap_confianza_sin_metricas(all_payloads[0].get("payload", {}), confidence_level)
    else:
        confidence_level = 0
    
    total_alerts = error_count + sensor_error_count

    # ── CÁLCULO PREVIO ────────────────────────────────────────────
    hay_criticos = any(
        _safe_string(e.get("riesgo_omision", "")).upper() == "CRÍTICO"
        for p in all_payloads for e in p.get("payload", {}).get("entidades_de_riesgo", [])
    )

    all_señales = []
    for p in all_payloads:
        all_señales.extend(p.get("payload", {}).get("señales_prioritarias", []))

    # ── CONSTRUIR JSON JERÁRQUICO ──────────────────────────────────
    hierarchical_json = None
    if all_payloads:
        hierarchical_json = {
            "metadata": {
                "abstracts_procesados": len(all_payloads),
                "total_entidades": len(final_df) if not final_df.empty else 0,
                "confianza_global": f"{confidence_level}%",
                "timestamp": pd.Timestamp.now().isoformat(),
                "tipo_extraccion": "Jerárquico de Alta Densidad"
            },
            "entidades_de_riesgo": [],
            "señales_prioritarias": [],
            "gaps_criticos": {},
            "resumen_ejecutivo": {
                "entidades_literales": 0,
                "entidades_inferidas": 0,
                "entidades_con_metricas": 0,
                "alertas_densidad": len(sensor_alerts)
            }
        }
        entitats_literals = 0
        entitats_inferides = 0
        entitats_amb_metriques = 0
        for _, row in final_df.iterrows() if not final_df.empty else []:
            resolucio = row.get("Resolución", "literal")
            if resolucio == "agregado_clinico":
                entitats_inferides += 1
            else:
                entitats_literals += 1
            if row.get("Métricas", "NO DISPONIBLE") != "NO DISPONIBLE":
                entitats_amb_metriques += 1
            hierarchical_json["entidades_de_riesgo"].append({
                "nombre": row["Entidad"],
                "tipo": row["Tipo"],
                "es_literal": resolucio != "agregado_clinico",
                "poblacion_afectada": row["Población Afectada"].split(", ") if row["Población Afectada"] else [],
                "relacion_causal": row["Relación Causal"],
                "metricas_completas": row["Métricas"],
                "p_value": row["P-value"] if pd.notna(row["P-value"]) else None,
                "nivel_evidencia": row["Nivel evidencia"],
                "estado_validacion": row["Estado"],
                "riesgo_omision": row["Riesgo de Omisión"],
                "fragmento_fuente": row["Fragmento fuente"]
            })
        hierarchical_json["resumen_ejecutivo"]["entidades_literales"] = entitats_literals
        hierarchical_json["resumen_ejecutivo"]["entidades_inferidas"] = entitats_inferides
        hierarchical_json["resumen_ejecutivo"]["entidades_con_metricas"] = entitats_amb_metriques
        for payload_data in all_payloads:
            payload = payload_data.get("payload", {})
            hierarchical_json["señales_prioritarias"].extend(
                payload.get("señales_prioritarias", [])
            )
            for key, value in payload.get("gaps_criticos", {}).items():
                if key not in hierarchical_json["gaps_criticos"] or \
                        hierarchical_json["gaps_criticos"][key] == "NO DISPONIBLE":
                    hierarchical_json["gaps_criticos"][key] = value

    # Persistir resultados en session_state
    st.session_state.last_df = final_df
    st.session_state.last_json = hierarchical_json
    st.session_state.last_results = {
        "hay_criticos": hay_criticos,
        "confidence_level": confidence_level,
        "all_señales": all_señales,
        "all_payloads": all_payloads,
        "errors": errors,
        "sensor_alerts": sensor_alerts,
        "error_count": error_count,
        "processed_count": processed_count,
        "entity_count": entity_count,
        "total_alerts": total_alerts,
    }


results_to_show = (
    st.session_state.last_results
    if not run_button and st.session_state.last_results is not None
    else None
)
if run_button or results_to_show:
    if not run_button and results_to_show:
        final_df = st.session_state.last_df
        hierarchical_json = st.session_state.last_json
        hay_criticos = results_to_show["hay_criticos"]
        confidence_level = results_to_show["confidence_level"]
        all_señales = results_to_show["all_señales"]
        all_payloads = results_to_show["all_payloads"]
        errors = results_to_show["errors"]
        sensor_alerts = results_to_show["sensor_alerts"]
        error_count = results_to_show["error_count"]

    # ── RIGHT COL: 5 SECCIONES CLÍNICAS ──────────────────────────
    with table_placeholder.container():

        # ══ SECCIÓN 1 — VEREDICTO DEL ANÁLISIS ════════════════════
        st.markdown('''
        <div class="section-label">VEREDICTO DEL ANÁLISIS</div>
        <div style="font-size:11px; color:#8896A5; margin-bottom:10px;">
            Evaluación automática de la integridad matemática del abstract.
            No evalúa calidad metodológica.
        </div>
        ''', unsafe_allow_html=True)

        if hay_criticos:
            st.markdown(f'''
            <div class="verdict-critical">
                <div class="verdict-title" style="font-size:14px; font-weight:600; margin-bottom:6px;">
                    Anomalía matemática crítica detectada
                </div>
                <div style="font-size:13px;">
                    Se encontraron valores estadísticamente imposibles.
                    Revisar el abstract antes de usar estos datos en ningún análisis.
                </div>
                <div style="font-size:11px; margin-top:8px; opacity:0.8;">
                    Confianza de extracción: {confidence_level}%
                </div>
            </div>
            ''', unsafe_allow_html=True)
        elif confidence_level >= 85:
            st.markdown(f'''
            <div class="verdict-ok">
                <div class="verdict-title" style="font-size:14px; font-weight:600; margin-bottom:6px;">
                    Extracción completa
                </div>
                <div style="font-size:13px;">
                    Métricas estructuradas disponibles.
                    Revisar señales prioritarias antes de usar los datos.
                </div>
                <div style="font-size:11px; margin-top:8px; opacity:0.8;">
                    Confianza de extracción: {confidence_level}%
                </div>
            </div>
            ''', unsafe_allow_html=True)
        elif confidence_level >= 60:
            st.markdown(f'''
            <div class="verdict-warning">
                <div class="verdict-title" style="font-size:14px; font-weight:600; margin-bottom:6px;">
                    Extracción parcial
                </div>
                <div style="font-size:13px;">
                    Datos utilizables con precaución.
                    Verificar métricas clave en el paper original.
                </div>
                <div style="font-size:11px; margin-top:8px; opacity:0.8;">
                    Confianza de extracción: {confidence_level}%
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="verdict-warning">
                <div class="verdict-title" style="font-size:14px; font-weight:600; margin-bottom:6px;">
                    Cobertura baja
                </div>
                <div style="font-size:13px;">
                    El abstract no contiene suficientes datos estructurados
                    para este análisis.
                </div>
                <div style="font-size:11px; margin-top:8px; opacity:0.8;">
                    Confianza de extracción: {confidence_level}%
                </div>
            </div>
            ''', unsafe_allow_html=True)

        # ══ SECCIÓN 2 — SEÑALES PRIORITARIAS ══════════════════════
        if all_señales:
            st.markdown('''
            <div class="section-label" style="margin-top:36px; padding-top:28px; border-top:1px solid #E4E4E7;">SEÑALES PRIORITARIAS</div>
            <div style="font-size:11px; color:#8896A5; margin-bottom:10px;">
                Hallazgos que requieren atención especial al leer el paper completo.
                Generadas automáticamente por el sistema.
            </div>
            ''', unsafe_allow_html=True)

            for señal in all_señales:
                tipo = señal.get("tipo", "").upper().replace("_", " ")
                desc = señal.get("descripcion", "")
                impacto = señal.get("impacto_clinico", "")
                poblacion = señal.get("poblacion_afectada", "")
                if impacto == "alto":
                    badge, badge_color = "ALTO", "#991B1B"
                elif impacto == "medio":
                    badge, badge_color = "MEDIO", "#92400E"
                else:
                    badge, badge_color = "BAJO", "#475569"

                poblacion_html = (
                    f'<div style="font-size:11px; color:#8896A5; margin-top:6px;">'
                    f'Población afectada: {poblacion}</div>'
                    if poblacion and poblacion not in ([], "", "[]", "None", None)
                    else ""
                )

                st.markdown(f'''
                <div class="signal-card" style="background:var(--surface);
                            border:1px solid var(--border);
                            border-radius:var(--radius-sm); padding:12px 16px; margin:6px 0;">
                    <div style="display:flex; justify-content:space-between;
                                align-items:center; margin-bottom:6px;">
                        <span style="font-size:11px; font-weight:600;
                                     color:var(--muted); letter-spacing:0.6px;">{tipo}</span>
                        <span style="font-size:10px; font-weight:600;
                                     color:{badge_color}; letter-spacing:0.5px;">{badge}</span>
                    </div>
                    <div style="font-size:14px; color:var(--ink); line-height:1.6;">{desc}</div>
                    {poblacion_html}
                </div>
                ''', unsafe_allow_html=True)

        # ══ SECCIÓN 3 — MÉTRICAS ESTADÍSTICAS EXTRAÍDAS ═══════════
        st.markdown('''
        <div class="section-label" style="margin-top:36px; padding-top:28px; border-top:1px solid #E4E4E7;">
            MÉTRICAS ESTADÍSTICAS EXTRAÍDAS
        </div>
        <div style="font-size:11px; color:#8896A5; margin-bottom:10px;">
            Entidades biomédicas estructuradas extraídas del abstract.
        </div>
        ''', unsafe_allow_html=True)

        if final_df.empty:
            if error_count > 0:
                main_error = errors[0][1] if errors else "Error desconocido"
                if "Dato No Fiable" in main_error or "contenido no" in main_error:
                    reason = main_error.split(":")[-1].strip() if ":" in main_error else main_error
                    st.markdown(
                        f'<div class="alert-danger">❌ Filtro de Coherencia Activado: {reason}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="alert-clinical alert-review">Error en extracción de biomarcadores: {main_error}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    '<div class="alert-clinical alert-acceptable">No se encontraron biomarcadores en los abstracts procesados</div>',
                    unsafe_allow_html=True,
                )
        else:
            columnas_clinicas = [
                "Estado", "Entidad", "Tipo",
                "Población Afectada", "Métricas", "Riesgo de Omisión",
            ]
            cols_ok = [c for c in columnas_clinicas if c in final_df.columns]
            tabla_clinica = final_df[cols_ok]

            def highlight_status(val):
                if val == "p<0.05":
                    return "background-color: #FFF3E0; color: #92400E; font-weight: 500;"
                elif val == "INFERIDO":
                    return "background-color: #E8EAF6; color: #3730A3; font-weight: 500;"
                elif val == "OK":
                    return "color: #94A3B8; font-weight: 400;"
                elif val in ("DEMOG.", "EPID.", "MOL."):
                    return "color: #94A3B8; font-weight: 400;"
                elif val == "–":
                    return "color: #CBD5E1;"
                return ""

            def highlight_omission_risk(val):
                if val == "CRÍTICO":
                    return "background-color: #FFEBEE; color: #D32F2F; font-weight: bold;"
                return ""

            def clean_metricas_display(val):
                if not val or val in ("NO DISPONIBLE", "—"):
                    return "—"
                prefijos = [
                    "incidencia_anual_pct=",
                    "mortalidad_pct=",
                    "otros=",
                    "n_absoluto=",
                    "percentage of cases: ",
                ]
                partes = str(val).split(" | ")
                resultado = []
                for parte in partes:
                    parte_limpia = parte.strip()
                    for prefijo in prefijos:
                        if parte_limpia.lower().startswith(
                            prefijo.lower()
                        ):
                            parte_limpia = parte_limpia[len(prefijo):]
                            break
                    if parte_limpia.startswith("n=") and any(
                        "n=" in r for r in resultado
                    ):
                        continue
                    resultado.append(parte_limpia)
                return " | ".join(resultado)

            if "Métricas" in tabla_clinica.columns:
                tabla_clinica = tabla_clinica.copy()
                tabla_clinica["Métricas"] = tabla_clinica[
                    "Métricas"
                ].apply(clean_metricas_display)

            styled_tabla = tabla_clinica.style.applymap(
                highlight_status, subset=["Estado"]
            )
            if "Riesgo de Omisión" in tabla_clinica.columns:
                styled_tabla = styled_tabla.applymap(
                    highlight_omission_risk, subset=["Riesgo de Omisión"]
                )
            st.dataframe(styled_tabla, use_container_width=True, hide_index=True)

        # ══ SECCIÓN 4 — TRAZABILIDAD — FRAGMENTOS FUENTE ══════════
        if not final_df.empty and "Fragmento fuente" in final_df.columns:
            fragmentos_df = final_df[
                final_df["Fragmento fuente"].notna() &
                (final_df["Fragmento fuente"].astype(str).str.strip() != "")
            ]
            if not fragmentos_df.empty:
                st.markdown('''
                <div class="section-label" style="margin-top:36px; padding-top:28px; border-top:1px solid #E4E4E7;">
                    TRAZABILIDAD — FRAGMENTOS FUENTE
                </div>
                <div style="font-size:11px; color:#8896A5; margin-bottom:10px;">
                    Texto exacto del abstract del que se extrajo cada entidad.
                    Permite verificar la extracción contra el texto original.
                </div>
                ''', unsafe_allow_html=True)

                for _, row in fragmentos_df.iterrows():
                    entidad = row.get("Entidad", "")
                    fragmento = str(row.get("Fragmento fuente", "")).strip()
                    estado = row.get("Estado", "")
                    metricas = row.get("Métricas", "")
                    es_critico = str(row.get("Riesgo de Omisión", "")) == "CRÍTICO"
                    border_color = "#991B1B" if es_critico else "#E2E8F0"
                    bg_color = "#FEF2F2" if es_critico else "#F7F9FC"
                    metricas_str = metricas if metricas and metricas != "NO DISPONIBLE" else ""

                    st.markdown(f'''
                    <div class="fragment-card" style="border:1px solid {border_color}; border-radius:6px;
                                padding:10px 14px; margin:4px 0; background:{bg_color};">
                        <div style="display:flex; justify-content:space-between;
                                    align-items:baseline; margin-bottom:4px;">
                            <span style="font-size:13px; font-weight:600;
                                         color:#0D1B2A;">{estado} {entidad}</span>
                            <span style="font-size:11px; color:#1A56DB;
                                         font-family:monospace;">{metricas_str}</span>
                        </div>
                        <div style="font-size:13px; color:#4A5568;
                                    font-style:italic; line-height:1.5;">
                            "{fragmento}"
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)

        # ══ SECCIÓN MASIVO — RESUMEN + DETALLE ══════════════════
        if mode == "Masivo" and all_payloads:
            st.markdown(
                '<div class="section-label" style="margin-top:36px; padding-top:28px; border-top:1px solid #E4E4E7;">RESUMEN EJECUTIVO</div>'
                '<div style="font-size:11px; color:#71717A; margin-bottom:10px;">Una fila por abstract. Ordena por Anomal\u00edas cr\u00edticas para priorizar revisi\u00f3n.</div>',
                unsafe_allow_html=True
            )
            resumen_rows = []
            for i, p in enumerate(all_payloads, start=1):
                _payload = p.get("payload", {})
                _abstract_id = p.get("ID_Abstract", "file_" + str(i))
                _entidades = _payload.get("entidades_de_riesgo", [])
                _confianza = _cap_confianza_sin_metricas(_payload, _payload.get("nivel_confianza", 0))
                _senales = _payload.get("senales_prioritarias", _payload.get("se\u00f1ales_prioritarias", []))
                _criticos = sum(
                    1 for e in _entidades
                    if str(e.get("riesgo_omision", "")).upper() == "CR\u00cdTICO"
                )
                _senales_altas = sum(
                    1 for s in _senales
                    if s.get("impacto_clinico") == "alto"
                )
                if _criticos > 0:
                    _estado = "\U0001f6a8 Anomal\u00eda cr\u00edtica"
                elif _confianza >= 85:
                    _estado = "\u2705 Extracci\u00f3n completa"
                elif _confianza >= 60:
                    _estado = "\u26a0\ufe0f Extracci\u00f3n parcial"
                else:
                    _estado = "\U0001f50d Cobertura baja"
                resumen_rows.append({
                    "#": i,
                    "Abstract": _abstract_id,
                    "Estado": _estado,
                    "Entidades": len(_entidades),
                    "Confianza": str(_confianza) + "%",
                    "Anomal\u00edas cr\u00edticas": _criticos,
                    "Se\u00f1ales alto impacto": _senales_altas,
                })
            resumen_df = pd.DataFrame(resumen_rows)
            st.dataframe(resumen_df, use_container_width=True, hide_index=True)

            st.markdown(
                '<div class="section-label" style="margin-top:36px; padding-top:28px; border-top:1px solid #E4E4E7;">DETALLE POR ABSTRACT</div>'
                '<div style="font-size:11px; color:#71717A; margin-bottom:10px;">Expande cada abstract para ver el detalle completo de la extracci\u00f3n.</div>',
                unsafe_allow_html=True
            )
            for i, p in enumerate(all_payloads, start=1):
                _payload = p.get("payload", {})
                _abstract_id = p.get("ID_Abstract", "file_" + str(i))
                _entidades = _payload.get("entidades_de_riesgo", [])
                _confianza = _cap_confianza_sin_metricas(_payload, _payload.get("nivel_confianza", 0))
                _senales = _payload.get("senales_prioritarias", _payload.get("se\u00f1ales_prioritarias", []))
                _criticos = sum(
                    1 for e in _entidades
                    if str(e.get("riesgo_omision", "")).upper() == "CR\u00cdTICO"
                )
                if _criticos > 0:
                    _icono = "\U0001f6a8"
                elif _confianza >= 85:
                    _icono = "\u2705"
                elif _confianza >= 60:
                    _icono = "\u26a0\ufe0f"
                else:
                    _icono = "\U0001f50d"
                _label = (
                    _icono + " Abstract " + str(i) + " \u2014 " + str(_abstract_id) +
                    " \u2014 " + str(_confianza) + "% confianza" +
                    (" \u2014 " + str(_criticos) + " CR\u00cdTICO(S)" if _criticos > 0 else "")
                )
                with st.expander(_label, expanded=False):
                    if _senales:
                        st.markdown("**Se\u00f1ales prioritarias:**")
                        for s in _senales:
                            _tipo = s.get("tipo", "").upper()
                            _desc = s.get("descripcion", "")
                            _impacto = s.get("impacto_clinico", "")
                            _badge = "\U0001f534" if _impacto == "alto" else "\U0001f7e1" if _impacto == "medio" else "\U0001f535"
                            st.markdown(_badge + " **" + _tipo + "** \u2014 " + _desc)
                    if not final_df.empty:
                        _filas_abstract = [
                            row for _, row in final_df.iterrows()
                            if row.get("ID_Abstract") == _abstract_id
                        ]
                        if _filas_abstract:
                            _df_abstract = pd.DataFrame(_filas_abstract)
                            _cols_mostrar = [
                                c for c in ["Estado", "Entidad", "Tipo", "M\u00e9tricas", "Riesgo de Omisi\u00f3n"]
                                if c in _df_abstract.columns
                            ]
                            if _cols_mostrar:
                                st.dataframe(
                                    _df_abstract[_cols_mostrar],
                                    use_container_width=True,
                                    hide_index=True
                                )

        # ══ SECCIÓN 5 — EXPORTAR RESULTADOS ═══════════════════════
        st.markdown('''
        <div class="section-label" style="margin-top:36px; padding-top:28px; border-top:1px solid #E4E4E7;">EXPORTAR RESULTADOS</div>
        <div style="font-size:11px; color:#8896A5; margin-bottom:10px;">
            Descarga los resultados para uso en tu investigación.
            CSV para Excel/análisis estadístico. JSON para procesamiento programático.
        </div>
        ''', unsafe_allow_html=True)

        exp_col1, exp_col2, exp_col3 = st.columns(3)
        with exp_col1:
            if not final_df.empty:
                csv_buffer = io.StringIO()
                final_df.to_csv(csv_buffer, index=False)
                st.download_button(
                    "💾 Descargar CSV",
                    data=csv_buffer.getvalue(),
                    file_name="biomarcadores_extraidos.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            else:
                empty_csv = io.StringIO()
                pd.DataFrame(columns=[
                    "Estado", "Entidad", "Tipo", "Población Afectada",
                    "Métricas", "Riesgo de Omisión", "Fragmento fuente",
                ]).to_csv(empty_csv, index=False)
                st.download_button(
                    "💾 Descargar CSV (vacío)",
                    data=empty_csv.getvalue(),
                    file_name="biomarcadores_extraidos.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        with exp_col2:
            if hierarchical_json:
                st.download_button(
                    "📋 Descargar JSON estructurado",
                    data=json.dumps(hierarchical_json, indent=2, ensure_ascii=False),
                    file_name="bioextract_output.json",
                    mime="application/json",
                    use_container_width=True,
                )
        with exp_col3:
            _txt_report = build_txt_report(all_payloads, final_df)
            st.download_button(
                "📄 Descargar informe TXT",
                data=_txt_report.encode("utf-8"),
                file_name="bioextract_informe.txt",
                mime="text/plain",
                use_container_width=True,
            )

        if hierarchical_json:
            with st.expander("👁 Previsualizar JSON estructurado", expanded=False):
                st.markdown('''
                <div style="font-size:11px; color:#8896A5; margin-bottom:8px;">
                    Estructura de datos completa generada por BioExtract.
                    Formato estándar para integración con otros sistemas.
                </div>
                ''', unsafe_allow_html=True)
                st.code(
                    json.dumps(hierarchical_json, indent=2, ensure_ascii=False),
                    language="json"
                )
            with st.expander(
                "🔧 Datos de auditoría técnica  ·  "
                "Payload completo de la API — solo para "
                "depuración técnica, no relevante para "
                "uso clínico",
                expanded=False
            ):
                st.markdown("Complete API payload for technical audit:")
                st.code(
                    json.dumps(all_payloads, indent=2, ensure_ascii=False),
                    language="json"
                )

    # Errores técnicos (compactos, fuera del flujo principal)
    if errors or sensor_alerts:
        col_err, col_alert = st.columns(2)
        if errors:
            with col_err.expander(f"❌ Errores ({len(errors)})", expanded=False):
                err_df = pd.DataFrame(errors, columns=["Fila", "Error"])
                st.dataframe(err_df, use_container_width=True, hide_index=True)
        if sensor_alerts:
            with col_alert.expander(f"⚠️ Alertas ({len(sensor_alerts)})", expanded=False):
                sensor_df = pd.DataFrame(sensor_alerts, columns=["Fila", "Alerta"])
                st.dataframe(sensor_df, use_container_width=True, hide_index=True)

# KPI BAR (solo visible cuando hay datos procesados)
with kpi_placeholder.container():
    if processed_count > 0:
        st.markdown('<div class="kpi-band">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Procesados", processed_count)
        with col2:
            st.metric("Entidades", entity_count)
        with col3:
            st.metric("Alertas", total_alerts)
        with col4:
            st.metric("Confianza", f"{confidence_level}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Indicador de demo gratuita
    _, es_demo_check = resolve_api_key(user_api_key)
    if es_demo_check and st.session_state.demo_count > 0:
        restantes = DEMO_LIMIT - st.session_state.demo_count
        st.markdown(f'''
        <div style="font-size: 11px; color: #8896A5; 
                    text-align: right; margin-top: -12px;
                    margin-bottom: 8px;">
            Demo gratuita — {restantes} análisis restantes 
            de {DEMO_LIMIT} · 
            <a href="https://aistudio.google.com/app/apikey"
               target="_blank" style="color: #1A56DB;">
                Usar tu propia key →
            </a>
        </div>
        ''', unsafe_allow_html=True)



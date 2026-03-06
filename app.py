import io
import json
import os
import re
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
from google import generativeai as genai


st.set_page_config(
    page_title="Extractor de Biomarcadores - Cáncer de Mama",
    page_icon="🧬",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --bg: #f6f9fc;
        --panel: #ffffff;
        --text: #12324a;
        --muted: #4f6f88;
        --primary: #0f62a8;
        --accent: #2b8a7e;
        --border: #dce8f2;
        --shadow-1: 0 1px 2px rgba(16, 40, 64, 0.06);
        --shadow-2: 0 12px 24px rgba(16, 40, 64, 0.08);
    }
    .stApp {
        background: linear-gradient(180deg, #f6f9fc 0%, #eef4f9 100%);
        color: var(--text);
    }
    .main-card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 24px;
        box-shadow: var(--shadow-1), var(--shadow-2);
        margin-bottom: 24px;
    }
    .title {
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: 0.2px;
        color: var(--text);
        margin-bottom: 8px;
    }
    .subtitle {
        font-size: 1rem;
        color: var(--muted);
        margin-bottom: 0;
    }
    .note {
        border-left: 4px solid var(--primary);
        background: #f0f7ff;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0 0 0;
        color: #1a4d7a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="main-card">
      <div class="title">Extractor de Biomarcadores para Recerca de Càncer de Mama</div>
      <p class="subtitle">
        Pega el abstract de un artículo científico y obtén biomarcadores, microbiota relacionada,
        métricas (LFC/P-value) y nivel de evidencia en JSON estructurado.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)


def get_api_key() -> str:
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        try:
            api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
        except Exception:
            api_key = ""
    if not api_key:
        api_key = st.text_input(
            "API Key de Gemini",
            type="password",
            help="También puedes configurar GOOGLE_API_KEY en secrets.toml o variable de entorno.",
        ).strip()
    return api_key


def build_prompt(abstract: str) -> str:
    schema = {
        "results": [
            {
                "biomarcador": "string",
                "tipo_biomarcador": "proteina|gen|otro",
                "microbiota_relacionada": ["string"],
                "metricas": {"lfc": "number|null", "p_value": "number|null"},
                "nivel_evidencia": "in vitro|in vivo|clinico|meta-analisis|desconocido",
                "fragmento_fuente": "string",
            }
        ]
    }
    return f"""
Eres un asistente experto en oncología molecular y minería de literatura biomédica.
Extrae SOLO información explícitamente presente en el abstract.
No inventes biomarcadores ni métricas.
Devuelve EXCLUSIVAMENTE JSON válido, sin texto adicional.

Esquema JSON requerido:
{json.dumps(schema, ensure_ascii=False, indent=2)}

Reglas:
1) Extrae biomarcadores (proteínas/gens) mencionados en cáncer de mama.
2) Extrae microbiota relacionada solo si está mencionada.
3) Extrae métricas LFC y P-value cuando aparezcan (si no, null).
4) Clasifica nivel de evidencia en: in vitro, in vivo, clinico, meta-analisis, desconocido.
5) Incluye fragmento_fuente breve del abstract para trazabilidad.
6) Si no hay elementos, responde: {{"results": []}}.

Abstract:
\"\"\"{abstract}\"\"\"
"""


def parse_json_response(raw_text: str) -> Dict[str, Any]:
    raw_text = raw_text.strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", raw_text)
        if match:
            return json.loads(match.group(0))
        raise


def call_gemini_extract(abstract: str, api_key: str) -> Dict[str, Any]:
    genai.configure(api_key=api_key)
    model_candidates = [
        "gemini-2.5-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
    ]
    last_error = None
    response = None
    for model_name in model_candidates:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                build_prompt(abstract),
                generation_config={
                    "temperature": 0.0,
                    "response_mime_type": "application/json",
                },
            )
            break
        except Exception as exc:
            last_error = exc
            continue
    if response is None:
        raise ValueError(f"No fue posible invocar un modelo Gemini disponible: {last_error}")
    text = response.text if hasattr(response, "text") else ""
    if not text:
        raise ValueError("Gemini no devolvió contenido de texto.")
    data = parse_json_response(text)
    if "results" not in data or not isinstance(data["results"], list):
        raise ValueError("El JSON no contiene la clave 'results' con una lista.")
    return data


def normalize_results(results: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for item in results:
        microbiota = item.get("microbiota_relacionada", [])
        if isinstance(microbiota, list):
            microbiota_str = ", ".join(str(x) for x in microbiota)
        else:
            microbiota_str = str(microbiota) if microbiota is not None else ""
        metricas = item.get("metricas", {}) or {}
        rows.append(
            {
                "Biomarcador": item.get("biomarcador", ""),
                "Tipo": item.get("tipo_biomarcador", ""),
                "Microbiota relacionada": microbiota_str,
                "LFC": metricas.get("lfc", None),
                "P-value": metricas.get("p_value", None),
                "Nivel de evidencia": item.get("nivel_evidencia", ""),
                "Fragmento fuente": item.get("fragmento_fuente", ""),
            }
        )
    return pd.DataFrame(rows)


with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    abstract = st.text_area(
        "Abstract científico",
        placeholder="Pega aquí el resumen del artículo científico...",
        height=260,
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        api_key = get_api_key()
    with col2:
        st.markdown(
            '<div class="note">Se procesa únicamente el texto que proporciones. '
            "No se generan datos de ejemplo.</div>",
            unsafe_allow_html=True,
        )
    extract_clicked = st.button("Extraer biomarcadores", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


if extract_clicked:
    if not abstract.strip():
        st.warning("Necesitas pegar un abstract antes de ejecutar la extracción.")
    elif not api_key:
        st.error("Introduce una API Key válida de Gemini para continuar.")
    else:
        with st.spinner("Analizando abstract con Gemini Flash..."):
            try:
                payload = call_gemini_extract(abstract=abstract, api_key=api_key)
                results = payload.get("results", [])
                st.markdown("### Resultados extraídos")
                if not results:
                    st.info("No se identificaron biomarcadores con la evidencia requerida en este abstract.")
                else:
                    df = normalize_results(results)
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                    )

                    json_pretty = json.dumps(payload, ensure_ascii=False, indent=2)
                    st.markdown("#### JSON estructurado")
                    st.code(json_pretty, language="json")

                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    st.download_button(
                        label="Descargar resultados en CSV",
                        data=csv_buffer.getvalue(),
                        file_name="biomarcadores_cancer_mama.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
            except Exception as exc:
                st.error(f"Error durante la extracción: {exc}")

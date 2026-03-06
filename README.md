# BioExtract — Structured Literature Triage

**Herramienta de extracción estructurada de abstracts científicos oncológicos mediante LLM.**

Desarrollada por Lucas Chabrera Querol como proyecto de investigación aplicada en oncología de precisión.

---

## Demo

Prueba 5 análisis gratuitos sin configuración:  
🔗 [bioextract.streamlit.app](#) ← actualizar con URL real

---

## ¿Qué hace?

- Extrae entidades biomédicas, métricas estadísticas y biomarcadores de abstracts científicos oncológicos
- Infiere biomarcadores implícitos clínicamente relevantes:
  - HR+ → ER+, PR+ (inferido)
  - TNBC → ER-, PR-, HER2- (inferido)
  - HER2+ → ERBB2 amplificado (inferido)
- Detecta anomalías matemáticas universales con certeza determinista:
  - p-value fuera de [0, 1]
  - HR o OR negativos o igual a cero
  - NNT < 1
  - Intervalos de confianza invertidos
  - HR fuera de su propio IC
- Procesa lotes de abstracts desde CSV exportado de PubMed
- Genera señales de triaje para priorizar lectura
- Exporta resultados estructurados en CSV y JSON

---

## ¿Qué NO hace?

- No evalúa la calidad metodológica del estudio
- No detecta p-hacking ni sesgo de selección
- No reemplaza la lectura del paper original
- No valida concentraciones fisiológicas específicas por molécula

---

## Caso de uso principal

Un investigador con 500 abstracts de PubMed no puede leerlos todos con la misma atención.

BioExtract convierte semanas de triaje manual en 2-4 horas de revisión priorizada:
PubMed CSV (500 abstracts)
↓
BioExtract
↓
80 abstracts priorizados con métricas estructuradas
↓
Lectura focalizada del paper original

---

## Stack técnico

| Componente | Tecnología |
|---|---|
| Backend | Python 3.11 |
| Frontend | Streamlit |
| LLM | Google Gemini API |
| Extracción | Gemini 2.5 Flash |
| Validación | Reglas deterministas + Gemini |
| Export | CSV / JSON estructurado |

---

## Instalación local
```bash
git clone https://github.com/lukyskywalkercs/bioextract
cd bioextract
pip install -r requirements.txt
streamlit run app_investigacio.py
```

Configura tu API key de Gemini:
```bash
# Opción 1 — variable de entorno
export GOOGLE_API_KEY=tu_key_aquí

# Opción 2 — archivo secrets
mkdir .streamlit
echo 'GOOGLE_API_KEY = "tu_key_aquí"' > .streamlit/secrets.toml
```

Obtén una API key gratuita en:  
🔗 https://aistudio.google.com/app/apikey

---

## Uso

### Modo individual
1. Pega un abstract científico en el área de texto
2. Pulsa **Ejecutar análisis**
3. Revisa entidades extraídas, métricas y señales

### Modo masivo (CSV de PubMed)
1. Exporta tu búsqueda de PubMed como CSV
2. Sube el archivo en modo Masivo
3. Selecciona la columna de abstracts
4. Pulsa **Ejecutar análisis**
5. Descarga los resultados en CSV

---

## Validación del sistema

El sistema fue validado con 10 abstracts de prueba cubriendo los principales casos clínicos:

| Tipo | Resultado esperado | Estado |
|---|---|---|
| RCT limpio | ✅ Extracción completa ≥85% | ✅ |
| HR negativo | 🚨 Anomalía crítica | ✅ |
| Supervivencia >100% | 🚨 Anomalía crítica | ✅ |
| NNT < 1 | 🚨 Anomalía crítica | ✅ |
| IC invertido | 🚨 Anomalía crítica | ✅ |
| Abstract epidemiológico | ✅ Extracción completa | ✅ |

---

## Autor

**Lucas Chabrera Querol**  
GitHub: [@lukyskywalkercs](https://github.com/lukyskywalkercs)

---

## Licencia

© 2026 Lucas Chabrera Querol  
Uso personal y académico únicamente.  
Prohibida la reproducción comercial sin autorización expresa del autor.

---

## Aviso

Este sistema es una herramienta de triaje y extracción.
No constituye validación científica ni reemplaza el criterio del investigador. El investigador es siempre responsable de verificar los datos en el paper original.

"""
Script de verificación de los 3 fixes estructurales.
Ejecutar: python test_verificacion_fixes.py
No requiere API key de Gemini — prueba coerce_payload con payload simulado.
"""
import sys
sys.path.insert(0, ".")

from app_investigacio import coerce_payload, calculate_hierarchical_confidence

ABSTRACT_TEST = """This multicenter RCT evaluated pembrolizumab plus nab-paclitaxel 
versus placebo in 312 patients with triple-negative breast cancer 
(PD-L1 positive, CPS>=10). Progression-free survival showed benefit 
(HR=0.73, 95% CI 0.74-0.89, p=0.003). Overall survival improved 
(HR=0.81, 95% CI 0.68-0.96, p=0.012). FOXP3 upregulation in 
responders (LFC=2.8, p=0.003). Samples centrifuged at 1500 rpm 
and stored at -20°C. Grade 3-4 adverse events: 38.2% vs 14.6% 
(OR=3.6, p=0.0023). NNT=0.8."""

PAYLOAD_TEST = {
    "metadata": {"nivel_evidencia": "clinico", "tipo_estudio": "RCT"},
    "entidades_de_riesgo": [
        {
            "nombre": "Progression-free survival",
            "tipo": "clinico",
            "metricas": {"HR": 0.73, "ci_lower": 0.74, "ci_upper": 0.89, "p_value": 0.003},
            "fragmento_fuente": "HR=0.73, 95% CI 0.74-0.89, p=0.003",
        },
        {
            "nombre": "Grade 3-4 adverse events",
            "tipo": "clinico",
            "metricas": {"OR": 3.6, "p_value": 0.0023, "NNT": 0.8},
            "fragmento_fuente": "NNT=0.8",
        },
    ],
    "señales_prioritarias": [],
    "gaps_criticos": {},
}

ABSTRACT_A01_LIMPIO = """Prospective cohort of 450 patients with hormone receptor-positive 
breast cancer. Five-year overall survival 92.3% (95% CI 89.1-94.8). 
Distant recurrence rate 8.2% (HR=0.45, 95% CI 0.32-0.61, p<0.001). 
ER+ status associated with better prognosis."""

PAYLOAD_A01_LIMPIO = {
    "metadata": {"nivel_evidencia": "epidemiologico", "tipo_estudio": "cohort"},
    "entidades_de_riesgo": [
        {"nombre": "Five-year overall survival", "tipo": "clinico",
         "metricas": {"mortalidad_pct": 7.7, "ci_lower": 89.1, "ci_upper": 94.8},
         "fragmento_fuente": "Five-year overall survival 92.3% (95% CI 89.1-94.8)",
         "cualificador_original": "significantly"},
        {"nombre": "Distant recurrence", "tipo": "clinico",
         "metricas": {"HR": 0.45, "ci_lower": 0.32, "ci_upper": 0.61, "p_value": 0.001},
         "fragmento_fuente": "HR=0.45, 95% CI 0.32-0.61, p<0.001",
         "cualificador_original": "significantly"},
        {"nombre": "ER+ status", "tipo": "molecular", "metricas": {"p_value": 0.003},
         "fragmento_fuente": "ER+ status associated with better prognosis",
         "cualificador_original": "associated"},
        {"nombre": "Hormone receptor-positive", "tipo": "clinico", "metricas": {},
         "fragmento_fuente": "hormone receptor-positive breast cancer"},
        {"nombre": "Distant recurrence rate", "tipo": "epidemiologico",
         "metricas": {"HR": 0.45, "ci_lower": 0.32, "ci_upper": 0.61},
         "fragmento_fuente": "Distant recurrence rate 8.2% (HR=0.45, 95% CI 0.32-0.61)"},
    ],
    "señales_prioritarias": [{"tipo": "tendencia_emergente", "descripcion": "HR favorable", "impacto_clinico": "medio"}],
    "gaps_criticos": {},
}


def test_abstract_problematico():
    """Abstract con HR fuera de IC y NNT<1 debe generar anomalías matemáticas CRÍTICO."""
    print("=" * 60)
    print("TEST: Abstract problematico (HR fuera IC + NNT<1)")
    print("=" * 60)
    coerced = coerce_payload(PAYLOAD_TEST, abstract_text=ABSTRACT_TEST)
    senales = coerced.get("señales_prioritarias", [])
    entidades = coerced.get("entidades_de_riesgo", [])
    descripciones = [s.get("descripcion", "") for s in senales]
    paradoja_ic = any("IC" in d or "HR" in d for d in descripciones)
    paradoja_nnt = any("NNT" in d for d in descripciones)
    criticos = sum(1 for e in entidades if str(e.get("riesgo_omision", "")).upper() == "CRÍTICO")
    score, _ = calculate_hierarchical_confidence(
        entidades, senales, coerced.get("gaps_criticos", {}), coerced.get("metadata", {}))
    print(f"  Senales: {len(senales)}, CRITICO: {criticos}, Confianza: {score}%")
    ok = criticos >= 2 and (paradoja_ic or paradoja_nnt) and len(senales) >= 1 and score <= 60
    print(f"  [PASS]" if ok else "  [FAIL]")
    return ok


def test_abstract_limpio():
    print("\n" + "=" * 60)
    print("TEST: Abstract limpio (A01)")
    print("=" * 60)
    coerced = coerce_payload(PAYLOAD_A01_LIMPIO, abstract_text=ABSTRACT_A01_LIMPIO)
    senales = coerced.get("señales_prioritarias", [])
    entidades = coerced.get("entidades_de_riesgo", [])
    criticos = sum(1 for e in entidades if str(e.get("riesgo_omision", "")).upper() == "CRÍTICO")
    score, _ = calculate_hierarchical_confidence(
        entidades, senales, coerced.get("gaps_criticos", {}), coerced.get("metadata", {}))
    print(f"  Senales: {len(senales)}, CRITICO: {criticos}, Confianza: {score}%")
    ok = criticos == 0 and score >= 85
    print(f"  [PASS]" if ok else f"  [FAIL] (esperado >=85%, got {score}%)")
    return ok


if __name__ == "__main__":
    r1 = test_abstract_problematico()
    r2 = test_abstract_limpio()
    print("\n" + "=" * 60)
    print(f"RESUMEN: {'Todos los tests pasaron' if (r1 and r2) else 'Algun test fallo'}")
    print("=" * 60)
    sys.exit(0 if (r1 and r2) else 1)

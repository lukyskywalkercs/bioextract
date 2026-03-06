"""
Test obligatorio tras los 4 cambios en app_investigacio.py.
CASO 1: abstract limpio → ≥80%
CASO 2: 1 error crítico → exactamente 60%
CASO 3: 2 errores críticos → ≤40%
"""
import sys
sys.path.insert(0, ".")

from app_investigacio import coerce_payload

def get_nivel_confianza(coerced, validacion_ia=None):
    """Replica la lógica de call_gemini_extract para nivel_confianza."""
    validacion_ia = validacion_ia or {"nivel_confianza_cientifico": 70}
    confianza_ia = validacion_ia.get("nivel_confianza_cientifico", 70)
    confianza_ia = max(confianza_ia, 65)

    criticos = sum(
        1 for e in coerced.get("entidades_de_riesgo", [])
        if str(e.get("riesgo_omision", "")).upper() == "CRÍTICO"
    )
    if criticos >= 2:
        return min(confianza_ia, 40)
    elif criticos == 1:
        return min(confianza_ia, 60)
    return confianza_ia

# CASO 1 — abstract limpio, debe dar ≥80%
print("CASO 1: Abstract limpio")
payload1 = {
    "metadata": {"nivel_evidencia": "epidemiologico"},
    "entidades_de_riesgo": [
        {"nombre": "Breast cancer incidence", "tipo": "epidemiologico",
         "metricas": {"HR": 1.23, "ci_lower": 1.18, "ci_upper": 1.29, "p_value": 0.003},
         "fragmento_fuente": "HR=1.23, 95% CI 1.18-1.29, p=0.003"}
    ],
    "señales_prioritarias": [],
    "gaps_criticos": {},
}
c1 = coerce_payload(payload1, abstract_text="Breast cancer incidence increased 1.8% annually (HR=1.23, 95% CI 1.18-1.29, p=0.003).")
n1 = get_nivel_confianza(c1, {"nivel_confianza_cientifico": 85})
ok1 = n1 >= 80
print("  Confianza: %d%% -> %s" % (n1, "PASS" if ok1 else "FAIL"))

# CASO 2 — 1 error crítico, debe dar exactamente 60%
print("\nCASO 2: 1 error crítico (HR negativo)")
payload2 = {
    "metadata": {},
    "entidades_de_riesgo": [
        {"nombre": "PFS", "tipo": "clinico", "metricas": {"HR": -0.34, "p_value": 0.028},
         "fragmento_fuente": "HR=-0.34"}
    ],
    "señales_prioritarias": [],
    "gaps_criticos": {},
}
c2 = coerce_payload(payload2, abstract_text="Five-year overall survival was 127% in patients diagnosed at localized stage.")
n2 = get_nivel_confianza(c2, {"nivel_confianza_cientifico": 70})
ok2 = n2 == 60
print("  Confianza: %d%% -> %s" % (n2, "PASS" if ok2 else "FAIL"))

# CASO 3 — 2 errores críticos, debe dar ≤40%
print("\nCASO 3: 2 errores críticos (HR negativo + NNT<1)")
payload3 = {
    "metadata": {},
    "entidades_de_riesgo": [
        {"nombre": "PFS", "tipo": "clinico", "metricas": {"HR": -0.34, "p_value": 0.028}, "fragmento_fuente": "HR=-0.34"},
        {"nombre": "NNT", "tipo": "clinico", "metricas": {"NNT": 0.8}, "fragmento_fuente": "NNT=0.8"}
    ],
    "señales_prioritarias": [],
    "gaps_criticos": {},
}
c3 = coerce_payload(payload3, abstract_text="Progression-free survival HR=-0.34 (p=0.028). NNT=0.8.")
n3 = get_nivel_confianza(c3, {"nivel_confianza_cientifico": 70})
ok3 = n3 <= 40
print("  Confianza: %d%% -> %s" % (n3, "PASS" if ok3 else "FAIL"))

print("\n" + "="*50)
print("RESUMEN: %s" % ("Todos PASS" if (ok1 and ok2 and ok3) else "Algun FAIL"))
sys.exit(0 if (ok1 and ok2 and ok3) else 1)

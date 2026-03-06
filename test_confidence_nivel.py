"""
Test obligatorio: nivel_confianza según CRÍTICO.
- 1 entidad CRÍTICO → confianza entre 55-65%
- Abstract limpio sin errores → confianza ≥ 80%
"""
import sys
sys.path.insert(0, ".")

from app_investigacio import coerce_payload

def get_nivel_confianza(coerced, validacion_ia=None):
    """Aplica la misma lógica que call_gemini_extract para nivel_confianza."""
    validacion_ia = validacion_ia or {"nivel_confianza_cientifico": 70}
    confianza_ia = validacion_ia.get("nivel_confianza_cientifico", 70)
    criticos = sum(
        1 for e in coerced.get("entidades_de_riesgo", [])
        if str(e.get("riesgo_omision", "")).upper() == "CRÍTICO"
    )
    if criticos >= 2:
        return min(confianza_ia, 40)
    elif criticos == 1:
        return min(confianza_ia, 60)
    return confianza_ia

# CASO 1: 1 entidad CRÍTICO → 55-65%
print("CASO 1: 1 entidad CRÍTICO")
payload_critico = {
    "metadata": {},
    "entidades_de_riesgo": [
        {"nombre": "PFS", "tipo": "clinico", "metricas": {"HR": -0.34, "p_value": 0.028},
         "fragmento_fuente": "HR=-0.34", "riesgo_omision": "CRÍTICO"}
    ],
    "señales_prioritarias": [],
    "gaps_criticos": {},
}
coerced1 = coerce_payload(payload_critico, abstract_text="HR=-0.34")
# coerce_payload marca CRÍTICO por validate_physical_limits; si el payload ya tiene 1 CRÍTICO
# lo mantendrá. Pero coerce_payload procesa y puede cambiar. Mejor usar payload que genere 1 CRÍTICO.
# HR=-0.34 genera CRÍTICO en validate_physical_limits.
coerced1 = coerce_payload(
    {"metadata": {}, "entidades_de_riesgo": [
        {"nombre": "PFS", "tipo": "clinico", "metricas": {"HR": -0.34, "p_value": 0.028},
         "fragmento_fuente": "HR=-0.34"}
    ], "señales_prioritarias": [], "gaps_criticos": {}},
    abstract_text="HR=-0.34"
)
nivel1 = get_nivel_confianza(coerced1, {"nivel_confianza_cientifico": 70})
ok1 = 55 <= nivel1 <= 65
print("  Confianza: %d%% -> %s" % (nivel1, "PASS" if ok1 else "FAIL"))

# CASO 2: Abstract limpio sin errores → ≥80%
print("\nCASO 2: Abstract limpio")
payload_limpio = {
    "metadata": {"nivel_evidencia": "epidemiologico"},
    "entidades_de_riesgo": [
        {"nombre": "Breast cancer", "tipo": "epidemiologico",
         "metricas": {"HR": 1.23, "ci_lower": 1.18, "ci_upper": 1.29, "p_value": 0.003},
         "fragmento_fuente": "HR=1.23, 95% CI 1.18-1.29, p=0.003"}
    ],
    "señales_prioritarias": [],
    "gaps_criticos": {},
}
coerced2 = coerce_payload(payload_limpio, abstract_text="HR=1.23, 95% CI 1.18-1.29, p=0.003")
nivel2 = get_nivel_confianza(coerced2, {"nivel_confianza_cientifico": 85})
ok2 = nivel2 >= 80
print("  Confianza: %d%% -> %s" % (nivel2, "PASS" if ok2 else "FAIL"))

print("\n" + "="*50)
print("RESUMEN: %s" % ("Todos PASS" if (ok1 and ok2) else "Algun FAIL"))
sys.exit(0 if (ok1 and ok2) else 1)

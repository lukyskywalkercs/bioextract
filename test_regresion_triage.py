"""
Test de regresion para BioExtract - Extractor de Triaje.
Verifica los 3 casos obligatorios tras la reestructuracion.
"""
import sys
sys.path.insert(0, ".")

from app_investigacio import coerce_payload, calculate_hierarchical_confidence

def run(abstract, payload):
    c = coerce_payload(payload, abstract_text=abstract)
    ent = c.get("entidades_de_riesgo", [])
    sen = c.get("señales_prioritarias", [])
    score, _ = calculate_hierarchical_confidence(
        ent, sen, c.get("gaps_criticos", {}), c.get("metadata", {}))
    criticos = sum(1 for e in ent if str(e.get("riesgo_omision","")).upper() == "CRÍTICO")
    return score, criticos, sen

# CASO 1 - Extraccion completa >=85%
print("CASO 1: Abstract coherente")
s1, c1, _ = run(
    "Breast cancer incidence increased 1.8% annually (HR=1.23, 95% CI 1.18-1.29, p=0.003).",
    {"metadata": {"nivel_evidencia": "epidemiologico"}, "entidades_de_riesgo": [
        {"nombre": "Breast cancer incidence", "tipo": "epidemiologico",
         "metricas": {"HR": 1.23, "ci_lower": 1.18, "ci_upper": 1.29, "p_value": 0.003},
         "fragmento_fuente": "HR=1.23, 95% CI 1.18-1.29, p=0.003"}
    ], "señales_prioritarias": [], "gaps_criticos": {}})
ok1 = s1 >= 85 and c1 == 0
print("  Score: %d%%, CRITICO: %d -> %s" % (s1, c1, "PASS" if ok1 else "FAIL"))

# CASO 2 - Anomalia matematica critica
print("\nCASO 2: HR negativo + NNT<1")
s2, c2, sen2 = run(
    "Progression-free survival HR=-0.34 (p=0.028). NNT=0.8.",
    {"metadata": {}, "entidades_de_riesgo": [
        {"nombre": "PFS", "tipo": "clinico", "metricas": {"HR": -0.34, "p_value": 0.028}, "fragmento_fuente": "HR=-0.34"},
        {"nombre": "NNT", "tipo": "clinico", "metricas": {"NNT": 0.8}, "fragmento_fuente": "NNT=0.8"}
    ], "señales_prioritarias": [], "gaps_criticos": {}})
ok2 = c2 >= 1 and len(sen2) >= 1
print("  Score: %d%%, CRITICO: %d, Senales: %d -> %s" % (s2, c2, len(sen2), "PASS" if ok2 else "FAIL"))

# CASO 3 - Extraccion completa, incoherencia NO activa alerta matematica
print("\nCASO 3: IC-pvalue incoherente (NO debe ser anomalia matematica)")
s3, c3, sen3 = run(
    "HR=0.76 (95% CI 0.58-0.99, p=0.12).",
    {"metadata": {}, "entidades_de_riesgo": [
        {"nombre": "PFS", "tipo": "clinico",
         "metricas": {"HR": 0.76, "ci_lower": 0.58, "ci_upper": 0.99, "p_value": 0.12},
         "fragmento_fuente": "HR=0.76 (95% CI 0.58-0.99, p=0.12)"}
    ], "señales_prioritarias": [], "gaps_criticos": {}})
ok3 = c3 == 0 and s3 >= 85
print("  Score: %d%%, CRITICO: %d -> %s" % (s3, c3, "PASS" if ok3 else "FAIL"))

print("\n" + "="*50)
print("RESUMEN: %s" % ("Todos PASS" if (ok1 and ok2 and ok3) else "Algun FAIL"))
sys.exit(0 if (ok1 and ok2 and ok3) else 1)

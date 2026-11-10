"""Verificación de trazabilidad (Paso 12).

1. Todos los enlaces relativos de los documentos Markdown del proyecto apuntan a archivos existentes.
2. Las cifras clave del informe final y de la presentación coinciden con los artefactos que las generan
   (tablas y JSON de `reports/` y `data/processed/qa_report.json`), con la tolerancia de redondeo indicada.

Uso (desde la raíz):  python scripts/check_traceability.py [--out docs/evidence/paso12/trazabilidad.json]
"""
import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "reports" / "tables"
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")


def check_links():
    rows = []
    for md in [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md")), ROOT / "presentation" / "README.md"]:
        for target in LINK.findall(md.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            ok = (md.parent / target).resolve().exists()
            rows.append({"documento": str(md.relative_to(ROOT)), "enlace": target, "existe": ok})
    return rows


def j(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def claims():
    qa = j("data/processed/qa_report.json")
    eda = j("reports/tables/01_EDA/eda_metrics.json")
    reg = pd.read_csv(T / "03_regression/metricas_test.csv").set_index("modelo")["MAE"]
    sel_r = j("reports/tables/03_regression/seleccion_congelada.json")["modelo_seleccionado"]
    clf = pd.read_csv(T / "04_classification/metricas_test.csv").set_index("modelo")
    sel_c = j("reports/tables/04_classification/seleccion_congelada.json")["modelo_seleccionado"]
    clu = j("reports/tables/05_clustering/clustering_metrics.json")
    integ = j("reports/tables/06_integrated_evaluation/integrated_metrics.json")
    cov = pd.read_csv(T / "06_integrated_evaluation/cobertura_topk.csv")
    c10 = cov[(cov["K"] == 10) & (cov["conjunto"] == "TEST2025")].set_index("estrategia")["cobertura"]
    eq = {r["perfil"]: r for r in integ["sesgos"]["selecciones_por_perfil"]}
    mort = eda["actores"]["participacion_en_hechos_mortales"]
    return [
        ("Hechos en la fuente", 65818, qa["hechos"]["filas_fuente"], 0),
        ("Víctimas en la fuente", 75197, qa["victimas"]["filas_fuente"], 0),
        ("% de hechos mortales con víctima moto o peatón", 81, mort["MOTO"] + mort["PEATON"], 0.5),
        ("% del top 10 mensual que se repite", 68, eda["concentracion"]["top10_mensual_repite_mes_siguiente"]["media"] * 100, 0.5),
        ("Cobertura top 10, media de 12 meses (2025, %)", 42.7, c10["historial_media12"] * 100, 0.05),
        ("Cobertura top 10, clasificador (2025, %)", 43.1, c10["clasificador"] * 100, 0.05),
        ("Cobertura top 10, oráculo (2025, %)", 44.6, c10["oraculo"] * 100, 0.05),
        ("% de la ganancia posible captada por el historial", 92, (c10["historial_media12"] - c10["azar_esperado"]) / (c10["oraculo"] - c10["azar_esperado"]) * 100, 0.5),
        ("MAE regresión seleccionada (2025)", 4.07, reg[sel_r], 0.005),
        ("MAE media de 12 meses (2025)", 4.06, reg["baseline:media12"], 0.005),
        ("P@10 clasificador (2025)", 0.808, clf.loc[sel_c, "P@10_R0"], 0.0005),
        ("P@10 media de 12 meses (2025)", 0.792, clf.loc["baseline:media12", "P@10_R0"], 0.0005),
        ("Silhouette del clustering seleccionado", 0.33, clu["seleccion"]["silhouette"], 0.005),
        ("% de corredores que cambia de cuartil", 43, integ["exposicion_h8"]["pct_cambia_cuartil"], 0.5),
        ("% de hechos en barrios de borde (2025)", 16.2, eq["Borde (Gral. Paz/autopistas)"]["pct_hechos"], 0.05),
        ("% de selecciones top 10 del clasificador en el borde", 8.3, eq["Borde (Gral. Paz/autopistas)"]["pct_selecciones_clf"], 0.05),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "evidence" / "paso12" / "trazabilidad.json")
    a = ap.parse_args()
    links = check_links()
    cl = [{"cifra": n, "informada": v, "artefacto": round(float(x), 4), "coincide": abs(float(x) - v) <= tol} for n, v, x, tol in claims()]
    res = {"enlaces_total": len(links), "enlaces_rotos": [l for l in links if not l["existe"]], "cifras": cl,
           "cifras_que_no_coinciden": [c for c in cl if not c["coincide"]]}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Enlaces: {len(links)} revisados, {len(res['enlaces_rotos'])} rotos")
    for c in cl:
        print(("OK  " if c["coincide"] else "DIF ") + f"{c['cifra']}: informada {c['informada']} | artefacto {c['artefacto']}")
    sys.exit(1 if res["enlaces_rotos"] or res["cifras_que_no_coinciden"] else 0)


if __name__ == "__main__":
    main()

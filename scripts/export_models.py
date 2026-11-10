"""Exporta los modelos finales congelados de los Pasos 07 y 08 (Paso 12).

Reajusta cada configuración seleccionada (`reports/tables/0{3,4}_*/seleccion_congelada.json`) con el entrenamiento
final (objetivos de 2020-01 a 2024-12, gap = 0) y la guarda en `models/`. Para comprobar la correspondencia, verifica
que las predicciones de 2025 coincidan con las guardadas por los notebooks. No vuelve a seleccionar ni a evaluar nada.

Uso (desde la raíz):  python scripts/export_models.py
"""
import hashlib
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import classification as Cl, features as F, regression as R  # noqa: E402


def main() -> None:
    out = ROOT / "models"
    out.mkdir(exist_ok=True)
    X = R.add_log_features(F.build_features(F.load_panel(), F.queen_neighbors(), h=1, gap=0))
    tr, te = F.final_split(X)
    meta = {"sklearn": sklearn.__version__, "entrenamiento": [str(X.loc[tr, "mes_objetivo"].min()), str(X.loc[tr, "mes_objetivo"].max())],
            "filas_entrenamiento": int(tr.sum()), "modelos": {}}
    specs = [("regresion", ROOT / "reports/tables/03_regression", R.make_model, "y_target", "predict"),
             ("clasificacion", ROOT / "reports/tables/04_classification", Cl.make_model, "top10_target", "predict_proba")]
    for name, tab, factory, target, method in specs:
        sel = json.loads((tab / "seleccion_congelada.json").read_text(encoding="utf-8"))
        trm = R.train_mask_excluding_pandemia(X, tr, sel["params"]["excluir_pandemia"])
        y = X.loc[trm, target].astype(int) if name == "clasificacion" else X.loc[trm, target]
        model = factory(sel["familia"], sel["params"]).fit(X.loc[trm], y)
        pred = getattr(model, method)(X.loc[te])
        pred = pred[:, 1] if pred.ndim == 2 else pred
        saved = pd.read_csv(tab / "predicciones_test.csv")[sel["modelo_seleccionado"]].to_numpy()
        ok = bool(np.allclose(pred, saved, rtol=1e-6, atol=1e-9))
        path = out / f"{name}_final.joblib"
        joblib.dump(model, path)
        meta["modelos"][name] = {"configuracion": sel["modelo_seleccionado"], "archivo": path.name,
                                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                 "predicciones_2025_coinciden_con_notebook": ok, "objetivo": target}
        if not ok:
            raise SystemExit(f"Las predicciones de {name} no coinciden con las guardadas")
    (out / "models_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(meta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

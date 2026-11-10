"""Atributos de perfil territorial y utilidades de estabilidad para el clustering (Paso 09).

Los atributos se calculan solo con los meses de la ventana indicada, que por defecto es el desarrollo 2019–2024 sin
meses anómalos. **Nunca incluyen 2025**, que es el test reservado de los Pasos 07, 08 y 10. Se distinguen:

- **perfil relativo:** proporciones que no dependen del volumen (horario, fin de semana, estacionalidad, modo de la
  víctima, tipo de vía del hecho);
- **volumen:** nivel medio y densidad, que se usan solo en la variante "volumen + relativo" y para caracterizar.

La gravedad (KSI) no entra en el agrupamiento, por su faltante diferencial y su registro cambiante (E9). Se usa solo
para describir los grupos.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

MODOS = ["MOTO", "PEATON", "BICICLETA", "AUTO", "TRANSPORTE PUBLICO"]
FRANJAS = {"madrugada_0_5": range(0, 6), "manana_6_11": range(6, 12), "tarde_12_17": range(12, 18), "noche_18_23": range(18, 24)}
ATTR_HORARIO = [f"pct_{k}" for k in FRANJAS] + ["pct_fin_de_semana"]
ATTR_ESTACION = ["pct_trim1", "pct_trim2", "pct_trim3", "pct_trim4"]
ATTR_MODO = [f"pct_{m.lower().replace(' ', '_')}" for m in MODOS] + ["pct_otros_modos"]
ATTR_VIA = ["pct_avenida", "pct_autopista_gralpaz"]
ATTR_RELATIVO = ATTR_HORARIO + ATTR_ESTACION + ATTR_MODO + ATTR_VIA
ATTR_VOLUMEN = ["log_hechos_mes", "log_densidad_km2_anio"]


def default_months() -> list[str]:
    """Desarrollo 2019-01 a 2024-12 sin los meses marcados (registro 2019-11/12 y pandemia 2020-03 a 2021-05)."""
    m = pd.period_range("2019-01", "2024-12", freq="M").astype(str)
    excl = {"2019-11", "2019-12"} | set(pd.period_range("2020-03", "2021-05", freq="M").astype(str))
    return [x for x in m if x not in excl]


def build_attributes(hechos: pd.DataFrame, area_km2: pd.Series, months: list[str]) -> pd.DataFrame:
    """Una fila por barrio con atributos de perfil calculados solo con `months`.

    Denominadores:
    - horario: hechos con hora;
    - modo: hechos con modo informado (SD excluido; su proporción se informa aparte);
    - vía: hechos de 2020 en adelante con `tipo_de_via` informado (en 2019 falta en el 95 %).
    """
    if any(m >= "2025-01" for m in months):
        raise ValueError("Los atributos de perfil no pueden usar el test 2025")
    h = hechos[hechos["mes"].isin(months) & hechos["barrio"].notna()].copy()
    g = h.groupby("barrio")
    out = pd.DataFrame({"hechos": g.size()})
    hh = h.dropna(subset=["hora_entera"])
    for k, rng in FRANJAS.items():
        out[f"pct_{k}"] = hh.assign(_x=hh["hora_entera"].astype(int).isin(rng)).groupby("barrio")["_x"].mean()
    out["pct_fin_de_semana"] = g["dia_semana"].apply(lambda s: s.isin([5, 6]).mean())
    trim = (h["mes"].str[5:7].astype(int) - 1) // 3 + 1
    for q in range(1, 5):
        out[f"pct_trim{q}"] = h.assign(_x=trim.eq(q)).groupby("barrio")["_x"].mean()
    hm = h[h["modo_victima"] != "SD"]
    for m, col in zip(MODOS, ATTR_MODO[:-1]):
        out[col] = hm.assign(_x=hm["modo_victima"].eq(m)).groupby("barrio")["_x"].mean()
    out["pct_otros_modos"] = hm.assign(_x=~hm["modo_victima"].isin(MODOS)).groupby("barrio")["_x"].mean()
    hv = h[(h["anio"] >= 2020) & (h["tipo_de_via"] != "SD")]
    out["pct_avenida"] = hv.assign(_x=hv["tipo_de_via"].eq("AVENIDA")).groupby("barrio")["_x"].mean()
    out["pct_autopista_gralpaz"] = hv.assign(_x=hv["tipo_de_via"].isin(["AUTOPISTA", "AV. GRAL. PAZ"])).groupby("barrio")["_x"].mean()
    n_months = len(months)
    out["log_hechos_mes"] = np.log(out["hechos"] / n_months)
    out["log_densidad_km2_anio"] = np.log(out["hechos"] / (n_months / 12) / area_km2.reindex(out.index))
    # Descriptivos (no se usan para agrupar)
    out["pct_modo_sd"] = g["modo_victima"].apply(lambda s: s.eq("SD").mean())
    out["pct_ksi"] = g["ksi"].mean()
    out["n_meses"] = n_months
    return out.fillna(0.0)


def bootstrap_ari(Z: np.ndarray, fit_predict, labels_full: np.ndarray, reps: int = 200, seed: int = 20261110) -> np.ndarray:
    """Estabilidad por remuestreo de barrios. En cada réplica se reajusta con una muestra bootstrap y se compara,
    con el ARI, la partición de los barrios incluidos frente a la solución completa. `fit_predict(Zb)` debe devolver
    las etiquetas de las filas de Zb."""
    from sklearn.metrics import adjusted_rand_score
    rng = np.random.default_rng(seed)
    n = len(Z)
    out = np.empty(reps)
    for r in range(reps):
        idx = np.unique(rng.choice(n, n, replace=True))
        out[r] = adjusted_rand_score(labels_full[idx], fit_predict(Z[idx]))
    return out

"""Variables predictoras, objetivos y particiones temporales (Paso 06).

Convenciones
------------
- **Fila:** barrio x mes objetivo ``T``.
- **Horizonte:** ``h`` (por defecto 1). El corte del pronóstico es ``c = T - h``.
- **Latencia:** ``gap`` (por defecto 0). Es la cantidad de meses del corte que aún no estarían disponibles por demoras de
  publicación. El último mes observable es ``L = T - h - gap``. **Toda variable usa solo meses <= L**, salvo los
  atributos estáticos (superficie, comuna) y el calendario del mes objetivo, que se conoce de antemano.
- **Objetivos:** ``y_target`` (hechos del mes T) y ``top10_target`` (T está entre los 10 barrios de más hechos del mes,
  con la regla de desempate R0, ``src.labels``).
- **Exclusiones:** se excluyen deliberadamente la infraestructura vial (D11), la exposición (D8), la gravedad (KSI, por
  registro cambiante y por la definición de mortal a 30 días) y las marcas de anomalía del mes objetivo o la marca de
  "registro" (conocimiento ex post). Ver ``EXCLUDED``.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.labels import SEED, top_k_labels

ROOT = Path(__file__).resolve().parents[1]
K_TOP = 10
MODOS = ["moto", "peaton", "bicicleta", "auto", "transporte_publico", "otros", "sd"]
PANDEMIA = pd.period_range("2020-03", "2021-05", freq="M")

FEATURES_HIST = ["y_lag1", "y_lag2", "y_lag3", "y_lag12", "y_ma3", "y_ma6", "y_ma12", "tendencia_ma3_ma12",
                 "share_lag1", "share_ma12", "rank_lag1", "rank_ma12", "top10_freq12", "densidad_ma12"]
FEATURES_CITY = ["ciudad_lag1", "ciudad_ma12", "ciudad_lag12"]
FEATURES_TEMP = ["mes_sin", "mes_cos", "n_pandemia_ventana12"]
FEATURES_TERR = ["area_km2"]
FEATURES_CAT = ["comuna"]
FEATURES_SPATIAL = ["vecinos_ma3", "vecinos_share_ma12"]
FEATURES_COMP = [f"comp_{m}_12m" for m in MODOS]
FEATURES_MAIN = FEATURES_HIST + FEATURES_CITY + FEATURES_TEMP + FEATURES_TERR + FEATURES_SPATIAL + FEATURES_COMP
EXCLUDED = {
    "infraestructura (callejero, semáforos)": "estado vigente sin fechas de vigencia; D11",
    "exposición (conteos vehiculares)": "solo 2024 y en corredores; D8",
    "KSI / gravedad rezagada": "registro cambiante entre años (E9) y gravedad mortal definida a 30 días",
    "anomalía del mes objetivo": "no se conoce en el corte (p. ej., el inicio de la pandemia)",
    "marca 'registro' 2019-11/12": "anotación ex post de la auditoría; no disponible en tiempo real",
}

TEST_START = pd.Period("2025-01", "M")
DEV_FIRST_TARGET = pd.Period("2020-01", "M")    # primer mes con 12 meses de historia completos
VAL_YEARS = (2022, 2023, 2024)


# --------------------------------------------------------------------------- carga
def load_panel(path: Path | None = None) -> pd.DataFrame:
    p = pd.read_csv(path or ROOT / "data" / "processed" / "panel_barrio_mes.csv", dtype={"mes": str})
    p["mes"] = pd.PeriodIndex(p["mes"], freq="M")
    return p.sort_values(["barrio", "mes"]).reset_index(drop=True)


def queen_neighbors(barrios_geojson: Path | None = None) -> dict[str, list[str]]:
    """Vecindad *queen*: barrios cuyos polígonos se tocan al menos en un punto (límite o vértice), en el CRS plano de
    CABA. Es la misma definición que el AED (§5)."""
    import geopandas as gpd
    from src.data_processing import CRS_CABA
    g = gpd.read_file(barrios_geojson or ROOT / "data" / "raw" / "limites" / "barrios.geojson").to_crs(CRS_CABA)
    g = g.rename(columns={"nombre": "barrio"}).set_index("barrio")
    nb = {}
    for b, geom in g.geometry.items():
        cand = g.index[g.geometry.intersects(geom)]
        nb[b] = sorted(o for o in cand if o != b)
    return nb


# --------------------------------------------------------------------------- variables
def _wide(panel: pd.DataFrame, col: str) -> pd.DataFrame:
    w = panel.pivot(index="mes", columns="barrio", values=col).sort_index()
    full = pd.period_range(w.index.min(), w.index.max(), freq="M")
    if len(full) != len(w) or w.isna().any().any():
        raise ValueError(f"Panel incompleto para {col}: debe tener todas las combinaciones barrio-mes")
    return w.astype(float)


def build_features(panel: pd.DataFrame, neighbors: dict[str, list[str]], h: int = 1, gap: int = 0,
                   seed: int = SEED) -> pd.DataFrame:
    """Devuelve una fila por (barrio, mes objetivo T) con variables que solo usan meses <= T - h - gap."""
    if h < 1 or gap < 0 or h + gap > 12:
        raise ValueError("Se requiere h >= 1, gap >= 0 y h + gap <= 12")
    s = h + gap                                     # desplazamiento desde el mes objetivo al último mes observable
    Y = _wide(panel, "y_hechos")
    city = Y.sum(axis=1)
    sh = Y.div(city, axis=0)
    rk = Y.rank(axis=1, ascending=False, method="average")
    # Top 10 observado en cada mes (R0); se usa solo en ventanas que terminan en L
    lab = top_k_labels(panel.assign(_y=panel["y_hechos"]), "barrio", "mes", K_TOP, seed=seed, ycol="_y")
    TOP = panel.assign(t=lab.astype(float)).pivot(index="mes", columns="barrio", values="t").sort_index()
    area = panel.groupby("barrio")["area_km2"].first()
    comuna = panel.groupby("barrio")["comuna_barrio"].first()
    comp = {m: _wide(panel, f"hechos_modo_{m}") for m in MODOS}

    def at(W, lag_from_L=0):       # valor en el mes L - lag_from_L, alineado con T
        return W.shift(s + lag_from_L)

    def roll(W, n, fn="mean"):     # ventana de n meses que termina en L
        return getattr(W.rolling(n, min_periods=n), fn)().shift(s)

    F = {
        "y_lag1": at(Y, 0), "y_lag2": at(Y, 1), "y_lag3": at(Y, 2),
        "y_lag12": Y.shift(12),                    # mismo mes del año anterior (T - 12 <= L porque s <= 12)
        "y_ma3": roll(Y, 3), "y_ma6": roll(Y, 6), "y_ma12": roll(Y, 12),
        "share_lag1": at(sh, 0), "share_ma12": roll(Y, 12, "sum").div(roll(city.to_frame("c"), 12, "sum")["c"], axis=0),
        "rank_lag1": at(rk, 0), "rank_ma12": roll(rk, 12), "top10_freq12": roll(TOP, 12),
    }
    F["tendencia_ma3_ma12"] = F["y_ma3"] / F["y_ma12"]
    F["densidad_ma12"] = F["y_ma12"].div(area, axis=1)
    nb_cols = list(Y.columns)
    Wn = pd.DataFrame(0.0, index=nb_cols, columns=nb_cols)
    for b in nb_cols:
        if neighbors.get(b):
            Wn.loc[b, neighbors[b]] = 1.0 / len(neighbors[b])
    F["vecinos_ma3"] = F["y_ma3"] @ Wn.T
    F["vecinos_share_ma12"] = F["share_ma12"] @ Wn.T
    tot12 = roll(Y, 12, "sum")
    for m in MODOS:
        F[f"comp_{m}_12m"] = roll(comp[m], 12, "sum") / tot12

    rows = []
    for name, W in F.items():
        rows.append(W.stack(future_stack=True).rename(name))
    X = pd.concat(rows, axis=1).rename_axis(["mes_objetivo", "barrio"]).reset_index()
    T = X["mes_objetivo"]
    X["mes_ultimo_observado"] = T - s
    X["horizonte"], X["gap"] = h, gap
    # Ciudad (nivel general), calendario del objetivo, pandemia en la ventana observada
    cs = pd.DataFrame({"ciudad_lag1": city.shift(s), "ciudad_ma12": city.rolling(12, min_periods=12).mean().shift(s),
                       "ciudad_lag12": city.shift(12)})
    X = X.merge(cs, left_on="mes_objetivo", right_index=True, how="left")
    X["mes_calendario"] = T.dt.month
    X["mes_sin"], X["mes_cos"] = np.sin(2 * np.pi * X["mes_calendario"] / 12), np.cos(2 * np.pi * X["mes_calendario"] / 12)
    pand = pd.Series(Y.index.isin(PANDEMIA).astype(float), index=Y.index)
    X = X.merge(pand.rolling(12, min_periods=12).sum().shift(s).rename("n_pandemia_ventana12"), left_on="mes_objetivo", right_index=True, how="left")
    X["area_km2"] = X["barrio"].map(area)
    X["comuna"] = X["barrio"].map(comuna).astype(int)
    # Objetivos
    X["y_target"] = [Y.at[t, b] for t, b in zip(X["mes_objetivo"], X["barrio"])]
    X["top10_target"] = [bool(TOP.at[t, b]) for t, b in zip(X["mes_objetivo"], X["barrio"])]
    X["features_completas"] = X[FEATURES_MAIN].notna().all(axis=1)
    X["particion"] = np.where(X["mes_objetivo"] >= TEST_START, "test", "desarrollo")
    cols = ["barrio", "mes_objetivo", "mes_ultimo_observado", "horizonte", "gap", "particion", "features_completas",
            "y_target", "top10_target", "comuna", "mes_calendario"] + [c for c in FEATURES_MAIN if c not in ("comuna",)]
    return X[cols].sort_values(["mes_objetivo", "barrio"]).reset_index(drop=True)


# --------------------------------------------------------------------------- particiones
def _observable_at_evaluation_start(X: pd.DataFrame, evaluation: pd.Series) -> pd.Period:
    first_target = X.loc[evaluation, "mes_objetivo"].min()
    first_month = evaluation & X["mes_objetivo"].eq(first_target)
    return X.loc[first_month, "mes_ultimo_observado"].min()


def temporal_folds(X: pd.DataFrame, val_years=VAL_YEARS, first_target=DEV_FIRST_TARGET):
    """Validación expansiva por año con etiquetas disponibles al inicio de cada fold.
    Las mismas fechas sirven para regresión y clasificación."""
    ok = X["features_completas"] & (X["particion"] == "desarrollo") & (X["mes_objetivo"] >= first_target)
    folds = []
    for y in val_years:
        va = ok & (X["mes_objetivo"].dt.year == y)
        observable = _observable_at_evaluation_start(X, va)
        tr = ok & X["mes_objetivo"].le(observable)
        folds.append({"fold": f"V{y}", "train": tr.to_numpy(), "val": va.to_numpy(),
                      "train_desde": str(X.loc[tr, "mes_objetivo"].min()), "train_hasta": str(X.loc[tr, "mes_objetivo"].max()),
                      "val_desde": str(X.loc[va, "mes_objetivo"].min()), "val_hasta": str(X.loc[va, "mes_objetivo"].max())})
    return folds


def final_split(X: pd.DataFrame, first_target=DEV_FIRST_TARGET):
    """Ajuste final con etiquetas de desarrollo disponibles al comienzo del test reservado."""
    tr = X["features_completas"] & (X["particion"] == "desarrollo") & (X["mes_objetivo"] >= first_target)
    te = X["features_completas"] & (X["particion"] == "test")
    observable = _observable_at_evaluation_start(X, te)
    tr &= X["mes_objetivo"].le(observable)
    return tr.to_numpy(), te.to_numpy()


# --------------------------------------------------------------------------- preprocesamiento por fold
def make_preprocessor(numeric: list[str] | None = None, categorical: list[str] | None = None, scale: bool = True):
    """ColumnTransformer que se ajusta **solo** con el entrenamiento del fold (dentro de un Pipeline)."""
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    numeric = [c for c in (numeric or FEATURES_MAIN) if c not in FEATURES_CAT]
    categorical = categorical if categorical is not None else FEATURES_CAT
    num_steps = [("imputar", SimpleImputer(strategy="median"))] + ([("escalar", StandardScaler())] if scale else [])
    return ColumnTransformer([("num", Pipeline(num_steps), numeric),
                              ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical)],
                             verbose_feature_names_out=False)


# --------------------------------------------------------------------------- CLI
def main() -> None:
    """Escribe data/processed/features_barrio_mes_h{h}_g{gap}.csv para la configuración principal (h=1, gap=0)
    y la de sensibilidad a la latencia (h=1, gap=1)."""
    import json
    panel, nb = load_panel(), queen_neighbors()
    out = ROOT / "data" / "processed"
    meta = {"features_main": FEATURES_MAIN, "excluidas": EXCLUDED, "test_desde": str(TEST_START),
            "primer_objetivo_desarrollo": str(DEV_FIRST_TARGET), "folds_validacion": list(VAL_YEARS), "K": K_TOP, "archivos": {}}
    for gap in (0, 1):
        X = build_features(panel, nb, h=1, gap=gap)
        name = f"features_barrio_mes_h1_g{gap}.csv"
        X.astype({"mes_objetivo": str, "mes_ultimo_observado": str}).to_csv(out / name, index=False)
        meta["archivos"][name] = {"filas": len(X), "completas_desarrollo": int((X["features_completas"] & (X["particion"] == "desarrollo")).sum()),
                                  "completas_test": int((X["features_completas"] & (X["particion"] == "test")).sum())}
    (out / "features_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(meta["archivos"], indent=2))


if __name__ == "__main__":
    main()

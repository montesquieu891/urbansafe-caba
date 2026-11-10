"""Integridad temporal y controles de fuga de src.features (Paso 06).

Requiere data/processed/panel_barrio_mes.csv (python -m src.data_processing) y data/raw/limites/barrios.geojson.
"""
import numpy as np
import pandas as pd
import pytest

from src import features as f

MODO_COLS = [f"hechos_modo_{m}" for m in f.MODOS]


@pytest.fixture(scope="module")
def base():
    panel = f.load_panel()
    nb = f.queen_neighbors()
    return panel, nb, f.build_features(panel, nb)


def _perturb_after(panel, cut, seed=0):
    """Reemplaza todos los datos posteriores a `cut` por valores aleatorios coherentes."""
    rng = np.random.default_rng(seed)
    p = panel.copy()
    m = p["mes"] > cut
    comp = rng.integers(0, 60, size=(m.sum(), len(MODO_COLS)))
    p.loc[m, MODO_COLS] = comp
    p.loc[m, "y_hechos"] = comp.sum(axis=1)
    return p


# ---------------------------------------------------------------- cobertura y unicidad
def test_panel_y_features_unicos_y_completos(base):
    panel, _, X = base
    assert X[["barrio", "mes_objetivo"]].drop_duplicates().shape[0] == len(X) == 48 * 84
    assert (X.groupby("mes_objetivo").size() == 48).all()
    ok = X[X["features_completas"]]
    assert ok["mes_objetivo"].min() == pd.Period("2020-01", "M")
    assert ok[f.FEATURES_MAIN].notna().all().all()


def test_objetivos_alineados(base):
    panel, _, X = base
    y = panel.set_index(["barrio", "mes"])["y_hechos"]
    assert (X["y_target"].to_numpy() == y.loc[list(zip(X["barrio"], X["mes_objetivo"]))].to_numpy()).all()
    assert (X.groupby("mes_objetivo")["top10_target"].sum() == 10).all()


# ---------------------------------------------------------------- fuga temporal
@pytest.mark.parametrize("gap", [0, 1])
@pytest.mark.parametrize("cut", ["2021-06", "2023-11"])
def test_perturbar_futuro_no_cambia_features_previas(base, cut, gap):
    panel, nb, _ = base
    cut = pd.Period(cut, "M")
    X0 = f.build_features(panel, nb, gap=gap)
    X1 = f.build_features(_perturb_after(panel, cut), nb, gap=gap)
    keep = X0["mes_ultimo_observado"] <= cut
    feats = [c for c in f.FEATURES_MAIN]
    pd.testing.assert_frame_equal(X0.loc[keep, feats].reset_index(drop=True), X1.loc[keep, feats].reset_index(drop=True))
    # control positivo: después del corte las variables sí cambian
    after = (X0["mes_ultimo_observado"] > cut) & X0["features_completas"]
    assert not np.allclose(X0.loc[after, "y_lag1"], X1.loc[after, "y_lag1"])


def test_objetivo_de_clasificacion_solo_depende_del_mes_objetivo(base):
    panel, nb, X0 = base
    p = panel.copy()
    other = p["mes"] != pd.Period("2022-05", "M")
    p.loc[other, "y_hechos"] = p.loc[other, "y_hechos"][::-1].to_numpy()
    p.loc[other, MODO_COLS] = p.loc[other, MODO_COLS][::-1].to_numpy()
    X1 = f.build_features(p, nb)
    m = X0["mes_objetivo"] == pd.Period("2022-05", "M")
    assert (X0.loc[m, "top10_target"].to_numpy() == X1.loc[m, "top10_target"].to_numpy()).all()


def test_rezagos_no_cruzan_barrios_y_son_independientes_del_orden(base):
    panel, nb, X = base
    shuffled = panel.sample(frac=1, random_state=3)
    Xs = f.build_features(shuffled, nb)
    pd.testing.assert_frame_equal(X[f.FEATURES_MAIN], Xs[f.FEATURES_MAIN])
    # rezago 1 manual por barrio
    y = panel.set_index(["barrio", "mes"])["y_hechos"]
    sub = X[X["features_completas"]].sample(300, random_state=0)
    manual = [y.loc[(b, t - 1)] for b, t in zip(sub["barrio"], sub["mes_objetivo"])]
    assert np.allclose(sub["y_lag1"], manual)
    first = X[X["mes_objetivo"] == X["mes_objetivo"].min()]
    assert first["y_lag1"].isna().all()                       # el primer mes de cada barrio no hereda datos de otro


def test_gap_desplaza_la_informacion(base):
    panel, nb, X0 = base
    X1 = f.build_features(panel, nb, gap=1)
    assert (X1["mes_ultimo_observado"] == X1["mes_objetivo"] - 2).all()
    m = X0["features_completas"] & X1["features_completas"]
    a = X0.set_index(["barrio", "mes_objetivo"])["y_lag1"]
    b = X1.set_index(["barrio", "mes_objetivo"])["y_lag1"]
    shifted = a.groupby(level=0).shift(1)
    idx = X1.loc[m].set_index(["barrio", "mes_objetivo"]).index
    assert np.allclose(b.loc[idx], shifted.loc[idx])


# ---------------------------------------------------------------- particiones
def test_folds_cronologicos_y_disjuntos(base):
    _, _, X = base
    folds = f.temporal_folds(X)
    tr_te, te = f.final_split(X)
    test_months = set(X.loc[te, "mes_objetivo"])
    assert test_months == set(pd.period_range("2025-01", "2025-12", freq="M"))
    for fo in folds:
        trm, vam = X.loc[fo["train"], "mes_objetivo"], X.loc[fo["val"], "mes_objetivo"]
        assert trm.max() < vam.min()                                   # entrenamiento estrictamente anterior
        assert not (fo["train"] & fo["val"]).any()
        assert not set(trm) & test_months and not set(vam) & test_months
        assert (X.loc[fo["train"], "mes_ultimo_observado"] < vam.min()).all()
    assert [fo["fold"] for fo in folds] == ["V2022", "V2023", "V2024"]
    assert not set(X.loc[tr_te, "mes_objetivo"]) & test_months


@pytest.mark.parametrize("gap", [0, 1])
@pytest.mark.parametrize("fold", ["V2022", "V2023", "V2024", "FINAL"])
def test_etiquetas_de_entrenamiento_disponibles_al_inicio(base, gap, fold):
    panel, neighbors, X0 = base
    X = X0 if gap == 0 else f.build_features(panel, neighbors, gap=gap)
    if fold == "FINAL":
        train, evaluation = f.final_split(X)
    else:
        split = next(fo for fo in f.temporal_folds(X) if fo["fold"] == fold)
        train, evaluation = split["train"], split["val"]

    evaluation_year = "2025" if fold == "FINAL" else fold[1:]
    first_target = pd.Period(f"{evaluation_year}-01", "M")
    assert X.loc[evaluation, "mes_objetivo"].min() == first_target
    observable = first_target - 1 - gap
    assert X.loc[train, "mes_objetivo"].max() == observable
    assert not (train & evaluation).any()


def test_preprocesador_se_ajusta_solo_con_entrenamiento(base):
    _, _, X = base
    fo = f.temporal_folds(X)[0]
    pre = f.make_preprocessor()
    pre.fit(X.loc[fo["train"]])
    scaler = pre.named_transformers_["num"].named_steps["escalar"]
    num = [c for c in f.FEATURES_MAIN if c not in f.FEATURES_CAT]
    assert np.allclose(scaler.mean_, X.loc[fo["train"], num].mean().to_numpy())
    assert not np.allclose(scaler.mean_, X.loc[fo["train"] | fo["val"], num].mean().to_numpy())


def test_variables_excluidas_no_estan(base):
    _, _, X = base
    prohibidas = ["ksi", "grave", "mortal", "anomalia_mes", "registro", "km_vias", "avenida", "semaforo", "conteo_vehicular", "particion"]
    for c in f.FEATURES_MAIN:
        assert not any(p in c for p in prohibidas), c

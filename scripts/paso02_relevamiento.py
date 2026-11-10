"""Paso 02 de UrbanSafe CABA: relevamiento reproducible de fuentes.

Hace tres cosas:
1. Descarga los metadatos CKAN y los archivos del portal de datos abiertos de
   CABA (BA Data) que se usan en docs/data_inventory.md.
2. Calcula el SHA-256 de cada archivo y registra la fecha de extracción.
3. Perfila la estructura de los archivos (forma, columnas, faltantes,
   cobertura temporal, relación hechos-víctimas).

No limpia ni transforma los datos; eso corresponde al ETL del Paso 04. La
auditoría detallada de viabilidad corresponde al Paso 03.

Uso:
    python scripts/paso02_relevamiento.py --out <directorio_descarga> \
        [--evidence docs/evidence/paso02] [--skip-download]

Requiere: pandas, openpyxl.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import time
import urllib.request
from pathlib import Path

import pandas as pd

USER_AGENT = "urbansafe-research-client"
CKAN = "https://data.buenosaires.gob.ar/api/3/action/package_show?id={}"
CDN = "https://cdn.buenosaires.gob.ar/datosabiertos/datasets/"

# Conjuntos cuyos metadatos CKAN se registran (ver docs/source_register.csv).
DATASETS = [
    "victimas-siniestros-viales",
    "barrios",
    "comunas",
    "calles",
    "volumen_vehicular",
    "conteos-peatonales",
    "conteo-vehicular",
    "sensores-transito",
    "cruces-semaforizados",
]

# Archivos descargados y perfilados (ruta relativa al CDN).
FILES = [
    "transporte-y-obras-publicas/victimas-siniestros-viales/siniestros_viales_hechos.csv",
    "transporte-y-obras-publicas/victimas-siniestros-viales/siniestros_viales_victimas.csv",
    "transporte-y-obras-publicas/victimas-siniestros-viales/siniestros_viales_hechos.xlsx",
    "transporte-y-obras-publicas/victimas-siniestros-viales/siniestros_viales_victimas.xlsx",
    "transporte-y-obras-publicas/victimas-siniestros-viales/NOTAS_SINIESTROS_VIALES_2019-2025.pdf",
    "innovacion-transformacion-digital/barrios/barrios.geojson",
    "innovacion-transformacion-digital/comunas/comunas.geojson",
    "jefatura-de-gabinete-de-ministros/calles/callejero.geojson",
    "jefatura-de-gabinete-de-ministros/calles/callejero.csv",
    "transporte-y-obras-publicas/volumen_vehicular/conteo_vehicular_2024.xlsx",
    "transporte-y-obras-publicas/volumen_vehicular/conteo_Vehicular_detalle_semanal_2024.xlsx",
    "transporte-y-obras-publicas/volumen_vehicular/ubicaciones.xlsx",
    "transporte-y-obras-publicas/volumen_vehicular/diccionario_conteo_vehicular.xlsx",
    "transporte-y-obras-publicas/conteos-peatonales/conteos-peatonales.csv",
    "transporte-y-obras-publicas/conteo-vehicular/conteo-vehicular.csv",
    "transporte-y-obras-publicas/sensores-transito/sensores.csv",
    "transporte-y-obras-publicas/cruces-semaforizados/cruces-semaforizados.csv",
]


def fetch(url: str, dest: Path) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = resp.read()
    dest.write_bytes(data)
    return len(data)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv_auto(path: Path) -> pd.DataFrame:
    raw = path.read_bytes()
    try:
        txt = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        txt = raw.decode("latin1")
    head = txt[:2000]
    sep = ";" if head.count(";") > head.count(",") else ","
    return pd.read_csv(io.StringIO(txt), sep=sep, dtype=str, low_memory=False)


def download(out: Path, evidence: Path) -> None:
    meta_dir = evidence / "ckan_metadata"
    meta_dir.mkdir(parents=True, exist_ok=True)
    for ds in DATASETS:
        dest = meta_dir / f"{ds}.json"
        try:
            fetch(CKAN.format(ds), dest)
            json.loads(dest.read_text(encoding="utf-8"))
            print(f"metadatos OK  {ds}")
        except Exception as exc:  # el portal aplica un WAF ante ráfagas
            print(f"metadatos ERR {ds}: {exc}")
        time.sleep(3)
    out.mkdir(parents=True, exist_ok=True)
    for rel in FILES:
        n = fetch(CDN + rel, out / Path(rel).name)
        print(f"archivo OK    {Path(rel).name} ({n} bytes)")
        time.sleep(1)
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    (evidence / "fecha_extraccion.txt").write_text(stamp + "\n", encoding="utf-8")


def write_hashes(out: Path, evidence: Path) -> None:
    lines = [f"{sha256(out / Path(rel).name)}  {Path(rel).name}" for rel in FILES]
    (evidence / "sha256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def profile(out: Path) -> str:
    log: list[str] = []
    p = log.append

    h = read_csv_auto(out / "siniestros_viales_hechos.csv")
    v = read_csv_auto(out / "siniestros_viales_victimas.csv")
    fecha = pd.to_datetime(h["fecha_siniestro"], format="mixed", errors="coerce")
    lat = pd.to_numeric(h["latitud_siniestro"].str.replace(",", "."), errors="coerce")
    lon = pd.to_numeric(h["longitud_siniestro"].str.replace(",", "."), errors="coerce")
    comuna = h["comuna_siniestro"].str.extract(r"(\d+)")[0]

    p("## Hechos (siniestros_viales_hechos.csv)")
    p(f"filas={len(h)} columnas={h.shape[1]} id_unico={h['id_siniestro'].is_unique}")
    p(f"columnas={list(h.columns)}")
    p(f"fecha_min={fecha.min().date()} fecha_max={fecha.max().date()} fechas_no_parseables={int(fecha.isna().sum())}")
    iso = h["fecha_siniestro"].str.match(r"^\d{4}-\d{2}-\d{2}$")
    p(f"fechas_sin_formato_ISO={int((~iso).sum())}")
    p("hechos por año y mes:\n" + pd.crosstab(fecha.dt.year, fecha.dt.month).to_string())
    p("hechos por año y gravedad:\n" + pd.crosstab(h["anio_siniestro"], h["gravedad_siniestro"]).to_string())
    p(f"prefijo_id={h['id_siniestro'].str[:2].value_counts().to_dict()}")
    p(f"sin_coordenada_numerica={int(lat.isna().sum())} ({lat.isna().mean():.4f})")
    p(f"fuera_bbox_CABA_aprox={int((lat.notna() & ~(lat.between(-34.71, -34.52) & lon.between(-58.54, -58.33))).sum())}")
    p(f"sin_coordenada_por_gravedad={lat.isna().groupby(h['gravedad_siniestro']).mean().round(3).to_dict()}")
    p(f"etiquetas_comuna_distintas={h['comuna_siniestro'].nunique()} comuna_sin_dato={int(comuna.isna().sum())}")
    p(f"sin_coordenada_y_sin_comuna={int((lat.isna() & comuna.isna()).sum())}")
    p(f"tipo_de_via_faltante_por_año={h['tipo_de_via_siniestro'].isna().groupby(h['anio_siniestro']).mean().round(3).to_dict()}")
    p(f"modo_victima_SD_por_año={(h['modo_desplazamiento_victima'] == 'SD').groupby(h['anio_siniestro']).mean().round(3).to_dict()}")

    p("\n## Víctimas (siniestros_viales_victimas.csv)")
    p(f"filas={len(v)} columnas={v.shape[1]} columnas={list(v.columns)}")
    p(f"id_nulos={int(v['id_siniestro'].isna().sum())} ids_distintos={v['id_siniestro'].nunique()}")
    p(f"huerfanos_victima_sin_hecho={int((~v['id_siniestro'].dropna().isin(h['id_siniestro'])).sum())}")
    p(f"hechos_sin_victima={int((~h['id_siniestro'].isin(v['id_siniestro'])).sum())}")
    filas = v.groupby("id_siniestro").size().reindex(h["id_siniestro"]).to_numpy()
    suma = h[["numero_victimas_leve_siniestro", "numero_victimas_grave_siniestro",
              "numero_victimas_mortal_siniestro"]].apply(pd.to_numeric).sum(axis=1).to_numpy()
    p(f"suma_leve_grave_mortal_igual_filas_victimas={(suma == filas).mean():.4f}")
    p(f"gravedad_victima_normalizada={v['GRAVEdad_victima'].str.upper().value_counts().to_dict()}")
    p(f"filas_victima_identicas={int(v.duplicated().sum())}")
    for c in ["modo_desplazamiento_victima", "sexo_victima", "edad_victima", "rol_victima"]:
        sd = (v[c].isna() | v[c].str.upper().isin(["SD"])).mean()
        p(f"faltante_o_SD[{c}]={sd:.4f}")

    p("\n## Límites y red vial")
    for name in ["barrios", "comunas", "callejero"]:
        g = json.loads((out / f"{name}.geojson").read_text(encoding="utf-8"))
        props = list(g["features"][0]["properties"].keys())
        p(f"{name}: entidades={len(g['features'])} crs={g.get('crs', {}).get('properties', {}).get('name')} campos={props}")

    p("\n## Exposición")
    a = pd.read_excel(out / "conteo_vehicular_2024.xlsx")
    p(f"volumen_2024: filas={len(a)} ubicaciones={a['ubicacion_conteo'].nunique()} "
      f"fechas={a['fecha_conteo'].min()}..{a['fecha_conteo'].max()} n_fechas={a['fecha_conteo'].nunique()} "
      f"dias_semana={pd.to_datetime(a['fecha_conteo']).dt.day_name().value_counts().to_dict()} "
      f"comunas={a['comuna_conteo'].nunique()} tipo_via={a['especificacion_via_conteos'].value_counts().to_dict()}")
    for f in ["conteos-peatonales.csv", "conteo-vehicular.csv", "sensores.csv", "cruces-semaforizados.csv"]:
        d = read_csv_auto(out / f)
        fcol = next((c for c in d.columns if c.startswith("fecha")), None)
        fechas = d[fcol].dropna() if fcol else None
        rng = f" fechas={fechas.min()}..{fechas.max()} (lexicográfico)" if fcol else ""
        p(f"{f}: filas={len(d)} columnas={list(d.columns)}{rng}")
    return "\n".join(log)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path, help="directorio de descarga (fuera del repo)")
    ap.add_argument("--evidence", type=Path, default=Path("docs/evidence/paso02"))
    ap.add_argument("--skip-download", action="store_true")
    args = ap.parse_args()
    args.evidence.mkdir(parents=True, exist_ok=True)
    if not args.skip_download:
        download(args.out, args.evidence)
    write_hashes(args.out, args.evidence)
    report = profile(args.out)
    (args.evidence / "perfil_estructural.txt").write_text(report + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()

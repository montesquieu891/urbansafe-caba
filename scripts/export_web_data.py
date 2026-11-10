"""Exportación pública v1: solo agregados auditados; nunca entrena modelos.

Ejecutar: python scripts/export_web_data.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.evaluation import block_bootstrap_ci, topk_coverage
from src.labels import top_k_labels

SCHEMA = '1.0.0'
SEED = 20261111
KS = (5, 10, 15)
TABLES = 'reports/tables/'
INPUTS = {
    'panel': 'data/processed/panel_barrio_mes.csv',
    'geometria': 'data/raw/limites/barrios.geojson',
    'regresion': TABLES + '03_regression/predicciones_test.csv',
    'clasificacion': TABLES + '04_classification/predicciones_test.csv',
    'seleccion_reg': TABLES + '03_regression/seleccion_congelada.json',
    'seleccion_clf': TABLES + '04_classification/seleccion_congelada.json',
    'perfiles': TABLES + '05_clustering/asignacion_barrios.csv',
    'cobertura': TABLES + '06_integrated_evaluation/cobertura_topk.csv',
    'diferencias': TABLES + '06_integrated_evaluation/cobertura_diferencias_vs_historial.csv',
    'fuentes': 'docs/source_register.csv',
    'diccionario': 'docs/data_dictionary.md',
    'protocolo': 'docs/experimental_protocol.md',
    'informe_perfiles': 'docs/clustering_report.md',
    'etiquetado': 'src/labels.py',
    'evaluacion': 'src/evaluation.py',
    'exportador': 'scripts/export_web_data.py',
}
STRATEGIES = {'historial_media12': 'y_ma12', 'historial_persistencia': 'y_lag1',
              'clasificador': 'clasificador', 'regresion': 'regresion', 'oraculo': 'y_target'}
MODES = ['auto', 'bicicleta', 'moto', 'otros', 'peaton', 'sd', 'transporte_publico']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + '\n').encode('utf-8')


def records(df):
    return json.loads(df.to_json(orient='records', force_ascii=False, double_precision=15))


def observation(value):
    """No imputar ausencia como cero, ni cero como ausencia."""
    if pd.isna(value):
        return {'valor': None, 'estado': 'sin_datos'}
    require(np.isfinite(value) and value >= 0 and int(value) == value, 'Conteo inválido')
    return {'valor': int(value), 'estado': 'observado'}


def unique(df, keys, n, label):
    require(len(df) == n and not df[keys].isna().any().any()
            and not df.duplicated(keys).any(), f'{label}: cantidad, nulos o claves duplicadas')


def close(a, b, label):
    require(np.allclose(a, b, rtol=0, atol=1e-12), f'Discrepancia: {label}')


def build(root=ROOT):
    paths = {k: root / v for k, v in INPUTS.items()}
    hashes = {k: sha(v) for k, v in paths.items()}
    csv = lambda key: pd.read_csv(paths[key])
    js = lambda key: json.loads(paths[key].read_text(encoding='utf-8-sig'))
    p = csv('panel').sort_values(['id_barrio', 'mes']).reset_index(drop=True)
    unique(p, ['id_barrio', 'mes'], 4032, 'panel')
    dictionary = p[['id_barrio', 'barrio', 'comuna_barrio', 'area_km2']].drop_duplicates()
    unique(dictionary, ['id_barrio'], 48, 'diccionario id')
    unique(dictionary, ['barrio'], 48, 'diccionario nombre')
    require((dictionary.area_km2 > 0).all(), 'Superficie inválida')
    months = pd.period_range('2019-01', '2025-12', freq='M').astype(str)
    expected = {(i, m) for i in dictionary.id_barrio for m in months}
    require(set(zip(p.id_barrio, p.mes)) == expected, 'Panel incompleto')
    counts = ['y_hechos'] + ['hechos_modo_' + m for m in MODES]
    require(p[counts].notna().all().all(), 'El panel auditado no admite nuevos faltantes')
    for col in counts:
        for value in p[col]:
            observation(value)
    require((p[counts[1:]].sum(axis=1) == p.y_hechos).all(), 'Composición no reconcilia')
    geo = js('geometria')
    require(geo['crs']['properties']['name'] == 'urn:ogc:def:crs:OGC:1.3:CRS84', 'CRS inesperado')
    properties = pd.DataFrame([f['properties'] for f in geo['features']])
    unique(properties, ['id'], 48, 'geometrías')
    mapped = dictionary.merge(properties, left_on='id_barrio', right_on='id',
                              how='outer', validate='one_to_one', indicator=True)
    require(mapped['_merge'].eq('both').all() and mapped.barrio.eq(mapped.nombre).all()
            and mapped.comuna.eq(mapped.comuna_barrio).all(), 'Correspondencia de geometrías inválida')
    from shapely.geometry import shape
    for f in geo['features']:
        geom = shape(f['geometry'])
        require(geom.geom_type in ('Polygon', 'MultiPolygon') and geom.is_valid and not geom.is_empty,
                'Geometría inválida')
    public_geo = {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'id': f['properties']['id'],
         'properties': {'id_barrio': f['properties']['id'], 'nombre': f['properties']['nombre'],
                        'comuna': f['properties']['comuna']}, 'geometry': f['geometry']}
        for f in sorted(geo['features'], key=lambda f: f['properties']['id'])]}
    name_to_id = dictionary.set_index('barrio').id_barrio.to_dict()

    def identify(df, n, keys):
        unique(df, keys, n, 'tabla fuente')
        require(set(df.barrio) == set(name_to_id), 'Nombres sin correspondencia o barrios ausentes')
        df = df.copy()
        df['id_barrio'] = df.barrio.map(name_to_id)
        return df

    r, c = (identify(csv(key), 576, ['barrio', 'mes_objetivo']) for key in ('regresion', 'clasificacion'))
    keys = ['id_barrio', 'mes_objetivo']
    r, c = (df.sort_values(keys).reset_index(drop=True) for df in (r, c))
    require(r[keys].equals(c[keys]), 'Claves de predicciones diferentes')
    for col in ['y_target', 'y_ma12', 'y_lag1']:
        close(r[col], c[col], col)
    model_r, model_c = js('seleccion_reg')['modelo_seleccionado'], js('seleccion_clf')['modelo_seleccionado']
    d = r[['barrio', 'id_barrio', 'mes_objetivo', 'y_target', 'y_ma12', 'y_lag1']].copy()
    d['regresion'], d['clasificador'] = r[model_r], c[model_c]
    require(np.isfinite(d[list(STRATEGIES.values())].to_numpy()).all(), 'Puntajes no finitos')
    require(d.clasificador.between(0, 1).all(), 'Probabilidad fuera de rango')
    obs = p[p.mes.str.startswith('2025')][['id_barrio', 'mes', 'y_hechos']].rename(columns={'mes': 'mes_objetivo'})
    joined = d.merge(obs, on=keys, how='outer', validate='one_to_one', indicator=True)
    require(joined['_merge'].eq('both').all(), 'Pérdida de filas en evaluación')
    close(joined.y_target, joined.y_hechos, 'observados 2025')
    # Reconciliar historial congelado contra meses anteriores, sin recalcular modelos.
    panel_lookup = p.set_index(['id_barrio', 'mes']).y_hechos
    for row in d.itertuples():
        target = pd.Period(row.mes_objetivo, freq='M')
        hist = [panel_lookup.loc[(row.id_barrio, str(target - j))] for j in range(1, 13)]
        close(row.y_lag1, hist[0], 'persistencia')
        close(row.y_ma12, np.mean(hist), 'historial 12 meses')
    d['mes_observable'] = (pd.PeriodIndex(d.mes_objetivo, freq='M') - 1).astype(str)
    frozen_top = top_k_labels(d, 'barrio', 'mes_objetivo', 10, seed=20261110, ycol='y_target')
    require(np.array_equal(frozen_top, c.top10_target), 'Etiqueta objetivo congelada difiere')
    profile = identify(csv('perfiles'), 48, ['barrio']).sort_values('id_barrio')
    require(profile.groupby('k3').grupo.nunique().eq(1).all()
            and sorted(profile.grupo.value_counts()) == [9, 39], 'Perfiles no anidados o grupos inesperados')
    require(profile[['grupo', 'k3', 'perfil_k3']].notna().all().all(), 'Perfil ausente')

    reference = csv('cobertura').query("conjunto == 'TEST2025'")
    unique(reference, ['K', 'estrategia'], 18, 'cobertura test')
    difference = csv('diferencias')
    unique(difference, ['K', 'estrategia'], 6, 'intervalos')
    monthly, annual, selections, series, tie_cases = [], [], {}, {}, 0
    for k in KS:
        for strategy, score in STRATEGIES.items():
            chosen = top_k_labels(d, 'barrio', 'mes_objetivo', k, seed=SEED, ycol=score)
            shuffled = d.sample(frac=1, random_state=42)
            invariant = top_k_labels(shuffled, 'barrio', 'mes_objetivo', k, seed=SEED, ycol=score)
            require(chosen.equals(invariant.reindex(d.index)), 'Desempate depende del orden de filas')
            selections[strategy, k] = chosen
            values, captured_total, total = [], 0, 0
            for month, g in d.groupby('mes_objetivo', sort=True):
                selected = g.loc[chosen.loc[g.index]]
                require(len(selected) == k, 'Selección mensual no respeta K')
                cutoff = selected[score].min()
                tie_cases += int((g[score].eq(cutoff).sum() > 1))
                captured, denominator = int(selected.y_target.sum()), int(g.y_target.sum())
                require(denominator > 0, 'Cobertura indefinida: denominador cero')
                coverage = captured / denominator
                values.append(coverage); captured_total += captured; total += denominator
                monthly.append({'mes_objetivo': month, 'estrategia': strategy, 'K': k,
                                'hechos_cubiertos': captured, 'hechos_totales': denominator,
                                'cobertura': coverage, 'ids_seleccionados': sorted(selected.id_barrio.tolist())})
            s = pd.Series(values, index=sorted(d.mes_objetivo.unique()))
            close(s, topk_coverage(d, score, k), 'módulo evaluación ' + strategy)
            saved = reference[(reference.K == k) & (reference.estrategia == strategy)]
            require(len(saved) == 1, 'Referencia faltante')
            close(s.mean(), saved.cobertura.iloc[0], 'tabla Paso 10 ' + strategy)
            series[strategy, k] = s
            annual.append({'periodo': '2025', 'estrategia': strategy, 'K': k,
                           'media_coberturas_mensuales': float(s.mean()),
                           'cobertura_agregada': captured_total / total})
        saved = reference[(reference.K == k) & (reference.estrategia == 'azar_esperado')]
        close(saved.cobertura, k / 48, 'azar esperado')
        annual.append({'periodo': '2025', 'estrategia': 'azar_esperado', 'K': k,
                       'media_coberturas_mensuales': k / 48, 'cobertura_agregada': k / 48})
        for strategy in ('clasificador', 'regresion'):
            diff = series[strategy, k] - series['historial_media12', k]
            ci = block_bootstrap_ci(diff)
            saved = difference[(difference.K == k) & (difference.estrategia == strategy)].iloc[0]
            close([ci['media'], ci['ic_inf'], ci['ic_sup']],
                  [saved.d_test, saved.ic_bloques_inf, saved.ic_bloques_sup], 'IC bloques')
    require(round(series['historial_media12', 10].mean() * 100, 2) == 42.73, 'Historial != 42,73 %')
    require(round(series['clasificador', 10].mean() * 100, 2) == 43.05, 'Clasificador != 43,05 %')
    gain = (series['historial_media12', 10].mean() - 10/48) / (series['oraculo', 10].mean() - 10/48)
    require(round(100 * gain) == 92, 'Fracción de ganancia != 92 %')
    public_panel = []
    for row in p.to_dict('records'):
        public_panel.append({'id_barrio': row['id_barrio'], 'mes': row['mes'],
                             'hechos': observation(row['y_hechos']), 'area_km2': row['area_km2'],
                             'hechos_por_km2': row['y_hechos'] / row['area_km2'],
                             'composicion_modo': {m: observation(row['hechos_modo_' + m]) for m in MODES},
                             'anomalia_mes': row['anomalia_mes']})
    forecasts = []
    for idx, row in d.iterrows():
        forecasts.append({'id_barrio': int(row.id_barrio), 'mes_objetivo': row.mes_objetivo,
                          'mes_observable': row.mes_observable, 'horizonte_meses': 1, 'gap_meses': 0,
                          'puntajes': {s: float(row[col]) for s, col in STRATEGIES.items() if s != 'oraculo'},
                          'resultado_posterior': {'hechos': observation(row.y_target),
                                                  'puntaje_oraculo': int(row.y_target)},
                          'selecciones': {s: {str(k): bool(selections[s, k].loc[idx]) for k in KS}
                                          for s in STRATEGIES}})
    sources = csv('fuentes').query("id_fuente in ['F01', 'F03', 'F04']")
    require(len(sources) == 3 and sources.licencia.notna().all(), 'Atribución incompleta')
    source_fields = ['id_fuente', 'nombre', 'organismo_responsable', 'dataset_url', 'recurso_url',
                     'licencia', 'fecha_extraccion', 'sha256', 'limitaciones']
    result = {
        'barrios.geojson': public_geo,
        'panel-mensual.json': public_panel,
        'priorizacion-2025.json': forecasts,
        'perfiles.json': records(profile[['id_barrio', 'grupo', 'k3', 'perfil_k3']]),
        'cobertura.json': {'mensual': monthly, 'anual': annual,
                          'diferencias_vs_historial': records(difference[['K', 'estrategia', 'd_test',
                              'ic_bloques_inf', 'ic_bloques_sup', 'desempate_p2.5', 'desempate_p97.5']]),
                          'fraccion_ganancia_sobre_azar_K10': float(gain),
                          'intervalos': {'metodo': 'bootstrap por bloques móviles', 'bloque_meses': 3,
                                         'replicas': 2000, 'semilla': 20261110, 'nivel': 0.95,
                                         'sensibilidad_desempate': 'Percentiles entre 200 semillas; no es IC temporal'}}}
    validation = {'estado': 'validado', 'barrios': 48, 'claves_panel': len(p), 'meses_panel': 84,
                  'filas_evaluacion': len(d), 'geometrias_unidas': len(mapped),
                  'ceros_observados': int(p.y_hechos.eq(0).sum()), 'hechos_ausentes': 0,
                  'casos_corte_con_empates': tie_cases, 'selecciones_mensuales_validadas': 180,
                  'cobertura_historial_K10': float(series['historial_media12', 10].mean()),
                  'cobertura_clasificador_K10': float(series['clasificador', 10].mean()),
                  'intervalos_reconciliados': 6, 'discrepancias_pendientes': []}
    require(observation(0) != observation(None), 'Cero confundido con ausencia')
    # Detectar cambios concurrentes de insumos antes de publicar el paquete.
    require(hashes == {k: sha(v) for k, v in paths.items()}, 'Los insumos cambiaron durante la exportación')
    encoded = {name: encode(value) for name, value in result.items()}
    version_hash = hashlib.sha256(encode(hashes)).hexdigest()[:12]
    manifest = {'schema_version': SCHEMA, 'data_version': '2019-2025-' + version_hash,
                'fecha_corte': '2025-12-31', 'fecha_extraccion_fuentes': '2026-11-10',
                'periodo_atlas': ['2019-01', '2025-12'], 'periodo_evaluacion': ['2025-01', '2025-12'],
                'fuentes': records(sources[source_fields]),
                'insumos': [{'rol': k, 'ruta': INPUTS[k], 'sha256': hashes[k]} for k in INPUTS],
                'modelos_congelados': {'regresion': model_r, 'clasificador': model_c},
                'desempate': {'regla': 'R0', 'semilla': SEED, 'orden_unidades': 'barrio ascendente',
                              'implementacion': 'src.labels.top_k_labels'},
                'definiciones': {'cobertura_anual': 'Media de 12 coberturas mensuales, igual peso por mes',
                    'cobertura_agregada': 'Suma de hechos cubiertos / suma de hechos del año; no es el indicador principal',
                    'cero': {'valor': 0, 'estado': 'observado'},
                    'ausencia': {'valor': None, 'estado': 'sin_datos'},
                    'densidad': 'Hechos registrados por km²; no mide riesgo por exposición',
                    'modo_sd': 'Hechos con modo sin informar; no equivale a celda sin datos',
                    'oraculo': 'Referencia retrospectiva que conoce el resultado posterior; no es pronóstico',
                    'azar_esperado': 'K/48; esperanza analítica, sin selección aleatoria concreta',
                    'grupo': 'K-Means k=2: 0 interior, 1 borde; desarrollo 2019–2024 sin meses anómalos',
                    'k3': 'Subdivisión exploratoria anidada; separación interior débil',
                    'mes_observable': 'Mes objetivo menos un mes; supuesto retrospectivo gap=0, no disponibilidad operativa acreditada'},
                'limitaciones': ['Solo hechos con víctimas asignados a barrio; excluye hechos no georreferenciables.',
                                  '2025 posiblemente provisorio; límites vigentes sin historial verificado.',
                                  'Concentración registrada, sin ajuste por exposición ni interpretación causal.',
                                  'CC-BY de hechos: versión no indicada por la fuente; se conserva atribución.'],
                'entorno': {'python': platform.python_version(), 'pandas': pd.__version__, 'numpy': np.__version__},
                'validacion': validation,
                'archivos': {name: {'sha256': hashlib.sha256(blob).hexdigest(), 'bytes': len(blob)}
                             for name, blob in encoded.items()}}
    encoded['manifest.json'] = encode(manifest)
    return encoded, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'web/public/data/v1')
    parser.add_argument('--check', action='store_true', help='Validar insumos y paquete existente sin escribir')
    args = parser.parse_args()
    payload, manifest = build()
    out = args.output.resolve()
    # No sobrescribir fuentes o un directorio con otros contenidos.
    require(out != ROOT and ROOT not in out.parents or out.is_relative_to(ROOT / 'web')
            or out.is_relative_to(ROOT / 'reports'), 'Salida dentro de una ruta de investigación protegida')
    if out.exists():
        require({p.name for p in out.iterdir()} <= set(payload), 'La salida contiene archivos ajenos al paquete')
    if args.check:
        for name, blob in payload.items():
            require((out / name).read_bytes() == blob, 'Paquete desactualizado o alterado: ' + name)
    else:
        out.mkdir(parents=True, exist_ok=True)
        for name, blob in payload.items():
            tmp = out / (name + '.tmp')
            tmp.write_bytes(blob)
            tmp.replace(out / name)
    print(json.dumps({'salida': str(out), **manifest['validacion']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

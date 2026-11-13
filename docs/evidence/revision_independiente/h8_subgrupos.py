"""H8 por subgrupos de sensores (corrección R1 de la revisión independiente).

Cada sensor de conteo vehicular 2024 registra un solo sentido de circulación. Este script cruza la tabla de
exposición del notebook 06 con el tipo de circulación del archivo crudo y recalcula el cambio de cuartil entre
el orden por conteo de hechos y el orden por tasa en subgrupos más homogéneos.

Uso, desde la raíz del repositorio:
    python docs/evidence/revision_independiente/h8_subgrupos.py > docs/evidence/revision_independiente/h8_subgrupos.txt
"""
import pandas as pd
from scipy.stats import spearmanr

EXPO = 'reports/tables/06_integrated_evaluation/exposicion_corredores_2024.csv'
RAW = 'data/raw/exposicion/conteo_vehicular_2024.xlsx'


def cambio_cuartil(d):
    """Mismo criterio que el notebook 06: cuartiles por rango, desempate por orden de aparición."""
    qc = pd.qcut(d['hechos_150m'].rank(method='first'), 4, labels=False)
    qt = pd.qcut(d['tasa_por_millon_veh'].rank(method='first'), 4, labels=False)
    return (qc != qt).mean() * 100


raw = pd.read_excel(RAW)
sentidos = raw.groupby('ubicacion_conteo')['sentido_circulacion_conteo'].nunique()
print(f'Sentidos registrados por ubicación: {sentidos.value_counts().to_dict()}')

e = pd.read_csv(EXPO).merge(raw.drop_duplicates('ubicacion_conteo')[['ubicacion_conteo', 'tipo_circulacion_via_conteos']],
                            on='ubicacion_conteo', how='left')
print('\nTipo de vía por tipo de circulación (sensores):')
print(pd.crosstab(e['especificacion_via_conteos'], e['tipo_circulacion_via_conteos']).to_string())
print('\nMedianas por tipo de vía:')
print(e.groupby('especificacion_via_conteos')[['veh_dia', 'hechos_150m', 'tasa_por_millon_veh']].median().round(1).to_string())

grupos = {
    'Todos los sensores': e,
    'Calles y avenidas': e[e['especificacion_via_conteos'] == 'calle_avenida'],
    'Sensores en vías de mano única': e[e['tipo_circulacion_via_conteos'] != 'doble'],
    'Calles y avenidas de mano única': e[(e['especificacion_via_conteos'] == 'calle_avenida') & (e['tipo_circulacion_via_conteos'] != 'doble')],
}
print('\n| Subgrupo | Sensores | Cambia de cuartil | Spearman conteo-tasa | Spearman conteo-volumen |')
print('|---|---|---|---|---|')
for nombre, d in grupos.items():
    print(f"| {nombre} | {len(d)} | {cambio_cuartil(d):.1f} % | {spearmanr(d['hechos_150m'], d['tasa_por_millon_veh'])[0]:.2f} | "
          f"{spearmanr(d['hechos_150m'], d['veh_dia'])[0]:.2f} |")

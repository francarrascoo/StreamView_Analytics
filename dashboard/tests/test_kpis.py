"""Verificación técnica: los KPIs del dashboard son consistentes con los datos.

Comprueba que la línea base declarada de cada KPI coincide con lo que se calcula
sobre los CSV, que el estado se asigna bien y que los filtros cambian el valor.

Uso:  python dashboard/tests/test_kpis.py      (o  python -m pytest dashboard/tests/)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from streamview.datos import cargar_catalogo  # noqa: E402
from streamview.kpis import CUMPLE, KPIS, NO_CUMPLE, RIESGO, SIN_DATOS, estado  # noqa: E402

DF, N_DUP = cargar_catalogo()


def test_catalogo_integrado():
    assert len(DF) == 31_991
    assert (DF["type"] == "Película").sum() == 16_000
    assert N_DUP == 9


def test_linea_base_coincide_con_los_datos():
    for k in KPIS:
        r = k.calcular(DF)
        assert abs(r.valor - k.linea_base) < 0.0006, (k.id, r.valor, k.linea_base)


def test_meta_y_alerta_coherentes():
    for k in KPIS:
        assert k.alerta < k.meta, k.id
        assert k.linea_base < k.meta, f"{k.id}: una meta ya cumplida no orienta decisiones"


def test_estados():
    k = KPIS[0]
    assert estado(k, k.meta) == CUMPLE
    assert estado(k, (k.meta + k.alerta) / 2) == RIESGO
    assert estado(k, k.alerta - 0.01) == NO_CUMPLE
    assert estado(k, None) == SIN_DATOS


def test_filtros_recalculan():
    k1 = KPIS[0]
    doc = DF[DF["genre_set"].apply(lambda s: "Documentary" in s)]
    ter = DF[DF["genre_set"].apply(lambda s: "Horror" in s)]
    assert k1.calcular(doc).estado == CUMPLE      # documentales superan la meta
    assert k1.calcular(ter).estado == NO_CUMPLE   # terror queda muy bajo
    assert KPIS[1].calcular(DF, filtro_pais=True).estado == SIN_DATOS


if __name__ == "__main__":
    for nombre, f in list(globals().items()):
        if nombre.startswith("test_"):
            f()
            print("ok", nombre)

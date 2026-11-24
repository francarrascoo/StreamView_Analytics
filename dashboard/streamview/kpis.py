"""KPIs de StreamView Analytics: métrica + meta + plazo + responsable + decisión.

Diferencia clave respecto de la versión EP4 (observación del docente): una MÉTRICA
describe ("26% de las películas está bien evaluada"); un KPI compara esa métrica
contra una META definida por el negocio, con plazo y responsable, y su estado
(cumple / en riesgo / no cumple) gatilla una decisión concreta.

Las metas son supuestos del caso (StreamView no las entrega). Cada una se fijó a
partir de la línea base del catálogo y de un referente ya observado en los
mismos datos, para que sea exigente pero alcanzable (ver campo `justificacion`).

Todas las metas son "mayor es mejor". Estados (misma regla para todos los KPIs):
    cumple      valor >= meta
    en riesgo   valor hasta 15% (relativo) bajo la meta: alerta = meta x 0,85
    no cumple   valor < alerta
"""
from dataclasses import dataclass, field
from typing import Callable, Optional

import pandas as pd

from .datos import GOOD_RATING, MERCADOS_PRIORITARIOS, MIN_VOTES

PLAZO = "Diciembre 2026"
FRECUENCIA = "Trimestral, sobre cada nueva extracción del catálogo"

CUMPLE, RIESGO, NO_CUMPLE, SIN_DATOS = "cumple", "riesgo", "no_cumple", "sin_datos"
ESTADOS = {
    CUMPLE: {"icono": "✓", "texto": "Cumple"},
    RIESGO: {"icono": "!", "texto": "En riesgo"},
    NO_CUMPLE: {"icono": "✕", "texto": "No cumple"},
    SIN_DATOS: {"icono": "–", "texto": "Sin datos suficientes"},
}
TOLERANCIA = 0.15  # "en riesgo" = hasta 15% bajo la meta
MIN_BASE = 30  # títulos mínimos en la base para evaluar un KPI en un segmento


@dataclass
class Resultado:
    valor: Optional[float]
    n: int                  # tamaño de la base sobre la que se calcula
    estado: str
    nota: str = ""


@dataclass
class KPI:
    id: str
    nombre: str
    pregunta: str           # pregunta de negocio que responde
    formula: str
    unidad: str             # "pct" (0-1) o "x" (veces)
    meta: float
    linea_base: float       # catálogo completo, extracción 2025 (Sección 3 del notebook)
    responsable: str
    audiencia: tuple
    decision: str           # qué se hace si no cumple (texto completo, informe y ficha técnica)
    accion: str             # la misma decisión en pocas palabras (tarjeta del dashboard)
    justificacion: str
    base: Callable = field(repr=False)     # df -> serie booleana/numérica sobre la que se evalúa
    agregado: str = "media"                # "media" de un booleano o "mediana" de un número
    requiere_sin_filtro_pais: bool = False

    @property
    def alerta(self):
        return round(self.meta * (1 - TOLERANCIA), 4)

    def calcular(self, df, filtro_pais=False):
        if self.requiere_sin_filtro_pais and filtro_pais:
            return Resultado(None, 0, SIN_DATOS,
                             "Mide la mezcla de países del catálogo: quite el filtro de país para evaluarlo.")
        s = self.base(df).dropna()
        if len(s) < MIN_BASE:
            return Resultado(None, len(s), SIN_DATOS, f"Menos de {MIN_BASE} títulos en la base.")
        valor = float(s.mean() if self.agregado == "media" else s.median())
        return Resultado(valor, len(s), estado(self, valor))

    def por_anio(self, df, hasta):
        """Valor del KPI por año de estreno (cohortes), para ver la trayectoria hacia la meta."""
        filas = []
        for anio, g in df[df["release_year"] <= hasta].groupby("release_year"):
            s = self.base(g).dropna()
            if len(s) >= MIN_BASE:
                filas.append((int(anio), float(s.mean() if self.agregado == "media" else s.median()), len(s)))
        return pd.DataFrame(filas, columns=["anio", "valor", "n"])


def estado(kpi, valor):
    if valor is None or pd.isna(valor):
        return SIN_DATOS
    if valor >= kpi.meta:
        return CUMPLE
    if valor >= kpi.alerta:
        return RIESGO
    return NO_CUMPLE


# ------------------------------------------------------------------
# Bases de cálculo
# ------------------------------------------------------------------
def _peliculas_bien_evaluadas(df):
    r = df.loc[df["type"] == "Película", "rating"]
    return (r >= GOOD_RATING).where(r.notna())


def _mercados_prioritarios(df):
    p = df[df["type"] == "Película"]
    prior = frozenset(MERCADOS_PRIORITARIOS)
    return p["country_set"].apply(lambda s: (not s.isdisjoint(prior)) if s else None)


def _series_calificadas(df):
    return df.loc[df["type"] == "Serie", "vote_count"] >= MIN_VOTES


KPIS = [
    KPI(
        id="K1", nombre="Películas bien evaluadas",
        pregunta="¿El catálogo de películas tiene la calidad que espera el público?",
        formula=f"Películas con calificación ≥ {GOOD_RATING:.0f} / películas con {MIN_VOTES}+ votos",
        unidad="pct", meta=0.30, linea_base=0.258,
        responsable="Gerencia de Contenidos y Adquisición",
        audiencia=("Directorio", "Contenidos y Adquisición", "Data & Analytics"),
        accion="Comprar más Documental, Animación y Música, y más cine de Japón, Corea del Sur y México.",
        decision="Priorizar adquisiciones en géneros y mercados que ya superan el 30% (Documental, Animación, "
                 "Música; Japón, Corea del Sur, México) y no renovar licencias de películas bajo 5,0.",
        justificacion="Las cohortes 2019-2021 ya alcanzaron 31-32%: la meta exige volver a ese nivel, no un "
                      "salto sin precedentes. +4,2 pp equivalen a unas 600 películas bien evaluadas más.",
        base=_peliculas_bien_evaluadas,
    ),
    KPI(
        id="K2", nombre="Películas de mercados de alto desempeño",
        pregunta="¿Estamos aumentando el peso de los mercados con mejor calidad?",
        formula="Películas producidas (total o en parte) en Japón, Corea del Sur o México / películas con país",
        unidad="pct", meta=0.18, linea_base=0.135,
        responsable="Gerencia de Contenidos y Adquisición",
        audiencia=("Directorio", "Contenidos y Adquisición", "Data & Analytics"),
        accion="Reservar una cuota de licencias para Japón, Corea del Sur y México.",
        decision="Reservar una cuota de las nuevas licencias de cine para estos tres mercados hasta llegar al 18%.",
        justificacion="Estos mercados tienen 2 veces la proporción de películas bien evaluadas de EE.UU. (43-51% "
                      "frente a 23%), con ventaja robusta a género y año. La cohorte 2020 ya llegó a 19%, y "
                      "+4,5 pp mantienen a EE.UU. como principal proveedor.",
        base=_mercados_prioritarios, requiere_sin_filtro_pais=True,
    ),
    KPI(
        id="K3", nombre="Series que el público califica",
        pregunta="¿El público participa con las series del catálogo?",
        formula=f"Series con {MIN_VOTES}+ votos / total de series",
        unidad="pct", meta=0.50, linea_base=0.384,
        responsable="Gerencia de Producto (con Marketing)",
        audiencia=("Directorio", "Marketing", "Data & Analytics"),
        accion="Pedir una calificación al terminar cada episodio y destacar las series populares sin votos.",
        decision="Pedir calificación al terminar un episodio y dar visibilidad a las series populares que aún no "
                 "tienen 10 votos, empezando por Conversación, Reality y Documental (los géneros con menos "
                 "participación); sin votos no se puede saber si una serie conviene renovarla.",
        justificacion="Es el mejor indicador de engagement disponible (el catálogo no trae reproducciones). La "
                      "cohorte 2024 ya llega a 49,7%: la meta lleva a todo el catálogo al nivel de lo más reciente.",
        base=_series_calificadas,
    ),
]
KPI_POR_ID = {k.id: k for k in KPIS}


def kpis_de(audiencia):
    return [k for k in KPIS if audiencia in k.audiencia]


def ficha_tecnica():
    """Tabla con la definición completa de cada KPI (para el informe y el dashboard)."""
    def f(k, v):
        return f"{v * 100:.1f}%".replace(".", ",") if k.unidad == "pct" else f"{v:.1f}×".replace(".", ",")
    return pd.DataFrame([{
        "KPI": f"{k.id} · {k.nombre}", "Fórmula": k.formula, "Línea base": f(k, k.linea_base),
        "Meta": "≥ " + f(k, k.meta), "En riesgo desde": f(k, k.alerta), "Plazo": PLAZO,
        "Responsable": k.responsable, "Decisión si no cumple": k.decision,
    } for k in KPIS])

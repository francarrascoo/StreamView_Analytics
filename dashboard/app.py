"""Dashboard interactivo del catálogo de StreamView Analytics (versión EP5 optimizada).

Streamlit + Plotly. La limpieza de datos y la definición de los KPIs viven en
dashboard/streamview/ (datos.py y kpis.py) y son las mismas que usa el notebook.

Reglas de diseño (Storytelling with Data, C. Nussbaumer Knaflic, y reglas del equipo)
------------------------------------------------------------------------------------
1. Todo se lee de un vistazo y sin scroll cuando se puede: cada pestaña cabe en una
   pantalla de notebook; los filtros van en un botón, no en una barra lateral.
2. Lo importante va arriba a la izquierda: la frase con la conclusión y los KPIs.
3. Una frase arriba dice la conclusión (Big Idea), recalculada con los filtros.
4. Cada pregunta va en su tarjeta, con un solo gráfico y un título que dice la respuesta.
5. Sin jerga y con pocas cifras: "puntos" en vez de "pp", sin "cohorte" ni "mediana".
6. Barras para comparar magnitudes (siempre desde cero), líneas solo para el tiempo,
   dispersión solo para relaciones; nada en 3D, sin tortas, treemaps ni áreas.
7. Mismas escalas y colores en todas las pantallas: todo porcentaje va de 0 a 100%;
   azul = película, naranjo = serie, verde = supera la meta, gris = contexto,
   tinta = énfasis neutro; verde/ámbar/rojo con ícono solo para el estado de un KPI.

Apple Human Interface Guidelines (aplicadas en EP5)
---------------------------------------------------
- Dark Mode: el tablero sigue la apariencia del sistema (claro u oscuro), sin un ajuste
  propio; cada color tiene variante clara y oscura con contraste AA (texto chico ~7:1).
- Color: un color, un significado; el acento de los controles es neutro (no compite con
  el rojo de "no cumple"); nunca solo color: ícono, texto, forma o patrón rayado (series).
- Charts: ejes fijos de 0 a 100% cuando el rango tiene sentido; marcas de eje conocidas;
  título que resume el mensaje; resumen en texto de cada gráfico para lectores de pantalla.
- Segmented controls: para elegir vista, orden y formato (opciones cercanas, con estado
  visible), en vez de botones de opción.
- Writing: lenguaje llano, sin "nosotros", estados vacíos que dicen qué hacer, montos sin
  abreviaturas ambiguas. Feedback: "Quitar filtros" a la vista cuando hay filtros activos.
- Typography: fuente del sistema (San Francisco en Apple), sin pesos livianos.
- Accesibilidad: respeta "reducir movimiento" y "aumentar contraste" del sistema.

Uso (desde la raíz del repositorio):
    streamlit run dashboard/app.py
"""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from streamview.datos import (  # noqa: E402
    GOOD_RATING, MAX_ROI, MERCADOS_PRIORITARIOS, MIN_BUDGET_ROI, MIN_N, MIN_N_FLOOR, MIN_VOTES,
    MIN_VOTES_TOP, ULTIMO_ANIO_COMPLETO, US, YEAR_RANGE, cargar_catalogo, explode, nombre_genero,
    nombre_pais,
)
from streamview.kpis import (  # noqa: E402
    CUMPLE, ESTADOS, KPI_POR_ID, NO_CUMPLE, PLAZO, RIESGO, SIN_DATOS, ficha_tecnica,
)

st.set_page_config(page_title="StreamView · KPIs del catálogo", page_icon="📊", layout="wide",
                   initial_sidebar_state="collapsed")

# ------------------------------------------------------------------
# Paleta: un color significa lo mismo en todas las pantallas, con variante clara y oscura
# (HIG Dark Mode: seguir la apariencia del sistema; contraste ≥ 4,5:1, ideal 7:1 en texto chico)
# ------------------------------------------------------------------
PALETAS = {
    "light": dict(AZUL="#2a78d6", NARANJO="#c85526", VERDE="#1a7f37", AMBAR="#9a6700", ROJO="#cf222e",
                  GRIS="#c9c7bf", GRIS_MEDIO="#8c959f", INK="#24292f", MUTED="#4a525c", GRILLA="#eef1f4",
                  FONDO="#ffffff"),
    "dark": dict(AZUL="#4c9bf5", NARANJO="#f0883e", VERDE="#3fb950", AMBAR="#d29922", ROJO="#f85149",
                 GRIS="#3d444d", GRIS_MEDIO="#6e7781", INK="#e6edf3", MUTED="#9ea7b3", GRILLA="#21262d",
                 FONDO="#0e1117"),
}
OSCURO = st.context.theme.type == "dark"
_p = PALETAS["dark" if OSCURO else "light"]
AZUL, NARANJO, VERDE, GRIS, GRIS_MEDIO, INK, MUTED = (_p[k] for k in
                                                     ("AZUL", "NARANJO", "VERDE", "GRIS", "GRIS_MEDIO", "INK", "MUTED"))
GRILLA, FONDO = _p["GRILLA"], _p["FONDO"]
TYPE_COLORS = {"Película": AZUL, "Serie": NARANJO}
TYPE_SYMBOLS = {"Película": "circle", "Serie": "square"}
TYPE_DASH = {"Película": "solid", "Serie": "dash"}
TYPE_PATRON = {"Película": "", "Serie": "/"}   # nunca solo color: las series llevan rayado
STATUS_COLORS = {CUMPLE: VERDE, RIESGO: _p["AMBAR"], NO_CUMPLE: _p["ROJO"], SIN_DATOS: MUTED}
PCT_RANGE = [0, 1.18]   # todo porcentaje en barras: de 0 a 100% (+ espacio para el rótulo)
ALTO = 300              # alto estándar de un gráfico dentro de una tarjeta
FUENTE = "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"


@st.cache_data(show_spinner="Preparando el catálogo de 31.991 películas y series…")
def load_data():
    return cargar_catalogo()


df, n_series_dup = load_data()

# ------------------------------------------------------------------
# Estilo: variables CSS con variante oscura (siguen al sistema en vivo)
# ------------------------------------------------------------------
st.markdown("""
<style>
:root { --ink:#24292f; --muted:#4a525c; --card:#ffffff; --borde:#d0d7de; --b1:#eef1f4; --b2:#d8dee4; --b3:#bcc5ce;
        --acento:#24292f; --sobre-acento:#ffffff; }
@media (prefers-color-scheme: dark) {
  :root { --ink:#e6edf3; --muted:#9ea7b3; --card:#161b22; --borde:#30363d; --b1:#21262d; --b2:#30363d; --b3:#484f58;
          --acento:#e6edf3; --sobre-acento:#0e1117; }
}
@media (prefers-contrast: more) { :root { --muted: var(--ink); --borde: var(--ink); } }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }
/* HIG Typography: fuente del sistema (San Francisco en Apple); los íconos conservan su fuente */
.stApp, .stApp *:not([data-testid="stIconMaterial"]):not(code):not(svg *) {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important; }
/* acento neutro en los controles: el rojo queda reservado para "no cumple" */
div[data-baseweb="tab-highlight"] { background-color: var(--acento) !important; }
button[data-baseweb="tab"][aria-selected="true"] p { color: var(--acento) !important; }
[data-testid="stBaseButton-segmented_controlActive"] { background-color: var(--acento) !important; border-color: var(--acento) !important; }
[data-testid="stBaseButton-segmented_controlActive"] p { color: var(--sobre-acento) !important; }
span[data-baseweb="tag"] { background-color: var(--acento) !important; }
span[data-baseweb="tag"] span, span[data-baseweb="tag"] svg { color: var(--sobre-acento) !important; fill: var(--sobre-acento) !important; }
[data-testid="stSlider"] { filter: grayscale(1); }
button[kind="secondary"]:hover, [data-testid="stPopoverButton"]:hover { border-color: var(--acento) !important; color: var(--acento) !important; }
.sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
</style>""", unsafe_allow_html=True)
st.markdown(f"""
<style>
[data-testid="stHeader"] {{ display: none; }}
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {{ display: none; }}
.block-container {{ padding-top: 1.1rem !important; padding-bottom: 1rem !important; max-width: 1500px; }}
.barra {{ border-bottom: 1px solid var(--borde); margin: .15rem 0 .5rem 0; }}
.marca {{ font-size: 1.05rem; font-weight: 700; color: var(--ink); }}
.marca span {{ font-weight: 400; color: var(--muted); }}
.bigidea {{ font-size: 1.42rem; font-weight: 700; line-height: 1.25; color: var(--ink); margin: .1rem 0 .1rem 0; }}
.alcance {{ font-size: .9rem; color: var(--muted); }}
.q {{ font-size: .88rem; color: var(--muted); font-weight: 600; }}
.accion {{ font-size: 1.08rem; font-weight: 650; line-height: 1.3; color: var(--ink); margin: .1rem 0 .1rem 0; }}
.nota {{ font-size: .85rem; color: var(--muted); margin: 0 0 .2rem 0; }}
.kpi-grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px; margin: .1rem 0 .3rem 0; }}
.kpi {{ border:1px solid var(--borde); border-radius:10px; padding:.55rem .75rem .5rem .75rem; background:var(--card); }}
.kpi-name {{ font-size:.9rem; font-weight:650; color:var(--ink); line-height:1.2; min-height:2.2em; }}
.kpi-row {{ display:flex; justify-content:space-between; align-items:center; gap:.4rem; margin:.15rem 0 .25rem 0; }}
.kpi-val {{ font-size:1.65rem; font-weight:700; color:var(--ink); font-variant-numeric: tabular-nums; line-height:1.1; }}
.badge {{ font-size:.8rem; font-weight:700; padding:.08rem .5rem; border-radius:999px; border:1.5px solid; white-space:nowrap; }}
.kpi-meta {{ font-size:.82rem; color:var(--ink); margin-top:.3rem; }}
.bullet {{ position:relative; height:12px; }}
.bullet .band {{ position:absolute; top:0; height:12px; }}
.bullet .bar {{ position:absolute; top:4px; height:4px; left:0; background:var(--ink); }}
.bullet .tick {{ position:absolute; top:-3px; width:3px; height:18px; background:var(--ink); }}
.leyenda {{ font-size:.82rem; color:var(--muted); margin:0 0 .35rem 0; }}
.decision li {{ margin-bottom:.5rem; font-size:.95rem; line-height:1.35; }}
button[data-baseweb="tab"] p {{ font-size: 1rem; font-weight: 600; }}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Encabezado: marca, vista y filtros en una sola fila
# ------------------------------------------------------------------
PERFILES = ["Directorio", "Contenidos y Adquisición", "Marketing", "Data & Analytics"]
FILTER_DEFAULTS = {"f_tipo": "Todos", "f_anios": YEAR_RANGE, "f_paises": [], "f_idiomas": [], "f_generos": []}
for k, v in FILTER_DEFAULTS.items():
    st.session_state.setdefault(k, v)


def reiniciar_filtros():
    for k, v in FILTER_DEFAULTS.items():
        st.session_state[k] = v


def segmentos(etiqueta, opciones, key, ayuda=None, fmt=None):
    """Control segmentado (HIG: opciones cercanas con estado visible) que no queda sin selección."""
    ultimo = f"_{key}_ultimo"
    st.session_state.setdefault(ultimo, opciones[0])
    if st.session_state.get(key) is None:
        st.session_state[key] = st.session_state[ultimo]
    valor = st.segmented_control(etiqueta, opciones, key=key, help=ayuda, format_func=fmt or str,
                                 label_visibility="collapsed")
    valor = valor if valor is not None else st.session_state[ultimo]
    st.session_state[ultimo] = valor
    return valor


n_filtros = sum(st.session_state[k] != v for k, v in FILTER_DEFAULTS.items())
c_marca, c_perfil, c_filtros = st.columns([2.1, 6.2, 1.2], vertical_alignment="center")
with c_marca:
    st.markdown('<div class="marca">StreamView <span>· catálogo 2010-2025</span></div>', unsafe_allow_html=True)
with c_perfil:
    perfil = segmentos("Vista para", PERFILES, "perfil", ayuda="Elige el público: cambia los KPIs, las pestañas y los gráficos")
with c_filtros:
    with st.popover(f"Filtros ({n_filtros})" if n_filtros else "Filtros",
                    help="Filtra por tipo, años, país, idioma y género; todo se recalcula"):
        if st.session_state.get("f_tipo") is None:
            st.session_state["f_tipo"] = "Todos"
        tipo = st.segmented_control("Tipo de contenido", ["Todos", "Película", "Serie"], key="f_tipo") or "Todos"
        year_min, year_max = st.slider("Año de estreno", *YEAR_RANGE, key="f_anios")
        all_countries = sorted(set().union(*df["country_set"]), key=nombre_pais)
        sel_countries = st.multiselect("País", all_countries, key="f_paises", format_func=nombre_pais,
                                       placeholder="Todos los países")
        all_langs = sorted(df["language"].dropna().unique().tolist())
        sel_langs = st.multiselect("Idioma", all_langs, key="f_idiomas", placeholder="Todos los idiomas")
        all_genres = sorted(set().union(*df["genre_set"]), key=nombre_genero)
        sel_genres = st.multiselect("Género", all_genres, key="f_generos", format_func=nombre_genero,
                                    placeholder="Todos los géneros")
        st.button("Reiniciar filtros", on_click=reiniciar_filtros)

mask = pd.Series(True, index=df.index)
mask &= df["release_year"].between(year_min, year_max) | df["release_year"].isna()
if sel_langs:
    mask &= df["language"].isin(sel_langs)
if sel_genres:
    sel = frozenset(sel_genres)
    mask &= df["genre_set"].apply(lambda s: not s.isdisjoint(sel))
# los rankings POR PAÍS ignoran el filtro de país y destacan los países elegidos
mask_sin_pais = mask.copy()
N_BASE_SIN_PAIS = int(mask_sin_pais.sum())
if sel_countries:
    sel = frozenset(sel_countries)
    mask &= df["country_set"].apply(lambda s: not s.isdisjoint(sel))
N_BASE = int(mask.sum())
if tipo != "Todos":
    mask &= df["type"] == tipo
    mask_sin_pais &= df["type"] == tipo
fdf = df[mask]
fdf_sin_pais = df[mask_sin_pais]
SEL_PAISES = set(sel_countries)


def umbral_categoria(sin_pais=False):
    base = N_BASE_SIN_PAIS if sin_pais else N_BASE
    return int(min(MIN_N, max(MIN_N_FLOOR, round(MIN_N * base / len(df)))))


active = []
if tipo != "Todos":
    active.append("solo películas" if tipo == "Película" else "solo series")
if (year_min, year_max) != YEAR_RANGE:
    active.append(f"estrenos {year_min}–{year_max}")
active += [nombre_pais(c) for c in sel_countries] + sel_langs + [nombre_genero(g) for g in sel_genres]


# ------------------------------------------------------------------
# Formato en español
# ------------------------------------------------------------------
def formato_es(texto):
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


def miles(n):
    return formato_es(f"{n:,.0f}")


def f1(v):
    return "—" if v is None or pd.isna(v) else formato_es(f"{v:,.1f}")


def pct(v):
    return "—" if v is None or pd.isna(v) else formato_es(f"{v * 100:.0f}") + "%"


def pct_meta(v, meta):
    """Entero, salvo que el redondeo iguale una meta que no se alcanza (49,7% no es 50%)."""
    if v is None or pd.isna(v):
        return "—"
    if v < meta and round(v * 100) >= round(meta * 100):
        return formato_es(f"{v * 100:.1f}") + "%"
    return pct(v)


def fmt_kpi(k, v):
    return "—" if v is None else (pct_meta(v, k.meta) if k.unidad == "pct" else f"{f1(v)}×")


def lista_es(items):
    items = list(items)
    if not items:
        return ""
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " y " + items[-1]


def cap(texto):
    return texto[:1].upper() + texto[1:]


# ------------------------------------------------------------------
# Componentes: tarjeta, barras, fila de KPIs
# ------------------------------------------------------------------
def tarjeta(pregunta, titulo, nota=None):
    """Una pregunta = una tarjeta: la pregunta (gris), la respuesta (título) y un solo gráfico."""
    c = st.container(border=True)
    c.markdown(f'<div class="q">{pregunta}</div><div class="accion">{cap(titulo)}</div>'
               + (f'<div class="nota">{nota}</div>' if nota else ""), unsafe_allow_html=True)
    return c


CONFIG = {"displayModeBar": False}
LAYOUT_BASE = dict(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", separators=",.",
                   font=dict(size=13, color=INK, family=FUENTE), hoverlabel=dict(font_size=13, font_family=FUENTE),
                   margin=dict(l=4, r=4, t=6, b=4), showlegend=False)


def grafico(fig):
    st.plotly_chart(fig, config=CONFIG)


def resumen_accesible(texto):
    """HIG Charts: un resumen en texto (tipo de gráfico, qué mide y valores) para lectores de pantalla."""
    st.markdown(f'<div class="sr-only" role="note">{texto}</div>', unsafe_allow_html=True)


def sin_html(t):
    return str(t).replace("<b>", "").replace("</b>", "")


def barras(etiquetas, valores, colores, texto_fmt, alto=None, meta=None, meta_txt=None, textos=None, rango=None,
           patrones=None, que=""):
    """Barras horizontales desde cero, con el valor escrito en la barra y sin eje (el dato ya está escrito).
    Si los valores son porcentajes, la escala es siempre de 0 a 100%."""
    n = len(valores)
    textos = textos or [texto_fmt(v) for v in valores]
    fig = go.Figure(go.Bar(x=valores, y=etiquetas, orientation="h", marker_color=colores,
                           marker_pattern_shape=patrones, marker_pattern_fgcolor=FONDO if patrones else None,
                           marker_pattern_fillmode="overlay", marker_pattern_solidity=0.35,
                           text=textos, textposition="outside",
                           cliponaxis=False, textfont=dict(size=13), hoverinfo="skip"))
    resumen_accesible(f"Gráfico de barras horizontales{': ' + que if que else ''}. "
                      + "; ".join(f"{sin_html(e)}: {t}" for e, t in zip(etiquetas, textos))
                      + (f". Línea de referencia: {meta_txt}." if meta is not None else "."))
    if rango is None:
        rango = PCT_RANGE if texto_fmt is pct else [0, max(valores) * 1.3]
    fig.update_layout(height=alto or min(ALTO + 60, max(150, 25 * n + 30)), bargap=0.3, **LAYOUT_BASE)
    if meta is not None:
        fig.update_layout(margin=dict(l=4, r=4, t=24, b=4))
        fig.add_vline(x=meta, line_dash="dash", line_color=INK, line_width=1.5, layer="below")
        fig.add_annotation(x=meta, y=1, yref="paper", yanchor="bottom", text=meta_txt or "meta",
                           showarrow=False, font=dict(size=12, color=INK), bgcolor=FONDO)
    fig.update_xaxes(range=rango, visible=False)
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=13), ticks="", showline=False)
    grafico(fig)


def resultados(ids):
    return [(KPI_POR_ID[i], KPI_POR_ID[i].calcular(fdf, filtro_pais=bool(sel_countries))) for i in ids]


def bullet_html(k, v):
    tope = max(k.meta * 1.3, (v or 0) * 1.08)
    p = lambda x: max(0.0, min(100.0, x / tope * 100))  # noqa: E731
    bandas = (f'<div class="band" style="left:0;width:{p(k.alerta)}%;background:var(--b1)"></div>'
              f'<div class="band" style="left:{p(k.alerta)}%;width:{p(k.meta) - p(k.alerta)}%;background:var(--b2)"></div>'
              f'<div class="band" style="left:{p(k.meta)}%;width:{100 - p(k.meta)}%;background:var(--b3)"></div>')
    barra = f'<div class="bar" style="width:{p(v)}%"></div>' if v is not None else ""
    aria = f"Valor {fmt_kpi(k, v)}, meta {fmt_kpi(k, k.meta)}"
    return (f'<div class="bullet" role="img" aria-label="{aria}">{bandas}{barra}'
            f'<div class="tick" style="left:calc({p(k.meta)}% - 1px)"></div></div>')


def brecha(k, v):
    d = round(v * 100) - round(k.meta * 100)
    if v >= k.meta:
        return f"la supera por {d} puntos" if d > 0 else "la alcanza"
    return f"falta {-d} punto" if -d == 1 else f"faltan {-d} puntos" if d < 0 else "falta menos de 1 punto"


def kpi_card(k, r):
    est, color = ESTADOS[r.estado], STATUS_COLORS[r.estado]
    pie = f"Meta {fmt_kpi(k, k.meta)} · {brecha(k, r.valor)}" if r.valor is not None else r.nota
    return (f'<div class="kpi" title="{k.formula}. Responsable: {k.responsable}.">'
            f'<div class="kpi-name">{k.id} · {k.nombre}</div>'
            f'<div class="kpi-row"><span class="kpi-val">{fmt_kpi(k, r.valor)}</span>'
            f'<span class="badge" style="color:{color};border-color:{color}">{est["icono"]} {est["texto"]}</span></div>'
            f'{bullet_html(k, r.valor)}<div class="kpi-meta">{pie}</div></div>')


def fila_kpis(ids):
    res = resultados(ids)
    st.markdown('<div class="kpi-grid">' + "".join(kpi_card(k, r) for k, r in res) + "</div>"
                f'<div class="leyenda">KPI: indicador con meta, plazo y responsable · ✓ cumple · ! en riesgo '
                f'(hasta 15% bajo la meta) · ✕ no cumple · la raya vertical es la meta a {PLAZO.lower()}</div>',
                unsafe_allow_html=True)


# ------------------------------------------------------------------
# Cálculos compartidos
# ------------------------------------------------------------------
def ranking_categoria(data, col, metric, stat, min_n):
    base = explode(data, col).join(data[[metric]]) if col in ("country", "genres") else data.dropna(subset=[col])
    g = base.groupby(col)[metric].agg(["mean", "median", "count"])
    if metric == "rating":
        g["bien"] = base.dropna(subset=[metric]).groupby(col)[metric].apply(lambda s: (s >= GOOD_RATING).mean())
    return g[g["count"] >= min_n].sort_values(stat, ascending=False)


def nombre_cat(col, v):
    return nombre_pais(v) if col == "country" else nombre_genero(v) if col == "genres" else v


def mercados_peliculas():
    m = fdf_sin_pais[fdf_sin_pais["type"] == "Película"]
    return ranking_categoria(m, "country", "rating", "bien", umbral_categoria(sin_pais=True)) if len(m) else pd.DataFrame()


fin = fdf[fdf["fin_ok"]]


def series_populares_sin_votos():
    """Series con público (popularidad sobre la típica de las series) que aún no tienen 10 votos: palanca de K3."""
    s_ = fdf[fdf["type"] == "Serie"]
    return s_[(s_["vote_count"] < MIN_VOTES) & (s_["popularity"] >= s_["pop_mediana_formato"])]


# ==================================================================
# Frase principal (Big Idea): la conclusión de la vista, arriba a la izquierda
# ==================================================================
def frase_mercados():
    mk = mercados_peliculas()
    r2 = KPI_POR_ID["K2"].calcular(fdf, filtro_pais=bool(sel_countries))
    if mk.empty or US not in mk.index or set(mk.index[:3]) != set(MERCADOS_PRIORITARIOS) or r2.valor is None:
        return None
    veces = mk["bien"].iloc[:3].mean() / mk.loc[US, "bien"]
    cuanto = "duplican" if 1.8 <= veces < 2.5 else f"multiplican por {f1(veces)}"
    return f"Japón, Corea del Sur y México {cuanto} la calidad del cine de EE.UU., pero son solo el {pct(r2.valor)} de las películas"


def big_idea():
    if perfil == "Directorio":
        res = [(k, r) for k, r in resultados(["K1", "K2", "K3"]) if r.valor is not None]
        n_ok = sum(r.estado == CUMPLE for _, r in res)
        estado = ("Ningún KPI cumple su meta todavía" if n_ok == 0 else
                  f"{n_ok} de {len(res)} KPIs cumplen su meta" if n_ok < len(res) else "Todos los KPIs cumplen su meta")
        m = frase_mercados()
        if m:
            return f"{estado}. La mejor calidad de cine está en mercados que casi no compramos."
        fuera = [(k, r) for k, r in res if r.estado != CUMPLE]
        if fuera:
            k, r = min(fuera, key=lambda kr: kr[1].valor / kr[0].meta)
            return f"{estado}: la brecha más grande es «{k.nombre.lower()}», {fmt_kpi(k, r.valor)} frente a {fmt_kpi(k, k.meta)}."
        return f"{estado} en este segmento: mantener la estrategia."
    if perfil == "Contenidos y Adquisición":
        m = frase_mercados()
        if m:
            return m + "."
        r1 = KPI_POR_ID["K1"].calcular(fdf)
        return (f"En este segmento, {pct(r1.valor)} de las películas está bien evaluada; la meta es 30%."
                if r1.valor is not None else "No hay películas calificadas suficientes en este segmento.")
    if perfil == "Marketing":
        r3 = KPI_POR_ID["K3"].calcular(fdf)
        if r3.valor is None:
            return "No hay series suficientes en este segmento para medir la participación del público."
        return (f"El {pct(1 - r3.valor)} de las series aún no se puede evaluar: "
                f"{miles(len(series_populares_sin_votos()))} tienen público pero menos de 10 votos.")
    pel, ser = fdf[fdf["type"] == "Película"], fdf[fdf["type"] == "Serie"]
    cob = lambda d: d["rating"].notna().mean() if len(d) else None  # noqa: E731
    return (f"La nota es confiable en el {pct(cob(pel))} de las películas, pero solo en el {pct(cob(ser))} de las series; "
            f"las finanzas cubren el {pct(pel['fin_ok'].mean() if len(pel) else None)} de las películas.")


st.markdown('<div class="barra"></div>', unsafe_allow_html=True)
st.markdown(f'<div class="bigidea">{big_idea()}</div>', unsafe_allow_html=True)
c_alc, c_quitar = st.columns([8, 1.2], vertical_alignment="center")
with c_alc:
    st.markdown(f'<div class="alcance">{"Filtrado: " + ", ".join(active) if active else "Catálogo completo"} · '
                f'{miles(len(fdf))} títulos · metas a {PLAZO.lower()}</div>', unsafe_allow_html=True)
if active:
    with c_quitar:
        st.button("Quitar filtros", on_click=reiniciar_filtros, help="Vuelve al catálogo completo", key="quitar")


# ==================================================================
# Tarjetas: una pregunta, un gráfico
# ==================================================================
def sin_datos(pregunta, motivo):
    """HIG Writing: un estado vacío dice qué pasó y qué hacer."""
    with tarjeta(pregunta, motivo, "Amplíe el rango de años o use «Quitar filtros» para volver al catálogo completo."):
        pass


def card_decisiones(ids):
    res = [(k, r) for k, r in resultados(ids) if r.estado in (NO_CUMPLE, RIESGO)]
    with tarjeta("¿Qué hacer ahora?", "Cada KPI bajo su meta tiene un responsable y una acción"):
        if not res:
            st.markdown("✓ Todos los KPIs de esta vista cumplen su meta en este segmento.")
            return
        items = "".join(f'<li><b>{k.id} {ESTADOS[r.estado]["icono"]} {k.responsable}:</b> {k.accion}</li>'
                        for k, r in res)
        st.markdown(f'<ol class="decision" style="padding-left:1.1rem;margin:0">{items}</ol>', unsafe_allow_html=True)


def card_k1_paises():
    k = KPI_POR_ID["K1"]
    pregunta = "¿Dónde están las películas mejor evaluadas?"
    mk = mercados_peliculas()
    if mk.empty:
        return sin_datos(pregunta, "No hay países con suficientes películas calificadas")
    elegidos = [c for c in mk.index if c in SEL_PAISES]
    sobre = [nombre_pais(c) for c in mk.index if mk.loc[c, "bien"] >= k.meta]
    if elegidos:
        titulo = lista_es([f"{nombre_pais(c)} queda {list(mk.index).index(c) + 1}° de {len(mk)}" for c in elegidos])
    elif sobre and US in mk.index:
        titulo = f"Solo {lista_es(sobre)} superan la meta de 30%; EE.UU. queda en {pct(mk.loc[US, 'bien'])}"
    else:
        titulo = f"{len(sobre)} países superan la meta de 30%"
    with tarjeta(pregunta, titulo, "Películas bien evaluadas (nota 7 o más) por país · verde y ✓: supera la meta · "
                                   "★ mercados del KPI K2"):
        datos = mk.head(9)
        extra = [c for c in mk.index if (c == US or c in SEL_PAISES) and c not in datos.index]
        if extra:
            datos = pd.concat([datos, mk.loc[extra]])
        colores = [VERDE if v >= k.meta else INK if c == US else GRIS for c, v in zip(datos.index, datos["bien"])]
        etiquetas = [(f"<b>{nombre_pais(c)}</b>" if c in SEL_PAISES else nombre_pais(c))
                     + (" ★" if c in MERCADOS_PRIORITARIOS else "") for c in datos.index]
        barras(etiquetas, list(datos["bien"]), colores, pct, meta=k.meta, meta_txt="meta 30%",
               textos=[f"{pct(v)} ✓" if v >= k.meta else pct(v) for v in datos["bien"]],
               que="películas bien evaluadas por país, de 0 a 100%; ✓ supera la meta")


def card_k1_generos():
    k = KPI_POR_ID["K1"]
    pregunta = "¿Qué géneros de película comprar?"
    m = fdf[fdf["type"] == "Película"]
    r = ranking_categoria(m, "genres", "rating", "bien", umbral_categoria()) if len(m) else pd.DataFrame()
    if r.empty:
        return sin_datos(pregunta, "No hay géneros con suficientes películas calificadas")
    cumplen = [nombre_genero(g) for g in r.index if r.loc[g, "bien"] >= k.meta]
    with tarjeta(pregunta, f"{len(cumplen)} de {len(r)} géneros superan la meta; {lista_es(cumplen[:3])} lideran y "
                           f"{nombre_genero(r.index[-1])} queda último",
                 "Películas bien evaluadas (nota 7 o más) por género · verde y ✓: supera la meta"):
        barras([nombre_genero(g) for g in r.index], list(r["bien"]), [VERDE if v >= k.meta else GRIS for v in r["bien"]],
               pct, meta=k.meta, meta_txt="meta 30%", alto=min(470, 22 * len(r) + 40),
               textos=[f"{pct(v)} ✓" if v >= k.meta else pct(v) for v in r["bien"]],
               que="películas bien evaluadas por género, de 0 a 100%; ✓ supera la meta")


def card_trayectoria(kid, compacto=False):
    k = KPI_POR_ID[kid]
    pregunta = f"{k.id} · {k.nombre}"
    if k.requiere_sin_filtro_pais and sel_countries:
        return sin_datos(pregunta, "Quite el filtro de país para ver este KPI")
    t = k.por_anio(fdf, min(year_max, ULTIMO_ANIO_COMPLETO))
    t = t[t["anio"] >= year_min]
    if len(t) < 2:
        return sin_datos(pregunta, "Faltan años con datos suficientes")
    sobre = t[t["valor"] >= k.meta]["anio"].tolist()
    ult = t.iloc[-1]
    if sobre:
        seguidos = sobre[-1] - sobre[0] == len(sobre) - 1
        cuando = str(sobre[0]) if len(sobre) == 1 else f"{sobre[0]}-{sobre[-1]}" if seguidos else lista_es([str(a) for a in sobre])
        titulo = f"Ya superó la meta con los estrenos de {cuando}; los de {int(ult['anio'])} quedaron en {pct_meta(ult['valor'], k.meta)}"
    else:
        titulo = f"Nunca llegó a la meta; los estrenos de {int(ult['anio'])} quedaron en {pct_meta(ult['valor'], k.meta)}"
    with tarjeta(pregunta, titulo):
        fig = go.Figure()
        fig.add_hline(y=k.meta, line_dash="dash", line_color=INK, line_width=1.5, layer="below")
        fig.add_annotation(x=0, xref="paper", xanchor="left", y=k.meta, yanchor="bottom",
                           text=f"meta {pct(k.meta)}", showarrow=False, font=dict(size=12, color=INK))
        fig.add_trace(go.Scatter(
            x=t["anio"], y=t["valor"], mode="lines+markers+text", line=dict(color=INK, width=2.5),
            marker=dict(size=7, color=[VERDE if v >= k.meta else INK for v in t["valor"]]),
            text=[pct_meta(v, k.meta) if i == len(t) - 1 else "" for i, v in enumerate(t["valor"])],
            textposition=["bottom center" if v < k.meta else "top center" for v in t["valor"]], textfont=dict(size=12),
            hovertext=[f"Estrenos {a}: {pct(v)}" for a, v in zip(t["anio"], t["valor"])], hoverinfo="text"))
        fig.update_layout(height=190 if compacto else ALTO, **LAYOUT_BASE)
        fig.update_yaxes(range=[0, 1.04], tickformat=".0%", tickvals=[0, .25, .5, .75, 1], gridcolor=GRILLA,
                         zeroline=False)
        fig.update_xaxes(dtick=2, showgrid=False)
        resumen_accesible(f"Gráfico de línea de {k.nombre.lower()} por año de estreno, de 0 a 100%, con la meta en "
                          f"{pct(k.meta)}. " + "; ".join(f"{a}: {pct_meta(v, k.meta)}" for a, v in zip(t["anio"], t["valor"])))
        grafico(fig)


def card_volumen(col, pregunta):
    base = fdf if col == "genres" else fdf_sin_pais
    c = explode(base, col)[col].value_counts()
    if c.empty:
        return sin_datos(pregunta, "Sin datos para este segmento")
    if col == "genres":
        titulo = f"{lista_es([nombre_genero(x) for x in c.index[:2]])} concentran la mayor cantidad de títulos"
        resaltar = set(c.index[:2])
    else:
        elegidos = [x for x in c.index if x in SEL_PAISES]
        foco = elegidos[0] if elegidos else c.index[0]
        titulo = f"{nombre_pais(foco)} aporta {pct(base['country_set'].apply(lambda s: foco in s).mean())} de los títulos"
        resaltar = set(elegidos) if elegidos else {c.index[0]}
    with tarjeta(pregunta, titulo, "Cantidad de títulos · un título con varios géneros o países suma en cada uno"):
        d = c.head(10)
        barras([nombre_cat(col, x) for x in d.index], list(d.values), [INK if x in resaltar else GRIS for x in d.index],
               miles, alto=ALTO, que=f"cantidad de títulos por {'género' if col == 'genres' else 'país'}")


def card_personas(campo):
    nombre = "directores" if campo == "director" else "actores"
    pregunta = f"¿Qué {nombre} tienen más títulos?"
    ex = explode(fdf, campo).join(fdf[["type"]])
    if ex.empty or ex[campo].dropna().empty:
        return sin_datos(pregunta, "Sin datos para este segmento")
    g = ex.groupby(campo).agg(n=("type", "size"), series=("type", lambda s: (s == "Serie").mean()))
    g = g.sort_values("n", ascending=False).head(10)
    nota = ("Títulos por persona · 68% de las series no registra director" if campo == "director"
            else "Títulos por persona · cada título registra hasta 5 actores")
    with tarjeta(pregunta, f"{g.index[0]} lidera con {miles(g['n'].iloc[0])} títulos",
                 nota + " · azul: sobre todo películas; naranjo rayado: sobre todo series"):
        barras(list(g.index), list(g["n"]), [NARANJO if s > 0.5 else AZUL for s in g["series"]], miles, alto=ALTO,
               patrones=["/" if s > 0.5 else "" for s in g["series"]],
               textos=[f"{miles(n)} · {'series' if s > 0.5 else 'películas'}" for n, s in zip(g["n"], g["series"])],
               que=f"cantidad de títulos por persona ({nombre})")


def card_popularidad(fmt_seg="Película", col="genres"):
    nombres = {"genres": "géneros", "country": "países", "language": "idiomas"}
    et = "películas" if fmt_seg == "Película" else "series"
    pregunta = f"¿Qué {nombres[col]} atraen más público?"
    rankings = {}
    for t in ("Película", "Serie"):   # misma escala para películas y series
        b = (fdf_sin_pais if col == "country" else fdf)
        b = b[b["type"] == t]
        rankings[t] = ranking_categoria(b, col, "popularity", "median",
                                        umbral_categoria(sin_pais=col == "country")) if len(b) else pd.DataFrame()
    r = rankings[fmt_seg]
    if r.empty:
        return sin_datos(pregunta, "Sin datos suficientes en este segmento")
    tope = max(x["median"].head(6).max() for x in rankings.values() if not x.empty) * 1.3
    vals = r["median"].head(6)
    parejo = len(vals) >= 3 and vals.iloc[0] / vals.iloc[2] < 1.1
    titulo = (f"En {et}, los {nombres[col]} casi no se diferencian en popularidad" if parejo else
              f"{lista_es([nombre_cat(col, x) for x in vals.index[:2]])} atraen más público en {et}")
    with tarjeta(pregunta, titulo, "Popularidad típica de un título (índice de TMDB) · misma escala en películas y series"):
        barras([nombre_cat(col, x) for x in vals.index], list(vals.values),
               [TYPE_COLORS[fmt_seg] if (i < 2 and not parejo) else GRIS for i in range(len(vals))], f1,
               rango=[0, tope], alto=168, que=f"popularidad típica de {et} por {nombres[col]}")


def card_bien_evaluados(fmt_seg):
    et = "películas" if fmt_seg == "Película" else "series"
    pregunta = "¿Qué géneros gustan más?"
    b = fdf[fdf["type"] == fmt_seg]
    r = ranking_categoria(b, "genres", "rating", "bien", umbral_categoria()) if len(b) else pd.DataFrame()
    if r.empty:
        return sin_datos(pregunta, "Sin datos suficientes en este segmento")
    vals = r["bien"].head(6)
    with tarjeta(pregunta, f"{lista_es([nombre_genero(x) for x in vals.index[:2]])} son los mejor evaluados en {et}",
                 "Títulos bien evaluados (nota 7 o más) por género"):
        barras([nombre_genero(x) for x in vals.index], list(vals.values),
               [TYPE_COLORS[fmt_seg] if i < 2 else GRIS for i in range(len(vals))], pct, alto=168,
               que=f"{et} bien evaluadas por género, de 0 a 100%")


def card_k3_generos():
    k = KPI_POR_ID["K3"]
    pregunta = "¿En qué series falta participación del público?"
    s_ = fdf[fdf["type"] == "Serie"]
    if s_.empty:
        return sin_datos(pregunta, "No hay series en este segmento")
    ex = explode(s_, "genres").join(s_[["vote_count"]])
    g = ex.groupby("genres")["vote_count"].agg(n="size", k3=lambda v: (v >= MIN_VOTES).mean())
    g = g[g["n"] >= umbral_categoria()].sort_values("k3")
    if g.empty:
        return sin_datos(pregunta, "No hay géneros con suficientes series")
    bajos = [nombre_genero(x) for x in g.index[:3]]
    cumplen = int((g["k3"] >= k.meta).sum())
    with tarjeta(pregunta, f"{lista_es(bajos)}, los más bajos; {cumplen} de {len(g)} géneros cumplen",
                 "Series con 10 o más votos por género · verde y ✓: supera la meta de K3"):
        barras([nombre_genero(x) for x in g.index], list(g["k3"]), [VERDE if v >= k.meta else GRIS for v in g["k3"]],
               pct, meta=k.meta, meta_txt="meta 50%", alto=min(330, 19 * len(g) + 30),
               textos=[f"{pct(v)} ✓" if v >= k.meta else pct(v) for v in g["k3"]],
               que="series con 10 o más votos por género, de 0 a 100%; ✓ supera la meta")


def card_series_sin_votos():
    pregunta = "¿Dónde pedir calificaciones primero?"
    sv = series_populares_sin_votos()
    if sv.empty:
        return sin_datos(pregunta, "No hay series populares sin votos en este segmento")
    top = sv.sort_values("popularity", ascending=False).head(9)
    with tarjeta(pregunta, f"{miles(len(sv))} series tienen público, pero todavía no 10 votos",
                 "Series con popularidad sobre la típica y menos de 10 votos · las más populares primero"):
        tabla = pd.DataFrame({
            "Serie": top["title"], "Votos": top["vote_count"].astype(int),
            "Género": top["genres"].fillna("").apply(
                lambda t: ", ".join(nombre_genero(x.strip()) for x in t.split(",")[:2] if x.strip())),
            "País": top["country"].fillna("").apply(
                lambda t: ", ".join(nombre_pais(x.strip()) for x in t.split(",")[:2] if x.strip())),
        })
        st.dataframe(tabla, hide_index=True, width="stretch", height=35 * (len(tabla) + 1) + 3)


def card_peliculas_mercados():
    pregunta = "¿Qué películas de Japón, Corea del Sur y México destacar?"
    prior = frozenset(MERCADOS_PRIORITARIOS)
    m = fdf[(fdf["type"] == "Película") & (fdf["vote_count"] >= MIN_VOTES_TOP)
            & fdf["country_set"].apply(lambda c: not c.isdisjoint(prior))]
    m = m[m["rating"] >= GOOD_RATING]
    if m.empty:
        return sin_datos(pregunta, "No hay películas bien evaluadas de estos mercados en este segmento")
    top = m.sort_values("vote_average", ascending=False).head(9)
    with tarjeta(pregunta, f"{miles(len(m))} películas bien evaluadas de los mercados de K2 respaldan su cuota",
                 f"Nota 7 o más y al menos {MIN_VOTES_TOP} votos · las mejor evaluadas primero"):
        tabla = pd.DataFrame({
            "Película": top["title"], "Nota (0 a 10)": top["vote_average"].apply(f1),
            "País": top["country"].fillna("").apply(
                lambda t: ", ".join(nombre_pais(x.strip()) for x in t.split(",")[:2] if x.strip())),
            "Género": top["genres"].fillna("").apply(
                lambda t: ", ".join(nombre_genero(x.strip()) for x in t.split(",")[:2] if x.strip())),
        })
        st.dataframe(tabla, hide_index=True, width="stretch", height=35 * (len(tabla) + 1) + 3)


def card_rentabilidad_nota():
    pregunta = "¿Invertir en calidad (K1) rinde?"
    f_ = fin.dropna(subset=["rating"])
    if len(f_) < 50:
        return sin_datos(pregunta, "Sin películas suficientes con datos financieros en este segmento")
    cortes = pd.cut(f_["rating"], [0, 5, 6, 7, 8, 10], right=False,
                    labels=["Nota bajo 5", "5 a 6", "6 a 7", "7 a 8", "8 o más"])
    r = f_.groupby(cortes, observed=True)["roi"].apply(lambda v: (v >= 1).mean())
    bien, resto = (f_["roi"][f_["rating"] >= GOOD_RATING] >= 1).mean(), (f_["roi"][f_["rating"] < GOOD_RATING] >= 1).mean()
    with tarjeta(pregunta, f"Las películas bien evaluadas recuperan su presupuesto el {pct(bien)} de las veces; "
                           f"las demás, el {pct(resto)}",
                 f"Películas que recuperan su presupuesto en taquilla, según su nota · {miles(len(f_))} películas con "
                 "datos financieros confiables (sobre todo grandes estudios)"):
        barras(list(r.index.astype(str)), list(r.values),
               [INK if i in ("7 a 8", "8 o más") else GRIS for i in r.index.astype(str)], pct, alto=230,
               que="porcentaje de películas que recuperan su presupuesto según su nota, de 0 a 100%")


def card_rentabilidad_mercado():
    pregunta = "¿Rinden las películas de los mercados de K2?"
    if len(fin) < 50:
        return sin_datos(pregunta, "Sin películas suficientes con datos financieros en este segmento")
    prior = frozenset(MERCADOS_PRIORITARIOS)
    grupo = fin["country_set"].apply(lambda c: "Japón, Corea del Sur y México ★" if not c.isdisjoint(prior)
                                     else "EE.UU." if US in c else "Otros países")
    r = fin.groupby(grupo)["roi"].agg(recupera=lambda v: (v >= 1).mean(), n="size")
    r = r.reindex([g for g in ["Japón, Corea del Sur y México ★", "EE.UU.", "Otros países"] if g in r.index])
    pri = "Japón, Corea del Sur y México ★"
    titulo = (f"Comprar en estos mercados no sacrifica rentabilidad: {pct(r.loc[pri, 'recupera'])} recupera su "
              f"presupuesto, frente a {pct(r.loc['EE.UU.', 'recupera'])} en EE.UU." if pri in r.index and "EE.UU." in r.index
              else "Películas que recuperan su presupuesto por mercado")
    with tarjeta(pregunta, titulo, "Películas que recuperan su presupuesto, por origen · ★ mercados del KPI K2 · "
                                   f"diferencia pequeña y con solo {miles(r.loc[pri, 'n']) if pri in r.index else 0} películas "
                                   "de estos mercados: muestra que no rinden menos, no que rindan más"):
        barras(list(r.index), list(r["recupera"]), [INK if g == pri else GRIS for g in r.index], pct, alto=160,
               que="porcentaje de películas que recuperan su presupuesto por mercado, de 0 a 100%")


def tres(a, b, c):
    c1, c2, c3 = st.columns(3)
    with c1:
        a()
    with c2:
        b()
    with c3:
        c()


def card_top10():
    c = st.container(border=True)
    with c:
        st.markdown('<div class="q">¿Qué títulos destacar en campañas?</div>', unsafe_allow_html=True)
        metrica = segmentos("Ordenar por", ["Más populares", "Mejor evaluados", "Más votados"], "top10_metric",
                            ayuda="Cambia el criterio del ranking")
        if metrica == "Más populares":
            d, col, fmt, nota = fdf.dropna(subset=["popularity"]).nlargest(10, "popularity"), "popularity", f1, \
                "Popularidad (índice de TMDB)"
        elif metrica == "Mejor evaluados":
            d, col, fmt, nota = fdf[fdf["vote_count"] >= MIN_VOTES_TOP].nlargest(10, "vote_average"), "vote_average", f1, \
                f"Nota de 0 a 10 · títulos con al menos {MIN_VOTES_TOP} votos"
        else:
            d, col, fmt, nota = fdf.nlargest(10, "vote_count"), "vote_count", miles, "Cantidad de votos del público"
        if d.empty:
            st.markdown('<div class="accion">Sin datos para este segmento</div>', unsafe_allow_html=True)
            return
        ns = int((d["type"] == "Serie").sum())
        titulo = (f"{ns} de los 10 son series" if ns >= 6 else f"{10 - ns} de los 10 son películas" if ns <= 4
                  else "Películas y series se reparten el top 10")
        st.markdown(f'<div class="accion">{titulo}</div><div class="nota">{nota} · azul: película; naranjo rayado: serie</div>',
                    unsafe_allow_html=True)
        barras(list(d["title"]), list(d[col]), [TYPE_COLORS[t] for t in d["type"]], fmt, alto=ALTO + 10,
               rango=[0, max(d[col]) * 1.5],
               textos=[f"{fmt(v)} · {t.lower()}" for v, t in zip(d[col], d["type"])],
               patrones=[TYPE_PATRON[t] for t in d["type"]], que=f"top 10 de títulos, {metrica.lower()}")


def card_top_peliculas():
    pregunta = "¿Qué películas rinden más?"
    if fin.empty:
        return sin_datos(pregunta, "Sin películas con datos financieros en este segmento")
    with st.container(border=True):
        st.markdown(f'<div class="q">{pregunta}</div>', unsafe_allow_html=True)
        orden = segmentos("Top por", ["Taquilla", "Retorno", "Taquilla con presupuesto bajo"], "fin_top",
                          ayuda="Cambia el criterio del ranking de películas")
        if orden == "Taquilla":
            top, val, fmt, nota = fin.nlargest(10, "revenue"), "revenue", lambda v: f"US$ {miles(v / 1e6)} millones", \
                "Taquilla en millones de dólares"
        elif orden == "Retorno":
            top, val, fmt, nota = fin[fin["budget"] >= MIN_BUDGET_ROI].nlargest(10, "roi"), "roi", \
                lambda v: f"{f1(v)} veces", "Veces que la taquilla cubre el presupuesto (presupuesto desde US$ 1 millón)"
        else:
            q1 = fin["budget"].quantile(0.25)
            top, val, fmt, nota = fin[fin["budget"] <= q1].nlargest(10, "revenue"), "revenue", \
                lambda v: f"US$ {f1(v / 1e6)} millones", \
                f"Taquilla de películas con presupuesto de hasta US$ {f1(q1 / 1e6)} millones"
        st.markdown(f'<div class="accion">«{top["title"].iloc[0]}» encabeza el ranking</div>'
                    f'<div class="nota">{nota}</div>', unsafe_allow_html=True)
        barras(list(top["title"]), list(top[val]), AZUL, fmt, alto=ALTO - 20, que=f"top 10 de películas por {orden.lower()}")


def card_scatter_popularidad():
    pregunta = "¿Lo mejor evaluado es lo más popular?"
    d = fdf.dropna(subset=["rating", "popularity"])
    if d.empty:
        return sin_datos(pregunta, "Sin datos para este segmento")
    rho = {t: g["popularity"].rank().corr(g["rating"].rank()) for t, g in d.groupby("type") if len(g) >= 30}
    with tarjeta(pregunta, "Solo un poco: la nota y la popularidad se relacionan de forma débil",
                 "Hasta 2.000 títulos · popularidad en escala logarítmica · correlación de Spearman: "
                 + ", ".join(f"{'películas' if t == 'Película' else 'series'} {formato_es(f'{v:.2f}')}"
                             for t, v in rho.items())):
        sample = d.sample(min(2000, len(d)), random_state=42)
        fig = px.scatter(sample, x="rating", y="popularity", color="type", symbol="type",
                         color_discrete_map=TYPE_COLORS, symbol_map=TYPE_SYMBOLS, log_y=True, opacity=0.5,
                         labels={"rating": "Nota (0 a 10)", "popularity": "Popularidad (escala log)", "type": ""},
                         hover_data={"title": True})
        fig.update_layout(height=ALTO, **{**LAYOUT_BASE, "showlegend": True},
                          legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0))
        fig.update_xaxes(range=[0, 10], showgrid=False)
        fig.update_yaxes(showgrid=False, tickvals=[1, 10, 100, 1000], ticktext=["1", "10", "100", "1.000"])
        resumen_accesible("Gráfico de dispersión: nota de 0 a 10 en el eje horizontal y popularidad en escala "
                          "logarítmica en el vertical; películas con círculos y series con cuadrados. Correlación de "
                          "Spearman: " + ", ".join(f"{t.lower()}s {formato_es(f'{v:.2f}')}" for t, v in rho.items()) + ".")
        grafico(fig)


def card_tramos_popularidad():
    pregunta = "¿La buena nota atrae público?"
    d = fdf.dropna(subset=["rating"])
    if len(d) < 50:
        return sin_datos(pregunta, "Sin datos suficientes en este segmento")
    cortes = pd.cut(d["rating"], [0, 5, 6, 7, 8, 10], labels=["5 o menos", "5 a 6", "6 a 7", "7 a 8", "8 o más"])
    t = d.groupby([cortes, "type"], observed=True)["popularity"].median().unstack()
    with tarjeta(pregunta, "Los títulos con mejor nota son más populares, en ambos formatos",
                 "Popularidad típica según la nota · azul: películas; naranjo rayado: series · misma escala"):
        fig = go.Figure([go.Bar(name=tp, x=list(t.index.astype(str)), y=t[tp], marker_color=TYPE_COLORS[tp],
                                marker_pattern_shape=TYPE_PATRON[tp], marker_pattern_fgcolor=FONDO, marker_pattern_fillmode="overlay", marker_pattern_solidity=0.35,
                                text=[f1(v) for v in t[tp]], textposition="outside", cliponaxis=False, hoverinfo="skip")
                         for tp in t.columns])
        fig.update_layout(height=ALTO, barmode="group", **LAYOUT_BASE)
        resumen_accesible("Gráfico de barras agrupadas: popularidad típica según la nota del título. "
                          + "; ".join(f"nota {i}: " + ", ".join(f"{tp.lower()}s {f1(t.loc[i, tp])}" for tp in t.columns)
                                      for i in t.index))
        fig.update_yaxes(visible=False, range=[0, t.max().max() * 1.2])
        fig.update_xaxes(title="Nota del título (0 a 10)", title_font=dict(size=12))
        grafico(fig)


def card_tendencia_calificacion():
    pregunta = "¿Cambia la nota con los años?"
    trend = fdf[fdf["release_year"].between(year_min, min(year_max, ULTIMO_ANIO_COMPLETO))].dropna(subset=["rating"])
    trend = trend.groupby(["release_year", "type"])["rating"].mean().reset_index()
    if trend["release_year"].nunique() < 2:
        return sin_datos(pregunta, "Faltan años con datos suficientes")
    with tarjeta(pregunta, "La nota promedio casi no cambia; las series siempre puntúan más alto",
                 "Nota promedio por año de estreno (0 a 10) · línea continua: películas, punteada: series"):
        fig = px.line(trend, x="release_year", y="rating", color="type", line_dash="type",
                      color_discrete_map=TYPE_COLORS, line_dash_map=TYPE_DASH,
                      labels={"release_year": "", "rating": "", "type": ""})
        fig.update_layout(height=ALTO, **LAYOUT_BASE)
        fig.update_yaxes(range=[0, 10], gridcolor=GRILLA)
        resumen_accesible("Gráfico de líneas: nota promedio por año de estreno, de 0 a 10, para películas (línea "
                          "continua) y series (línea punteada).")
        fig.update_xaxes(dtick=2, showgrid=False)
        grafico(fig)


def card_idiomas():
    pregunta = "¿En qué idiomas está el catálogo?"
    comp = fdf.dropna(subset=["language"]).groupby(["language", "type"]).size().unstack(fill_value=0)
    if comp.empty:
        return sin_datos(pregunta, "Sin datos para este segmento")
    comp = comp.loc[comp.sum(axis=1).sort_values(ascending=False).index[:8]]
    lider = comp.index[0]
    with tarjeta(pregunta, f"El {lider} concentra {pct(comp.loc[lider].sum() / len(fdf))} de los títulos",
                 "Cantidad de títulos por idioma principal · azul: películas; naranjo rayado: series"):
        fig = go.Figure([go.Bar(name=tp, y=list(comp.index), x=comp[tp], orientation="h", marker_color=TYPE_COLORS[tp],
                                marker_pattern_shape=TYPE_PATRON[tp], marker_pattern_fgcolor=FONDO, marker_pattern_fillmode="overlay", marker_pattern_solidity=0.35,
                                text=[miles(v) for v in comp[tp]], textposition="outside", cliponaxis=False,
                                hoverinfo="skip") for tp in comp.columns])
        resumen_accesible("Gráfico de barras agrupadas: títulos por idioma principal. " + "; ".join(
            f"{i}: " + ", ".join(f"{miles(comp.loc[i, tp])} {tp.lower()}s" for tp in comp.columns) for i in comp.index))
        fig.update_layout(height=ALTO + 30, barmode="group", bargap=0.25, **LAYOUT_BASE)
        fig.update_xaxes(visible=False, range=[0, comp.max().max() * 1.25])
        fig.update_yaxes(autorange="reversed")
        grafico(fig)


def card_titulos_por_anio():
    pregunta = "¿Creció el catálogo?"
    vol = fdf[fdf["release_year"].between(year_min, year_max)].groupby(["release_year", "type"]).size().unstack(fill_value=0)
    if vol.empty:
        return sin_datos(pregunta, "Sin datos para este segmento")
    with tarjeta(pregunta, "No se puede saber: el catálogo trae la misma cantidad de títulos cada año",
                 "Títulos por año de estreno · azul: películas; naranjo rayado: series"):
        fig = go.Figure([go.Bar(name=tp, x=vol.index, y=vol[tp], marker_color=TYPE_COLORS[tp], hoverinfo="x+y",
                                marker_pattern_shape=TYPE_PATRON[tp], marker_pattern_fgcolor=FONDO, marker_pattern_fillmode="overlay", marker_pattern_solidity=0.35,
                                marker_line=dict(width=1, color=FONDO))   # HIG: separar áreas contiguas de color
                         for tp in vol.columns])
        resumen_accesible("Gráfico de barras apiladas: títulos por año de estreno. " + "; ".join(
            f"{a}: " + ", ".join(f"{vol.loc[a, tp]} {tp.lower()}s" for tp in vol.columns) for a in vol.index))
        fig.update_layout(height=ALTO, barmode="stack", bargap=0.2, **LAYOUT_BASE)
        fig.update_yaxes(showgrid=False, tickformat=",.0f")
        fig.update_xaxes(dtick=2)
        grafico(fig)


def card_scatter_finanzas():
    pregunta = "¿Más presupuesto da más taquilla?"
    if fin.empty:
        return sin_datos(pregunta, "Sin películas con datos financieros en este segmento")
    with tarjeta(pregunta, "En general sí, pero con mucha variación: bajo la línea no se recupera lo invertido",
                 "Una película por punto · escalas logarítmicas · línea punteada: taquilla igual al presupuesto"):
        fig = px.scatter(fin, x="budget", y="revenue", log_x=True, log_y=True, opacity=0.45, hover_data={"title": True},
                         labels={"budget": "Presupuesto (US$)", "revenue": "Taquilla (US$)"})
        lo, hi = min(fin["budget"].min(), fin["revenue"].min()), max(fin["budget"].max(), fin["revenue"].max())
        fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", hoverinfo="skip",
                                 line=dict(color=INK, width=1.5, dash="dot")))
        fig.update_traces(marker_color=AZUL, selector=dict(mode="markers"))
        marcas, textos = [1e4, 1e5, 1e6, 1e7, 1e8, 1e9], ["10 mil", "100 mil", "1 M", "10 M", "100 M", "1.000 M"]
        fig.update_xaxes(tickvals=marcas, ticktext=textos, showgrid=False)
        fig.update_yaxes(tickvals=marcas, ticktext=textos, showgrid=False)
        fig.update_layout(height=ALTO, **LAYOUT_BASE)
        resumen_accesible("Gráfico de dispersión: presupuesto en el eje horizontal y taquilla en el vertical, en "
                          f"escala logarítmica; {miles(len(fin))} películas. Bajo la diagonal están las que no "
                          f"recuperan su presupuesto ({pct((fin['roi'] < 1).mean())}).")
        grafico(fig)


def card_ficha():
    with tarjeta("¿Cómo se calcula cada KPI?", "Fórmula, meta, responsable y decisión de los 3 KPIs",
                 "Misma definición en el dashboard y el notebook (dashboard/streamview/kpis.py), verificada con dashboard/tests/test_kpis.py"):
        tabla = ficha_tecnica()
        st.dataframe(tabla, hide_index=True, width="stretch", height=38 + 35 * len(tabla) + 3)


def card_calidad_datos():
    movies_f = fdf[fdf["type"] == "Película"]
    sin_votos = (fdf["vote_count"] == 0).mean() if len(fdf) else None
    sin_fin = 1 - movies_f["fin_ok"].mean() if len(movies_f) else None
    with tarjeta("¿Qué tan confiables son los datos?",
                 f"{pct(sin_votos)} de los títulos no tiene votos y {pct(sin_fin)} de las películas no tiene finanzas confiables"):
        st.markdown(
            f"- **Nota:** solo cuenta con {MIN_VOTES} o más votos (sin votos, la nota viene en 0). Define K1 y es lo que mide K3.\n"
            "- **Comparaciones:** películas con películas y series con series (las series tienen el triple de popularidad).\n"
            f"- **Finanzas:** solo montos desde US$10.000 y retorno de hasta {MAX_ROI} veces; describen sobre todo a grandes estudios.\n"
            f"- **Duplicados:** se eliminaron {n_series_dup} series repetidas.\n"
            "- **Rankings:** cada categoría necesita al menos 200 títulos (menos con filtros, nunca menos de 30).")


# ==================================================================
# Vistas: cada pestaña cabe en una pantalla
# ==================================================================
def dos(a, b, pesos=(1, 1)):
    c1, c2 = st.columns(pesos)
    with c1:
        a()
    with c2:
        b()


def vista_segmentos():
    fmt_seg = tipo if tipo != "Todos" else segmentos(
        "Comparar dentro de", ["Película", "Serie"], "seg_fmt", ayuda="Compara películas con películas o series con series",
        fmt=lambda t: "Películas" if t == "Película" else "Series")
    dos(lambda: card_popularidad(fmt_seg, "genres"), lambda: card_popularidad(fmt_seg, "country"))
    dos(lambda: card_popularidad(fmt_seg, "language"), lambda: card_bien_evaluados(fmt_seg))


TODOS = ["K1", "K2", "K3"]
VISTAS = {
    "Directorio": [
        ("Resumen", lambda: (fila_kpis(TODOS), dos(card_k1_paises, lambda: card_decisiones(TODOS), (3, 2)))),
        ("Avance hacia la meta", lambda: tres(lambda: card_trayectoria("K1"), lambda: card_trayectoria("K2"),
                                              lambda: card_trayectoria("K3"))),
        ("Catálogo", lambda: dos(lambda: card_volumen("genres", "¿Qué géneros predominan?"),
                                 lambda: card_volumen("country", "¿Qué países producen más?"))),
        ("Rentabilidad", lambda: dos(card_rentabilidad_nota, card_rentabilidad_mercado)),
    ],
    "Contenidos y Adquisición": [
        ("Mercados", lambda: (fila_kpis(["K1", "K2"]), dos(card_k1_paises, lambda: card_trayectoria("K2")))),
        ("Géneros", lambda: dos(card_k1_generos, lambda: card_popularidad("Película", "genres"))),
        ("Directores y actores", lambda: dos(lambda: card_personas("director"), lambda: card_personas("cast"))),
    ],
    "Marketing": [
        ("Participación", lambda: (fila_kpis(["K3"]), dos(card_k3_generos, card_series_sin_votos))),
        ("Qué promover", lambda: dos(card_peliculas_mercados, card_top10)),
        ("Segmentos", vista_segmentos),
    ],
    "Data & Analytics": [
        ("KPIs y calidad de datos", lambda: (fila_kpis(TODOS), dos(card_ficha, card_calidad_datos, (3, 2)))),
        ("Catálogo", lambda: dos(card_idiomas, card_titulos_por_anio)),
        ("Popularidad y nota", lambda: dos(card_scatter_popularidad, card_tramos_popularidad)),
        ("Tendencia", lambda: dos(card_tendencia_calificacion, lambda: card_trayectoria("K3"))),
        ("Finanzas", lambda: dos(card_scatter_finanzas, card_top_peliculas)),
    ],
}

pestanas = VISTAS[perfil]
for tab, (_, contenido) in zip(st.tabs([n for n, _ in pestanas]), pestanas):
    with tab:
        contenido()

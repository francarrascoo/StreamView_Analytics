"""Dashboard ejecutivo interactivo del catálogo de StreamView Analytics.

Streamlit + Plotly. Reutiliza exactamente la misma limpieza de datos que
analisis_exploratorio.ipynb (dedup de show_id, estandarización de géneros,
descarte de "Unknown"), para que las cifras coincidan con las ya verificadas
del notebook.

Uso:
    streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------
# Datos
# ------------------------------------------------------------------
HERE = Path(__file__).resolve().parent  # .resolve() antes de .parent, __file__ puede llegar
DATA = HERE.parent / "data"             # como ruta relativa segun como se invoque streamlit

PALETTE_BLUE = "#2a78d6"    # Película, solo cuando el grafico realmente distingue tipo
PALETTE_ORANGE = "#c85526"  # Serie, idem
PALETTE_NEUTRAL = "#898781"  # "Combinado" (INK_MUTED del notebook), rankings que mezclan ambos
# tipos. En el notebook el azul sirve como tono neutro de magnitud porque cada grafico es una
# imagen suelta sin leyenda Pelicula/Serie cerca. Aca conviven en la misma pagina scrolleable,
# asi que reusar el azul en un grafico combinado se leeria como "esto es de peliculas". Blue/orange
# quedan reservados para donde de verdad hay comparacion por tipo.

# el dataset trae el idioma como codigo ISO 639-1 (el propio notebook lo muestra asi en sus
# graficos, ver images/v17_idiomas_predominantes.png). Se traduce a un nombre legible cuando el
# codigo es estandar, "cn" y "xx" no son codigos ISO 639-1 validos en este dataset y se dejan
# tal cual en vez de adivinar que significan (mismo criterio que dashboard.html).
LANG_NAMES = {
    "af": "afrikáans", "am": "amárico", "ar": "árabe", "as": "asamés", "az": "azerbaiyano",
    "bg": "búlgaro", "bn": "bengalí", "bs": "bosnio", "ca": "catalán",
    "cn": "chino mandarín",  # variante de "zh" para el mismo idioma, se unifican bajo el mismo nombre
    "cs": "checo",
    "cy": "galés", "da": "danés", "de": "alemán", "dz": "dzongkha", "el": "griego",
    "en": "inglés", "es": "español", "et": "estonio", "eu": "euskera", "fa": "persa",
    "fi": "finés", "fr": "francés", "ga": "irlandés", "gl": "gallego", "he": "hebreo",
    "hi": "hindi", "hr": "croata", "ht": "criollo haitiano", "hu": "húngaro", "hy": "armenio",
    "id": "indonesio", "is": "islandés", "it": "italiano", "ja": "japonés", "ka": "georgiano",
    "kk": "kazajo", "kl": "groenlandés", "km": "jemer", "kn": "canarés", "ko": "coreano",
    "ku": "kurdo", "ky": "kirguís", "la": "latín", "lb": "luxemburgués", "lt": "lituano",
    "lv": "letón", "mi": "maorí", "mk": "macedonio", "ml": "malayalam", "mn": "mongol",
    "mr": "maratí", "ms": "malayo", "mt": "maltés", "nb": "noruego bokmål", "ne": "nepalí",
    "nl": "neerlandés", "no": "noruego", "or": "oriya", "pa": "panyabí", "pl": "polaco",
    "ps": "pastún", "pt": "portugués", "ro": "rumano", "ru": "ruso", "si": "cingalés",
    "sk": "eslovaco", "sl": "esloveno", "sr": "serbio", "sv": "sueco", "ta": "tamil",
    "te": "telugu", "th": "tailandés", "tl": "tagalo", "tr": "turco", "uk": "ucraniano",
    "ur": "urdu", "vi": "vietnamita",
    "xx": "sin diálogo",  # codigo de TMDB para contenido sin idioma hablado (animaciones mudas,
                          # piezas ambientales), no es un error de carga
    "yo": "yoruba", "za": "zhuang", "zh": "chino mandarín",
    "zu": "zulú",
}

GENRE_STANDARDIZE = {
    "Action & Adventure": "Action, Adventure",
    "Sci-Fi & Fantasy": "Science Fiction, Fantasy",
    "War & Politics": "War",
}

MIN_N = 200  # mismo umbral que usa el notebook para rankings por categoria (Seccion 4.9-4.14)


def estandarizar_generos(serie):
    def fix(g):
        if pd.isna(g):
            return g
        tokens = [p.strip() for p in g.split(",") if p.strip() != "Unknown"]
        partes = [GENRE_STANDARDIZE.get(t, t) for t in tokens]
        return ", ".join(partes) if partes else None
    return serie.apply(fix)


def explode(df, col):
    return df[[col]].assign(**{col: df[col].dropna().astype(str).str.split(",")}).explode(col).assign(
        **{col: lambda d: d[col].str.strip()}
    )


@st.cache_data
def load_data():
    movies = pd.read_csv(DATA / "netflix_movies_detailed_up_to_2025.csv")
    shows = pd.read_csv(DATA / "netflix_tv_shows_detailed_up_to_2025.csv")
    shows_clean = shows.drop_duplicates(subset="show_id").copy()

    movies["genres"] = estandarizar_generos(movies["genres"])
    shows_clean["genres"] = estandarizar_generos(shows_clean["genres"])
    movies["language"] = movies["language"].map(lambda c: LANG_NAMES.get(c, c))
    shows_clean["language"] = shows_clean["language"].map(lambda c: LANG_NAMES.get(c, c))

    movies["type"] = "Película"
    shows_clean["type"] = "Serie"

    cols = ["title", "type", "country", "genres", "language", "release_year",
            "popularity", "vote_average", "vote_count"]
    combo = pd.concat([movies[cols + ["budget", "revenue"]],
                        shows_clean.reindex(columns=cols + ["budget", "revenue"])],
                       ignore_index=True)
    # budget/revenue en cero se tratan como dato ausente (Seccion 2.5/2.12 del notebook)
    combo.loc[combo["budget"] <= 0, "budget"] = None
    combo.loc[combo["revenue"] <= 0, "revenue"] = None
    return combo


@st.cache_data
def count_series_duplicates():
    """show_id duplicados en el CSV crudo de series, antes del dedup (Seccion 2.3 del notebook).
    Es un dato estatico de calidad de origen, no depende de los filtros activos."""
    shows_raw = pd.read_csv(DATA / "netflix_tv_shows_detailed_up_to_2025.csv")
    return int(shows_raw.duplicated(subset="show_id").sum())


df = load_data()
n_series_dup = count_series_duplicates()

# ------------------------------------------------------------------
# Configuración de página y estilo
# ------------------------------------------------------------------
st.set_page_config(page_title="Catálogo StreamView", page_icon="📊", layout="wide")

st.markdown("""
<style>
div[data-testid="stMetricValue"] { font-family: monospace; font-variant-numeric: tabular-nums; }
h3 { margin-top: 0.3rem !important; }
.tier-note { color: #8a8878; font-size: 0.85rem; margin-bottom: 0.8rem; }
</style>
""", unsafe_allow_html=True)

st.title("Catálogo StreamView")
st.caption("Dashboard ejecutivo · películas y series · datos hasta 2025")

# ------------------------------------------------------------------
# Perfil (stakeholder), Sección 9 del caso
# ------------------------------------------------------------------
# necesidad citada tal cual del caso (docs/Caso_Semestral_STREAMVIEW_ANALYTICS.pdf, Seccion 9),
# no redactada de memoria. "secciones" son las claves de contenido que ese perfil necesita ver,
# el resto del dashboard queda oculto para ese perfil.
ROLES = {
    "Directorio": {
        # fusiona Directorio y Gerencia General (Seccion 9 del caso), el dashboard se redujo a 3
        # perfiles, Directorio absorbe el nivel "junta directiva / gerencia general" completo en
        # vez de separarse en dos radios distintos
        # sin "volumen" a proposito, lo temporal ya lo cubre "tendencia" (calificacion por anio),
        # "volumen" (titulos por anio) le corresponde solo a Marketing, es su unica senal
        # temporal y su necesidad textual lo pide literal ("evolucion temporal del catalogo").
        # Directorio y Marketing lo compartian antes, quedaba el mismo grafico en ambos perfiles.
        "necesita": "Indicadores consolidados, tendencias, comparaciones, recomendaciones "
                    "ejecutivas (apoya decisiones de inversión y crecimiento). Visión global "
                    "del catálogo para la planificación estratégica.",
        "secciones": {"panorama", "scatter", "tendencia", "top10", "finanzas"},
    },
    "Marketing": {
        # sin "panorama" a proposito, ese grafico es por CANTIDAD y la necesidad real de
        # Marketing es "potencial" (calidad/popularidad), que ya cubre "segmento" en exclusiva.
        # Darle panorama tambien sugeriria lo contrario de lo que demuestra el proyecto entero
        # (el genero mas frecuente, Drama, no es el de mayor potencial). "tendencia" (calificacion
        # por anio) se cambio por "volumen" (titulos por anio), que calza mejor con "evolucion
        # temporal DEL CATALOGO" que con una tendencia de calificacion.
        "necesita": "Contenidos más populares, categorías con mayor potencial, evolución "
                    "temporal del catálogo, oportunidades comerciales. Identificar géneros, "
                    "países y contenidos con mayor potencial estratégico.",
        "secciones": {"segmento", "volumen", "top10"},
    },
    "Data & Analytics": {
        # ya incluia diversidad (el aporte de Producto), se mantiene igual, vista completa
        "necesita": "Mantener los dashboards corporativos y asegurar la calidad de la "
                    "información presentada (vista completa, sin recorte).",
        "secciones": {"panorama", "scatter", "volumen", "tendencia", "segmento", "top10",
                      "finanzas", "diversidad"},
    },
}

perfil = st.radio("Perfil", list(ROLES.keys()), horizontal=True, label_visibility="collapsed")
secciones = ROLES[perfil]["secciones"]

st.divider()

# ------------------------------------------------------------------
# Filtros (barra lateral)
# ------------------------------------------------------------------
st.sidebar.header("Filtros")

tipo = st.sidebar.radio("Tipo de contenido", ["Todos", "Película", "Serie"], horizontal=True)

year_min, year_max = st.sidebar.slider(
    "Año de estreno", 2010, 2025, (2010, 2025),
)

all_countries = sorted(explode(df, "country")["country"].dropna().unique().tolist())
sel_countries = st.sidebar.multiselect("País", all_countries)

all_langs = sorted(df["language"].dropna().unique().tolist())
sel_langs = st.sidebar.multiselect("Idioma", all_langs)

all_genres = sorted(explode(df, "genres")["genres"].dropna().unique().tolist())
sel_genres = st.sidebar.multiselect("Género", all_genres)

if st.sidebar.button("Reiniciar filtros"):
    st.rerun()

# ------------------------------------------------------------------
# Aplicar filtros
# ------------------------------------------------------------------
mask = pd.Series(True, index=df.index)
if tipo != "Todos":
    mask &= df["type"] == tipo
mask &= df["release_year"].between(year_min, year_max) | df["release_year"].isna()
if sel_countries:
    pattern = "|".join([c.replace("(", r"\(").replace(")", r"\)") for c in sel_countries])
    mask &= df["country"].fillna("").str.contains(pattern, regex=True)
if sel_langs:
    mask &= df["language"].isin(sel_langs)
if sel_genres:
    pattern_g = "|".join([g.replace("(", r"\(").replace(")", r"\)") for g in sel_genres])
    mask &= df["genres"].fillna("").str.contains(pattern_g, regex=True)

fdf = df[mask]

active = []
if tipo != "Todos":
    active.append(tipo + "s" if tipo == "Película" else tipo + "s")
if (year_min, year_max) != (2010, 2025):
    active.append(f"{year_min}–{year_max}")
active += sel_countries + sel_langs + sel_genres
st.caption(("Filtros activos, " + ", ".join(active)) if active else "Sin filtros activos, mostrando el catálogo completo")
st.caption(f"{len(fdf):,} / {len(df):,} títulos".replace(",", "."))

# ------------------------------------------------------------------
# KPIs
# ------------------------------------------------------------------
n_movies = int((fdf["type"] == "Película").sum())
n_series = int((fdf["type"] == "Serie").sum())
avg_pop = fdf["popularity"].mean()
avg_rating = fdf["vote_average"].mean()
n_countries = explode(fdf, "country")["country"].nunique()
n_langs = fdf["language"].nunique()
n_genres = explode(fdf, "genres")["genres"].nunique()

def miles(n):
    return f"{n:,.0f}".replace(",", ".")


def f1(v):
    return "—" if pd.isna(v) else f"{v:.1f}".replace(".", ",")


# tiles HTML propios en vez de st.metric, que recorta valores largos con "..."
# cuando la columna queda angosta (ej. "16.000 / 15.991" no cabia en 1/6 del ancho)
def render_kpi_row(items):
    st.markdown(
        '<div style="display:flex;gap:0;border-top:1px solid #ddd;border-bottom:1px solid #ddd;">'
        + "".join(
            f'<div style="flex:1;padding:.7rem 1rem;border-right:1px solid #ddd;">'
            f'<div style="font-family:monospace;font-size:1.5rem;font-weight:600;">{v}</div>'
            f'<div style="font-size:.72rem;color:#8a8878;text-transform:uppercase;letter-spacing:.04em;">{l}</div>'
            f"</div>"
            for v, l in items
        )
        + "</div>",
        unsafe_allow_html=True,
    )


render_kpi_row([
    (miles(len(fdf)), "Títulos"),
    (f"{miles(n_movies)} / {miles(n_series)}", "Películas / Series"),
    (f1(avg_pop), "Popularidad prom."),
    (f1(avg_rating), "Calificación prom."),
    (f"{n_countries} / {n_langs}", "Países / Idiomas"),
    (str(n_genres), "Géneros"),
])

st.divider()


# ------------------------------------------------------------------
# Helpers de gráficos
# ------------------------------------------------------------------
def bar_ranking(data, x_col, y_col, color, x_title, hover_fmt="{:,.0f}"):
    if data.empty:
        st.info("Sin datos para esta combinación de filtros.")
        return
    data = data.sort_values(x_col)
    fig = go.Figure(go.Bar(
        x=data[x_col], y=data[y_col], orientation="h",
        marker_color=color,
        text=[hover_fmt.format(v).replace(",", ".") for v in data[x_col]],
        textposition="outside", cliponaxis=False,
    ))
    fig.update_layout(
        height=340, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=x_title, xaxis=dict(range=[0, data[x_col].max() * 1.18]),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def top_by_count(exploded, col, n=10):
    return exploded[col].value_counts().head(n).rename_axis(col).reset_index(name="count")


def top_by_stat(exploded, col, metric_col, stat, n=10, min_n=MIN_N):
    g = exploded.groupby(col)[metric_col].agg(["mean", "median", "count"])
    g = g[g["count"] >= min_n]
    return g.sort_values(stat, ascending=False).head(n).reset_index()


def render_top10_chart(data, metric_col, x_title, hover_fmt="{:,.0f}"):
    """Top 10 por título, un solo grafico (no tabla). Coloreado por tipo, aca si tiene sentido
    porque cada barra es un titulo puntual, no un ranking combinado (mismo criterio que usa el
    notebook en v7_top10_populares/v14_top10_mejor_evaluados, un color por barra segun su tipo)."""
    if data.empty:
        st.info("Sin datos para esta combinación de filtros.")
        return
    data = data.sort_values(metric_col)
    colors = [PALETTE_BLUE if t == "Película" else PALETTE_ORANGE for t in data["type"]]
    fig = go.Figure(go.Bar(
        x=data[metric_col], y=data["title"], orientation="h",
        marker_color=colors,
        text=[hover_fmt.format(v).replace(",", ".") for v in data[metric_col]],
        textposition="outside", cliponaxis=False,
    ))
    fig.update_layout(
        height=380, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=x_title, xaxis=dict(range=[0, data[metric_col].max() * 1.22]),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def genre_leader():
    g = explode(fdf, "genres")["genres"]
    return g.value_counts().idxmax() if len(g) else "—"


def country_leader():
    c = explode(fdf, "country")["country"]
    return c.value_counts().idxmax() if len(c) else "—"


def pct_finance_valid():
    movies_f = fdf[fdf["type"] == "Película"]
    if movies_f.empty:
        return None
    return (movies_f["budget"].notna() & movies_f["revenue"].notna()).mean() * 100


def top_title(metric_col):
    pool = fdf.dropna(subset=[metric_col])
    return pool.sort_values(metric_col, ascending=False).iloc[0]["title"] if len(pool) else "—"


def top_by_stat_leader(col, metric_col, stat, exploded=True):
    data = top_by_stat(explode(fdf, col).join(fdf[[metric_col]]) if exploded
                        else fdf.dropna(subset=[col]), col, metric_col, stat, n=1)
    return data.iloc[0][col] if len(data) else "sin categoría con mínimo de datos"


# ------------------------------------------------------------------
# KPIs propios del perfil activo
# ------------------------------------------------------------------
role_kpis = []
if perfil == "Directorio":
    # Directorio + Gerencia General fusionados (ver ROLES)
    corr_pool = fdf[fdf["vote_count"] >= 10]
    corr = corr_pool["popularity"].corr(corr_pool["vote_average"]) if len(corr_pool) > 1 else None
    role_kpis = [
        (f1(corr) if corr is not None else "—", "Correlación popularidad-calificación"),
        (f1(pct_finance_valid()) + "%" if pct_finance_valid() is not None else "—", "Películas con datos financieros válidos"),
        (country_leader(), "País con más títulos"),
        (genre_leader(), "Género con más títulos"),
    ]
elif perfil == "Marketing":
    # Marketing + Contenidos y Adquisición fusionados (ver ROLES)
    role_kpis = [
        (top_title("popularity"), "Título más popular"),
        (top_by_stat_leader("language", "popularity", "median", exploded=False), "Idioma, mayor popularidad típica"),
        (top_by_stat_leader("country", "popularity", "median"), "País, mayor popularidad típica"),
        (top_by_stat_leader("genres", "vote_average", "mean"), "Género mejor evaluado"),
    ]
elif perfil == "Data & Analytics":
    # incluye el indicador que antes era de Producto (promedio de generos por titulo)
    avg_genres = explode(fdf, "genres").groupby(level=0).size().mean()
    role_kpis = [
        (str(n_series_dup), "Series duplicadas removidas"),
        (f1(pct_finance_valid()) + "%" if pct_finance_valid() is not None else "—", "Presupuesto/ingresos válidos"),
        (f1(avg_genres), "Géneros promedio por título"),
    ]

if role_kpis:
    st.caption(f"Indicadores propios de {perfil}")
    render_kpi_row(role_kpis)
    st.divider()

mostro_algo = False

# ==================================================================
# Panorama general (género, país, idioma por cantidad)
# ==================================================================
if "panorama" in secciones:
    mostro_algo = True
    st.subheader("Panorama general")
    st.markdown(
        '<p class="tier-note">Cuánto produce el catálogo por género, país e idioma.</p>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Top 10 géneros**")
        st.caption("Por cantidad de títulos, según los filtros activos.")
        bar_ranking(top_by_count(explode(fdf, "genres"), "genres"), "count", "genres",
                    PALETTE_NEUTRAL, "Cantidad de títulos")
    with c2:
        st.markdown("**Top 10 países**")
        st.caption("Coproducciones suman en cada país.")
        bar_ranking(top_by_count(explode(fdf, "country"), "country"), "count", "country",
                    PALETTE_NEUTRAL, "Cantidad de títulos")
    with c3:
        st.markdown("**Top 10 idiomas**")
        st.caption("Por cantidad de títulos.")
        lang_counts = fdf["language"].value_counts().head(10).rename_axis("language").reset_index(name="count")
        bar_ranking(lang_counts, "count", "language", PALETTE_NEUTRAL, "Cantidad de títulos")
    st.divider()

# ==================================================================
# Diversidad de géneros por título (cuantos generos trae cada titulo)
# ==================================================================
if "diversidad" in secciones:
    mostro_algo = True
    st.subheader("Diversidad de géneros por título")
    st.markdown(
        '<p class="tier-note">Cuántos géneros distintos trae cada título, relevante para diseñar '
        'filtros y etiquetas de navegación.</p>',
        unsafe_allow_html=True,
    )
    genres_per_title = explode(fdf, "genres").groupby(level=0).size()
    dist = genres_per_title.value_counts().sort_index().rename_axis("n_generos").reset_index(name="count")
    dist["n_generos"] = dist["n_generos"].apply(lambda n: f"{n} género" + ("" if n == 1 else "s"))
    if dist.empty:
        st.info("Sin datos para esta combinación de filtros.")
    else:
        fig = go.Figure(go.Bar(
            x=dist["count"], y=dist["n_generos"], orientation="h",
            marker_color=PALETTE_NEUTRAL,
            text=[miles(v) for v in dist["count"]], textposition="outside", cliponaxis=False,
        ))
        fig.update_layout(
            height=280, margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Cantidad de títulos", xaxis=dict(range=[0, dist["count"].max() * 1.18]),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
    st.divider()

# ==================================================================
# Relación central (popularidad vs calificación)
# ==================================================================
if "scatter" in secciones:
    mostro_algo = True
    st.subheader("Relación central")
    st.markdown(
        '<p class="tier-note">El hallazgo más importante del análisis, la popularidad no depende '
        'de la calificación.</p>',
        unsafe_allow_html=True,
    )
    scatter_df = fdf[(fdf["vote_count"] >= 10) & fdf["popularity"].notna() & fdf["vote_average"].notna()]
    if scatter_df.empty:
        st.info("Sin datos para esta combinación de filtros.")
    else:
        sample = scatter_df.sample(min(2000, len(scatter_df)), random_state=42)
        fig = px.scatter(
            sample, x="vote_average", y="popularity", color="type",
            color_discrete_map={"Película": PALETTE_BLUE, "Serie": PALETTE_ORANGE},
            log_y=True, opacity=0.55,
            labels={"vote_average": "Calificación (0-10)", "popularity": "Popularidad", "type": ""},
            hover_data={"title": True, "vote_average": ":.1f", "popularity": ":.1f"},
        )
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10),
                           plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.markdown("**Popularidad vs calificación**")
        st.caption("Solo títulos con 10+ votos. Muestra de hasta 2.000 puntos para mantener el gráfico legible.")
        st.plotly_chart(fig, use_container_width=True)
    st.divider()

# ==================================================================
# Tendencias en el tiempo (volumen y calificación por año)
# ==================================================================
if "volumen" in secciones or "tendencia" in secciones:
    mostro_algo = True
    st.subheader("Tendencias en el tiempo")
    st.markdown(
        '<p class="tier-note">Cómo evoluciona el catálogo en el tiempo, incluida una alerta de '
        'calidad de datos.</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(2) if ("volumen" in secciones and "tendencia" in secciones) else [st.container()]
    col_idx = 0
    if "volumen" in secciones:
        with cols[col_idx]:
            st.markdown("**Títulos por año de estreno**")
            st.caption("Casi exactamente parejo entre películas y series, no es una tendencia de "
                       "crecimiento real, es una muestra curada.")
            vol = fdf[fdf["release_year"].between(year_min, year_max)].groupby(
                ["release_year", "type"]).size().reset_index(name="count")
            if vol.empty:
                st.info("Sin datos para esta combinación de filtros.")
            else:
                fig = px.line(vol, x="release_year", y="count", color="type", markers=True,
                               color_discrete_map={"Película": PALETTE_BLUE, "Serie": PALETTE_ORANGE},
                               labels={"release_year": "", "count": "Títulos por año", "type": ""})
                fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10),
                                   plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                   legend=dict(orientation="h", yanchor="bottom", y=1.02))
                st.plotly_chart(fig, use_container_width=True)
        col_idx += 1
    if "tendencia" in secciones:
        with cols[col_idx]:
            st.markdown("**Calificación promedio por año de estreno**")
            st.caption("2025 excluido de esta serie, catálogo incompleto para ese año.")
            trend = fdf[(fdf["release_year"].between(year_min, min(year_max, 2024))) & fdf["vote_average"].notna()]
            trend = trend.groupby(["release_year", "type"])["vote_average"].mean().reset_index()
            if trend.empty:
                st.info("Sin datos para esta combinación de filtros.")
            else:
                fig = px.line(trend, x="release_year", y="vote_average", color="type", markers=True,
                               color_discrete_map={"Película": PALETTE_BLUE, "Serie": PALETTE_ORANGE},
                               labels={"release_year": "", "vote_average": "Calificación promedio", "type": ""})
                fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10), yaxis_range=[0, 10],
                                   plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                   legend=dict(orientation="h", yanchor="bottom", y=1.02))
                st.plotly_chart(fig, use_container_width=True)
    st.divider()

# ==================================================================
# Popularidad y calidad por segmento
# ==================================================================
if "segmento" in secciones:
    mostro_algo = True
    st.subheader("Popularidad y calidad por segmento")
    st.markdown(
        '<p class="tier-note">Comparaciones más finas por país, idioma y género. Usan mediana '
        'para popularidad (robusta a títulos virales) y un mínimo de '
        f'{MIN_N} títulos por categoría para evitar que un puñado de casos distorsione el '
        'ranking.</p>',
        unsafe_allow_html=True,
    )
    c6, c7 = st.columns(2)
    with c6:
        st.markdown("**Popularidad típica por país**")
        st.caption(f"Mediana, mínimo {MIN_N} títulos por país.")
        d = top_by_stat(explode(fdf, "country").join(fdf[["popularity"]]), "country", "popularity", "median")
        bar_ranking(d, "median", "country", PALETTE_NEUTRAL, "Popularidad típica (mediana)", "{:.1f}")
    with c7:
        st.markdown("**Popularidad típica por idioma**")
        st.caption(f"Mediana, mínimo {MIN_N} títulos por idioma.")
        d = top_by_stat(fdf.dropna(subset=["language"]), "language", "popularity", "median")
        bar_ranking(d, "median", "language", PALETTE_NEUTRAL, "Popularidad típica (mediana)", "{:.1f}")

    c8, c9 = st.columns(2)
    with c8:
        st.markdown("**Calificación promedio por país**")
        st.caption(f"Mínimo {MIN_N} títulos por país.")
        d = top_by_stat(explode(fdf, "country").join(fdf[["vote_average"]]), "country", "vote_average", "mean")
        bar_ranking(d, "mean", "country", PALETTE_NEUTRAL, "Calificación promedio (0-10)", "{:.1f}")
    with c9:
        st.markdown("**Calificación promedio por género**")
        st.caption(f"Mínimo {MIN_N} títulos por género, los géneros más frecuentes no son "
                   "necesariamente los mejor evaluados.")
        d = top_by_stat(explode(fdf, "genres").join(fdf[["vote_average"]]), "genres", "vote_average", "mean")
        bar_ranking(d, "mean", "genres", PALETTE_NEUTRAL, "Calificación promedio (0-10)", "{:.1f}")
    st.divider()

# ==================================================================
# Detalle operativo y financiero
# ==================================================================
if "top10" in secciones or "finanzas" in secciones:
    mostro_algo = True
    st.subheader("Detalle operativo y financiero")
    st.markdown(
        '<p class="tier-note">Títulos individuales y, cuando corresponde, la relación entre '
        'presupuesto e ingresos. Combina con los filtros de la izquierda para explorar un corte '
        'específico.</p>',
        unsafe_allow_html=True,
    )

    if "top10" in secciones:
        st.markdown("**Top 10 títulos**")
        metric_label = st.radio(
            "Ordenar por", ["Popularidad", "Calificación (mín. 200 votos)", "Votos (blockbusters)"],
            horizontal=True, label_visibility="collapsed",
        )
        if metric_label == "Popularidad":
            pool = fdf.dropna(subset=["popularity"])
            top10 = pool.sort_values("popularity", ascending=False).head(10)
            render_top10_chart(top10, "popularity", "Popularidad", "{:,.1f}")
        elif metric_label.startswith("Calificación"):
            pool = fdf[(fdf["vote_count"] >= MIN_N) & fdf["vote_average"].notna()]
            top10 = pool.sort_values("vote_average", ascending=False).head(10)
            render_top10_chart(top10, "vote_average", "Calificación (0-10)", "{:,.1f}")
        else:
            pool = fdf.dropna(subset=["vote_count"])
            top10 = pool.sort_values("vote_count", ascending=False).head(10)
            render_top10_chart(top10, "vote_count", "Votos", "{:,.0f}")

    if "finanzas" in secciones:
        st.markdown("**Presupuesto vs ingresos**")
        st.caption("Solo películas con ambos valores registrados (22,1% del total). Sin datos de "
                   "presupuesto o ingresos para series. Se excluyen ~0,8% de los casos válidos "
                   "(razón ingreso/presupuesto mayor a 50 veces), candidatos a error de captura "
                   "del dato y no a éxitos financieros reales.")
        fin = fdf[(fdf["type"] == "Película") & fdf["budget"].notna() & fdf["revenue"].notna()]
        fin = fin[(fin["revenue"] / fin["budget"]) <= 50]
        if fin.empty:
            st.info("Sin películas con presupuesto e ingresos válidos en esta combinación de filtros.")
        else:
            fig = px.scatter(
                fin, x="budget", y="revenue", log_x=True, log_y=True, opacity=0.55,
                hover_data={"title": True},
                labels={"budget": "Presupuesto (USD, escala log)", "revenue": "Ingresos (USD, escala log)"},
            )
            fig.update_traces(marker_color=PALETTE_BLUE)
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10),
                               plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

if not mostro_algo:
    st.info("Este perfil no tiene secciones configuradas todavía.")

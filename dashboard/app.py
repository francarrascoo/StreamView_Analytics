"""Dashboard ejecutivo interactivo del catálogo de StreamView Analytics.

Streamlit + Plotly. Reutiliza la misma limpieza de datos que
analisis_exploratorio.ipynb (dedup de show_id, estandarización de géneros,
descarte de "Unknown", "cn" unificado con "zh").

Diseño por audiencia (Storytelling with Data, C. Nussbaumer Knaflic)
--------------------------------------------------------------------
- Directorio y Marketing reciben una vista EXPLICATIVA: pocos gráficos, títulos que
  dicen la conclusión ("títulos de acción", calculados con los datos filtrados para
  que sigan siendo ciertos), barras y líneas, color solo en lo que importa (el resto
  en gris), lenguaje de negocio y ninguna dispersión, treemap ni estadístico técnico.
- Data & Analytics recibe la vista EXPLORATORIA: dispersiones, treemap, áreas, n de
  cada categoría, correlación de Spearman y cobertura de cada indicador. Ahí se
  cumplen los requisitos técnicos del caso (treemap, áreas, dispersión).

Reglas de análisis (cada una evita un sesgo concreto)
-----------------------------------------------------
1. Calificación solo con títulos de MIN_VOTES+ votos. Con 0 votos vote_average
   viene en 0, que no es una nota real.
2. Rankings por país, idioma y género DENTRO de un formato: las series tienen más
   popularidad y calificación que las películas (paradoja de Simpson).
3. Mínimo de títulos por categoría: MIN_N con el catálogo completo, proporcional
   con filtros, nunca menos de MIN_N_FLOOR.
4. Finanzas solo con presupuesto e ingresos >= MIN_FIN_USD y razón <= MAX_ROI.
5. Popularidad con mediana (outliers extremos). Es un índice de TMDB, no reproducciones.

Uso:
    streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------
# Constantes
# ------------------------------------------------------------------
HERE = Path(__file__).resolve().parent  # .resolve() antes de .parent, __file__ puede llegar
DATA = HERE.parent / "data"             # como ruta relativa segun como se invoque streamlit

PALETTE_BLUE = "#2a78d6"     # Película
PALETTE_ORANGE = "#c85526"   # Serie
GRAY = "#c9c7bf"             # contexto (SWD: todo lo que no es el mensaje va en gris)
INK = "#3d3c38"              # referencia destacada sin ser el mensaje (p. ej. EE.UU.)
HIGHLIGHT = "#0f766e"        # enfasis en graficos que no distinguen formato
TYPE_COLORS = {"Película": PALETTE_BLUE, "Serie": PALETTE_ORANGE}

LANG_NAMES = {
    "af": "afrikáans", "am": "amárico", "ar": "árabe", "as": "asamés", "az": "azerbaiyano",
    "bg": "búlgaro", "bn": "bengalí", "bs": "bosnio", "ca": "catalán",
    "cn": "chino mandarín",  # variante de "zh" para el mismo idioma
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
    "ur": "urdu", "vi": "vietnamita", "xx": "sin diálogo", "yo": "yoruba", "za": "zhuang",
    "zh": "chino mandarín", "zu": "zulú",
}

# nombres en español para mostrar; el dato original (ingles) se conserva para filtrar
COUNTRY_ES = {
    "United States of America": "EE.UU.", "United Kingdom": "Reino Unido", "Japan": "Japón",
    "South Korea": "Corea del Sur", "China": "China", "France": "Francia", "Germany": "Alemania",
    "Canada": "Canadá", "India": "India", "Spain": "España", "Italy": "Italia", "Mexico": "México",
    "Australia": "Australia", "Belgium": "Bélgica", "Sweden": "Suecia", "Hong Kong": "Hong Kong",
    "Brazil": "Brasil", "Philippines": "Filipinas", "Turkey": "Turquía", "Russia": "Rusia",
    "Denmark": "Dinamarca", "Norway": "Noruega", "Netherlands": "Países Bajos", "Taiwan": "Taiwán",
    "Thailand": "Tailandia", "Argentina": "Argentina", "Colombia": "Colombia", "Chile": "Chile",
    "Ireland": "Irlanda", "New Zealand": "Nueva Zelanda", "Switzerland": "Suiza", "Poland": "Polonia",
    "Indonesia": "Indonesia", "Egypt": "Egipto", "South Africa": "Sudáfrica", "Austria": "Austria",
    "Finland": "Finlandia", "Portugal": "Portugal", "Israel": "Israel", "Nigeria": "Nigeria",
    "Peru": "Perú", "Czech Republic": "República Checa", "Greece": "Grecia",
}
GENRE_ES = {
    "Drama": "Drama", "Comedy": "Comedia", "Action": "Acción", "Adventure": "Aventura",
    "Animation": "Animación", "Thriller": "Suspenso", "Science Fiction": "Ciencia ficción",
    "Fantasy": "Fantasía", "Crime": "Crimen", "Family": "Familia", "Romance": "Romance",
    "Horror": "Terror", "Mystery": "Misterio", "Documentary": "Documental", "History": "Historia",
    "War": "Bélico", "Music": "Música", "TV Movie": "Película para TV", "Western": "Western",
    "Reality": "Reality", "Kids": "Infantil", "Soap": "Telenovela", "Talk": "Conversación",
    "News": "Noticias",
}

GENRE_STANDARDIZE = {
    "Action & Adventure": "Action, Adventure",
    "Sci-Fi & Fantasy": "Science Fiction, Fantasy",
    "War & Politics": "War",
}

MIN_N = 200          # titulos por categoria sobre el catalogo completo (Seccion 4.6 del notebook)
MIN_N_FLOOR = 30     # piso del umbral con filtros activos
MIN_VOTES = 10       # votos minimos para que una calificacion cuente (Seccion 2.7 del notebook)
MIN_VOTES_TOP = 200  # votos minimos para entrar al top 10 por calificacion
GOOD_RATING = 7.0    # "bien evaluado"
MIN_FIN_USD = 10_000
MAX_ROI = 50
MIN_BUDGET_ROI = 1_000_000
YEAR_RANGE = (2010, 2025)
US = "United States of America"


def nombre_pais(c):
    return COUNTRY_ES.get(c, c)


def nombre_genero(g):
    return GENRE_ES.get(g, g)


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

    for d in (movies, shows_clean):
        d["genres"] = estandarizar_generos(d["genres"])
        d["language"] = d["language"].map(lambda c: LANG_NAMES.get(c, c))
    movies["type"] = "Película"
    shows_clean["type"] = "Serie"

    cols = ["title", "type", "country", "genres", "language", "release_year",
            "popularity", "vote_average", "vote_count"]
    combo = pd.concat([movies[cols + ["budget", "revenue"]],
                        shows_clean.reindex(columns=cols + ["budget", "revenue"])],
                       ignore_index=True)
    combo.loc[combo["budget"] <= 0, "budget"] = None
    combo.loc[combo["revenue"] <= 0, "revenue"] = None
    combo["roi"] = combo["revenue"] / combo["budget"]
    combo["fin_ok"] = ((combo["type"] == "Película")
                       & (combo["budget"] >= MIN_FIN_USD) & (combo["revenue"] >= MIN_FIN_USD)
                       & (combo["roi"] <= MAX_ROI))
    combo["rating"] = combo["vote_average"].where(combo["vote_count"] >= MIN_VOTES)
    combo["country_set"] = combo["country"].fillna("").apply(
        lambda s: frozenset(p.strip() for p in s.split(",") if p.strip()))
    combo["genre_set"] = combo["genres"].fillna("").apply(
        lambda s: frozenset(p.strip() for p in s.split(",") if p.strip()))
    return combo


@st.cache_data
def count_series_duplicates():
    shows_raw = pd.read_csv(DATA / "netflix_tv_shows_detailed_up_to_2025.csv")
    return int(shows_raw.duplicated(subset="show_id").sum())


df = load_data()
n_series_dup = count_series_duplicates()

# ------------------------------------------------------------------
# Página y estilo
# ------------------------------------------------------------------
st.set_page_config(page_title="Catálogo StreamView", page_icon="📊", layout="wide")
st.markdown("""
<style>
h3 { margin-top: 0.3rem !important; }
.tier-note { color: #8a8878; font-size: 0.85rem; margin-bottom: 0.8rem; }
.guia { border-left: 3px solid #898781; padding: .5rem .9rem; margin: .2rem 0 .4rem 0; font-size: .9rem; }
.guia b { font-weight: 600; }
.accion { font-size: 1.05rem; font-weight: 600; margin: .6rem 0 .1rem 0; }
.big { font-size: 2.6rem; font-weight: 700; line-height: 1.1; }
</style>
""", unsafe_allow_html=True)

st.title("Catálogo StreamView")
st.caption("Películas y series estrenadas entre 2010 y 2025 · fuente: catálogo StreamView (metadatos TMDB)")

# ------------------------------------------------------------------
# Perfiles: qué ve cada público y en qué orden
# ------------------------------------------------------------------
ROLES = {
    "Directorio": {
        "pregunta": "¿Cómo está el catálogo y dónde conviene invertir?",
        "uso": "<b>Resumen</b> responde la pregunta en una pantalla. <b>Catálogo</b> y <b>Finanzas</b> "
               "dan el detalle si lo necesita.",
        "pestanas": [
            ("Resumen", ["calidad_audiencia", "mercados", "calidad_popularidad"]),
            ("Catálogo", ["panorama", "tendencia"]),
            ("Finanzas", ["finanzas"]),
        ],
        "tecnico": False,
    },
    "Marketing": {
        "pregunta": "¿Qué contenidos y segmentos promover?",
        "uso": "<b>Oportunidades</b> compara países, idiomas y géneros dentro de un formato. "
               "<b>Títulos destacados</b> lista candidatos a campaña.",
        "pestanas": [
            ("Oportunidades", ["calidad_audiencia", "segmento"]),
            ("Títulos destacados", ["top10"]),
            ("Catálogo", ["volumen_texto", "panorama"]),
        ],
        "tecnico": False,
    },
    "Data & Analytics": {
        "pregunta": "¿Las cifras son confiables antes de publicarlas?",
        "uso": "Vista exploratoria completa, con cobertura y tamaño de muestra de cada indicador. "
               "Incluye las vistas técnicas (dispersión, treemap, áreas).",
        "pestanas": [
            ("Catálogo", ["panorama", "treemap", "diversidad", "volumen"]),
            ("Popularidad y calidad", ["calidad_audiencia", "scatter", "calidad_popularidad", "tendencia",
                                       "mercados", "segmento", "top10"]),
            ("Finanzas", ["finanzas", "finanzas_scatter"]),
        ],
        "tecnico": True,
    },
}

perfil = st.radio("Perfil", list(ROLES.keys()), horizontal=True, label_visibility="collapsed", key="perfil")
ROL = ROLES[perfil]
TECNICO = ROL["tecnico"]
st.markdown(f'<div class="guia"><b>{ROL["pregunta"]}</b><br>{ROL["uso"]}</div>', unsafe_allow_html=True)
st.divider()

# ------------------------------------------------------------------
# Filtros
# ------------------------------------------------------------------
FILTER_DEFAULTS = {"f_tipo": "Todos", "f_anios": YEAR_RANGE, "f_paises": [], "f_idiomas": [], "f_generos": []}
for k, v in FILTER_DEFAULTS.items():
    st.session_state.setdefault(k, v)


def reiniciar_filtros():
    for k, v in FILTER_DEFAULTS.items():
        st.session_state[k] = v


st.sidebar.header("Filtros")
tipo = st.sidebar.radio("Tipo de contenido", ["Todos", "Película", "Serie"], horizontal=True, key="f_tipo")
year_min, year_max = st.sidebar.slider("Año de estreno", *YEAR_RANGE, key="f_anios")
all_countries = sorted(set().union(*df["country_set"]), key=nombre_pais)
sel_countries = st.sidebar.multiselect("País", all_countries, key="f_paises", format_func=nombre_pais,
                                       placeholder="Todos los países")
all_langs = sorted(df["language"].dropna().unique().tolist())
sel_langs = st.sidebar.multiselect("Idioma", all_langs, key="f_idiomas", placeholder="Todos los idiomas")
all_genres = sorted(set().union(*df["genre_set"]), key=nombre_genero)
sel_genres = st.sidebar.multiselect("Género", all_genres, key="f_generos", format_func=nombre_genero,
                                     placeholder="Todos los géneros")
st.sidebar.button("Reiniciar filtros", on_click=reiniciar_filtros)

mask = pd.Series(True, index=df.index)
mask &= df["release_year"].between(year_min, year_max) | df["release_year"].isna()
if sel_langs:
    mask &= df["language"].isin(sel_langs)
if sel_genres:
    sel = frozenset(sel_genres)
    mask &= df["genre_set"].apply(lambda s: not s.isdisjoint(sel))
# los rankings POR PAIS ignoran el filtro de pais y destacan los paises elegidos: si se filtrara, un
# ranking de paises con "Japon" seleccionado solo mostraria a Japon y a sus socios de coproduccion
# (p. ej. EE.UU. con 32%, que son solo coproducciones con Japon), una comparacion sin sentido.
mask_sin_pais = mask.copy()
N_BASE_SIN_PAIS = int(mask_sin_pais.sum())
if sel_countries:
    sel = frozenset(sel_countries)
    mask &= df["country_set"].apply(lambda s: not s.isdisjoint(sel))
# el umbral de las categorias se escala con los filtros de contenido (anio, pais, idioma, genero) pero
# NO con el tipo: comparar dentro de un formato ya es parte del metodo, no un recorte del catalogo.
# Asi, sin filtros el minimo es MIN_N (200) en todas las vistas, igual que en el notebook.
N_BASE = int(mask.sum())
if tipo != "Todos":
    mask &= df["type"] == tipo
    mask_sin_pais &= df["type"] == tipo
fdf = df[mask]
fdf_sin_pais = df[mask_sin_pais]   # base de los rankings por pais
SEL_PAISES = set(sel_countries)


def umbral_categoria(data=None, sin_pais=False):
    base = N_BASE_SIN_PAIS if sin_pais else N_BASE
    proporcional = round(MIN_N * base / len(df))
    return int(min(MIN_N, max(MIN_N_FLOOR, proporcional)))


active = []
if tipo != "Todos":
    active.append("Películas" if tipo == "Película" else "Series")
if (year_min, year_max) != YEAR_RANGE:
    active.append(f"{year_min}–{year_max}")
active += [nombre_pais(c) for c in sel_countries] + sel_langs + [nombre_genero(g) for g in sel_genres]
st.caption(("Filtros activos: " + ", ".join(active)) if active else "Sin filtros: catálogo completo")


# ------------------------------------------------------------------
# Formato
# ------------------------------------------------------------------
def formato_es(texto):
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


def miles(n):
    return formato_es(f"{n:,.0f}")


def f1(v):
    return "—" if v is None or pd.isna(v) else formato_es(f"{v:,.1f}")


def f2(v):
    return "—" if v is None or pd.isna(v) else formato_es(f"{v:.2f}")


def pct(v):
    return "—" if v is None or pd.isna(v) else formato_es(f"{v * 100:.0f}") + "%"


def lista_es(items):
    items = list(items)
    if not items:
        return ""
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " y " + items[-1]


def titulo_accion(texto):
    """SWD: el titulo dice la conclusion, no el contenido del grafico."""
    st.markdown(f'<div class="accion">{texto}</div>', unsafe_allow_html=True)


def render_kpi_row(items):
    st.markdown(
        '<div style="display:flex;flex-wrap:wrap;gap:0;border-top:1px solid #ddd;border-bottom:1px solid #ddd;">'
        + "".join(
            f'<div style="flex:1;min-width:150px;padding:.7rem 1rem;border-right:1px solid #ddd;">'
            f'<div style="font-family:monospace;font-size:1.45rem;font-weight:600;">{v}</div>'
            f'<div style="font-size:.74rem;color:#8a8878;letter-spacing:.02em;">{l}</div>'
            f"</div>"
            for v, l in items
        )
        + "</div>",
        unsafe_allow_html=True,
    )


LAYOUT_BASE = dict(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", separators=",.")


def barras(etiquetas, valores, colores, texto_fmt, eje="", alto=None, hover=None):
    """Barras horizontales al estilo SWD: etiquetas de valor en la barra, sin grilla ni eje x
    en las vistas explicativas (el valor ya esta escrito), eje visible en la vista tecnica."""
    n = len(valores)
    fig = go.Figure(go.Bar(
        x=valores, y=etiquetas, orientation="h", marker_color=colores,
        text=[texto_fmt(v) for v in valores], textposition="outside", cliponaxis=False,
        hovertext=hover, hoverinfo="text" if hover is not None else None,
    ))
    fig.update_layout(height=alto or max(220, 34 * n + 40), margin=dict(l=10, r=10, t=10, b=10),
                      showlegend=False, **LAYOUT_BASE)
    fig.update_xaxes(range=[0, max(valores) * 1.25], title=eje if TECNICO else None,
                     visible=TECNICO, showgrid=TECNICO)
    if texto_fmt is pct:
        fig.update_xaxes(tickformat=".0%")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig)


def ranking_categoria(data, col, metric, stat, min_n):
    base = explode(data, col).join(data[[metric]]) if col in ("country", "genres") else data.dropna(subset=[col])
    g = base.groupby(col)[metric].agg(["mean", "median", "count"])
    if metric == "rating":
        g["bien"] = base.dropna(subset=[metric]).groupby(col)[metric].apply(lambda s: (s >= GOOD_RATING).mean())
    return g[g["count"] >= min_n].sort_values(stat, ascending=False)


def nombre_cat(col, v):
    return nombre_pais(v) if col == "country" else nombre_genero(v) if col == "genres" else v


# ------------------------------------------------------------------
# KPIs generales
# ------------------------------------------------------------------
n_movies = int((fdf["type"] == "Película").sum())
n_series = int((fdf["type"] == "Serie").sum())
cobertura = fdf["rating"].notna().mean() if len(fdf) else None
render_kpi_row([
    (miles(len(fdf)), "Títulos"),
    (f"{miles(n_movies)} / {miles(n_series)}", "Películas / Series"),
    (str(explode(fdf, "country")["country"].nunique()), "Países productores"),
    (str(fdf["language"].nunique()), "Idiomas"),
    (str(explode(fdf, "genres")["genres"].nunique()), "Géneros"),
] + ([(f1(fdf["rating"].mean()), f"Calificación prom. ({MIN_VOTES}+ votos, cubre {pct(cobertura)})"),
      (f1(fdf["popularity"].median()), "Popularidad típica (mediana)")] if TECNICO else []))
st.divider()


# ------------------------------------------------------------------
# Cálculos compartidos
# ------------------------------------------------------------------
def tramos_popularidad(d):
    d = d.dropna(subset=["rating"])
    if len(d) < 50:
        return None
    t = d.groupby(pd.cut(d["rating"], [0, 5, 6, 7, 8, 10], labels=["5 o menos", "5 a 6", "6 a 7", "7 a 8", "8 o más"]),
                  observed=True)["popularity"].median()
    return t if len(t) >= 2 else None


def mercados_peliculas():
    movies_f = fdf_sin_pais[fdf_sin_pais["type"] == "Película"]
    return (ranking_categoria(movies_f, "country", "rating", "bien", umbral_categoria(sin_pais=True))
            if len(movies_f) else pd.DataFrame())


fin = fdf[fdf["fin_ok"]]


# ------------------------------------------------------------------
# KPIs propios del perfil
# ------------------------------------------------------------------
role_kpis = []
if perfil == "Directorio":
    mk = mercados_peliculas()
    tp = tramos_popularidad(fdf[fdf["type"] == "Película"])
    role_kpis = [
        (nombre_pais(mk.index[0]) if len(mk) else "—", "Mercado con películas mejor evaluadas"),
        (f"{f1(tp.iloc[-1] / tp.iloc[0])}×" if tp is not None else "—",
         "Popularidad de las películas muy bien evaluadas frente a las mal evaluadas"),
        (f"{f1(fin['roi'].median())}×" if len(fin) else "—", "Lo que recauda la película típica sobre su presupuesto"),
        (pct((fin["roi"] < 1).mean()) if len(fin) else "—", "Películas que no recuperan lo invertido"),
    ]
elif perfil == "Marketing":
    pool = fdf.dropna(subset=["popularity"])
    role_kpis = [(pool.nlargest(1, "popularity").iloc[0]["title"] if len(pool) else "—", "Título más popular")]
    for t, et in [("Película", "películas"), ("Serie", "series")]:
        d = fdf[fdf["type"] == t]
        if len(d):
            r = ranking_categoria(d, "genres", "popularity", "median", umbral_categoria(d))
            role_kpis.append((nombre_genero(r.index[0]) if len(r) else "—", f"Género más popular en {et}"))
elif perfil == "Data & Analytics":
    rho = {}
    for t in ["Película", "Serie"]:
        d = fdf[fdf["type"] == t].dropna(subset=["rating", "popularity"])
        # Pearson sobre rangos = Spearman, sin depender de scipy
        rho[t] = d["popularity"].rank().corr(d["rating"].rank()) if len(d) >= 30 else None
    sin_votos = int((fdf["vote_count"] == 0).sum())
    movies_f = fdf[fdf["type"] == "Película"]
    role_kpis = [
        (f"{f2(rho['Película'])} / {f2(rho['Serie'])}", "Spearman popularidad-calificación (pelíc. / series)"),
        (str(n_series_dup), "Series duplicadas removidas"),
        (f"{miles(sin_votos)} ({pct(sin_votos / len(fdf) if len(fdf) else None)})", "Títulos sin votos"),
        (pct(movies_f["fin_ok"].mean() if len(movies_f) else None), "Películas con finanzas válidas"),
    ]
if role_kpis:
    render_kpi_row(role_kpis)
    st.divider()


# ==================================================================
# Secciones
# ==================================================================
def sec_calidad_audiencia():
    """Engagement y experiencia (proxies), en lenguaje de negocio."""
    st.subheader("Cómo responde el público")
    st.markdown('<p class="tier-note">Aproximación con la actividad del público en TMDB: el catálogo no trae '
                'reproducciones ni suscripciones, así que la retención no se puede medir con estos datos.</p>',
                unsafe_allow_html=True)
    for t, et in [("Película", "Películas"), ("Serie", "Series")]:
        d = fdf[fdf["type"] == t]
        if d.empty:
            continue
        calif = d["rating"].dropna()
        st.caption(f"{et} · {miles(len(d))} títulos")
        render_kpi_row([
            (pct((d["vote_count"] >= MIN_VOTES).mean()), f"Títulos que el público califica ({MIN_VOTES}+ votos)"),
            (f1(calif.mean()), "Calificación promedio (0 a 10)"),
            (pct((calif >= GOOD_RATING).mean() if len(calif) else None), "Bien evaluados (7 o más)"),
            (f1(d["popularity"].median()), "Popularidad típica"),
        ])


def sec_mercados():
    mk = mercados_peliculas()
    if mk.empty:
        st.info("Sin países con suficientes películas calificadas para esta combinación de filtros.")
        return
    top3 = list(mk.index[:3])
    elegidos = [c for c in mk.index if c in SEL_PAISES]
    if elegidos:
        partes = [f"{nombre_pais(c)} {pct(mk.loc[c, 'bien'])} (puesto {list(mk.index).index(c) + 1} de {len(mk)})"
                  for c in elegidos]
        titulo_accion("Películas bien evaluadas: " + lista_es(partes))
    else:
        us_txt = f"; en EE.UU., {pct(mk.loc[US, 'bien'])}" if US in mk.index else ""
        titulo_accion(f"{lista_es([nombre_pais(c) for c in top3])} tienen la mayor proporción de películas bien "
                      f"evaluadas: {pct(mk.loc[top3[0], 'bien'])} en {nombre_pais(top3[0])}{us_txt}")
    st.caption(f"Porcentaje de películas con calificación 7 o más (sobre 10), entre las que tienen {MIN_VOTES}+ votos. "
               f"Países con al menos {umbral_categoria(sin_pais=True)} películas calificadas."
               + (" Se comparan todos los países; el filtro de país destaca los seleccionados." if SEL_PAISES else ""))
    fuera = [nombre_pais(c) for c in SEL_PAISES if c not in mk.index]
    if fuera:
        st.info(f"{lista_es(sorted(fuera))}: menos de {umbral_categoria(sin_pais=True)} películas calificadas, "
                "no alcanza para compararse con confianza.")
    datos = mk.head(10)
    extra = [c for c in mk.index if (c == US or c in SEL_PAISES) and c not in datos.index]
    if extra:
        datos = pd.concat([datos, mk.loc[extra]])  # referencia y seleccion siempre visibles
    resaltar = set(elegidos) if elegidos else set(top3)
    colores = [PALETTE_BLUE if c in resaltar else INK if c == US else GRAY for c in datos.index]
    barras([nombre_pais(c) for c in datos.index], list(datos["bien"]), colores, pct,
           eje="Películas bien evaluadas (%)",
           hover=[f"{nombre_pais(c)}: {pct(r.bien)} bien evaluadas · prom. {f2(r['mean'])} · n={miles(r['count'])}"
                  for c, r in datos.iterrows()])
    if set(top3) == {"Japan", "South Korea", "Mexico"} and not elegidos:
        st.caption("La ventaja de los tres primeros se mantiene al comparar películas del mismo género y año, y al "
                   "incluir películas con pocos votos. En series no hay una diferencia consistente entre países.")


def sec_calidad_popularidad():
    pares = [(t, et, tramos_popularidad(fdf[fdf["type"] == t])) for t, et in [("Película", "películas"), ("Serie", "series")]]
    pares = [p for p in pares if p[2] is not None]
    if not pares:
        st.info("Sin suficientes títulos calificados para esta combinación de filtros.")
        return
    t0, et0, tp0 = pares[0]
    titulo_accion(f"Las {et0} muy bien evaluadas son {f1(tp0.iloc[-1] / tp0.iloc[0])} veces más populares que las mal "
                  "evaluadas: la calidad ayuda, pero no lo explica todo")
    st.caption("Popularidad típica (mediana) según la calificación del título. Cada formato con su propia escala.")
    cols = st.columns(len(pares))
    for col, (t, et, tp) in zip(cols, pares):
        with col:
            st.markdown(f"**{et.capitalize()}**")
            colores = [TYPE_COLORS[t] if i == len(tp) - 1 else GRAY for i in range(len(tp))]
            fig = go.Figure(go.Bar(x=list(tp.index.astype(str)), y=list(tp.values), marker_color=colores,
                                   text=[f1(v) for v in tp.values], textposition="outside", cliponaxis=False))
            fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, **LAYOUT_BASE)
            fig.update_yaxes(visible=TECNICO, showgrid=TECNICO, range=[0, tp.max() * 1.2], title="Popularidad típica" if TECNICO else None)
            fig.update_xaxes(title="Calificación del título")
            st.plotly_chart(fig)


def sec_scatter():
    st.markdown("**Popularidad vs calificación (vista técnica)**")
    st.caption(f"Solo títulos con {MIN_VOTES}+ votos, muestra aleatoria de hasta 2.000. Escala log en popularidad.")
    d = fdf.dropna(subset=["rating", "popularity"])
    if d.empty:
        st.info("Sin datos para esta combinación de filtros.")
        return
    sample = d.sample(min(2000, len(d)), random_state=42)
    fig = px.scatter(sample, x="rating", y="popularity", color="type", color_discrete_map=TYPE_COLORS, log_y=True,
                     opacity=0.55, labels={"rating": "Calificación (0-10)", "popularity": "Popularidad (log)", "type": ""},
                     hover_data={"title": True, "rating": ":.1f", "popularity": ":.1f"})
    fig.update_yaxes(dtick=1)
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02), **LAYOUT_BASE)
    st.plotly_chart(fig)


def sec_tendencia():
    trend = fdf[fdf["release_year"].between(year_min, min(year_max, 2024))].dropna(subset=["rating"])
    trend = trend.groupby(["release_year", "type"])["rating"].mean().reset_index()
    if trend.empty or trend["release_year"].nunique() < 2:
        st.info("Se necesitan al menos dos años con títulos calificados para mostrar la evolución.")
        return
    cambios = []
    for t, et in [("Película", "películas"), ("Serie", "series")]:
        s = trend[trend["type"] == t].set_index("release_year")["rating"]
        if len(s) >= 2:
            cambios.append(f"{et} {formato_es(f'{s.iloc[-1] - s.iloc[0]:+.1f}')}")
    titulo_accion(f"La calificación cambia poco con los años ({lista_es(cambios)} puntos entre "
                  f"{int(trend['release_year'].min())} y {int(trend['release_year'].max())})")
    st.caption(f"Calificación promedio por año de estreno (0 a 10). Solo títulos con {MIN_VOTES}+ votos; 2025 excluido "
               "porque menos del 10% de sus títulos tiene votos suficientes.")
    fig = px.line(trend, x="release_year", y="rating", color="type", markers=True, color_discrete_map=TYPE_COLORS,
                  labels={"release_year": "", "rating": "Calificación promedio", "type": ""})
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), yaxis_range=[0, 10],
                      legend=dict(orientation="h", yanchor="bottom", y=1.02), **LAYOUT_BASE)
    st.plotly_chart(fig)


def sec_panorama():
    g = explode(fdf, "genres")["genres"].value_counts()
    c = explode(fdf_sin_pais, "country")["country"].value_counts()
    if g.empty or c.empty:
        st.info("Sin datos para esta combinación de filtros.")
        return
    col1, col2 = st.columns(2)
    with col1:
        top2 = list(g.index[:2])
        titulo_accion(f"{lista_es([nombre_genero(x) for x in top2])} son los géneros con más títulos")
        st.caption("Un título con varios géneros suma en cada uno.")
        d = g.head(10)
        barras([nombre_genero(x) for x in d.index], list(d.values),
               [HIGHLIGHT if i < 2 else GRAY for i in range(len(d))], miles, eje="Títulos")
    with col2:
        elegidos = [x for x in c.index if x in SEL_PAISES]
        foco = elegidos[0] if elegidos else c.index[0]
        share = (fdf_sin_pais["country_set"].apply(lambda s: foco in s)).mean()
        puesto = f" (puesto {list(c.index).index(foco) + 1})" if elegidos else ""
        titulo_accion(f"{nombre_pais(foco)} aporta {pct(share)} de los títulos{puesto}")
        st.caption("Las coproducciones suman en cada país."
                   + (" Se comparan todos los países; el filtro de país destaca los seleccionados." if SEL_PAISES else ""))
        d = c.head(10)
        extra = [x for x in elegidos if x not in d.index]
        if extra:
            d = pd.concat([d, c.loc[extra]])
        resaltar = set(elegidos) if elegidos else {c.index[0]}
        barras([nombre_pais(x) for x in d.index], list(d.values),
               [HIGHLIGHT if x in resaltar else GRAY for x in d.index], miles, eje="Títulos")


def sec_treemap():
    st.markdown("**Composición del catálogo por tipo e idioma (vista técnica)**")
    st.caption("Área proporcional a la cantidad de títulos; 8 idiomas principales por tipo, el resto en «otros».")
    comp = fdf.dropna(subset=["language"]).groupby(["type", "language"]).size().reset_index(name="count")
    if comp.empty:
        st.info("Sin datos para esta combinación de filtros.")
        return
    comp["rank"] = comp.groupby("type")["count"].rank(method="first", ascending=False)
    comp.loc[comp["rank"] > 8, "language"] = "otros idiomas"
    comp = comp.groupby(["type", "language"], as_index=False)["count"].sum()
    fig = px.treemap(comp, path=[px.Constant("Catálogo"), "type", "language"], values="count",
                     color="type", color_discrete_map={**TYPE_COLORS, "(?)": "#d9d7d0"})
    fig.update_traces(texttemplate="%{label}<br>%{value:,.0f} · %{percentParent:.0%}",
                      hovertemplate="%{label}<br>%{value:,.0f} títulos<br>%{percentParent:.1%} de %{parent}<extra></extra>",
                      root_color="#d9d7d0", marker=dict(line=dict(width=1, color="white")))
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0), **LAYOUT_BASE)
    st.plotly_chart(fig)


def sec_diversidad():
    st.markdown("**Géneros por título**")
    dist = explode(fdf, "genres").groupby(level=0).size().value_counts().sort_index()
    if dist.empty:
        return
    barras([f"{n} género" + ("" if n == 1 else "s") for n in dist.index], list(dist.values), GRAY, miles, eje="Títulos")


def sec_volumen():
    st.markdown("**Títulos por año de estreno (vista técnica)**")
    st.caption("Áreas apiladas. 1.000 películas + 1.000 series por año: muestra curada, no crecimiento real.")
    vol = fdf[fdf["release_year"].between(year_min, year_max)].groupby(["release_year", "type"]).size().reset_index(name="count")
    if vol.empty:
        return
    fig = px.area(vol, x="release_year", y="count", color="type", color_discrete_map=TYPE_COLORS,
                  labels={"release_year": "", "count": "Títulos por año", "type": ""})
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02), **LAYOUT_BASE)
    st.plotly_chart(fig)


def sec_volumen_texto():
    """SWD: cuando el mensaje es uno o dos numeros, texto simple en vez de grafico."""
    vol = fdf[fdf["release_year"].between(year_min, min(year_max, 2024))].groupby("release_year").size()
    if vol.empty:
        return
    st.markdown(f'<div class="big">{miles(vol.median())}</div>', unsafe_allow_html=True)
    st.markdown(f"títulos por año de estreno, prácticamente el mismo número cada año entre {int(vol.index.min())} y "
                f"{int(vol.index.max())}. El catálogo es una selección curada: no muestra crecimiento ni caída, así que "
                "el año de estreno no sirve para detectar tendencias de consumo.")
    st.divider()


def sec_segmento():
    st.subheader("Popularidad y calidad por segmento")
    if tipo == "Todos":
        fmt_seg = st.radio("Comparar dentro de", ["Película", "Serie"], horizontal=True, key="seg_fmt",
                           format_func=lambda t: "Películas" if t == "Película" else "Series")
    else:
        fmt_seg = tipo
    sdf = fdf[fdf["type"] == fmt_seg]
    min_n = umbral_categoria(sdf)
    color = TYPE_COLORS[fmt_seg]
    et = "películas" if fmt_seg == "Película" else "series"
    st.caption(f"Se compara dentro de {et} porque las series son más populares y mejor evaluadas que las películas: "
               f"mezclarlas premiaría a los segmentos con más series. Mínimo {min_n} títulos por categoría.")
    graficos = [
        ("genres", "popularity", "median", "géneros", "más populares", "Popularidad típica", f1),
        ("country", "popularity", "median", "países", "más populares", "Popularidad típica", f1),
        ("language", "popularity", "median", "idiomas", "más populares", "Popularidad típica", f1),
        ("genres", "rating", "bien", "géneros", "mejor evaluados", "Bien evaluados (%)", pct),
    ]
    for fila in (graficos[:2], graficos[2:]):
        cols = st.columns(2)
        for colw, (col, metric, stat, nombre, adj, eje, fmt) in zip(cols, fila):
            with colw:
                if col == "country":
                    base_pais = fdf_sin_pais[fdf_sin_pais["type"] == fmt_seg]
                    r = ranking_categoria(base_pais, col, metric, stat, umbral_categoria(sin_pais=True))
                else:
                    r = ranking_categoria(sdf, col, metric, stat, min_n)
                if r.empty:
                    st.info(f"Sin {nombre} con suficientes títulos.")
                    continue
                top = [nombre_cat(col, x) for x in r.index[:2]]
                vals = r[stat].head(8)
                # titulo honesto: si las categorias casi no se diferencian, decirlo en vez de nombrar un lider
                parejo = (vals.iloc[0] / vals.iloc[-1] < 1.2) if metric == "popularity" else (vals.iloc[0] - vals.iloc[-1] < 0.05)
                parejo = parejo and len(vals) >= 3
                elegidos = [x for x in r.index if x in SEL_PAISES] if col == "country" else []
                if elegidos:
                    titulo_accion(lista_es([f"{nombre_cat(col, x)} es {list(r.index).index(x) + 1}° de {len(r)}"
                                            for x in elegidos]) + f" en popularidad típica de {et}")
                elif parejo:
                    titulo_accion(f"En {et}, los {nombre} casi no se diferencian: de {fmt(vals.iloc[-1])} a {fmt(vals.iloc[0])}")
                else:
                    titulo_accion(f"{lista_es(top)}: {nombre} {adj} en {et}")
                if metric == "rating":
                    st.caption(f"Porcentaje con calificación 7 o más ({MIN_VOTES}+ votos).")
                d = r.head(8)
                extra = [x for x in elegidos if x not in d.index]
                if extra:
                    d = pd.concat([d, r.loc[extra]])
                colores = ([color if x in elegidos else GRAY for x in d.index] if elegidos
                           else [color if (i < 2 and not parejo) else GRAY for i in range(len(d))])
                barras([nombre_cat(col, x) for x in d.index], list(d[stat]), colores, fmt, eje=eje,
                       hover=[f"{nombre_cat(col, x)}: {fmt(v)} · n={miles(n)}" for x, v, n in zip(d.index, d[stat], d["count"])])
    if fmt_seg == "Serie":
        st.caption("En series, las telenovelas y los programas de conversación tienen popularidad muy alta en TMDB; los "
                   "países con muchos de esos formatos (p. ej. México o Filipinas) suben en el ranking por esa mezcla.")


def sec_top10():
    st.subheader("Títulos destacados")
    metric_label = st.radio("Ordenar por", ["Más populares", f"Mejor evaluados (mín. {MIN_VOTES_TOP} votos)", "Más votados"],
                            horizontal=True, label_visibility="collapsed", key="top10_metric")
    if metric_label == "Más populares":
        d, col, fmt = fdf.dropna(subset=["popularity"]).nlargest(10, "popularity"), "popularity", f1
    elif metric_label.startswith("Mejor"):
        d, col, fmt = fdf[fdf["vote_count"] >= MIN_VOTES_TOP].nlargest(10, "vote_average"), "vote_average", f1
    else:
        d, col, fmt = fdf.nlargest(10, "vote_count"), "vote_count", miles
    if d.empty:
        st.info("Sin datos para esta combinación de filtros.")
        return
    n_series_top = int((d["type"] == "Serie").sum())
    titulo_accion(f"{n_series_top} de los 10 son series" if n_series_top >= 6
                  else f"{10 - n_series_top} de los 10 son películas" if n_series_top <= 4
                  else "Películas y series se reparten el top 10")
    st.caption("Azul: película · naranjo: serie.")
    barras(list(d["title"]), list(d[col]), [TYPE_COLORS[t] for t in d["type"]], fmt, eje=metric_label)


def sec_finanzas():
    st.subheader("Rentabilidad de las películas")
    if fin.empty:
        st.info("Sin películas con datos financieros confiables en esta combinación de filtros.")
        return
    n_mov_f = int((fdf["type"] == "Película").sum())
    st.markdown(f'<p class="tier-note">Solo {miles(len(fin))} películas ({pct(len(fin) / n_mov_f if n_mov_f else None)} '
                'del total) tienen presupuesto y taquilla confiables, sobre todo grandes estudios: las cifras describen a ese '
                'grupo, no a todo el catálogo. Las series no tienen datos financieros. Montos en dólares de cada año.</p>',
                unsafe_allow_html=True)
    render_kpi_row([
        (f1(fin["budget"].sum() / 1e9), "Presupuesto total (miles de millones US$)"),
        (f1(fin["revenue"].sum() / 1e9), "Taquilla total (miles de millones US$)"),
        (f1(fin["budget"].mean() / 1e6), "Presupuesto promedio (millones US$)"),
        (f"US$ {f1(fin['revenue'].sum() / fin['budget'].sum())}", "Recaudados por cada US$1 invertido (total)"),
        (f"{f1(fin['roi'].median())}×", "Recauda la película típica sobre su presupuesto"),
    ])
    st.caption("ROI aproximado = taquilla / presupuesto, como define el caso. No descuenta marketing ni la parte de la "
               "taquilla que no llega al estudio.")

    tramos = pd.cut(fin["roi"], [0, 1, 2, 5, MAX_ROI + 1], right=False,
                    labels=["No recupera lo invertido", "Recupera hasta 2 veces", "Entre 2 y 5 veces", "Más de 5 veces"])
    dist = tramos.value_counts(normalize=True).sort_index()
    titulo_accion(f"{pct(dist.iloc[0])} de las películas con datos no recupera su presupuesto en taquilla")
    barras(list(dist.index.astype(str)), list(dist.values), [INK] + [GRAY] * (len(dist) - 1), pct, eje="Películas (%)")

    orden = st.radio("Top 10 películas por", ["Taquilla", f"Retorno (presupuesto ≥ US$ {miles(MIN_BUDGET_ROI / 1e6)} M)",
                                              "Taquilla con presupuesto bajo"],
                     horizontal=True, key="fin_top")
    if orden == "Taquilla":
        top = fin.nlargest(10, "revenue")
        barras(list(top["title"]), list(top["revenue"] / 1e6), PALETTE_BLUE, lambda v: f"US$ {miles(v)} M", eje="Taquilla")
    elif orden.startswith("Retorno"):
        top = fin[fin["budget"] >= MIN_BUDGET_ROI].nlargest(10, "roi")
        barras(list(top["title"]), list(top["roi"]), PALETTE_BLUE, lambda v: f"{f1(v)}×", eje="Taquilla / presupuesto")
    else:
        q1 = fin["budget"].quantile(0.25)
        top = fin[fin["budget"] <= q1].nlargest(10, "revenue")
        st.caption(f"Presupuesto bajo: el 25% de películas con menor presupuesto (US$ {f1(q1 / 1e6)} M o menos).")
        barras(list(top["title"]), list(top["revenue"] / 1e6), PALETTE_BLUE, lambda v: f"US$ {f1(v)} M", eje="Taquilla")


def sec_finanzas_scatter():
    st.markdown("**Presupuesto vs taquilla (vista técnica)**")
    st.caption("Escalas logarítmicas. Sobre la línea punteada están las películas que recuperan su inversión.")
    if fin.empty:
        return
    fig = px.scatter(fin, x="budget", y="revenue", log_x=True, log_y=True, opacity=0.55, hover_data={"title": True},
                     labels={"budget": "Presupuesto (USD, log)", "revenue": "Taquilla (USD, log)"})
    lo = min(fin["budget"].min(), fin["revenue"].min())
    hi = max(fin["budget"].max(), fin["revenue"].max())
    fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", hoverinfo="skip",
                             line=dict(color="#8a8878", width=1, dash="dot")))
    fig.update_traces(marker_color=PALETTE_BLUE, selector=dict(mode="markers"))
    marcas = [1e4, 1e5, 1e6, 1e7, 1e8, 1e9]
    textos = ["10 mil", "100 mil", "1 M", "10 M", "100 M", "1.000 M"]
    fig.update_xaxes(tickvals=marcas, ticktext=textos)
    fig.update_yaxes(tickvals=marcas, ticktext=textos)
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, **LAYOUT_BASE)
    st.plotly_chart(fig)


SECCIONES = {
    "calidad_audiencia": sec_calidad_audiencia, "mercados": sec_mercados,
    "calidad_popularidad": sec_calidad_popularidad, "scatter": sec_scatter, "tendencia": sec_tendencia,
    "panorama": sec_panorama, "treemap": sec_treemap, "diversidad": sec_diversidad, "volumen": sec_volumen,
    "volumen_texto": sec_volumen_texto, "segmento": sec_segmento, "top10": sec_top10,
    "finanzas": sec_finanzas, "finanzas_scatter": sec_finanzas_scatter,
}

pestanas = st.tabs([nombre for nombre, _ in ROL["pestanas"]])
for tab, (_, secciones) in zip(pestanas, ROL["pestanas"]):
    with tab:
        for i, s in enumerate(secciones):
            if i:
                st.divider()
            SECCIONES[s]()

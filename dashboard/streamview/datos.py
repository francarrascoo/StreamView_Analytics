"""Carga, limpieza e integración del catálogo de StreamView.

Única fuente de la limpieza de datos: la usan el dashboard (dashboard/app.py) y el
notebook (notebooks/analisis_exploratorio.ipynb), de modo que ambos productos
entregan las mismas cifras.

Reglas de calidad (cada una evita un sesgo concreto, ver Sección 2 del notebook):
1. Calificación solo con MIN_VOTES+ votos: con 0 votos vote_average viene en 0.
2. Rankings por país, idioma y género dentro de un mismo formato (paradoja de Simpson).
3. Mínimo de títulos por categoría para entrar a un ranking.
4. Finanzas solo con presupuesto e ingresos >= MIN_FIN_USD y retorno <= MAX_ROI.
5. Popularidad con mediana (valores extremos). Es un índice de TMDB, no reproducciones.
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
DATA = RAIZ / "data"
ARCHIVO_PELICULAS = "netflix_movies_detailed_up_to_2025.csv"
ARCHIVO_SERIES = "netflix_tv_shows_detailed_up_to_2025.csv"

MIN_N = 200          # títulos por categoría sobre el catálogo completo
MIN_N_FLOOR = 30     # piso del umbral con filtros activos
MIN_VOTES = 10       # votos mínimos para que una calificación cuente
MIN_VOTES_TOP = 200  # votos mínimos para entrar al top 10 por calificación
GOOD_RATING = 7.0    # "bien evaluado"
MIN_FIN_USD = 10_000
MAX_ROI = 50
MIN_BUDGET_ROI = 1_000_000
YEAR_RANGE = (2010, 2025)
ULTIMO_ANIO_COMPLETO = 2024  # 2025 tiene menos del 10% de títulos con votos suficientes
US = "United States of America"
MERCADOS_PRIORITARIOS = ("Japan", "South Korea", "Mexico")

GENRE_STANDARDIZE = {
    "Action & Adventure": "Action, Adventure",
    "Sci-Fi & Fantasy": "Science Fiction, Fantasy",
    "War & Politics": "War",
}

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

# nombres en español para mostrar; el dato original (inglés) se conserva para filtrar
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
    """Una fila por valor de una columna con valores separados por coma (país, género, elenco)."""
    return df[[col]].assign(**{col: df[col].dropna().astype(str).str.split(",")}).explode(col).assign(
        **{col: lambda d: d[col].str.strip()}
    )


def _conjunto(s):
    return frozenset(p.strip() for p in s.split(",") if p.strip())


def cargar_catalogo(data_dir=DATA):
    """Devuelve (catálogo integrado, n° de series duplicadas removidas).

    Una fila por título (31.991): 16.000 películas y 15.991 series únicas.
    """
    data_dir = Path(data_dir)
    movies = pd.read_csv(data_dir / ARCHIVO_PELICULAS)
    shows = pd.read_csv(data_dir / ARCHIVO_SERIES)
    n_dup = int(shows.duplicated(subset="show_id").sum())
    shows = shows.drop_duplicates(subset="show_id").copy()

    for d in (movies, shows):
        d["genres"] = estandarizar_generos(d["genres"])
        d["language"] = d["language"].map(lambda c: LANG_NAMES.get(c, c))
    movies["type"] = "Película"
    shows["type"] = "Serie"

    cols = ["title", "type", "director", "cast", "country", "genres", "language", "release_year",
            "popularity", "vote_average", "vote_count"]
    combo = pd.concat([movies[cols + ["budget", "revenue"]],
                       shows.reindex(columns=cols + ["budget", "revenue"])],
                      ignore_index=True)
    combo.loc[combo["budget"] <= 0, "budget"] = None
    combo.loc[combo["revenue"] <= 0, "revenue"] = None
    combo["roi"] = combo["revenue"] / combo["budget"]
    combo["fin_ok"] = ((combo["type"] == "Película")
                       & (combo["budget"] >= MIN_FIN_USD) & (combo["revenue"] >= MIN_FIN_USD)
                       & (combo["roi"] <= MAX_ROI))
    combo["rating"] = combo["vote_average"].where(combo["vote_count"] >= MIN_VOTES)
    combo["country_set"] = combo["country"].fillna("").apply(_conjunto)
    combo["genre_set"] = combo["genres"].fillna("").apply(_conjunto)
    # mediana de popularidad de cada formato sobre el catálogo COMPLETO: es una referencia fija,
    # para que el KPI de visibilidad no cambie de vara al filtrar
    combo["pop_mediana_formato"] = combo.groupby("type")["popularity"].transform("median")
    return combo, n_dup

# StreamView Analytics · Visual Analytics del catálogo (EP5)

Solución de visualización para StreamView Analytics, plataforma de streaming que necesita decidir **qué contenido
adquirir, qué promover y dónde invertir** a partir de su catálogo de películas y series. Proyecto de ADY1104
Visualización de Datos (Duoc UC). Esta versión corresponde a la **EP5: revisión crítica y optimización** de la
solución desarrollada durante el semestre, y es la misma que se defiende en la EP6.

**Equipo:** Felipe Ahumada Silva · Francisca Carrasco Lozano

## Qué cambió en EP5

La observación central de la revisión fue que **confundíamos métricas con KPIs**: el dashboard mostraba cifras
("26% bien evaluadas", "Japón", "1,9×") sin una meta contra la cual juzgarlas. En EP5:

- Definimos **3 KPIs con meta, plazo, umbral de alerta, responsable y decisión** (`dashboard/streamview/kpis.py`), uno
  por cada decisión central del caso: qué cine adquirir (K1), de qué mercados (K2) y cómo medir la participación del
  público en series (K3). El resto del tablero es evidencia o contexto de esos tres KPIs.
- El dashboard muestra cada KPI con su **estado** escrito (cumple / en riesgo / no cumple), un **gráfico de bala**
  contra la meta, la **trayectoria** por año y las **decisiones** que gatilla.
- Agregamos el perfil **Contenidos y Adquisición**, las preguntas del caso que faltaban (directores y actores), la
  vista de **participación** para Marketing (series populares sin votos suficientes) y la **rentabilidad** como
  evidencia de que invertir en calidad (K1) y en esos mercados (K2) rinde.
- Corregimos contraste, tipografía, unidades y el uso exclusivo del color.

El detalle de los 43 cambios, con el problema, la mejora, el fundamento y la evidencia, está en
[`entregables/evidencias/registro_cambios.md`](entregables/evidencias/registro_cambios.md).

## KPIs

Metas a **diciembre de 2026**, medidas trimestralmente sobre cada extracción del catálogo. Son supuestos del caso
definidos por el equipo a partir de la línea base y de cohortes de estreno que ya las alcanzaron
(K1 en 2019-2021, K2 en 2020) o están a punto de hacerlo (K3: 49,7% en 2024).
Estado: **cumple** si alcanza la meta; **en riesgo** si queda hasta 15% (relativo) bajo la meta; **no cumple** si
queda más abajo.

| KPI | Fórmula | Línea base | Meta | Estado | Responsable |
|---|---|---|---|---|---|
| K1 Películas bien evaluadas | películas con calificación ≥ 7 / películas con 10+ votos | 25,8% | ≥ 30% | En riesgo | Contenidos y Adquisición |
| K2 Películas de mercados de alto desempeño | películas de Japón, Corea del Sur o México / películas con país | 13,5% | ≥ 18% | No cumple | Contenidos y Adquisición |
| K3 Series que el público califica | series con 10+ votos / series | 38,4% | ≥ 50% | No cumple | Producto (con Marketing) |

Las cifras descriptivas (total de títulos, países, idiomas, presupuesto total, etc.) se presentan como
**métricas de contexto**: no tienen meta, así que no son KPIs. La rentabilidad (63,6% de las películas recupera
su presupuesto) tampoco es un KPI: solo 21,7% de las películas tiene datos financieros confiables. Se usa como
evidencia: las bien evaluadas recuperan su presupuesto el 77% de las veces y las demás el 58%.

## Estructura del repositorio

```text
StreamView_Analytics/
├── README.md
├── dashboard/
│   ├── app.py                dashboard interactivo (Streamlit + Plotly)
│   ├── requirements.txt      dependencias del proyecto
│   ├── streamview/
│   │   ├── datos.py          carga, limpieza e integración (fuente única para dashboard y notebook)
│   │   └── kpis.py           definición de los 3 KPIs: fórmula, meta, alerta, responsable, decisión
│   └── tests/
│       └── test_kpis.py      verificación técnica: KPIs consistentes con los datos
├── data/                     los dos CSV oficiales del caso, sin modificar
├── docs/                     caso semestral y guía de defensa EP6
├── entregables/
│   ├── Informe_Ejecutivo_EP5_StreamView_Analytics.pdf
│   ├── Presentacion_EP6_StreamView_Analytics.pptx / .pdf
│   ├── evidencias/
│   │   ├── registro_cambios.md   43 cambios: problema, mejora, fundamento, resultado, evidencia
│   │   ├── antes/            capturas de la versión EP4 (commit 221f72f)
│   │   ├── despues/          capturas de la versión EP5 (modo claro)
│   │   ├── despues_oscuro/   capturas de la versión EP5 en modo oscuro
│   │   ├── comparativas/     antes/después lado a lado
│   │   ├── escenarios/       5 escenarios con filtros activos
│   │   └── figuras/          figuras del informe
│   ├── fuente/               fuente del informe y la presentación, y scripts que regeneran evidencias y PDF
│   └── (entregables de etapas anteriores: EV1, EP3, EP4)
├── images/                   los 17 PNG que genera el notebook
└── notebooks/
    └── analisis_exploratorio.ipynb   auditoría de calidad, métricas, KPIs y 17 visualizaciones
```

## Fuentes de datos

Los dos datasets oficiales del caso, en `data/` y sin modificar:

- `netflix_movies_detailed_up_to_2025.csv`: 16.000 películas, 18 columnas.
- `netflix_tv_shows_detailed_up_to_2025.csv`: 16.000 filas, 16 columnas (15.991 series únicas: 9 duplicados por
  `show_id`).

Ambos son metadatos de TMDB (popularidad, votos, calificación, presupuesto, ingresos) del catálogo de StreamView,
estrenos 2010-2025. Se integran en una tabla de 31.991 títulos con una columna de formato (película o serie).
**No contienen reproducciones, suscripciones ni datos de usuarios**, así que la retención no se puede medir: el
engagement se aproxima con la participación del público en TMDB (K3).

Reglas de calidad aplicadas en todo el proyecto (detalle en la Sección 2 del notebook):

1. **Calificación solo con 10 o más votos.** El 14% de los títulos no tiene votos y su calificación viene en 0.
2. **Comparar países, idiomas y géneros dentro de un mismo formato.** Las series tienen el triple de popularidad
   típica que las películas; mezclarlas produce una paradoja de Simpson.
3. **Finanzas solo con montos ≥ US$10.000 y retorno ≤ 50 veces.** Hay presupuestos de US$1. Quedan 3.468
   películas (21,7%); por eso la rentabilidad se presenta como evidencia y no como KPI.
4. **Popularidad con mediana** (valores extremos); categorías con al menos 200 títulos para entrar a un ranking;
   2025 fuera de las tendencias (menos del 10% de sus títulos tiene votos suficientes).

## Cómo ejecutar

Requiere Python 3.9 o superior. Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r dashboard/requirements.txt
```

### Dashboard

```bash
streamlit run dashboard/app.py
```

Queda disponible en `http://localhost:8501`. También funciona con `cd dashboard && streamlit run app.py`. Solo
necesita `streamlit`, `pandas` y `plotly`; el resto de `dashboard/requirements.txt` es para el notebook y para
regenerar evidencias.

### Verificación técnica

```bash
python dashboard/tests/test_kpis.py
```

Comprueba que el catálogo integrado tenga 31.991 títulos, que cada línea base declarada coincida con los datos,
que meta y alerta sean coherentes, que los estados se asignen bien y que los filtros recalculen los KPIs.

### Notebook

```bash
cd notebooks
jupyter notebook analisis_exploratorio.ipynb
# o, para regenerar todas las salidas y los 17 PNG de images/:
python -m nbconvert --to notebook --execute --inplace analisis_exploratorio.ipynb
```

### Regenerar las evidencias antes/después

Con el dashboard corriendo en `http://localhost:8501` y Google Chrome instalado:

```bash
cd entregables/fuente
python capturar_evidencias.py --url http://localhost:8501 --salida ../evidencias/despues
python capturar_escenarios.py --url http://localhost:8501 --salida ../evidencias/escenarios
python capturar_figuras.py --url http://localhost:8501 --salida ../evidencias/figuras
python comparativas.py
```

Para las capturas del "antes", se ejecuta lo mismo sobre la versión EP4 (`git checkout 221f72f -- dashboard/app.py`
en una copia del repositorio) con `--salida ../evidencias/antes`.

## Funcionamiento del dashboard

Diseñado con los principios de *Storytelling with Data* (C. Nussbaumer Knaflic) y siete reglas: todo se lee de
un vistazo y sin scroll (cada pestaña cabe en una pantalla de 1440 × 900); lo importante va arriba a la izquierda;
una frase arriba dice la conclusión; cada pregunta va en su tarjeta con un solo gráfico; sin jerga y con pocas
cifras; barras para comparar magnitudes y nada en 3D; y las mismas escalas y colores en todas las pantallas.
Además aplica las *Human Interface Guidelines* de Apple: sigue la apariencia del sistema (modo claro u oscuro),
usa la fuente del sistema, controles segmentados para elegir vista y orden, un resumen en texto de cada gráfico
para lectores de pantalla, y nunca distingue solo por color (el estado va escrito, la raya de la meta marca lo que la supera y las series van rayadas).

Arriba, un control segmentado de vista adapta pestañas, KPIs y nivel de detalle al público:

| Perfil | Pregunta que responde | Pestañas | KPIs |
|---|---|---|---|
| Directorio (ejecutivo) | ¿Cumplimos las metas y dónde invertir? | Resumen · Avance hacia la meta · Catálogo · Rentabilidad | K1, K2, K3 |
| Contenidos y Adquisición (analítico) | ¿Qué mercados y géneros adquirir? | Mercados · Géneros · Directores y actores | K1, K2 |
| Marketing | ¿Cómo aumentar la participación del público y qué destacar? | Participación · Qué promover · Segmentos | K3 |
| Data & Analytics (técnico) | ¿Las cifras son confiables? | KPIs y calidad de datos · Catálogo · Popularidad y nota · Tendencia · Finanzas | K1, K2, K3 + ficha técnica |

- **Frase principal:** arriba a la izquierda, la conclusión de la vista, recalculada con los filtros.
- **Tarjetas de KPI:** valor, estado (texto + color), meta y puntos que faltan, con un gráfico de bala
  (barra = valor, raya vertical = meta, tramos grises = no cumple / en riesgo / cumple). Al pasar el mouse se ven
  la fórmula y el responsable.
- **Una tarjeta por pregunta:** la pregunta en gris, la respuesta como título y un solo gráfico o tabla.
- **¿Qué hacer ahora?:** por cada KPI fuera de meta, el responsable y la acción acordada.
- **Filtros** (botón arriba a la derecha): tipo, rango de años, país, idioma y género. Recalculan la frase
  principal, KPIs, estados, gráficos, títulos y decisiones; la línea bajo la frase resume los filtros activos y,
  cuando hay filtros, aparece el botón **Quitar filtros**. El filtro de país destaca en vez de
  recortar los rankings por país. K2 no se evalúa con filtro de país (mide justamente la mezcla de países) y el
  dashboard lo explica. Un botón reinicia los filtros.
- **Mismas escalas y colores en todas las pantallas:** todo porcentaje va de 0 a 100%; azul = película,
  naranjo rayado = serie, verde = supera la meta (a la derecha de la raya), gris = contexto, tinta = énfasis (EE.UU.); verde, ámbar y
  rojo, siempre con texto, solo para el estado de un KPI. Barras para comparar magnitudes, líneas solo para el tiempo y
  dispersión solo para relaciones (vista técnica).

## Entregables

- `entregables/Informe_Ejecutivo_EP5_StreamView_Analytics.pdf`: informe ejecutivo final de la EP5. Fuente:
  `entregables/fuente/informe_ep5.html`; se regenera con `python entregables/fuente/generar_pdf.py`.
- `entregables/Presentacion_EP6_StreamView_Analytics.pptx` (y su versión `.pdf`): presentación ejecutiva para la
  defensa EP6, con notas del orador. Fuente: `entregables/fuente/presentacion_ep6.js` (pptxgenjs).
- `docs/Guia_Defensa_EP6.md`: guion de la demostración y preguntas cruzadas por indicador de la rúbrica.
- `entregables/Infografia_Mercados_StreamView.pdf`, informe EP3, presentaciones EP4 y EV1: etapas anteriores,
  que se conservan como referencia del antes/después.
